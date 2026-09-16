from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.database import ActivityHistory, SessionLocal, init_db
from app.schemas import ExecuteRequest, HealthResponse, OrganizeRequest, PlanRequest, ScanRequest, VerifyRequest
from app.services.executor_v2 import execute_plan, iter_execute_plan
from app.services.organizer import organize_photos, scan_photos
from app.services.planner_v2 import OperationPlan
from app.services.report_v2 import build_report
from app.services.review_gate import filter_review_queue
from app.services.verifier import verify_files

app = FastAPI(title="Safe Photo Organizer", description="Developed by Udara Irunika")
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static"), name="static")


def record_history(category: str, source: str, details: dict) -> None:
    init_db()
    db = SessionLocal()
    try:
        db.add(ActivityHistory(category=category, source=source, details=details))
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def read_index() -> str:
    with open(Path(__file__).resolve().parent / "static" / "index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {"status": "ok", "app": "Safe Photo Organizer"}


@app.post("/api/scan")
def api_scan(payload: ScanRequest) -> dict:
    source_root = Path(payload.source).expanduser()
    if not source_root.exists() or not source_root.is_dir():
        raise HTTPException(status_code=400, detail="Source folder does not exist or is not a directory.")

    scan = scan_photos(source_root)
    return {
        "source": str(source_root),
        "scan": scan,
    }


@app.post("/api/organize")
def api_organize(payload: OrganizeRequest) -> dict:
    source_root = Path(payload.source).expanduser()
    destination_root = Path(payload.destination).expanduser()

    if not source_root.exists() or not source_root.is_dir():
        raise HTTPException(status_code=400, detail="Source folder does not exist or is not a directory.")
    if source_root == destination_root:
        raise HTTPException(status_code=400, detail="Source and destination must differ.")
    if destination_root.is_relative_to(source_root):
        raise HTTPException(status_code=400, detail="Destination cannot be inside the source folder.")

    result = organize_photos(source_root, destination_root, dry_run=payload.dry_run)
    return result


@app.post("/api/plan")
def api_plan(payload: PlanRequest) -> dict:
    source_root = Path(payload.source).expanduser()
    if not source_root.exists() or not source_root.is_dir():
        raise HTTPException(status_code=400, detail="Source folder does not exist or is not a directory.")

    plan = OperationPlan(source_root).build()
    record_history("plan", str(source_root), {
        "media_count": plan["summary"].get("total", 0),
        "summary": plan["summary"],
    })
    record_history("directories", str(source_root), {
        "folders": plan.get("scan", {}).get("folder_paths", []),
        "count": max(plan.get("scan", {}).get("folders", 0) - 1, 0),
    })
    record_history("file_names", str(source_root), {
        "files": [item.get("name") or Path(item["source"]).name for item in plan.get("plan", [])],
    })
    return plan


@app.post("/api/execute")
def api_execute(payload: ExecuteRequest) -> dict:
    source_root = Path(payload.source).expanduser()
    if not source_root.exists() or not source_root.is_dir():
        raise HTTPException(status_code=400, detail="Source folder does not exist or is not a directory.")

    plan = OperationPlan(source_root).build()
    review = filter_review_queue(plan)
    execution = execute_plan(plan, dry_run=payload.dry_run)
    report = build_report(plan, execution)
    record_history("dry_run" if payload.dry_run else "execute_approved", str(source_root), {
        "report": report,
        "execution": execution["summary"],
    })

    return {
        "review": review,
        "execution": execution,
        "report": report,
    }


@app.post("/api/execute/stream")
def api_execute_stream(payload: ExecuteRequest) -> StreamingResponse:
    source_root = Path(payload.source).expanduser()
    if not source_root.exists() or not source_root.is_dir():
        raise HTTPException(status_code=400, detail="Source folder does not exist or is not a directory.")

    plan = OperationPlan(source_root).build()
    review = filter_review_queue(plan)

    def events() -> Iterator[str]:
        yield json.dumps({
            "type": "started",
            "total": len(plan.get("plan", [])),
            "summary": plan.get("summary", {}),
        }) + "\n"

        for event in iter_execute_plan(plan, dry_run=payload.dry_run):
            if event["type"] == "complete":
                execution = event["execution"]
                yield json.dumps({
                    "type": "complete",
                    "review": review,
                    "execution": execution,
                    "report": build_report(plan, execution),
                }) + "\n"
                record_history("dry_run" if payload.dry_run else "execute_approved", str(source_root), {
                    "report": build_report(plan, execution),
                    "execution": execution["summary"],
                })
            else:
                yield json.dumps(event) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")


@app.post("/api/verify")
def api_verify(payload: VerifyRequest) -> dict:
    result = verify_files(payload.source, payload.destination)
    return result


@app.get("/api/preview")
def api_preview(path: str) -> FileResponse:
    media_path = Path(path).expanduser()
    if not media_path.exists() or not media_path.is_file():
        raise HTTPException(status_code=404, detail="Preview file does not exist.")

    media_type, _ = mimetypes.guess_type(media_path.name)
    if not media_type or not (media_type.startswith("image/") or media_type.startswith("video/")):
        raise HTTPException(status_code=400, detail="Preview is only available for image and video files.")

    return FileResponse(media_path, media_type=media_type, content_disposition_type="inline")


@app.get("/api/about-image")
def api_about_image() -> FileResponse:
    about_image = Path(__file__).resolve().parent.parent / "photo_2026-09-06_20-37-22.jpg"
    if not about_image.exists() or not about_image.is_file():
        raise HTTPException(status_code=404, detail="About image does not exist.")
    return FileResponse(about_image, media_type="image/jpeg", content_disposition_type="inline")


@app.get("/api/status")
def api_status() -> dict:
    return {"status": "ready", "message": "Application is ready."}


@app.get("/api/history")
def api_history() -> dict:
    init_db()
    db = SessionLocal()
    try:
        records = db.query(ActivityHistory).order_by(ActivityHistory.created_at.desc()).limit(100).all()
        history = {
            "plan": [],
            "directories": [],
            "execute_approved": [],
            "dry_run": [],
            "file_names": [],
        }
        for record in records:
            if record.category in history:
                history[record.category].append({
                    "id": record.id,
                    "source": record.source,
                    "created_at": record.created_at.isoformat(),
                    "details": record.details or {},
                })
        return history
    finally:
        db.close()


@app.delete("/api/history")
def api_clear_history() -> dict[str, int | str]:
    init_db()
    db = SessionLocal()
    try:
        deleted = db.query(ActivityHistory).delete()
        db.commit()
        return {"status": "cleared", "deleted": deleted}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

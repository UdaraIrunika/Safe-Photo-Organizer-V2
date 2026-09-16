from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Iterator

from app.services.verifier import sha256_file


def _unique_target(path: Path) -> Path:
    if not path.exists():
        return path

    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def iter_execute_plan(plan: dict[str, Any], *, dry_run: bool = True) -> Iterator[dict[str, Any]]:
    items = plan.get("plan", [])
    results = []
    summary = {
        "total": 0,
        "copied": 0,
        "verified": 0,
        "duplicates": 0,
        "failed": 0,
        "skipped": 0,
    }

    total_items = len(items)
    for completed, item in enumerate(items, start=1):
        if item.get("status") in {"DATE_CONFLICT", "REVIEW_REQUIRED"}:
            summary["skipped"] += 1
            result = {**item, "execution_status": "SKIPPED_REVIEW"}
            results.append(result)
            yield {"type": "progress", "completed": completed, "total": total_items, "item": result, "summary": summary.copy()}
            continue

        source = Path(item["source"])
        destination = Path(item["planned_destination"])
        summary["total"] += 1

        if dry_run:
            result = {**item, "execution_status": "PLANNED"}
            results.append(result)
            yield {"type": "progress", "completed": completed, "total": total_items, "item": result, "summary": summary.copy()}
            continue

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if sha256_file(source) == sha256_file(destination):
                    summary["duplicates"] += 1
                    summary["skipped"] += 1
                    result = {**item, "execution_status": "DUPLICATE_ALREADY_EXISTS"}
                    results.append(result)
                    yield {"type": "progress", "completed": completed, "total": total_items, "item": result, "summary": summary.copy()}
                    continue
                destination = _unique_target(destination)

            shutil.copy2(source, destination)
            if sha256_file(source) == sha256_file(destination):
                summary["copied"] += 1
                summary["verified"] += 1
                result = {**item, "execution_status": "VERIFIED", "final_destination": str(destination)}
            else:
                summary["failed"] += 1
                result = {**item, "execution_status": "HASH_MISMATCH", "final_destination": str(destination)}
        except Exception:
            summary["failed"] += 1
            result = {**item, "execution_status": "FAILED", "final_destination": str(destination)}

        results.append(result)
        yield {"type": "progress", "completed": completed, "total": total_items, "item": result, "summary": summary.copy()}

    yield {"type": "complete", "execution": {"summary": summary, "results": results}}


def execute_plan(plan: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
    execution = None
    for event in iter_execute_plan(plan, dry_run=dry_run):
        if event["type"] == "complete":
            execution = event["execution"]

    return execution or {"summary": {}, "results": []}

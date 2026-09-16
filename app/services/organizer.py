from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from app.metadata import SUPPORTED_IMAGE_EXTENSIONS, get_photo_date
from app.services.verifier import sha256_file


def ensure_safe_destination(source_root: str | Path, destination_root: str | Path) -> None:
    source = Path(source_root).resolve()
    destination = Path(destination_root).resolve()

    if source == destination:
        raise ValueError("Source and destination must be different.")
    if destination.is_relative_to(source):
        raise ValueError("Destination cannot be inside the source folder.")


def _generate_unique_destination(path: Path) -> Path:
    if not path.exists():
        return path

    suffix = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{suffix}{path.suffix}")
        if not candidate.exists():
            return candidate
        suffix += 1


def build_destination_path(source_root: Path, destination_root: Path, file_path: Path, photo_date: str) -> Path:
    relative = file_path.relative_to(source_root)
    parent = relative.parent
    return destination_root / parent / photo_date / file_path.name


def scan_photos(source_root: str | Path) -> dict[str, Any]:
    source = Path(source_root)
    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source}")

    folders = 0
    total_files = 0
    supported_photos = 0
    exif_dates = 0
    fallback_dates = 0
    unsupported_files = 0
    errors = 0
    items: list[dict[str, Any]] = []

    for current, dirs, files in __import__("os").walk(source):
        dirs[:] = [d for d in dirs if not Path(current, d).is_symlink()]
        folders += 1
        for file_name in files:
            file_path = Path(current) / file_name
            total_files += 1
            if file_path.is_symlink():
                continue

            suffix = file_path.suffix.lower()
            if suffix not in SUPPORTED_IMAGE_EXTENSIONS:
                unsupported_files += 1
                continue

            supported_photos += 1
            try:
                metadata = get_photo_date(file_path)
                if metadata["source"] == "EXIF":
                    exif_dates += 1
                else:
                    fallback_dates += 1
                items.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "date": metadata["date"],
                    "source": metadata["source"],
                    "relative": str(file_path.relative_to(source)),
                })
            except Exception:
                errors += 1

    return {
        "folders": folders,
        "total_files": total_files,
        "supported_photos": supported_photos,
        "exif_dates": exif_dates,
        "fallback_dates": fallback_dates,
        "unsupported_files": unsupported_files,
        "errors": errors,
        "items": items,
    }


def organize_photos(source_root: str | Path, destination_root: str | Path, dry_run: bool = True) -> dict[str, Any]:
    ensure_safe_destination(source_root, destination_root)
    source = Path(source_root).resolve()
    destination = Path(destination_root).resolve()
    results = []
    summary = {
        "total": 0,
        "copied": 0,
        "verified": 0,
        "duplicates": 0,
        "failed": 0,
        "skipped": 0,
    }

    scan = scan_photos(source)
    for item in scan["items"]:
        source_file = Path(item["path"])
        date_value = item["date"]
        destination_file = build_destination_path(source, destination, source_file, date_value)
        planned_destination = destination_file
        status = "PLANNED"

        if destination_file.exists():
            if sha256_file(source_file) == sha256_file(destination_file):
                status = "DUPLICATE_ALREADY_EXISTS"
            else:
                candidate = _generate_unique_destination(destination_file)
                planned_destination = candidate
                status = "NAME_CONFLICT"

        if dry_run:
            summary["total"] += 1
            if status == "DUPLICATE_ALREADY_EXISTS":
                summary["duplicates"] += 1
            results.append({
                "source": str(source_file),
                "destination": str(planned_destination),
                "status": status,
                "date": date_value,
                "date_source": item["source"],
                "relative_path": item["relative"],
            })
            continue

        try:
            if status == "DUPLICATE_ALREADY_EXISTS":
                summary["duplicates"] += 1
                summary["skipped"] += 1
                summary["total"] += 1
                results.append({
                    "source": str(source_file),
                    "destination": str(planned_destination),
                    "status": status,
                    "date": date_value,
                    "date_source": item["source"],
                    "relative_path": item["relative"],
                })
                continue

            planned_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, planned_destination)
            source_hash = sha256_file(source_file)
            destination_hash = sha256_file(planned_destination)
            result_status = "VERIFIED" if source_hash == destination_hash else "HASH_MISMATCH"
            if result_status == "VERIFIED":
                summary["copied"] += 1
                summary["verified"] += 1
            else:
                summary["failed"] += 1
            summary["total"] += 1
            results.append({
                "source": str(source_file),
                "destination": str(planned_destination),
                "status": result_status,
                "date": date_value,
                "date_source": item["source"],
                "relative_path": item["relative"],
            })
        except Exception:
            summary["failed"] += 1
            summary["total"] += 1
            results.append({
                "source": str(source_file),
                "destination": str(planned_destination),
                "status": "FAILED",
                "date": date_value,
                "date_source": item["source"],
                "relative_path": item["relative"],
            })

    return {
        "scan": scan,
        "summary": summary,
        "results": results,
    }

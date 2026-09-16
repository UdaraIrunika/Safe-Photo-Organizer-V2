from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.metadata import SUPPORTED_IMAGE_EXTENSIONS
from app.services.date_folders import is_date_folder

SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp"}
SUPPORTED_MEDIA_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS


def scan_media_root(source_root: str | Path) -> dict[str, Any]:
    source = Path(source_root).resolve()
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"Source path does not exist: {source}")

    folders = 0
    total_files = 0
    supported_media = 0
    unsupported_files = 0
    errors = 0
    folder_paths: list[str] = []
    items: list[dict[str, Any]] = []

    for current, dirs, files in os.walk(source):
        current_path = Path(current)
        dirs[:] = [
            d for d in dirs
            if not (current_path / d).is_symlink() and not is_date_folder(current_path / d)
        ]
        folders += 1
        folder_paths.append(str(current_path.relative_to(source)) if current_path != source else ".")

        for file_name in files:
            file_path = current_path / file_name
            total_files += 1

            if file_path.is_symlink():
                continue

            suffix = file_path.suffix.lower()
            if suffix not in SUPPORTED_MEDIA_EXTENSIONS:
                unsupported_files += 1
                continue

            supported_media += 1
            items.append(
                {
                    "path": str(file_path),
                    "name": file_path.name,
                    "relative": str(file_path.relative_to(source)),
                    "media_type": "IMAGE" if suffix in SUPPORTED_IMAGE_EXTENSIONS else "VIDEO",
                }
            )

    return {
        "folders": folders,
        "subfolders": max(folders - 1, 0),
        "folder_paths": folder_paths,
        "total_files": total_files,
        "supported_media": supported_media,
        "unsupported_files": unsupported_files,
        "errors": errors,
        "items": items,
    }

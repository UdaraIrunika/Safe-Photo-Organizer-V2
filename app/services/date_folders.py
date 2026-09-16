from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

DATE_FOLDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_date_folder(path: str | Path) -> bool:
    name = Path(path).name
    if not DATE_FOLDER_RE.fullmatch(name):
        return False

    try:
        year, month, day = map(int, name.split("-"))
        datetime(year, month, day)
        return True
    except ValueError:
        return False


def build_organized_path(source_root: str | Path, file_path: str | Path, detected_date: str) -> Path | None:
    source = Path(source_root).resolve()
    candidate = Path(file_path)

    if not candidate.is_absolute():
        candidate = source / candidate

    try:
        relative = candidate.relative_to(source)
    except ValueError:
        return None

    if relative.parts and is_date_folder(relative.parts[-2]) if len(relative.parts) > 1 else False:
        return None

    if not detected_date:
        return None

    return source / relative.parent / detected_date / candidate.name

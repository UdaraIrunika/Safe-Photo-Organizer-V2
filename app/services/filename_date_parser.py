from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


DATE_PATTERNS = [
    re.compile(r"(?<!\d)(\d{4})(\d{2})(\d{2})(?:[_-](\d{6}))?(?!\d)", re.IGNORECASE),
    re.compile(r"(?<!\d)(\d{4})[-_.](\d{2})[-_.](\d{2})(?:[-_.](\d{2})[-_.](\d{2})[-_.](\d{2}))?(?!\d)", re.IGNORECASE),
    re.compile(r"(?<!\d)(\d{8})(?!\d)", re.IGNORECASE),
    re.compile(r"(?<!\d)(\d{4})[-_.](\d{2})[-_.](\d{2})[-_.](\d{2})[-_.](\d{2})[-_.](\d{2})(?!\d)", re.IGNORECASE),
]


def _valid_date(year: int, month: int, day: int) -> bool:
    try:
        datetime(year, month, day)
        return True
    except ValueError:
        return False


def _extract_date_from_string(value: str) -> str | None:
    if not value:
        return None

    text = value.replace("\\", "/")
    text = text.strip()
    if not text:
        return None

    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue

        groups = match.groups()
        if len(groups) >= 3 and all(g is not None and g.isdigit() for g in groups[:3]):
            year, month, day = [int(g) for g in groups[:3]]
            if _valid_date(year, month, day):
                return f"{year:04d}-{month:02d}-{day:02d}"

        if len(groups) == 1 and groups[0] is not None and groups[0].isdigit():
            digits = groups[0]
            if len(digits) == 8:
                year = int(digits[0:4])
                month = int(digits[4:6])
                day = int(digits[6:8])
                if _valid_date(year, month, day):
                    return f"{year:04d}-{month:02d}-{day:02d}"

    return None


def detect_filename_date(file_name: str | Path, parent_folder: str | None = None) -> dict | None:
    text = str(file_name)
    if parent_folder:
        parent_text = str(parent_folder)
        parent_date = _extract_date_from_string(parent_text)
        if parent_date:
            return {"date": parent_date, "source": "FILENAME", "confidence": "MEDIUM", "evidence": parent_text}

    candidate = _extract_date_from_string(Path(text).name)
    if candidate is None:
        return None

    if "IMG-" in text.upper() or "WA" in text.upper() or "WHATSAPP" in text.upper():
        source = "WHATSAPP_FILENAME"
    elif "SCREENSHOT" in text.upper():
        source = "SCREENSHOT_FILENAME"
    elif "IMG_" in text.upper() or "PXL_" in text.upper() or "PHOTO_" in text.upper() or "VID_" in text.upper():
        source = "FILENAME"
    else:
        source = "FILENAME"

    return {
        "date": candidate,
        "source": source,
        "confidence": "HIGH",
        "evidence": Path(text).name,
    }

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".tif",
    ".tiff",
    ".bmp",
    ".gif",
}


def _parse_exif_date(raw_value: Any) -> str | None:
    if raw_value is None:
        return None

    value = str(raw_value).strip()
    if not value:
        return None

    value = value.replace("\x00", "")
    if isinstance(raw_value, bytes):
        value = raw_value.decode("utf-8", errors="ignore").strip()

    for fmt in (
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(value).date().isoformat()
    except ValueError:
        return None


def get_photo_date(path: str | Path) -> dict[str, str]:
    file_path = Path(path)

    try:
        with Image.open(file_path) as image:
            exif_data = image.getexif()
            for key_name in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
                if key_name in exif_data:
                    value = exif_data.get(key_name)
                    parsed = _parse_exif_date(value)
                    if parsed:
                        return {"date": parsed, "source": "EXIF"}
    except Exception:
        pass

    try:
        modified = file_path.stat().st_mtime
        return {
            "date": datetime.fromtimestamp(modified).date().isoformat(),
            "source": "FILESYSTEM",
        }
    except OSError as exc:
        raise ValueError(f"Unable to read date metadata for {file_path}: {exc}") from exc

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from app.services.date_engine import DateEngine
from app.services.date_folders import build_organized_path
from app.services.scanner_v2 import scan_media_root


class OperationPlan:
    def __init__(self, source_root: str | Path) -> None:
        self.source_root = Path(source_root).resolve()
        self.plan_items: list[dict[str, Any]] = []
        self.summary: dict[str, int] = {
            "total": 0,
            "planned": 0,
            "duplicates": 0,
            "conflicts": 0,
            "review_required": 0,
            "failed": 0,
        }

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def build(self) -> dict[str, Any]:
        scan = scan_media_root(self.source_root)
        engine = DateEngine()

        for item in scan["items"]:
            source_path = Path(item["path"])
            detection = engine.detect(source_path)
            planned_dest = build_organized_path(
                self.source_root,
                source_path,
                detection["date"] or "REVIEW_REQUIRED",
            )

            record = {
                "source": str(source_path),
                "relative_path": item["relative"],
                "media_type": item["media_type"],
                "detected_date": detection["date"],
                "date_source": detection["source"],
                "confidence": detection["confidence"],
                "evidence": detection.get("evidence", []),
                "conflicts": detection.get("conflicts", []),
                "planned_destination": str(planned_dest) if planned_dest else None,
                "status": "PLANNED",
                "sha256": self._sha256(source_path),
            }

            if detection["date"] is None:
                record["status"] = "REVIEW_REQUIRED"
                self.summary["review_required"] += 1
            elif detection.get("conflicts"):
                record["status"] = "DATE_CONFLICT"
                self.summary["conflicts"] += 1

            self.plan_items.append(record)
            self.summary["total"] += 1
            if record["status"] == "PLANNED":
                self.summary["planned"] += 1

        return {
            "source_root": str(self.source_root),
            "scan": scan,
            "plan": self.plan_items,
            "summary": self.summary,
        }

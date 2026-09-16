from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.metadata import get_photo_date
from app.services.filename_date_parser import detect_filename_date


@dataclass
class CandidateDate:
    date: str
    source: str
    confidence: str
    evidence: str
    rank: int


class DateEngine:
    def __init__(self) -> None:
        self.providers = [
            self._exif_provider,
            self._filename_provider,
            self._filesystem_provider,
        ]

    def _exif_provider(self, file_path: str | Path) -> list[CandidateDate]:
        try:
            metadata = get_photo_date(file_path)
        except Exception:
            return []

        if not metadata or not metadata.get("date"):
            return []

        if metadata.get("source") not in {"EXIF", "XMP", "EMBEDDED_METADATA"}:
            return []

        return [
            CandidateDate(
                date=metadata["date"],
                source=metadata.get("source", "EXIF"),
                confidence="VERY_HIGH",
                evidence=str(file_path),
                rank=1,
            )
        ]

    def _filename_provider(self, file_path: str | Path) -> list[CandidateDate]:
        path = Path(file_path)
        filename = detect_filename_date(path.name, parent_folder=str(path.parent))
        if not filename:
            return []

        return [
            CandidateDate(
                date=filename["date"],
                source=filename["source"],
                confidence=filename["confidence"],
                evidence=filename["evidence"],
                rank=2,
            )
        ]

    def _filesystem_provider(self, file_path: str | Path) -> list[CandidateDate]:
        file_path = Path(file_path)
        try:
            file_date = datetime.fromtimestamp(file_path.stat().st_mtime).date().isoformat()
        except OSError:
            return []

        return [
            CandidateDate(
                date=file_date,
                source="FILESYSTEM_MODIFIED",
                confidence="LOW",
                evidence=str(file_path),
                rank=8,
            )
        ]

    def detect(self, file_path: str | Path) -> dict[str, Any]:
        candidates: list[CandidateDate] = []
        for provider in self.providers:
            candidates.extend(provider(file_path))

        if not candidates:
            return {
                "date": None,
                "source": "UNKNOWN",
                "confidence": "REVIEW_REQUIRED",
                "evidence": [],
                "conflicts": [],
            }

        best = sorted(candidates, key=lambda item: item.rank)[0]
        unique_dates = {c.date for c in candidates}
        conflicts = [
            {"source": c.source, "date": c.date, "confidence": c.confidence}
            for c in candidates
            if c.date != best.date
        ]

        return {
            "date": best.date,
            "source": best.source,
            "confidence": best.confidence,
            "evidence": [
                {"date": c.date, "source": c.source, "confidence": c.confidence, "evidence": c.evidence}
                for c in candidates
            ],
            "conflicts": conflicts,
            "selected_from_multiple": len(unique_dates) > 1,
        }

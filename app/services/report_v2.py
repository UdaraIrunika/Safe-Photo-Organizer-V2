from __future__ import annotations

from typing import Any


def build_report(plan: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    summary = plan.get("summary", {})
    execution_summary = execution.get("summary", {})

    report = {
        "total_media": summary.get("total", 0),
        "planned": summary.get("planned", 0),
        "review_required": summary.get("review_required", 0),
        "conflicts": summary.get("conflicts", 0),
        "copied": execution_summary.get("copied", 0),
        "verified": execution_summary.get("verified", 0),
        "duplicates": execution_summary.get("duplicates", 0),
        "failed": execution_summary.get("failed", 0),
        "skipped": execution_summary.get("skipped", 0),
    }
    return report

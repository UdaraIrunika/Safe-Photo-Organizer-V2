from __future__ import annotations

from typing import Any


def filter_review_queue(plan: dict[str, Any]) -> dict[str, Any]:
    items = plan.get("plan", [])
    approved = []
    review = []
    conflicts = []

    for item in items:
        status = item.get("status")
        if status in {"PLANNED", "VERIFIED"}:
            approved.append(item)
        elif status in {"DATE_CONFLICT", "REVIEW_REQUIRED"}:
            review.append(item)
        if item.get("conflicts"):
            conflicts.append(item)

    return {
        "approved": approved,
        "review": review,
        "conflicts": conflicts,
        "can_execute": not review,
    }

from app.services.review_gate import filter_review_queue


def test_review_gate_filters_conflicts_and_review_items():
    plan = {
        "plan": [
            {"status": "PLANNED", "conflicts": []},
            {"status": "DATE_CONFLICT", "conflicts": [{"source": "FILESYSTEM", "date": "2026-05-01"}]},
            {"status": "REVIEW_REQUIRED", "conflicts": []},
        ]
    }

    result = filter_review_queue(plan)
    assert result["can_execute"] is False
    assert len(result["approved"]) == 1
    assert len(result["review"]) == 2
    assert len(result["conflicts"]) == 1

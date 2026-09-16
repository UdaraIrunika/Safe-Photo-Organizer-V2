from app.services.report_v2 import build_report


def test_build_report_aggregates_summary_values():
    plan = {"summary": {"total": 5, "planned": 3, "review_required": 1, "conflicts": 1}}
    execution = {"summary": {"copied": 2, "verified": 2, "duplicates": 1, "failed": 0, "skipped": 2}}

    report = build_report(plan, execution)
    assert report["total_media"] == 5
    assert report["planned"] == 3
    assert report["review_required"] == 1
    assert report["conflicts"] == 1
    assert report["copied"] == 2
    assert report["verified"] == 2
    assert report["duplicates"] == 1
    assert report["failed"] == 0
    assert report["skipped"] == 2

from pathlib import Path
from tempfile import TemporaryDirectory

from app.services.planner_v2 import OperationPlan


def test_planner_builds_plan_for_source_root():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        family = root / 'Family'
        family.mkdir()
        image = family / '20240130_080421.jpg'
        image.write_bytes(b'fake-image')

        plan = OperationPlan(root).build()

        assert plan['summary']['total'] == 1
        assert plan['plan'][0]['detected_date'] == '2024-01-30'
        assert str(root / 'Family' / '2024-01-30' / '20240130_080421.jpg') in plan['plan'][0]['planned_destination']

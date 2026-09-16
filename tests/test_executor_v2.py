from pathlib import Path
from tempfile import TemporaryDirectory

from app.services.executor_v2 import execute_plan


def test_executor_dry_run_marks_plan_without_copying():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / 'Family' / 'image1.jpg'
        source.parent.mkdir(parents=True)
        source.write_bytes(b'abc')

        plan = {
            'plan': [{
                'source': str(source),
                'planned_destination': str(root / 'Family' / '2024-01-30' / 'image1.jpg'),
                'status': 'PLANNED',
                'conflicts': [],
            }]
        }

        result = execute_plan(plan, dry_run=True)
        assert result['summary']['total'] == 1
        assert result['results'][0]['execution_status'] == 'PLANNED'
        assert not (root / 'Family' / '2024-01-30').exists()

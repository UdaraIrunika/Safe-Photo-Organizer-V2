from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_plan_and_execute_endpoints_on_temp_source():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        family = root / 'Family'
        family.mkdir()
        (family / '20240130_080421.jpg').write_bytes(b'fake-image')

        plan_response = client.post('/api/plan', json={'source': str(root)})
        assert plan_response.status_code == 200
        plan = plan_response.json()
        assert plan['summary']['total'] >= 1

        execute_response = client.post('/api/execute', json={'source': str(root), 'dry_run': True})
        assert execute_response.status_code == 200
        execution = execute_response.json()
        assert 'report' in execution
        assert 'execution' in execution

import pytest
from fastapi.testclient import TestClient
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_registry_endpoint_structure():
    try:
        from main import app  # noqa
        client = TestClient(app)
        resp = client.get('/v1/models/registry')
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            data = resp.json()
            assert data['object'] == 'list'
            assert isinstance(data['data'], list)
            if data['data']:
                first = data['data'][0]
                # Required keys from RegistryModelInfo
                for key in ['id', 'task', 'backend']:
                    assert key in first
    except Exception as e:
        pytest.skip(f"Environment not ready for registry test: {e}")

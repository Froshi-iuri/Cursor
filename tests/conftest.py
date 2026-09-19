import pytest
from fastapi.testclient import TestClient

from backend.main import app
from database.connection import connect, init_schema, set_db_path


@pytest.fixture()
def db_path(tmp_path):
    path = str(tmp_path / "vetericano_test.db")
    set_db_path(path)
    conn = connect(path)
    init_schema(conn)
    conn.close()
    yield path
    set_db_path(None)


@pytest.fixture()
def client(db_path):
    return TestClient(app)

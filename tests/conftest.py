import os
import tempfile
import pytest
import utils.db as db

@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", str(path))
    db.init_db()
    return str(path)

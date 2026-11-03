from fastapi.testclient import TestClient

from app.main import app


def test_mode_demo_remplit_la_base(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "demo.db"))
    monkeypatch.setenv("DEMO_MODE", "1")
    with TestClient(app) as client:
        assert client.get("/api/stats").json()["total"] == 5


def test_mode_demo_ne_duplique_pas(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "demo.db"))
    monkeypatch.setenv("DEMO_MODE", "1")
    with TestClient(app):
        pass
    with TestClient(app) as client:
        assert client.get("/api/stats").json()["total"] == 5

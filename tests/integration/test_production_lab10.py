"""Lab 10 production configuration and API smoke tests."""

from fastapi.testclient import TestClient
from warehouse_persistence.api import app
from warehouse_persistence.config import Settings
from warehouse_persistence.database import make_engine


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_settings_defaults():
    settings = Settings(_env_file=None)
    assert settings.log_level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    assert settings.database_url.startswith("sqlite:///")


def test_sqlite_url(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'stock.db'}")
    try:
        with engine.connect() as connection:
            assert connection.exec_driver_sql("SELECT 1").scalar_one() == 1
    finally:
        engine.dispose()

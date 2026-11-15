from datetime import UTC, datetime

from fastapi.testclient import TestClient

from vitalis.core.config import Settings
from vitalis.main import create_app


def test_demo_api_exposes_synthetic_observations(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite+aiosqlite:///{database_path}",
        demo_mode=True,
        demo_seed=2026,
    )
    app = create_app(settings)

    with TestClient(app) as client:
        health = client.get("/api/v1/health")
        observations = client.get("/api/v1/observations")

        assert health.status_code == 200
        assert health.json()["demo_mode"] is True
        assert observations.status_code == 200
        assert len(observations.json()) == 35
        assert all(item["synthetic"] is True for item in observations.json())


def test_observation_can_be_submitted_and_persisted(tmp_path) -> None:
    database_path = tmp_path / "write-test.db"
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite+aiosqlite:///{database_path}",
        demo_mode=False,
    )
    app = create_app(settings)
    payload = {
        "crew_member_id": "crew-test",
        "metric_id": "sleep_duration_hours",
        "value": 7.1,
        "unit": "h",
        "observed_at": "2026-11-14T09:00:00+05:30",
        "source": "manual",
        "synthetic": False,
    }

    with TestClient(app) as client:
        created = client.post("/api/v1/observations", json=payload)
        listed = client.get("/api/v1/observations")

        assert created.status_code == 201
        returned_timestamp = datetime.fromisoformat(created.json()["observed_at"])
        expected_timestamp = datetime.fromisoformat("2026-11-14T09:00:00+05:30").astimezone(UTC)
        assert returned_timestamp == expected_timestamp
        assert returned_timestamp == datetime(2026, 11, 14, 3, 30, tzinfo=UTC)
        assert listed.status_code == 200
        assert len(listed.json()) == 1


def test_environmental_observation_survives_persistence_round_trip(tmp_path) -> None:
    database_path = tmp_path / "environment-test.db"
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite+aiosqlite:///{database_path}",
        demo_mode=False,
    )
    app = create_app(settings)
    payload = {
        "metric_id": "cabin_temperature",
        "value": 22.4,
        "unit": "degC",
        "observed_at": "2026-11-14T03:30:00Z",
        "source": "nasa_environment",
        "synthetic": False,
        "context": {"dataset": "test-environmental-source"},
    }

    with TestClient(app) as client:
        created = client.post("/api/v1/observations", json=payload)
        listed = client.get("/api/v1/observations")

        assert created.status_code == 201
        assert listed.status_code == 200
        assert len(listed.json()) == 1

    persisted = listed.json()[0]
    assert persisted["crew_member_id"] is None
    assert persisted["source"] == "nasa_environment"
    assert persisted["synthetic"] is False
    assert persisted["metric_id"] == "cabin_temperature"
    assert persisted["value"] == 22.4
    assert persisted["unit"] == "degC"
    assert persisted["context"] == {"dataset": "test-environmental-source"}
    assert datetime.fromisoformat(persisted["observed_at"]) == datetime(
        2026, 11, 14, 3, 30, tzinfo=UTC
    )


def test_demo_reset_is_unavailable_when_demo_mode_is_disabled(tmp_path) -> None:
    database_path = tmp_path / "production-like.db"
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite+aiosqlite:///{database_path}",
        demo_mode=False,
    )
    app = create_app(settings)

    with TestClient(app) as client:
        response = client.post("/api/v1/demo/reset")
        assert response.status_code == 404

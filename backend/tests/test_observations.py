from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from vitalis.domain.observations import HealthObservation


def test_observation_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValidationError):
        HealthObservation(
            crew_member_id="crew-1",
            metric_id="sleep_duration_hours",
            value=7.0,
            unit="h",
            observed_at=datetime(2026, 11, 14, 9, 0),
        )


def test_observation_accepts_timezone_aware_timestamp() -> None:
    observation = HealthObservation(
        crew_member_id="crew-1",
        metric_id="sleep_duration_hours",
        value=7.0,
        unit="h",
        observed_at=datetime(2026, 11, 14, 9, 0, tzinfo=UTC),
    )
    assert observation.synthetic is False
    assert observation.source == "manual"


def test_environmental_observation_cannot_be_assigned_to_a_crew_member() -> None:
    with pytest.raises(ValidationError):
        HealthObservation(
            crew_member_id="crew-1",
            metric_id="cabin_temperature",
            value=22.0,
            unit="degC",
            source="nasa_environment",
        )

    observation = HealthObservation(
        metric_id="cabin_temperature",
        value=22.0,
        unit="degC",
        source="nasa_environment",
        context={"dataset": "example-environmental-source"},
    )
    assert observation.crew_member_id is None


@pytest.mark.parametrize(
    ("source", "synthetic"),
    [
        ("manual", False),
        ("serial", False),
        ("ble", False),
        ("mqtt", False),
        ("simulator", True),
    ],
)
def test_non_environmental_observation_requires_crew_member(
    source: str,
    synthetic: bool,
) -> None:
    with pytest.raises(ValidationError):
        HealthObservation(
            metric_id="example_metric",
            value=1.0,
            unit="unit",
            source=source,
            synthetic=synthetic,
        )


def test_simulator_source_must_be_marked_synthetic() -> None:
    with pytest.raises(ValidationError):
        HealthObservation(
            crew_member_id="crew-1",
            metric_id="example_metric",
            value=1.0,
            unit="unit",
            source="simulator",
            synthetic=False,
        )

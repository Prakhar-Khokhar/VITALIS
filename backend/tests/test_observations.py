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

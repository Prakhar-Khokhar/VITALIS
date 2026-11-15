import json

import pytest
from pydantic import ValidationError

from vitalis.domain.observations import HealthObservation
from vitalis.hardware.common import parse_device_payload


def test_transport_sets_provenance_and_clears_synthetic_flag() -> None:
    payload = json.dumps(
        {
            "crew_member_id": "crew-test",
            "metric_id": "example_metric",
            "value": 12.5,
            "unit": "unit",
        }
    )

    observation = parse_device_payload(payload, "serial")

    assert observation is not None
    assert observation.source == "serial"
    assert observation.synthetic is False


def test_invalid_device_payload_is_rejected() -> None:
    assert parse_device_payload(b'{"not_an_observation": true}', "mqtt") is None


def test_environmental_payload_cannot_become_crew_device_observation() -> None:
    payload = json.dumps(
        {
            "metric_id": "cabin_temperature",
            "value": 22.0,
            "unit": "degC",
            "source": "nasa_environment",
        }
    )

    assert parse_device_payload(payload, "ble") is None


def test_transport_provenance_is_revalidated_against_observation_scope() -> None:
    payload = {
        "metric_id": "cabin_temperature",
        "value": 22.0,
        "unit": "degC",
        "source": "nasa_environment",
    }
    environmental_observation = HealthObservation.model_validate(payload)
    invalid_transport_observation = {
        **environmental_observation.model_dump(mode="python"),
        "source": "serial",
        "synthetic": False,
    }

    with pytest.raises(ValidationError):
        HealthObservation.model_validate(invalid_transport_observation)
    assert parse_device_payload(json.dumps(payload), "serial") is None

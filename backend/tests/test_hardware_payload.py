import json

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

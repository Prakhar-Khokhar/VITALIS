import logging
from typing import Literal

from pydantic import ValidationError

from vitalis.domain.observations import HealthObservation

logger = logging.getLogger(__name__)
TransportSource = Literal["serial", "ble", "mqtt"]


def parse_device_payload(
    payload: bytes | str,
    source: TransportSource,
) -> HealthObservation | None:
    try:
        observation = HealthObservation.model_validate_json(payload)
    except (ValidationError, ValueError, UnicodeDecodeError):
        logger.warning("Discarding invalid %s observation payload", source, exc_info=True)
        return None
    return observation.model_copy(update={"source": source, "synthetic": False})

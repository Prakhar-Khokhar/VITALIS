from collections.abc import AsyncIterator
from typing import Protocol

from vitalis.domain.observations import HealthObservation


class ObservationSource(Protocol):
    """Common async interface implemented by simulators and hardware transports."""

    def stream(self) -> AsyncIterator[HealthObservation]:
        ...

import asyncio
import logging
from collections.abc import AsyncIterator

from vitalis.domain.observations import HealthObservation
from vitalis.hardware.common import parse_device_payload

logger = logging.getLogger(__name__)


class SerialJsonSource:
    """Read newline-delimited JSON observations from a USB/UART device such as an ESP32."""

    def __init__(self, port: str, baudrate: int = 115200) -> None:
        self.port = port
        self.baudrate = baudrate

    async def stream(self) -> AsyncIterator[HealthObservation]:
        try:
            import serial_asyncio
        except ImportError as exc:
            raise RuntimeError(
                "Serial support is optional; install VITALIS with the 'hardware' extra."
            ) from exc

        reader, writer = await serial_asyncio.open_serial_connection(
            url=self.port,
            baudrate=self.baudrate,
        )
        logger.info("Serial observation source connected on %s", self.port)
        try:
            while True:
                line = await reader.readline()
                if not line:
                    await asyncio.sleep(0.05)
                    continue
                observation = parse_device_payload(line, "serial")
                if observation is not None:
                    yield observation
        finally:
            writer.close()
            logger.info("Serial observation source closed on %s", self.port)

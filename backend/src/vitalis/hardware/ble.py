import asyncio
import logging
from collections.abc import AsyncIterator

from vitalis.domain.observations import HealthObservation
from vitalis.hardware.common import parse_device_payload

logger = logging.getLogger(__name__)


class BleakJsonSource:
    """Consume JSON observation messages from a configured BLE GATT notification."""

    def __init__(self, address: str, characteristic_uuid: str) -> None:
        self.address = address
        self.characteristic_uuid = characteristic_uuid

    async def stream(self) -> AsyncIterator[HealthObservation]:
        try:
            from bleak import BleakClient
        except ImportError as exc:
            raise RuntimeError(
                "BLE support is optional; install VITALIS with the 'hardware' extra."
            ) from exc

        queue: asyncio.Queue[HealthObservation] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def on_notification(_sender: int, data: bytearray) -> None:
            observation = parse_device_payload(bytes(data), "ble")
            if observation is not None:
                loop.call_soon_threadsafe(queue.put_nowait, observation)

        async with BleakClient(self.address) as client:
            await client.start_notify(self.characteristic_uuid, on_notification)
            logger.info("BLE observation notifications enabled for %s", self.address)
            try:
                while True:
                    yield await queue.get()
            finally:
                await client.stop_notify(self.characteristic_uuid)

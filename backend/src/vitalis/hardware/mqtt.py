import asyncio
import logging
from collections.abc import AsyncIterator

from vitalis.domain.observations import HealthObservation
from vitalis.hardware.common import parse_device_payload

logger = logging.getLogger(__name__)


class MqttJsonSource:
    """Consume canonical observation JSON messages from an MQTT topic using Paho MQTT 2.x."""

    def __init__(
        self,
        host: str,
        topic: str,
        port: int = 1883,
        client_id: str = "vitalis-observation-ingest",
    ) -> None:
        self.host = host
        self.topic = topic
        self.port = port
        self.client_id = client_id

    async def stream(self) -> AsyncIterator[HealthObservation]:
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:
            raise RuntimeError(
                "MQTT support is optional; install VITALIS with the 'hardware' extra."
            ) from exc

        queue: asyncio.Queue[HealthObservation] = asyncio.Queue()
        loop = asyncio.get_running_loop()
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
        )

        def on_connect(_client, _userdata, _flags, reason_code, _properties) -> None:
            if not reason_code.is_failure:
                _client.subscribe(self.topic)

        def on_message(_client, _userdata, message) -> None:
            observation = parse_device_payload(message.payload, "mqtt")
            if observation is not None:
                loop.call_soon_threadsafe(queue.put_nowait, observation)

        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(self.host, self.port, keepalive=30)
        client.loop_start()
        logger.info("MQTT observation source subscribed to %s", self.topic)
        try:
            while True:
                yield await queue.get()
        finally:
            client.loop_stop()
            client.disconnect()

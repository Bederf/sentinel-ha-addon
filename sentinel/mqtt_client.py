<<<<<<< HEAD
"""
MQTT client for SENTINEL broker.
Connects, registers site, publishes EnergySnapshot.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class EnergySnapshot:
    """Normalized energy reading for MQTT publish."""
    
    def __init__(self, entity_id: str, metric_type: str, state: str, attributes: dict):
        self.entity_id = entity_id
        self.metric_type = metric_type
        self.state = state
        self.attributes = attributes
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "metric_type": self.metric_type,
            "value": self._parse_state(),
            "unit": self._unit(),
            "timestamp": self.timestamp,
        }
    
    def _parse_state(self) -> float:
        try:
            return float(self.state)
        except (ValueError, TypeError):
            return 0.0
    
    def _unit(self) -> str:
        units = {
            "battery_soc_pct": "%",
            "pv_power_w": "W",
            "grid_power_w": "W",
            "battery_power_w": "W",
            "load_power_w": "W",
            "battery_temp_c": "°C",
            "battery_soh_pct": "%",
        }
        return units.get(self.metric_type, "")


class SentinelMQTTClient:
    """MQTT client for SENTINEL broker."""
    
    def __init__(self, host: str, port: int, client_id: str, site_id: str):
=======
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None  # type: ignore[assignment]

from energy_snapshot import EnergySnapshot

logger = logging.getLogger(__name__)

_HA_UNAVAILABLE = {"unavailable", "unknown", "none", ""}


class SentinelMQTTClient:
    def __init__(
        self,
        host: str,
        port: int,
        client_id: str,
        site_id: str,
        username: str = "",
        password: str = "",
    ):
>>>>>>> 46e0279 (Initial scaffold: SENTINEL HA Add-on v1.0.0)
        self.host = host
        self.port = port
        self.client_id = client_id
        self.site_id = site_id
<<<<<<< HEAD
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT connected with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        logger.warning(f"MQTT disconnected with code {rc}")
    
    async def connect_and_register(self, entities: list[dict]):
        """Connect to MQTT and register with SENTINEL API."""
        try:
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()
            
            # Subscribe to own site topic for incoming commands
            self.client.subscribe(f"sentinel/{self.site_id}/#", qos=1)
            
            logger.info(f"Connected to {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect MQTT: {e}")
            raise
    
    async def monitor_entities(self, entities: list[dict]):
        """Subscribe to HA entity state changes and publish EnergySnapshots."""
        # In production: subscribe to HA state change events via Supervisor API websocket
        # For v1: poll periodically
        import asyncio
        while True:
            for entity in entities:
=======
        self._username = username
        self._password = password
        self._retry_count = 0
        self._MAX_RETRIES = 10

        if mqtt is None:
            raise ImportError("paho-mqtt is not installed")

        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected to %s:%s", self.host, self.port)
            self._retry_count = 0
        else:
            logger.error("MQTT connection failed: rc=%d", rc)

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self._retry_count += 1
            backoff = min(60 * (2 ** max(0, self._retry_count - 3)), 300)
            logger.warning(
                "MQTT disconnected rc=%d — retry %d in %ds",
                rc, self._retry_count, backoff,
            )
            time.sleep(backoff)
            try:
                client.reconnect()
            except Exception as e:
                logger.error("Reconnect failed: %s", e)

    def _parse_state(self, state: str, metric_type: str) -> float | str | None:
        v = state.strip().lower()
        if v in _HA_UNAVAILABLE:
            return None
        if v in ("on", "off"):
            if metric_type == "geyser_state":
                return v
            return 1.0 if v == "on" else 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    async def connect_and_register(self, entities: list[dict]):
        if self._username:
            self.client.username_pw_set(self._username, self._password)

        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()

        self.client.publish(
            f"sentinel/{self.site_id}/energy/last_updated",
            datetime.now(timezone.utc).isoformat(),
            qos=1,
            retain=True,
        )
        logger.info("Connected to %s:%s", self.host, self.port)

    async def monitor_entities(self, entities: list[dict]):
        while True:
            for entity in entities:
                parsed = self._parse_state(entity.get("state", "0"), entity["metric_type"])
>>>>>>> 46e0279 (Initial scaffold: SENTINEL HA Add-on v1.0.0)
                snapshot = EnergySnapshot(
                    entity_id=entity["entity_id"],
                    metric_type=entity["metric_type"],
                    state=entity.get("state", "0"),
                    attributes=entity.get("attributes", {}),
                )
<<<<<<< HEAD
                topic = f"sentinel/{self.site_id}/{entity['metric_type']}"
                self.client.publish(topic, json.dumps(snapshot.to_dict()), qos=1)
            await asyncio.sleep(30)  # Poll every 30s
=======
                topic = f"sentinel/{self.site_id}/energy/{entity['metric_type']}"
                self.client.publish(
                    topic,
                    json.dumps(snapshot.to_dict()),
                    qos=1,
                    retain=True,
                )

            self.client.publish(
                f"sentinel/{self.site_id}/energy/last_updated",
                datetime.now(timezone.utc).isoformat(),
                qos=1,
                retain=True,
            )

            await asyncio.sleep(30)

    async def subscribe_ha_events(self, entities: list[dict]):
        import aiohttp

        token = self._read_supervisor_token()
        if not token:
            logger.warning("No supervisor token — falling back to 30s polling")
            await self.monitor_entities(entities)
            return

        entity_ids = {e["entity_id"] for e in entities}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(
                    "ws://supervisor/api/websocket",
                    headers={"Authorization": f"Bearer {token}"},
                ) as ws:
                    auth_msg = await ws.receive_json()
                    if auth_msg.get("type") != "auth_ok":
                        logger.error("Websocket auth failed: %s", auth_msg)
                        await self.monitor_entities(entities)
                        return

                    await ws.send_json({
                        "id": 1,
                        "type": "subscribe_events",
                        "event_type": "state_changed",
                    })

                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            event = data.get("event", {})
                            event_data = event.get("data", {})
                            entity_id = event_data.get("entity_id", "")

                            if entity_id in entity_ids:
                                new_state = event_data.get("new_state", {})
                                state = new_state.get("state", "") if new_state else ""
                                attrs = new_state.get("attributes", {}) if new_state else {}

                                metric_type = next(
                                    (e["metric_type"] for e in entities if e["entity_id"] == entity_id),
                                    entity_id,
                                )
                                parsed = self._parse_state(state, metric_type)
                                topic = f"sentinel/{self.site_id}/energy/{metric_type}"
                                payload = json.dumps({
                                    "entity_id": entity_id,
                                    "metric_type": metric_type,
                                    "state": state,
                                    "attributes": attrs,
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                })
                                self.client.publish(topic, payload, qos=1, retain=True)

        except Exception as e:
            logger.warning("HA websocket failed: %s — falling back to 30s polling", e)
            await self.monitor_entities(entities)

    def _read_supervisor_token(self) -> str | None:
        try:
            with open("/data/supervisor_token") as f:
                return f.read().strip()
        except (FileNotFoundError, OSError):
            return None


if __name__ == "__main__":
    import asyncio

    async def test():
        client = SentinelMQTTClient(
            host="localhost", port=1883,
            client_id="test", site_id="test",
            username="", password="",
        )
        entities = [{"entity_id": "sensor.test", "metric_type": "pv_power_w", "state": "2500"}]
        await client.connect_and_register(entities)
        await client.monitor_entities(entities)

    asyncio.run(test())
>>>>>>> 46e0279 (Initial scaffold: SENTINEL HA Add-on v1.0.0)

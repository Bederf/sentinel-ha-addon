<<<<<<< HEAD
"""
SENTINEL HA Add-on — Main service
Reads options.json, discovers entities, publishes EnergySnapshot via MQTT.
"""

import asyncio
import json
import sys
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class AddonOptions:
    """Validated addon configuration from /data/options.json"""
    def __init__(self, opts: dict):
        required = ['sentinel_host', 'telegram_chat_id', 'mqtt_host', 'mqtt_port']
        missing = [f for f in required if f not in opts or not opts[f]]
        if missing:
            raise ValueError(f"FATAL: Missing required fields: {missing}")
        self.sentinel_host: str = opts['sentinel_host']
        self.telegram_chat_id: str = opts['telegram_chat_id']
        self.mqtt_host: str = opts['mqtt_host']
        self.mqtt_port: int = int(opts['mqtt_port'])
        logger.info(f"Addon configured for site {self.telegram_chat_id}")


async def main():
    # Load and validate options
    try:
        with open('/data/options.json') as f:
            opts = json.load(f)
        config = AddonOptions(opts)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
    
    logger.info("Starting SENTINEL HA Add-on...")
    
    # Import after options validated
    from entity_discovery import EntityDiscovery
    from mqtt_client import SentinelMQTTClient
    
    # Discover entities via HA Supervisor API
    discovery = EntityDiscovery()
    entities = await discovery.discover_all(max_retries=3, backoff=[2, 4, 8])
    
    if not entities:
        logger.error("No solar/battery entities found. Check HA entity names.")
        sys.exit(1)
    
    logger.info(f"Discovered {len(entities)} entities: {[e['entity_id'] for e in entities]}")
    
    # Connect MQTT and register
=======
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys

import aiohttp

from entity_discovery import EntityDiscovery
from mqtt_client import SentinelMQTTClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sentinel_addon")

SENTINEL_API_BASE = "https://bms.sentinel-ai.co.za"

CONFIG_PATH = "/data/options.json"


class AddonOptions:
    def __init__(self, opts: dict):
        self.telegram_chat_id: str = opts.get("telegram_chat_id", "")
        self.sentinel_api_key: str = opts.get("sentinel_api_key", "")
        self.site_id: str = f"res-{self.telegram_chat_id}" if self.telegram_chat_id else ""
        self.mqtt_host: str = opts.get("mqtt_host", "")
        self.mqtt_port: int = opts.get("mqtt_port", 1883)
        self.mqtt_username: str = opts.get("mqtt_username", "")
        self.mqtt_password: str = opts.get("mqtt_password", "")
        self.tier: str = "free"

        if not self.telegram_chat_id:
            raise ValueError("FATAL: telegram_chat_id is required")

        logger.info("Addon configured for chat_id=%s tier=%s", self.telegram_chat_id, "paid" if self.sentinel_api_key else "free")


def load_options() -> AddonOptions:
    try:
        with open(CONFIG_PATH) as f:
            opts = json.load(f)
        return AddonOptions(opts)
    except FileNotFoundError:
        logger.error("Config file not found at %s", CONFIG_PATH)
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid config JSON: %s", e)
        sys.exit(1)
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)


async def register_with_sentinel(config: AddonOptions, entities: list[dict]) -> bool:
    payload = {
        "chat_id": config.telegram_chat_id,
        "entities": [
            {"entity_id": e["entity_id"], "metric_type": e["metric_type"]}
            for e in entities
        ],
        "platform": "home_assistant",
    }

    headers = {"Content-Type": "application/json"}
    if config.sentinel_api_key:
        headers["X-Sentinel-Api-Key"] = config.sentinel_api_key

    backoff = [5, 10, 20]
    for attempt, wait in enumerate(backoff, 1):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    f"{SENTINEL_API_BASE}/api/residential/addon-register",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        config.mqtt_host = data["mqtt_host"]
                        config.mqtt_port = data["mqtt_port"]
                        config.mqtt_username = data["mqtt_username"]
                        config.mqtt_password = data["mqtt_password"]
                        config.tier = data.get("tier", "free")
                        logger.info(
                            "Registered with SENTINEL: site_id=%s tier=%s",
                            data["site_id"], config.tier,
                        )
                        return True

                    body = await resp.text()
                    logger.warning(
                        "Registration attempt %d/3 failed: HTTP %d — %s",
                        attempt, resp.status, body[:200],
                    )

        except Exception as e:
            logger.warning("Registration attempt %d/3 error: %s", attempt, e)

        if attempt < len(backoff):
            logger.info("Retrying in %ds...", wait)
            await asyncio.sleep(wait)

    logger.error("SENTINEL registration failed after 3 attempts")
    return False


async def main():
    logger.info("SENTINEL HA Add-on starting")

    config = load_options()

    discovery = EntityDiscovery()
    entities = await discovery.discover_all(max_retries=3, backoff=[2, 4, 8])

    if not entities:
        logger.error("No solar entities found — check your HA integrations")
        sys.exit(1)

    logger.info("Discovered %d entities", len(entities))

    ok = await register_with_sentinel(config, entities)
    if not ok:
        logger.error("Could not register with SENTINEL backend")
        sys.exit(1)

>>>>>>> 46e0279 (Initial scaffold: SENTINEL HA Add-on v1.0.0)
    client = SentinelMQTTClient(
        host=config.mqtt_host,
        port=config.mqtt_port,
        client_id=f"sentinel-ha-{config.telegram_chat_id}",
        site_id=config.telegram_chat_id,
<<<<<<< HEAD
    )
    
    await client.connect_and_register(entities)
    logger.info("MQTT connected and registered")
    
    # Start entity monitoring loop
=======
        username=config.mqtt_username,
        password=config.mqtt_password,
    )

    await client.connect_and_register(entities)
>>>>>>> 46e0279 (Initial scaffold: SENTINEL HA Add-on v1.0.0)
    await client.monitor_entities(entities)


if __name__ == "__main__":
    asyncio.run(main())

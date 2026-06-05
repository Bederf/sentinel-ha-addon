from __future__ import annotations

import json
import logging

import aiohttp

logger = logging.getLogger(__name__)

HA_TOKEN_PATH = "/data/options.json"
SUPERVISOR_TOKEN_PATH = "/data/supervisor_token"

_SOLAR_ENTITY_PATTERNS = {
    "sensor": [
        "pv_power",
        "solar_power",
        "battery_soc",
        "battery_power",
        "grid_power",
        "load_power",
        "use_power",
        "purchase_power",
        "generation_power",
        "battery_voltage",
        "grid_voltage",
        "inverter_power",
        "geyser_power",
        "ev_charger_power",
    ],
    "switch": [
        "geyser",
        "load_shedding",
        "battery_charge",
    ],
    "binary_sensor": [
        "grid_status",
        "load_shedding",
    ],
}

_METRIC_TYPE_MAP = {
    "pv_power": "pv_power_w",
    "solar_power": "pv_power_w",
    "generation_power": "pv_power_w",
    "battery_soc": "battery_soc_pct",
    "battery_power": "battery_power_w",
    "grid_power": "grid_power_w",
    "load_power": "load_power_w",
    "use_power": "load_power_w",
    "purchase_power": "grid_power_w",
    "grid_voltage": "grid_voltage_v",
    "battery_voltage": "battery_voltage_v",
    "inverter_power": "pv_power_w",
    "geyser_power": "geyser_power_w",
    "geyser": "geyser_state",
    "ev_charger_power": "ev_charger_power_w",
}


class EntityDiscovery:
    def __init__(self):
        self._ha_token: str | None = None

    def _read_supervisor_token(self) -> str | None:
        try:
            with open(SUPERVISOR_TOKEN_PATH) as f:
                return f.read().strip()
        except (FileNotFoundError, OSError) as e:
            logger.warning("Cannot read supervisor token: %s", e)
            return None

    async def discover_all(self, max_retries: int = 3, backoff: list[int] | None = None) -> list[dict]:
        token = self._read_supervisor_token()
        if not token:
            logger.error("No HA supervisor token — cannot discover entities")
            return []

        if backoff is None:
            backoff = [2, 4, 8]

        for attempt in range(1, max_retries + 1):
            try:
                return await self._discover(token)
            except Exception as e:
                wait = backoff[min(attempt - 1, len(backoff) - 1)]
                logger.warning(
                    "Entity discovery attempt %d/%d failed: %s — retrying in %ds",
                    attempt, max_retries, e, wait,
                )
                if attempt < max_retries:
                    import asyncio
                    await asyncio.sleep(wait)

        logger.error("Entity discovery failed after %d attempts", max_retries)
        return []

    async def _discover(self, token: str) -> list[dict]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        entities = []

        async with aiohttp.ClientSession(headers=headers) as session:
            states_url = "http://supervisor/core/api/states"
            async with session.get(states_url) as resp:
                if resp.status != 200:
                    logger.error("HA API returned %d — cannot discover entities", resp.status)
                    return []
                states = await resp.json()

            for state in states:
                entity_id = state.get("entity_id", "")
                domain = entity_id.split(".")[0] if "." in entity_id else ""
                if domain not in _SOLAR_ENTITY_PATTERNS:
                    continue

                patterns = _SOLAR_ENTITY_PATTERNS[domain]
                entity_name = entity_id.split(".")[-1].lower()

                matched_pattern = None
                for pattern in patterns:
                    if pattern in entity_name:
                        matched_pattern = pattern
                        break

                if not matched_pattern:
                    continue

                metric_type = _METRIC_TYPE_MAP.get(matched_pattern, matched_pattern)
                entities.append({
                    "entity_id": entity_id,
                    "metric_type": metric_type,
                    "state": state.get("state", "0"),
                    "attributes": state.get("attributes", {}),
                })

        logger.info("Discovered %d solar entities from HA", len(entities))
        return entities

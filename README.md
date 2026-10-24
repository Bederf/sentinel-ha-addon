# SENTINEL Solar Intelligence for Home Assistant

Monitor your home energy system and turn Home Assistant solar data into useful, plain-language alerts.

SENTINEL Solar Intelligence is a Home Assistant add-on for South African solar and battery setups. It discovers relevant entities, publishes structured energy snapshots and connects them to the SENTINEL notification and intelligence layer.

> **Home Assistant → entity discovery → energy snapshots → SENTINEL intelligence → notifications**

## What it does

- Discovers solar, battery, grid, load, geyser and EV-charger entities
- Normalises readings into stable metric types
- Publishes retained energy snapshots over MQTT
- Uses the Home Assistant Supervisor API and websocket events
- Falls back to periodic polling when event streaming is unavailable
- Supports SENTINEL alerts and recommendations through the optional cloud connection

## Why it is useful

South African homes have a very specific energy problem: solar generation, battery health, grid availability and loadshedding all affect one another.

This add-on creates a small, reliable bridge between the energy data already available in Home Assistant and higher-level monitoring or notification workflows.

## Requirements

- Home Assistant OS or a Supervised installation
- Home Assistant entities for the energy metrics you want to monitor
- A Telegram account if you want Telegram notifications
- A SENTINEL account/API key for cloud alerts and recommendations

## Install

1. Open **Settings → Add-ons → Add-on Store**.
2. Open the **⋮** menu and choose **Repositories**.
3. Add:

   ```text
   https://github.com/Bederf/sentinel-ha-addon
   ```

4. Install **SENTINEL Solar Intelligence**.
5. Configure the add-on and start it.

The repository is compatible with the Home Assistant add-on model and supports common Home Assistant architectures through the add-on build configuration.

## Configuration

The add-on exposes two options:

| Option | Required | Description |
|---|---:|---|
| `telegram_chat_id` | Yes | Telegram chat identifier used to associate the installation with notifications. |
| `sentinel_api_key` | No | Optional key for an enabled SENTINEL cloud account. |

Create the Telegram chat ID by messaging [@userinfobot](https://t.me/userinfobot) and sending `/start`.

Do not put MQTT passwords, service credentials or production connection strings in this repository. They are provisioned by the add-on registration flow or Home Assistant configuration.

## Entities discovered

The add-on matches entity IDs by keyword and maps them to stable metric types:

| Entity type | Examples |
|---|---|
| Solar/PV power | `sensor.pv_power`, `sensor.solar_power` |
| Battery state and power | `sensor.battery_soc`, `sensor.battery_power` |
| Grid and load | `sensor.grid_power`, `sensor.load_power`, `sensor.grid_voltage` |
| Geyser | `switch.geyser`, `sensor.geyser_power` |
| EV charging | `sensor.ev_charger_power` |

Entity IDs must use lowercase Home Assistant naming. Non-standard names may need an additional mapping before they are discovered.

## Data flow

```text
Home Assistant
      ↓ Supervisor API / websocket
SENTINEL add-on
      ↓ MQTT energy topics
SENTINEL intelligence layer
      ↓
Alerts, summaries and recommendations
```

The add-on is responsible for discovery and telemetry publishing. Account-specific alerts, recommendations and any optional control workflows belong to the configured SENTINEL service and are not hard-coded into the local add-on.

## Local development

The add-on normally runs inside Home Assistant because it relies on Supervisor APIs and the mounted supervisor token. The Python modules can still be tested locally with a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r sentinel/requirements.txt pytest
PYTHONPATH=sentinel pytest -q sentinel/test_addon.py
```

## Troubleshooting

**No entities found**

- Confirm the add-on has Home Assistant API access.
- Check that entity IDs contain supported keywords such as `pv_power`, `battery_soc`, `grid_power` or `load_power`.
- Review the add-on log for discovery errors.

**Registration fails**

- Confirm network access from Home Assistant.
- Check that the Telegram chat ID is correct.
- If using a paid or private SENTINEL account, verify the API key through the account’s secure configuration path.

**Updates are delayed**

- The add-on uses Home Assistant events when available.
- If the Supervisor websocket is unavailable, it falls back to periodic polling.

## Project status

This is a focused integration project, not the complete SENTINEL platform. The public repository contains the Home Assistant bridge and its tests; the broader SENTINEL intelligence platform remains separately developed.

## Contributing

Useful contributions include new entity-name mappings, improved validation, Home Assistant compatibility fixes, tests and clearer diagnostics. Please include the Home Assistant version, add-on version, entity examples and logs when reporting an issue.

## Links

- [SENTINEL](https://github.com/Bederf/sentinel-ai)
- [Issue tracker](https://github.com/Bederf/sentinel-ha-addon/issues)
- [Home Assistant add-ons documentation](https://www.home-assistant.io/addons/)

## License

See the repository license and add-on metadata for distribution terms.

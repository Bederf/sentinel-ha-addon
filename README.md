# SENTINEL Solar Intelligence — Home Assistant Add-on

AI-powered solar monitoring and loadshedding alerts for South Africa.

Connects your Home Assistant solar entities to SENTINEL for proactive alerts, battery longevity insights, Eskom loadshedding-aware recommendations, and plain-language Telegram notifications.

---

## Requirements

- Home Assistant OS or Supervised (add-on system required)
- Solar entities exposed in HA (PV power, battery SOC, grid power, load power)
- Telegram account for alerts

---

## Installation

1. Go to **Settings → Add-ons → Add-on Store**
2. Tap the **⋮** menu (top-right) → **Repositories**
3. Add: `https://github.com/Bederf/sentinel-ha-addon`
4. Close the dialog
5. Scroll down or search for **SENTINEL Solar Intelligence**
6. Tap **Install** (allow a few minutes for the build)

---

## Configuration

### Step 1: Get your Telegram Chat ID

Talk to [@userinfobot](https://t.me/userinfobot) on Telegram. Send `/start` — it replies with your numeric ID.

### Step 2: Configure the add-on

Go to the **Configuration** tab and set:

| Field | Required | Description |
|-------|----------|-------------|
| `telegram_chat_id` | ✅ Yes | Your numeric Telegram ID from @userinfobot |
| `sentinel_api_key` | ❌ No | Leave blank for free tier. See [Tiers](#tiers) below. |

### Step 3: Start the add-on

Tap **Start**. Check the **Log** tab for progress:

```
SENTINEL HA Add-on starting
Discovered 6 entities
Registered with SENTINEL: site_id=res-123456789 tier=free
MQTT connected to bms.sentinel-ai.co.za:1883
```

Once registered, you'll receive a Telegram confirmation from @Sentinelaihomebot.

---

## Tiers

### Free
- AEGIS critical alerts (battery critical, inverter fault, overtemp)
- Eskom loadshedding alerts for your area
- Connection health monitoring

### Paid
Everything in Free, plus:
- AI-powered daily recommendations (e.g., "Switch geyser off — Stage 4 starts in 45min")
- Morning summary with yesterday's generation, consumption, and estimated ZAR savings
- Battery longevity tracking
- Priority support

To upgrade: set `sentinel_api_key` in Configuration and restart. Keys are available from SENTINEL.

---

## What Gets Monitored

The add-on automatically discovers these entities from your HA installation:

| Metric | HA Entity Type | Example |
|--------|---------------|---------|
| PV Power | `sensor` | `sensor.solaredge_current_power` |
| Battery SOC | `sensor` | `sensor.solaredge_battery_soc` |
| Battery Power | `sensor` | `sensor.solaredge_battery_power` |
| Grid Power | `sensor` | `sensor.solaredge_grid_power` |
| Load Power | `sensor` | `sensor.solaredge_house_consumption` |
| Grid Voltage | `sensor` | `sensor.solaredge_grid_voltage` |
| Geyser State | `switch` | `switch.geyser` |
| Geyser Power | `sensor` | `sensor.geyser_power` |
| EV Charger Power | `sensor` | `sensor.ev_charger_power` |

Entities are matched by keyword in the entity ID (e.g., `pv_power`, `battery_soc`, `grid_power`).

---

## Data Flow

```
HA → Supervisor API → SENTINEL Add-on → MQTT → SENTINEL Cloud → Telegram
```

Entity states are published every 30 seconds via MQTT over TLS. When an entity changes state in HA, the add-on picks it up in real-time via the Supervisor websocket.

---

## Commands

Once connected, talk to @Sentinelaihomebot on Telegram:

| Command | Description |
|---------|-------------|
| `/status` | Current solar readings |
| `/setarea` | Configure Eskom loadshedding area |
| `/devices` | List available controllable devices |
| `/control geyser on` | Turn geyser on |
| `/control geyser off` | Turn geyser off |
| `/disconnect` | Remove your system from SENTINEL |

---

## Troubleshooting

**Add-on won't start:**
Check the Log tab. Common issues:
- `telegram_chat_id` not set → set it in Configuration
- No solar entities found → verify HA has solar sensors
- Registration failed → check network connectivity

**No Telegram alerts:**
- Verify your chat ID is correct
- Check the add-on logs for "Registered with SENTINEL"
- Send `/start` to @Sentinelaihomebot to wake it up

**Entities not detected:**
The add-on matches by keywords in entity IDs. If your entities use non-standard names, they may not be picked up. Check the logs for "Discovered N entities" — if 0, your entity IDs may need renaming.

---

## Uninstall

1. Stop the add-on
2. Send `/disconnect` to @Sentinelaihomebot
3. Uninstall from the Add-on Store
4. Optional: remove the repository from Settings → Add-ons → Repositories

---

## Repository

Source: https://github.com/Bederf/sentinel-ha-addon
Issues: https://github.com/Bederf/sentinel-ha-addon/issues

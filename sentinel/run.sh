#!/usr/bin/env bashio
set -e

CONFIG_PATH=/data/options.json

TELEGRAM_CHAT_ID=$(bashio::config 'telegram_chat_id')
MQTT_HOST=$(bashio::config 'mqtt_host')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_USERNAME=$(bashio::config 'mqtt_username')
MQTT_PASSWORD=$(bashio::config 'mqtt_password')

export TELEGRAM_CHAT_ID
export MQTT_HOST
export MQTT_PORT
export MQTT_USERNAME
export MQTT_PASSWORD

python3 /sentinel_addon.py

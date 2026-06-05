#!/usr/bin/env bashio
set -e

CONFIG_PATH=/data/options.json

TELEGRAM_CHAT_ID=$(bashio::config 'telegram_chat_id')
SENTINEL_API_KEY=$(bashio::config 'sentinel_api_key')

export TELEGRAM_CHAT_ID
export SENTINEL_API_KEY

python3 /sentinel_addon.py

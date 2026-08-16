"""
Fast-forward one channel's state past its current backlog without translating/
resending it -- e.g. after an outage, to skip old messages instead of flooding the
destination channel when the next cron tick runs.

Usage: python3 reset_channel.py <channel-name>
(channel-name must match a "name" entry in config/channels.json)
"""
import asyncio
import json
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot"))
from telegram_client import build_client, find_group

ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT, ".env"))


async def main(channel_name):
    with open(os.path.join(ROOT, "config", "channels.json")) as f:
        channels = json.load(f)
    channel_cfg = next((c for c in channels if c["name"] == channel_name), None)
    if not channel_cfg:
        print(f"No channel named '{channel_name}' in config/channels.json")
        return

    api_id = int(os.environ["API_ID"])
    api_hash = os.environ["API_HASH"]
    phone_number = os.environ["PHONE_NUMBER"]

    client = build_client(api_id, api_hash)
    await client.start(phone_number)

    source = await find_group(client, channel_cfg["source_id"])
    if not source:
        print("Could not resolve source channel.")
        await client.disconnect()
        return

    latest = await client.get_messages(source, limit=1)
    await client.disconnect()

    if not latest:
        print("No messages found in source channel.")
        return

    state_file = os.path.join(ROOT, "state", "last_ids.json")
    state = {}
    if os.path.exists(state_file):
        with open(state_file) as f:
            state = json.load(f)
    state[channel_name] = latest[0].id

    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    print(f"'{channel_name}' fast-forwarded to message id {latest[0].id}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 reset_channel.py <channel-name>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))

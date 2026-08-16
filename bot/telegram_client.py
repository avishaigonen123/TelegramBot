import logging
import os

from telethon import TelegramClient

SESSION_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "session", "main")


def build_client(api_id, api_hash):
    # flood_sleep_threshold=0 disables Telethon's default behavior of silently
    # auto-sleeping-and-retrying on any FloodWaitError under the threshold. Left at
    # its default (60s), a persistent flood wait can retry forever with no way for
    # our code to intervene or bound the run -- we want FloodWaitError raised so
    # run_tick.py can catch it, log it, and move on within a bounded time.
    return TelegramClient(SESSION_PATH, api_id, api_hash, flood_sleep_threshold=0)


async def find_group(client: TelegramClient, group_id: int):
    try:
        return await client.get_entity(group_id)
    except Exception as e:
        logging.warning(f"Could not resolve group {group_id} via get_entity: {e}")
        async for dialog in client.iter_dialogs():
            if dialog.id == group_id:
                return dialog
        logging.warning(f"Group with ID {group_id} not found in dialogs either.")
        return None

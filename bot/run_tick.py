import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime

import pytz
import requests
from dotenv import load_dotenv
from telethon.errors import FloodWaitError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from telegram_client import build_client, find_group
from translate import translate_or_fallback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNELS_FILE = os.path.join(ROOT, "config", "channels.json")
STATE_FILE = os.path.join(ROOT, "state", "last_ids.json")
LOCK_FILE = os.path.join(ROOT, "state", "run.lock")
LOG_FILE = os.path.join(ROOT, "bot.log")

# Cron runs every 60s; don't let one tick's FloodWait retry run long enough to
# collide with the next tick.
MAX_FLOOD_WAIT_SECONDS = 45

# Bounds the read-only fetch step only (safe to cancel -- each channel now has its
# own connection, so cancelling one channel's fetch can't corrupt another's).
FETCH_TIMEOUT_SECONDS = 40

# Cap how many backlog messages one tick will process per channel. Without this, a
# channel that accumulated a large backlog (e.g. after being paused for hours) would
# try to fetch+translate+send everything in a single tick, which can legitimately run
# for minutes -- confirmed live during testing (a single 21-hour-old backlog on one
# channel took several minutes just to translate+send, no bug involved, just volume).
# Uncapped, this collides badly with any timeout applied to the send/translate loop
# (see note below on why that loop is NOT wrapped in a timeout). With this cap,
# remaining backlog simply catches up over the next several ticks.
MESSAGES_PER_CHANNEL_LIMIT = 20

load_dotenv(os.path.join(ROOT, ".env"))

logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)
for handler in logging.getLogger().handlers:
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    formatter.converter = lambda *a: datetime.now(pytz.timezone("Asia/Jerusalem")).timetuple()
    handler.setFormatter(formatter)


def load_channels():
    with open(CHANNELS_FILE) as f:
        return json.load(f)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def acquire_lock():
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            logging.warning(f"Previous run (pid {pid}) still active, skipping this tick.")
            return False
        except (ValueError, ProcessLookupError, PermissionError):
            logging.info("Stale lock file found, removing it.")
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


async def fetch_new_messages(client, source_channel, last_id):
    messages = []
    if last_id is None:
        async for msg in client.iter_messages(source_channel, limit=10, reverse=True):
            if not msg.action:
                messages.append(msg)
    else:
        async for msg in client.iter_messages(
            source_channel, min_id=last_id, reverse=True, limit=MESSAGES_PER_CHANNEL_LIMIT
        ):
            if not msg.action:
                messages.append(msg)
    return messages


async def process_channel(client, channel_cfg, state, api_keys):
    name = channel_cfg["name"]
    source_id = channel_cfg["source_id"]
    dest_id = channel_cfg["dest_id"]

    source_channel = await find_group(client, source_id)
    dest_channel = await find_group(client, dest_id)
    if not source_channel or not dest_channel:
        logging.error(f"[{name}] could not resolve source/dest channel, skipping.")
        return

    last_id = state.get(name)
    try:
        # Only the fetch is time-bounded. It's read-only and each channel has its own
        # connection, so cancelling it on timeout can't corrupt another channel or
        # leave a dangling send in flight -- unlike the translate/send loop below,
        # which must NOT be cancelled (see its comment for why).
        messages = await asyncio.wait_for(
            fetch_new_messages(client, source_channel, last_id), timeout=FETCH_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        logging.error(f"[{name}] fetch exceeded {FETCH_TIMEOUT_SECONDS}s, skipping this tick.")
        return
    except FloodWaitError as e:
        logging.warning(f"[{name}] flood wait {e.seconds}s while fetching messages, skipping this tick.")
        return
    except Exception as e:
        logging.error(f"[{name}] error fetching messages: {e}")
        return

    if not messages:
        return

    if len(messages) >= MESSAGES_PER_CHANNEL_LIMIT:
        logging.info(f"[{name}] backlog capped at {MESSAGES_PER_CHANNEL_LIMIT}, remainder will catch up next ticks.")

    # Deliberately NOT wrapped in asyncio.wait_for/a timeout: translate_or_fallback
    # runs on a thread (asyncio.to_thread), and cancelling the coroutine awaiting a
    # thread does NOT stop that thread -- it keeps running in the background and can
    # still call send_message later, after this coroutine already considered itself
    # "given up" and moved on (confirmed live: a message landed in the destination
    # channel with the fallback prefix well after the tick had logged a timeout and
    # disconnected). Since state is only saved after a successful send, a message
    # sent that way would never get recorded and would be resent on the next tick --
    # a real duplicate-post bug. MESSAGES_PER_CHANNEL_LIMIT above is what keeps this
    # loop's total worst-case duration bounded instead; the run.lock file (see
    # acquire_lock) safely absorbs a tick that runs past the next cron minute.
    for msg in messages:
        if not msg.text and not msg.media:
            state[name] = msg.id
            save_state(state)
            continue

        text_to_send = ""
        if msg.text and msg.text.strip():
            # translate_or_fallback does blocking requests.post/time.sleep calls --
            # run it on a thread so it can't freeze the asyncio event loop (which
            # would also stall Telethon's own connection handling and defeat any
            # asyncio.wait_for timeout wrapping this coroutine).
            text_to_send = await asyncio.to_thread(translate_or_fallback, msg.text, api_keys)

        try:
            if msg.media:
                try:
                    await client.send_message(dest_channel, file=msg.media, message=text_to_send)
                except Exception as e:
                    logging.warning(f"[{name}] send with caption failed, retrying without: {e}")
                    await client.send_message(dest_channel, file=msg.media)
            else:
                await client.send_message(dest_channel, text_to_send)
            logging.info(f"[{name}] forwarded message {msg.id}")
        except FloodWaitError as e:
            if e.seconds <= MAX_FLOOD_WAIT_SECONDS:
                logging.warning(f"[{name}] flood wait {e.seconds}s, retrying once.")
                time.sleep(e.seconds)
                try:
                    if msg.media:
                        await client.send_message(dest_channel, file=msg.media, message=text_to_send)
                    else:
                        await client.send_message(dest_channel, text_to_send)
                except Exception as e2:
                    logging.error(f"[{name}] retry after flood wait failed for message {msg.id}: {e2}")
                    break
            else:
                logging.error(f"[{name}] flood wait {e.seconds}s exceeds cap, stopping this tick for this channel.")
                break
        except Exception as e:
            logging.error(f"[{name}] error sending message {msg.id}: {e}")
            break

        try:
            await client.send_read_acknowledge(source_channel, max_id=msg.id)
        except Exception as e:
            logging.warning(f"[{name}] read-ack failed for message {msg.id}: {e}")

        state[name] = msg.id
        save_state(state)


def ping_healthcheck():
    url = os.getenv("HEALTHCHECK_URL")
    if not url:
        return
    try:
        requests.get(url, timeout=10)
    except Exception as e:
        logging.warning(f"Healthcheck ping failed: {e}")


async def main(only_channel=None):
    api_id = int(os.environ["API_ID"])
    api_hash = os.environ["API_HASH"]
    phone_number = os.environ["PHONE_NUMBER"]
    api_keys = [k.strip() for k in os.environ["OPENROUTER_API_KEYS"].split(",") if k.strip()]

    channels = load_channels()
    if only_channel:
        channels = [c for c in channels if c["name"] == only_channel]
        if not channels:
            logging.error(f"No channel named '{only_channel}' in config/channels.json")
            print(f"No channel named '{only_channel}' in config/channels.json")
            return
    state = load_state()

    # Each channel gets its own connect/disconnect cycle on a fresh client instance
    # (same session/account -- Telethon supports multiple concurrent connections from
    # one authorized session, which is exactly what the original per-bot processes did).
    # This is deliberate isolation: asyncio.wait_for's timeout cancels the coroutine it
    # wraps, and cancelling a Telethon request mid-flight can corrupt that connection's
    # internal state. With one client shared across all 9 channels, a single timeout
    # cascaded into every subsequent channel hanging on the same now-broken connection --
    # confirmed live during testing. A fresh connection per channel contains the damage
    # to just that channel.
    for i, channel_cfg in enumerate(channels):
        if i > 0:
            await asyncio.sleep(1.5)  # space out connections across channels
        name = channel_cfg["name"]
        client = build_client(api_id, api_hash)
        try:
            await asyncio.wait_for(client.start(phone_number), timeout=FETCH_TIMEOUT_SECONDS)
            # process_channel itself is not time-bounded here -- see its comment on
            # why cancelling the translate/send loop is unsafe. Its own fetch step is
            # bounded internally; the send/translate portion runs to completion.
            await process_channel(client, channel_cfg, state, api_keys)
        except asyncio.TimeoutError:
            logging.error(f"[{name}] connect exceeded {FETCH_TIMEOUT_SECONDS}s, moving on.")
        finally:
            await client.disconnect()

    if not only_channel:
        ping_healthcheck()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", help="Process only this one channel (by name in config/channels.json), for testing.")
    args = parser.parse_args()

    if not acquire_lock():
        sys.exit(0)
    try:
        asyncio.run(main(only_channel=args.channel))
    finally:
        release_lock()

"""
One-time interactive provisioning for the single shared Telegram session used by
bot/run_tick.py. Only needed if session/main.session doesn't exist yet or has been
invalidated (e.g. logged out from another device). Prompts for the Telegram login
code on first run.
"""
import os

from dotenv import load_dotenv

from bot.telegram_client import build_client

ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT, ".env"))

if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "session"), exist_ok=True)
    api_id = int(os.environ["API_ID"])
    api_hash = os.environ["API_HASH"]
    phone_number = os.environ["PHONE_NUMBER"]

    client = build_client(api_id, api_hash)
    client.start(phone_number)
    print("Session created at session/main.session")
    client.disconnect()

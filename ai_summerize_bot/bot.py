import sys
import logging
from config import API_ID, API_HASH, SOURCE_CHANNEL_ID, DEST_CHANNEL_ID, PHONE_NUMBER
from summarizer import summarize
from utils import (
    fetch_messages,
    send_message,
    find_group,
    connect_to_client,
    filter_messages,
    get_time_range
)

logging.basicConfig(level=logging.INFO)

NUM_OF_MESSAGES = 500  # Number of messages to fetch
client = connect_to_client(API_ID, API_HASH)

async def main():
    """
    Main bot logic:
    - Finds source and destination channels
    - Fetches messages
    - Filters messages by time range (day/night)
    - Summarizes and sends to destination
    """
    logging.info("Starting the bot...")
    source_channel = await find_group(client, SOURCE_CHANNEL_ID)
    destination_channel = await find_group(client, DEST_CHANNEL_ID)

    if not source_channel or not destination_channel:
        logging.error("Could not find source or destination channel.")
        return

    all_messages = await fetch_messages(client, source_channel, NUM_OF_MESSAGES)

    # Get period from command-line argument: "day" or "night"
    period = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] == "night" else "day"
    start_dt, end_dt = get_time_range(period)

    filtered_messages = filter_messages(all_messages, start_dt, end_dt)

    summary = await summarize(filtered_messages, period)
    if not summary:
        logging.info("empty summary, nothing to send.")
        return

    await send_message(client, summary, destination_channel)

if __name__ == "__main__":
    client.start(PHONE_NUMBER)
    client.loop.run_until_complete(main())

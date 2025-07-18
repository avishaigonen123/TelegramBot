import logging
from open_router_api import summarize_text_remotely

logging.basicConfig(level=logging.INFO)

async def summarize(messages: str, destination_channel_link: str) -> str:
    logging.info(f"Summarizing {len(messages)} messages...")
    combined_text = "\n".join([msg['content'] for msg in messages if msg['content']])
    logging.info(f"Combined text for summarization: {combined_text}")
    summary = summarize_text_remotely(combined_text, destination_channel_link)
    logging.info(f"Summary received: {summary}")
    return summary
from googletrans import Translator
from telethon import TelegramClient, events, types

# Replace '22426045' and 'e7b8ee99e8bf9c36984d18f1baae5591' with your actual API ID and API hash
api_id = 22426045
api_hash = 'e7b8ee99e8bf9c36984d18f1baae5591'

# Replace 'mySession' with a unique session name
session_name = 'gonenSession'

# Replace '-1001300814792' with the actual chat ID of the source channel
source_channel_id = -1001300814792

# Replace '-1002027365084' with the actual chat ID of your bot's channel
destination_channel_id = -1002027365084

# Create a TelegramClient instance
client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(chats=source_channel_id))
async def translate_and_forward(event):
    message = event.message

    print(f"Translating and forwarding message with ID: {message.id}.")
    print(message.text)
    # Translate the message text to Hebrew
    translator = Translator()
    # Use message.text directly
    translated_text = translator.translate(message.text, dest='he').text

    print(f"Translated Text: {translated_text}")  # Print the translated text for debugging

 # If the message has a photo, forward it with translated caption
    if message.photo:
        # Forward the message with the translated text as the caption
        await client.send_message(destination_channel_id, translated_text, file=message.photo)


    # If the message has a video, forward it with translated caption
    elif message.video:
        # Forward the message with the translated text as the caption
        await client.send_message(destination_channel_id, translated_text, file=message.video)


    # If the message is text only, forward the translated text
    else:
        # Forward the message with the translated text as the message text
        await client.send_message(destination_channel_id, translated_text)




client.start("+972585328077")
# Start the userbot
client.run_until_disconnected()

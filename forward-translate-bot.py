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
    if message.text:  # maybe there would be a picture without text
        #print(f"Translating and forwarding message with ID: {message.id}.")
        #print(message.text)
        # Translate the message text to Hebrew
        translator = Translator()
        # Use message.text directly
        translated_text = translator.translate(message.text, dest='he').text

        #print(f"Translated Text: {translated_text}")  # Print the translated text for debugging
        message.text = translated_text
    await client.send_message(destination_channel_id, message)


                  
async def findGroup(GroupID: int):
    async for i in client.iter_dialogs(folder=0):
        if i.id==GroupID:
            return i
        


async def main():
    translator = Translator()

    source_channel = await findGroup(source_channel_id)
    destination_channel = await findGroup(destination_channel_id)

    if source_channel.unread_count!=0:
        count=source_channel.unread_count
        mess=[]
        async for i in client.iter_messages(source_channel,count):
            if not (i.action):#patched.Message.
                    mess+=[i]
        mess.reverse()
        if len(mess)>0:
           for i in mess:
                sendMes=i
                if(sendMes.text):
                    sendMes.text=translator.translate(sendMes.text, dest='he').text
                await client.send_message(destination_channel,sendMes)
                await client.send_read_acknowledge(source_channel,max_id=i.id)

    #else: print("not found new messages")
    
    #translation = translator.translate("Der Himmel ist blau und ich mag Bananen", dest='he')
    #print(translation.text)
    


client.start("+972585328077") # here enter your phone number, in the first time you would need to give the code from telegram, each time you create a new session

# Run the main function once before starting the event loop
client.loop.run_until_complete(main()) # i want that first it will send all the unread messages, and then it will use the event mechanic.

# Start the userbot and run the event loop
client.run_until_disconnected()
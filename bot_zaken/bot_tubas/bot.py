import config
from googletrans import Translator
from telethon import TelegramClient, events, types
import random

api_id = config.API_ID
api_hash = config.API_HASH

source_channel_id = config.SOURCE_CHANNEL_ID
destination_channel_id = config.DEST_CHANNEL_ID

phone_number = config.PHONE_NUMBER

sessions_list = ['gonenSession751966', 'gonenSession308740', 'gonenSession633348']

# Create a TelegramClient instance
client = TelegramClient(sessions_list[random.randint(0,len(sessions_list)-1)], api_id, api_hash) 


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
            if not (i.action): #patched.Message.
                mess.insert(0,i)

        if len(mess)>0:
            for i in mess:
                    sendMes=i
                    if(sendMes.text):
                        sendMes.text=translator.translate(sendMes.text, dest='he').text
                    await client.send_message(destination_channel,sendMes)
                    await client.send_read_acknowledge(source_channel,max_id=i.id)



client.start(phone_number)
# Run the main function once before starting the event loop
client.loop.run_until_complete(main()) # i want that first it will send all the unread messages, and then it will use the event mechanic.

from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sessions import StringSession
import json
import random
import time

# Load configuration and language files
file_1 = open('./config.json').read()
config = json.loads(file_1)
file_2 = open('./lang.json', encoding='utf-8').read()
lang = json.loads(file_2)

API_ID = config['API_ID']
API_HASH = config['API_HASH']
STRING_SESSION = config['STRING_SESSION']
COMMENT_TEXT = config['COMMENT_TEXT']

# Initialize client
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# Load channel IDs
CHANNEL_ID = config['CHANNEL_ID']


# Helper function to join a channel if not already joined
async def join_channel_if_needed(channel_id):
    try:
        await client(JoinChannelRequest(channel_id))
        print(f"Successfully joined channel: {channel_id}")
    except errors.UserAlreadyParticipantError:
        print(f"Already a member of the channel: {channel_id}")
    except Exception as e:
        print(f"Failed to join channel {channel_id}: {e}")


# Function to check and join all channels
async def check_and_join_channels():
    for channel_id in CHANNEL_ID:
        await join_channel_if_needed(channel_id)


# Auto comment function for new messages in channels
@client.on(events.NewMessage)
async def auto_comment(event):
    if event.chat_id not in CHANNEL_ID:
        return

    # Ensure user is joined in the channel before commenting
    await join_channel_if_needed(event.chat_id)

    try:
        await client.send_message(event.chat_id, random.choice(COMMENT_TEXT), comment_to=event.id)
        print(f"Commented on new post in {event.chat_id}")
    except errors.FloodWaitError as e:
        print(f"Flood wait error: {e.seconds} seconds")
        time.sleep(e.seconds)
    except Exception as e:
        print(f"Error while commenting: {e}")


# Main function to start the client
async def main():
    # Check and join channels at startup
    await check_and_join_channels()
    print("Client is ready and joined necessary channels!")


# Start the client and run the main function
with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()

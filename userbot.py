import asyncio
from telethon import *
from telethon.sessions import StringSession
import random
import json
import time
import re

file_1 = open('./config.json').read()
config = json.loads(file_1)
file_2 = open('./lang.json', encoding='utf-8').read()
lang = json.loads(file_2)

API_ID = config['API_ID']
API_HASH = config['API_HASH']
STRING_SESSION = config['STRING_SESSION']

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH).start()

client.parse_mode = 'html'

COMMENT_TEXT = config['COMMENT_TEXT']

_lang = config['LANGUAGE']
lang = lang[_lang]


def CONFIG_FUNC():
    file = open('config.json')
    read = file.read()
    j = json.loads(read)
    file.close()
    return j


global CHANNEL_ID
CHANNEL_ID = CONFIG_FUNC()['CHANNEL_ID']


@client.on(events.NewMessage)
async def _auto_comment(event):
    if event.chat_id not in CHANNEL_ID:
        return

    # گرفتن آی‌دی پست و نام کاربری کانال (در صورت وجود)
    post_id = event.id
    channel_username = event.chat.username if event.chat.username else "بدون نام کاربری"

    print(f"پست جدید در کانال: {channel_username} (آی‌دی کانال: {event.chat_id}), آی‌دی پست: {post_id}")

    try:
        # ارسال کامنت تصادفی از لیست COMMENT_TEXT
        await client.send_message(event.chat_id, random.choice(COMMENT_TEXT), comment_to=post_id)
        print(f"کامنت ارسال شد به پست {post_id} در کانال {channel_username}")
        delay = random.uniform(10, 20)
        time.sleep(delay)
    except errors.FloodWaitError as e:
        print(lang['FLOOD_WAIT_ERROR'].format(e.seconds))
        time.sleep(e.seconds)
    except Exception as e:
        print(lang['ERROR_WHILE_POSTING'] + '\n' + str(e))


async def monitor_channels():
    """مانیتور کردن پیام‌های جدید از کانال‌ها"""
    while True:
        for channel_id in CHANNEL_ID:
            try:
                async for message in client.iter_messages(channel_id):
                    # چاپ متن پیام و نام کاربری یا آی‌دی کانال
                    print(
                        f"پیام جدید در کانال {message.chat.username if message.chat.username else message.chat_id}: {message.text}")
                    await _auto_comment(message)
            except Exception as e:
                print(f"Error while fetching messages from {channel_id}: {str(e)}")
        await asyncio.sleep(5)  # بررسی کانال‌ها هر 5 ثانیه یک بار


print(lang['START_MSG'])
client.loop.run_until_complete(monitor_channels())
client.run_until_disconnected()

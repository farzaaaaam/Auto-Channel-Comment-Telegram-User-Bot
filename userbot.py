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

# دیکشنری برای ذخیره آخرین آی‌دی پست هر کانال
last_post_ids = {}


@client.on(events.NewMessage)
async def _auto_comment(event):
    if event.chat_id not in CHANNEL_ID:
        return

    post_id = event.id
    channel_username = event.chat.username if event.chat.username else "بدون نام کاربری"

    # بررسی آی‌دی آخرین پست در این کانال
    if event.chat_id in last_post_ids:
        if post_id <= last_post_ids[event.chat_id]:
            # اگر پست قدیمی یا تکراری است، هیچ کاری انجام نده
            return

    # ذخیره آی‌دی پست به عنوان آخرین پست پردازش شده برای این کانال
    last_post_ids[event.chat_id] = post_id

    print(f"پست جدید در کانال: {channel_username} (آی‌دی کانال: {event.chat_id}), آی‌دی پست: {post_id}")

    try:
        time.sleep(3)
        message = (
            "❤️‍🔥 <b>آهای ایرانی با غیرتی که پیاممو میخونی</b>❗️\n\n"
            "<b><i>امیدوارم</i></b>\n\n"
            "<b><i>امسال</i></b>\n\n"
            "<u>خودت و خانوادت در </u>"
            "<b>سلامتی و عشق</b> "
            "<u>باشید!</u>"
        )

        await client.send_message(event.chat_id, message, comment_to=post_id,parse_mode='html')
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
                # مانیتور کردن فقط آخرین پیام‌ها از هر کانال
                async for message in client.iter_messages(channel_id, limit=1):
                    print(
                        f"پیام جدید در کانال {message.chat.username if message.chat.username else message.chat_id}: {message.text}")
                    await _auto_comment(message)
            except Exception as e:
                print(f"Error while fetching messages from {channel_id}: {str(e)}")
        await asyncio.sleep(5)  # بررسی کانال‌ها هر 5 ثانیه یک بار


print(lang['START_MSG'])
client.loop.run_until_complete(monitor_channels())
client.run_until_disconnected()

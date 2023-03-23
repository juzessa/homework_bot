
import logging
import os
from datetime import time

import requests
import telegram
from dotenv import load_dotenv
from telegram import Bot

PRACTICUM_TOKEN = os.getenv('token')
TELEGRAM_TOKEN = os.getenv('telegram_token')
TELEGRAM_CHAT_ID = os.getenv('chat_id')

PRACTICUM_TOKEN = 'y0_AgAAAABlRb_RAAYckQAAAADeUpc1zl2ir9wpTomQBZIGi6gQUQyJBJA'
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
PAYLOAD = {'from_date': 0}
homework_status = requests.get(ENDPOINT, headers=HEADERS, params=PAYLOAD)
response = homework_status.json()
print(response)

TELEGRAM_TOKEN = '5736618803:AAHn6k7hXNdL01GTgphrU5yb26QH9Bk0J24'
TELEGRAM_CHAT_ID = '474780451'

bot = telegram.Bot(token=TELEGRAM_TOKEN)
print(bot.send_message(TELEGRAM_CHAT_ID, 'Hi'))
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from endpoints import API_YANDEX_ENDPOINT

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log',
    filemode='w'
)

PRACTICUM_TOKEN = os.getenv('token')
TELEGRAM_TOKEN = os.getenv('telegram_token')
TELEGRAM_CHAT_ID = os.getenv('chat_id')


RETRY_PERIOD = 600
ENDPOINT = API_YANDEX_ENDPOINT
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция проверяет, что все переменные доступны."""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logging.critical('Отсутствие переменных')
    return(all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]))


def send_message(bot, message):
    """Отправляет сообщение в телеграм."""
    logging.info('Начали отправку сообщения в tg')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение успешно отправлено')
    except Exception as error:
        logging.error(f'Сообщение не отправлено {error}')


def get_api_answer(timestamp):
    """Функция проверяет статус API."""
    try:
        homework_status = requests.get(
            ENDPOINT, headers=HEADERS, params={
                'from_date': timestamp})
        response = homework_status.json()
        if homework_status.status_code != HTTPStatus.OK:
            raise ConnectionRefusedError('API недоступна')
        return response
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        raise ConnectionRefusedError('API недоступна')


def check_response(response):
    """Функция проверяет, что ответ соответствует ожидаемому."""
    logging.info('Начали проверять ответ API')
    if not isinstance(response, dict):
        logging.error('Неожиданный статус домашней работы')
        raise TypeError('Wrong format of the response')
    if response.get('homeworks') is None:
        logging.error('Неожиданный статус домашней работы')
        raise KeyError('Wrong format of the response')
    if not isinstance(response['homeworks'], list):
        logging.error('Неожиданный статус домашней работы')
        raise TypeError('Wrong format of the response')
    if 'homeworks' not in response or 'current_date' not in response:
        logging.error('Неожиданный статус домашней работы')
        raise TypeError('Wrong format of the response')
    return response['homeworks'][0]


def parse_status(homework):
    """Функция проверяет, что статус соответствует ожидаемому."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status is None:
        raise KeyError('No new status')
    if homework_name is None:
        logging.debug('Отсутствие в ответе новых статусов')
        raise TypeError('No new homework')
    if homework_status not in HOMEWORK_VERDICTS:
        logging.debug('Неверный формат')
        raise TypeError('Ответ не соответсвует ожидаемому')
    return (f'Изменился статус проверки'
            f' работы "{homework_name}". {HOMEWORK_VERDICTS[homework_status]}')


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    if not check_tokens():
        sys.exit()

    while True:
        try:
            homeworks = get_api_answer(timestamp)
            one_homework = check_response(homeworks)
            if len(one_homework) != 0:
                message = parse_status(one_homework)
            else:
                message = None

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.ERROR(message)
        finally:
            if message is not None:
                send_message(bot, message)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

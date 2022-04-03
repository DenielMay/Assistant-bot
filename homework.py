import sys
import requests
import time
import telegram
import os
import logging
from dotenv import load_dotenv
from http import HTTPStatus

from exceptions import SendMessageError, NoApiResponse

load_dotenv()

secret_token = os.getenv('TOKEN')

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s')
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """Функция отправки сообщений."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info('Сообщение отправлено')
    except SendMessageError:
        logging.error('Сообщение не отправлено')


def get_api_answer(current_timestamp):
    """Функция запроса от API."""
    while True:
        timestamp = current_timestamp or int(time.time())
        params = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            logging.error('Нет ответа от API')
            raise NoApiResponse


def check_response(response):
    """Функция проверки запроса."""
    if isinstance(response, dict) and 'homeworks' in response:
        homeworks = response['homeworks']
        if isinstance(homeworks, list):
            return response.get('homeworks')
        else:
            logging.error('Отсутствие ожидаемых ключей в ответе API')
            raise TypeError('Под ключом `homeworks` домашки приходят не в '
                            'виде списка в ответ от API')
    else:
        logging.error('Отсутствие ожидаемых ключей в ответе API')
        raise TypeError('Ответ от API не является словарем')


def parse_status(homework):
    """Парсинг статуса."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status not in HOMEWORK_STATUSES:
        logging.debug('Отсутствие в ответе новых статусов')
        raise KeyError('Отсутствие в ответе новых статусов')
    else:
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверки обязательных переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    else:
        return False


def main():
    """Основная функция."""
    if check_tokens() is False:
        logger.critical('Отсутствие обязательных переменных окружения во '
                        'время запуска бота')
    else:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())

        while True:
            try:
                response = get_api_answer(current_timestamp)
                homeworks = check_response(response)
                for work in homeworks:
                    message = parse_status(work)
                    send_message(bot, message)
                    logger.info(f'Сообщение {message} успешно отправлено')
                current_timestamp = current_timestamp = int(
                    response['current_date'])

            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.critical('Сбой в работе программы')
                send_message(bot, message)
            finally:
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

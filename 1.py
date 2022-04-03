import requests


def get_api_answer():
    PRACTICUM_TOKEN = 'AQAAAAAMRD9ZAAYckXJe2Avhp0ASmUyyE7i70Og'
    ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
    HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    """Функция запроса от API."""
    params = {'from_date': 0}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    print(response.json())

get_api_answer()
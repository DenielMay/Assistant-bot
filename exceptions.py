class SendMessageError(Exception):
    def __str__(self):
        return 'Ошибка отправки сообщения'


class NoApiResponse(Exception):
    def __str__(self):
        return 'Нет ответа от API'

class SendMessageError(Exception):
    def SendMessageError(self):
        return 'Ошибка отправки сообщения'


class NoApiResponse(Exception):
    def NoApiResponse(self):
        return 'Нет ответа от API'

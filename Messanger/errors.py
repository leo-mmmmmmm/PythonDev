"""Все ошибки"""


class UsernameToLongError(Exception):
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f'Имя пользователя {self.username} должно быть менее 26 символов'


class ResponseCodeError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f'Неверный код ответа {self.code}'


class ResponseCodeLenError(ResponseCodeError):
    def __str__(self):
        return f'Неверная длина кода {self.code}. Длина кода должна быть 3 символа.'


class MandatoryKeyError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f'Не хватает обязательного атрибута {self.key}'


class WrongAnswerError(Exception, ):
    def __init__(self, reply):
        self.reply = reply

    def __str__(self):
        return f'Неверно введенные данные: {self.reply}. Запустите клиент заново.'




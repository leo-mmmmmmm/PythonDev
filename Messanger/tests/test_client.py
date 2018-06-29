import time
import json
from pytest import raises
import socket
from homework_03.client import Client
from homework_03.errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, \
    ResponseCodeError, WrongAnswerError


# МОДУЛЬНЫЕ ТЕСТЫ


def test_create_presence():
    # Без параметров
    message = Client.create_presence()
    assert message['action'] == "presence"
    # Берем разницу во времени
    assert abs(message['time'] - time.time()) < 0.1
    assert message["user"]["account_name"] == 'Guest'
    # С именем
    message = Client.create_presence('test_user_name')
    assert message["user"]["account_name"] == 'test_user_name'
    # Неверный тип
    with raises(TypeError):
        Client.create_presence(200)
    with raises(TypeError):
        Client.create_presence(None)
    # Имя пользователя слишком длинное
    with raises(UsernameToLongError):
        Client.create_presence('11111111111111111111111111')


def test_translate_message():
    # Неправильный тип
    with raises(TypeError):
        Client.translate_message(100)
    # Неверная длина кода ответа
    with raises(ResponseCodeLenError):
        Client. translate_message({'response': '5'})
    # Нет ключа response
    with raises(MandatoryKeyError):
        Client.translate_message({'one': 'two'})
    # неверный код ответа
    with raises(ResponseCodeError):
        Client.translate_message({'response': 700})
    # Всё правильно
    assert Client.translate_message({'response': 200}) == {'response': 200}




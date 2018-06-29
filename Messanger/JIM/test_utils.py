from pytest import raises
import socket
import json
from .utils import JimSend, JimRcv, JimTranslate


# МОДУЛЬНОЕ ТЕСТИРОВАНИЕ
def test_dict_to_bytes():
    with raises(TypeError):
        JimTranslate.dict_to_bytes('abc')
    assert JimTranslate.dict_to_bytes({'test': 'test'}) == b'{"test": "test"}'


def test_bytes_to_dict():
    with raises(TypeError):
        JimTranslate.bytes_to_dict(100)
    with raises(TypeError):
        JimTranslate.bytes_to_dict(b'["abc"]')
    assert JimTranslate.bytes_to_dict(b'{"test": "test"}') == {'test': 'test'}


# ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ

# Класс-заглушка для сокета клиента
class ClientSocket():
    """Класс-заглушка для операций с сокетом"""

    def __init__(self, sock_type=socket.AF_INET, sock_family=socket.SOCK_STREAM):
        pass

    def recv(self, n):

        message = {'response': 200}
        jmessage = json.dumps(message)
        bmessage = jmessage.encode('utf-8')
        return bmessage

    def send(self, bmessage):
        # Можно переопределить метод send просто pass
        pass


def test_get_message(monkeypatch):
    # Подменяем настоящий сокет нашим классом заглушкой
    monkeypatch.setattr("socket.socket", ClientSocket)
    # Создаем сокет, он уже был подменен
    sock = socket.socket()
    # Теперь можем протестировать работу метода
    assert JimRcv.get_message(sock) == {'response': 200}


def test_send_message(monkeypatch):
    # Подменяем настоящий сокет нашим классом заглушкой
    monkeypatch.setattr("socket.socket", ClientSocket)
    # Создаем сокет, он уже был подменен
    sock = socket.socket()
    # Т.к. возвращаемого значения нет, можно просто проверить, что метод отрабатывает без ошибок
    assert JimSend.send_message(sock, {'test': 'test'}) is None
    # И проверяем, чтобы обязательно передавали словарь на всякий пожарный
    with raises(TypeError):
        JimSend.send_message(sock, 'test')


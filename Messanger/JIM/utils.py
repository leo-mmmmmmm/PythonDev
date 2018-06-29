import json
from logs.info_log_decorator import info_log


# Кодировка
ENCODING = 'utf-8'


class JimTranslate:

    @staticmethod
    def dict_to_bytes(message_dict):
        """
        Преобразование словаря в байты
        :param message_dict: словарь
        :return: bytes
        """
        # Проверям, что пришел словарь
        if isinstance(message_dict, dict):
            # Преобразуем словарь в json
            jmessage = json.dumps(message_dict)
            # Переводим json в байты
            bmessage = jmessage.encode(ENCODING)
            # Возвращаем байты
            return bmessage
        else:
            raise TypeError

    @staticmethod
    def bytes_to_dict(message_bytes):
        """
        Получение словаря из байтов
        :param message_bytes: сообщение в виде байтов
        :return: словарь сообщения
        """
        # Если переданы байты
        if isinstance(message_bytes, bytes):
            # Декодируем
            jmessage = message_bytes.decode(ENCODING)
            # Из json делаем словарь
            message = json.loads(jmessage)
            # Если там был словарь
            if isinstance(message, dict):
                # Возвращаем сообщение
                return message
            else:
                # Нам прислали неверный тип
                raise TypeError
        else:
            # Передан неверный тип
            raise TypeError


class JimSend:

    def __init__(self, sock):
        self.sock = sock

    def send_message(self, message):
        """
        Отправка сообщения
        :param sock: сокет
        :param message: словарь сообщения
        :return: None
        """
        # Словарь переводим в байты
        bprescence = JimTranslate.dict_to_bytes(message)
        # Отправляем
        self.sock.send(bprescence)


class JimRcv:

    def __init__(self, sock):
        self.sock = sock

    def get_message(self):
        """
        Получение сообщения
        :param sock:
        :return: словарь ответа
        """
        # Получаем байты
        bresponse = self.sock.recv(1024)
        if bresponse != b'':
            # переводим байты в словарь
            response = JimTranslate.bytes_to_dict(bresponse)
            # возвращаем словарь
            return response

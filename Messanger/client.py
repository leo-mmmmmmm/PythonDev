import time
from socket import socket, AF_INET, SOCK_STREAM
from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, \
    ResponseCodeError
from JIM.utils import JimSend, JimRcv
from JIM.config import *
from logs.info_log_decorator_config import logger

ADDRESS = ('localhost', 8777)


def translate_message(response):
    """
    Разбор сообщения
    :param response: Словарь ответа от сервера
    :return: корректный словарь ответа
    """
    # Передали не словарь
    if not isinstance(response, dict):
        logger.error('С сервера был передан не словарь.')
        raise TypeError
    # Нету ключа response
    if RESPONSE not in response:
        # Ошибка нужен обязательный ключ
        logger.error('С сервера не пришёл ключ в response.')
        raise MandatoryKeyError(RESPONSE)
    # получаем код ответа
    code = response[RESPONSE]
    logger.debug(f'Получен код ответа: { code }')
    # длина кода не 3 символа
    if len(str(code)) != 3:
        # Ошибка неверная длина кода ошибки
        logger.error('Неверная длина кода ответа сервера.')
        raise ResponseCodeLenError(code)
    # неправильные коды символов
    if code not in RESPONSE_CODES:
        # ошибка неверный код ответа
        logger.error('Несуществующий код ответа сервера.')
        raise ResponseCodeError(code)
    # возвращаем ответ
    logger.debug(f'Возвращается ответ: { response }')
    return response


class Client:

    def create_presence(self):
        """
        Формируем ​​presence-сообщение
        :param account_name: Имя пользователя
        :return: Словарь сообщения
        tests: pytest
        """

        # Если имя не строка
        if not isinstance(self.login, str):
            logger.error(f'Введённый account_name: { self.login } - не является строкой.')
            raise TypeError
        # Если длина имени пользователя больше 20 символов
        if len(self.login) >= 20:
            logger.error(
                f'Длина account_name: { self.login } - превышает разрешённую. Максимальная длина имени 20 символов.')
            raise UsernameToLongError(self.login)

        # Формируем словарь сообщения
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                LOGIN: self.login,
                PASSWORD: self.password
            }
        }
        logger.debug('Формируем presence-message.')

        return message

    def choice(self):

        print('Нажмите -hepl, чтобы получить полный список команд.')
        reply = input()
        if reply[0] == '-':
            if reply[1:] == 'help':
                logger.debug('Пользователь. Список всех команд.')
                print(
                    '-w == писать сообщения, \n'
                    '-r == читать сообщения, \n'
                    '-add username == добавить в друзья username \n'
                    '-del username == удалить из друзей username \n'
                    '-get_contacts == получить список контактов, \n'
                    '-exit == выйти'

                )
                Client.choice(self)
            elif reply[1:] == 'w':
                logger.debug('Пользователь. Отправка сообщений.')
                Actions(self.sock).write_client()
            elif reply[1:] == 'r':
                logger.debug('Пользователь. Получение сообщений.')
                Actions(self.sock).read_client()
            elif reply[1:] == 'get_contacts':
                Actions(self.sock).get_contacts()
            elif reply[1:] == 'exit':
                raise ERROR
            elif 'add' in reply[1:]:
                pass
            elif 'del' in reply[1:]:
                pass
            else:
                print('Неверно введенная команда. Повторите попытку.')
                logger.debug('Неправльно введенные данные при выборе функции.')
                Client.choice(self)
        else:
            print('Неверно введенная команда. Повторите попытку.')
            logger.debug('Неправльно введенные данные при выборе функции.')
            Client.choice(self)

    def __init__(self):

        # Получаем логин и пароль
        self.get_login_pas()
        # Подключаемся
        self.connect()
        self.choice()

    def get_login_pas(self):
        print('Введите Ваш логин и пароль или выйдете, набрав -escape')

        reply = input()

        if reply == '-escape':
            raise ERROR
        else:
            self.login = reply
            self.password = input()

    def connect(self):
        # Соединиться с сервером
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect(ADDRESS)
        # Создаем сообщение
        self.presence = self.create_presence()
        # Отсылаем сообщение
        logger.debug('Отправляем presence-message.')
        JimSend(self.sock).send_message(self.presence)
        # Получаем ответ
        logger.debug('Получаем ответ сервера.')
        response = JimRcv(self.sock).get_message()
        # Проверяем ответ
        logger.debug('Проверяем ответ сервера.')
        response = translate_message(response)
        logger.debug(f'Ответ сервера: {response}')
        return response


class Actions:

    def __init__(self, sock):
        self.sock = sock

    def write_client(self):
        message = {
            ACTION: 'write',
            'message': '',
            TIME: time.time()
        }

        while True:
            message['message'] = input('Ваше сообщение: ')

            # TODO: logger.info(f'Введено сообщение: { message['message'] }')
            if message['message'] == '-exit':
                logger.debug(print(f'Клиент { self.sock.fileno() } { self.sock.getpeername() } отключился.'))
                break

            JimSend(self.sock).send_message(message)
            logger.debug('Сообщение было успешно отправлено.')

            data = JimRcv(self.sock).get_message()

            print(f'Вы отправили: { data["message"] }')

    def read_client(self):

        while True:
            data = JimRcv(self.sock).get_message()
            logger.debug(f'Пользователь получил ответ: { data["message"] }')
            print(f'Ответ: { data["message"] }')

    def get_contacts(self):
        # Формируем словарь сообщения
        message = {
            ACTION: 'get_contacts',
            TIME: time.time(),
        }

        JimSend(self.sock).send_message(message)

        data = JimRcv(self.sock).get_message()
        # TODO: response = translate_message(response)
        logger.debug(f'Ответ сервера: { data }')
        print(data)

        for i in range(data['quantity']):
            response = JimRcv(self.sock).get_message()
            print(response)

        Actions(self.sock)


if __name__ == '__main__':
    client = Client()

























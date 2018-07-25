import sys
import select
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from JIM.utils import JimRcv, JimSend
from JIM.config import *
from logs.info_log_decorator_config import logger
from logs.info_log_decorator import info_log, log_extra
from server_db import User, UserHistory, Session


class Server:

    def presence_response(self):
        """
        Формирование ответа клиенту
        :param presence_message: Словарь presence запроса
        :return: Словарь ответа
        """
        # Делаем проверки
        if ACTION in self.presence and \
                self.presence[ACTION] == PRESENCE and \
                TIME in self.presence and \
                isinstance(self.presence[TIME], float):
            # Если всё хорошо шлем ОК
            logger.info('Клиент подключён.')

            return {RESPONSE: 200}
        else:
            # Шлем код ошибки
            logger.error('Не верный запрос.')
            return {RESPONSE: 400, ERROR: 'Не верный запрос'}

    def add_user_db(self):

        # Логин и пароль пользователя
        self.new_user = User(self.presence[USER][LOGIN], self.presence[USER][PASSWORD])

        # IP и время входа пользователя
        new_user_history = UserHistory(
            f'{ datetime.now().month }.{ datetime.now().day }.{ datetime.now().year } | { datetime.now().hour }:{ datetime.now().minute }:{ datetime.now().second }',
            gethostbyname(gethostname()),
            self.new_user.id
        )

        self.session.add(self.new_user)
        self.session.add(new_user_history)

        self.session.commit()

    def get_contacts(self, sock):

        print('USER ', self.new_user)

        quantity = len(self.new_user.all_friends)

        message = {
            RESPONSE: 200,
            'quantity': quantity
        }

        JimSend(sock).send_message(message)

        for i in range(quantity):
            message = {
                'action': 'contact_list',
                'username': self.new_user.all_friends[1].login
            }
            JimSend(sock).send_message(message)
        self.session.close()

    def read_requests(self):
        # Чтение запросов из списка клиентов

        responses = {}  # Словарь ответов сервера вида {сокет: запрос}

        for sock in self.r:
            try:
                data = JimRcv(sock).get_message()
                logger.debug(f'Получили сообщение от клиента: {data}')


                # responses[sock] = data
                for sock2 in self.w:
                    responses[sock2] = data
                logger.debug(f'Отпраляем словарь ответов сервера: {responses}')
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                logger.info('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                self.clients.remove(sock)

        return responses

    def write_responses(self):
        # Эхо-ответ сервера клиентам, от которых были запросы
        for sock in self.w:
            if sock in self.requests:
                try:
                    if self.requests[sock][ACTION] == 'get_contacts':
                        Server.get_contacts(self, sock)
                    elif self.requests[sock][ACTION] == 'write':
                        # Подготовить и отправить ответ сервера
                        resp = {
                            RESPONSE: 200,
                            'message': self.requests[sock]['message']
                        }
                        JimSend(sock).send_message(resp)
                    logger.debug(f'Отвера сервера был отправлен клинету {sock.fileno()} {sock.getpeername()}')
                except:  # Сокет недоступен, клиент отключился
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    logger.info('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    sock.close()
                    self.clients.remove(sock)

    def __init__(self):
        address = ('', 8777)

        try:
            addr = sys.argv[1]
        except IndexError:
            addr = ''
        try:
            port = int(sys.argv[2])
        except IndexError:
            port = 8777
        except ValueError:
            print('Порт должен быть целым числом')
            sys.exit(0)

        self.clients = []

        self.s = socket(AF_INET, SOCK_STREAM)
        # TODO что такое bind, и зачем он нужен
        self.s.bind(address)
        self.s.listen(100)
        self.s.settimeout(0.2)  # Таймаут для операций с сокетом

        while True:

            try:
                self.conn, self.addr = self.s.accept()  # Проверка подключения
                logger.debug('Проверка подключения прошла успешно.')
                # Получаем сообщение от клиента
                self.presence = JimRcv(self.conn).get_message()
                logger.debug(f'Сообщение от клиента было получено: {self.presence}')
                # Формируем ответ
                response = Server.presence_response(self)
                logger.debug(f'Клинту был сформирован ответ: {response}')
                # Отправляем ответ клиенту
                JimSend(self.conn).send_message(response)
                logger.info(f'Клиенту был отправлен ответ: {response}')

                self.connect_to_db()
                print('Done 1')
                # Выполним вход
                Server.login(self)

            except OSError as e:
                pass  # timeout Вышел
            else:
                self.clients.append(self.conn)
            finally:

                # Проверяю наличие событий ввода-вывода
                self.wait = 0
                self.r = []
                self.w = []
                try:
                    self.r, self.w, self.e = select.select(self.clients, self.clients, [], self.wait)
                    # print('r | ', self.r)
                    # print('w | ', self.w)
                    # r делают send
                    # w делают read
                except:
                    pass

                self.requests = Server.read_requests(self)  # Сохраним запросы клиентов
                Server.write_responses(self)  # Выполним отправку ответов клиентам

    def connect_to_db(self):
        self.session = Session()
        print('Session:', self.session)

    def login(self):
        self.login = self.presence[USER][LOGIN]
        self.password = self.presence[USER][PASSWORD]

        user_in_mas = self.session.query(User).filter(User.login == self.login).all()
        self.user = self.session.query(User).filter(User.login == self.login).all()[0]
        if user_in_mas == []:
            self.add_user_db()
        else:
            print('Done 2')
            if self.user.password != self.password:
                self.change_password()

    def change_password(self):
        self.user.password == self.password





if __name__ == '__main__':
    print('Эхо-сервер запущен!')
    Server()

# Служебный скрипт запуска/останова нескольких клиентских приложений

import platform
from subprocess import Popen, PIPE #, CREATE_NEW_CONSOLE

p_list = []

if platform.system() == 'Windows':
    pass

# while True:
#     user = input("Запустить 3 клиента (s) / Закрыть клиентов (x) / Выйти (q) ")
#
#     if user == 'q':
#         break
#     elif user == 's':
#         for _ in range(3):
#             # Флаг CREATE_NEW_CONSOLE нужен для ОС Windows,
#             # чтобы каждый процесс запускался в отдельном окне консоли
#             # p_list.append(Popen(['python', 'client.py'], creationflags=CREATE_NEW_CONSOLE))
#             p1 = Popen('open -a Terminal'.split(), stdout=PIPE)
#             p_list.append(Popen([ 'python3', 'client.py'], stdout=PIPE))
#             p1.stdout.close()
#         print(' Запущено 3 клиента')
#     elif user == 'x':
#         for p in p_list:
#             p.kill()
#         p_list.clear()

def subprocess_cmd(cmd1,cmd2):
    p1 = Popen(cmd1.split(),stdout=PIPE)
    p2 = Popen(cmd2.split(),stdin=p1.stdout,stdout=PIPE)
    p1.stdout.close()
    return p2.communicate()[0]

subprocess_cmd('open -a Terminal','python client.py')

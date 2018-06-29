from logs.info_log_decorator_config import logger
import inspect


class FuncInfo:

    def __call__(self, old_func):
        def new_func(*args, **kwargs):
            logger.info(f'Имя функции: {old_func.__name__}')
            logger.info(f'Параметры по имени: {args}')
            # logger.debug(f'Параметры по названию: {kwargs}')

            result = old_func(*args, **kwargs)
            logger.info(f'Результат {result}')
            return result
        return new_func


info_log = FuncInfo()


class ExtraFuncInfo:

    def __call__(self, old_func):
        def new_func(*args, **kwargs):
            logger.info(f'Функции {old_func.__name__}() вызвана из функции {inspect.stack()[1][3]}')

            result = old_func(*args, **kwargs)
            return result
        return new_func


log_extra = ExtraFuncInfo()




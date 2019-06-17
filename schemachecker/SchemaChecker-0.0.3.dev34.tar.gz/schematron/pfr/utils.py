import errno
import fcntl
import os
import logging
from time import time, sleep


class Translator:
    translation_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'e', 'ж': 'j', 'з': 'z', 'и': 'i',
        'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'c', 'ш': 'sh', 'щ': 'sch',
        'ч': 'ch', 'ы': 'i', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    @staticmethod
    def translate(expr):
        return ''.join(map(lambda ch: Translator.translation_dict.get(ch) or ch,
                           expr.lower()))


class Flock:
    """
    Менеджер контекста для синхронизации записи в файл
    между несколькими процессами
    """
    def __init__(self, path, timeout=None):
        self._path = path
        self._timeout = timeout
        self.fd = None

    def __enter__(self):
        self.fd = os.open(self._path, os.O_RDWR)
        start_time = time()

        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self.fd
            except (OSError, IOError) as ex:
                # Ресурс недоступен
                if ex.errno != errno.EAGAIN:
                    raise
                # Не смогли взять лок в течение заданного времени
                elif (self._timeout is not None
                      and time() > start_time + self._timeout):
                    raise

            # Ждём некоторое время и пробуем взять лок снова
            sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)
        self.fd = None


class Logger:
    def __init__(self, logs_path):
        self.log_format = "%(asctime)s [%(levelname)5s] %(message)s"
        self.date_format = "%d.%m.%Y %H:%M:%S"
        self.logs_path = logs_path

    def get_logger(self, name):
        __formatter = logging.Formatter(fmt=self.log_format,
                                        datefmt=self.date_format)

        logger = logging.getLogger(name)
        handler = logging.FileHandler(os.path.join(self.logs_path,
                                                   f"{name}.log"))
        handler.setFormatter(__formatter)
        logger.setLevel('DEBUG')
        logger.addHandler(handler)
        return logger

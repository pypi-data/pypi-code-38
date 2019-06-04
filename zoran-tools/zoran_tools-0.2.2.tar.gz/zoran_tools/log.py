import logging
import time
import json


class Logger(object):
    levels = {
        None: -1,
        'DEBUG': 100,
        'INFO': 200,
        'WARN': 300,
        'ERROR': 400,
    }
    time_format = '%y-%m-%d %H:%M:%S'

    def __init__(self, obj='root', level='DEBUG'):
        self._level = level
        self._levels = Logger.levels
        self._message = ''
        self.role = obj.__repr__()
        self._message_bak = obj.__str__()
        self._time_format = Logger.time_format

        self._print_time: str = ''
        self._print = '{level}: {role} {time}\n\t{message}'

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        if level in self._levels:
            self._level = level
        else:
            raise ValueError

    @property
    def time_fmt(self):
        return self._time_format

    @time_fmt.setter
    def time_fmt(self, fmt):
        self._time_format = fmt

    def time(self):
        self._print_time = time.strftime(self._time_format)
        return self

    def json(self, dictionary):
        self._message += '\n' + json.dumps(dictionary, indent=2, ensure_ascii=False)
        return self

    def message(self, message):
        self._message += message.__str__()
        return self

    def print_message(self, message, level):
        if Logger.levels.get(level) >= Logger.levels.get(self._level):
            self.message(message)
            print(self._print.format(level=level, role=self.role, time=self._print_time, message=self._message))
            self._message = level + ': ' + self._message + ' '
        self._print_time = ''
        self._message = ''
        return self

    def info(self, message):
        return self.print_message(message, 'INFO')

    def debug(self, message):
        return self.print_message(message, 'DEBUG')

    def warn(self, message):
        return self.print_message(message, 'WARN')

    def error(self, message):
        return self.print_message(message, 'ERROR')

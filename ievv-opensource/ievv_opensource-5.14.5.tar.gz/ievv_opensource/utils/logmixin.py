from __future__ import print_function

import sys
import textwrap
import threading

from ievv_opensource.utils import ievv_colorize
from ievv_opensource.utils.desktopnotifications import desktopnotificationapi


class Logger(object):
    """
    Logger class used by :class:`.LogMixin`.
    """
    loggers = {}
    # messagelock = threading.Lock()
    DEBUG = 5
    STDOUT = 4
    INFO = 3
    WARNING = 2
    ERROR = 1

    @classmethod
    def get_instance(cls, name, level=None, command_error_message=None):
        """
        Get an instance of the logger by the given name.

        Parameters:
            name: The name of the logger.
        """
        if name not in cls.loggers:
            cls.loggers[name] = cls(name=name)
        cls.loggers[name].set_level(level=level)
        cls.loggers[name].set_command_error_message(command_error_message=command_error_message)
        return cls.loggers[name]

    def __init__(self, name, level=None):
        """
        Parameters:
            name: The name of the logger.
        """
        self.name = name
        self.level = level or self.DEBUG
        self._has_messagelock = False
        self._messagelocktimer = None

    def set_level(self, level):
        self.level = level or self.DEBUG

    def set_command_error_message(self, command_error_message):
        self.command_error_message = command_error_message

    def _acquire_messagelock(self):
        # if not self._has_messagelock:
        #     self.__class__.messagelock.acquire()
        #     self._has_messagelock = True
        pass

    def _release_messagelock(self):
        # self._messagelocktimer = None
        # try:
        #     self.__class__.messagelock.release()
        # except RuntimeError:
        #     pass
        # self._has_messagelock = False
        pass

    def _slowrelease_messagelock(self):
        if not self._messagelocktimer:
            self._messagelocktimer = threading.Timer(0.3, self._release_messagelock)
            self._messagelocktimer.start()

    def _queue_message(self, message=''):
        # self._messagequeue.append(message)
        self._acquire_messagelock()
        # self._flush_message_queue()
        print(message)
        sys.stdout.flush()
        self._slowrelease_messagelock()

    # def _flush_message_queue(self):
    #     for message in self._messagequeue:
    #         print(message)

    def stdout(self, line):
        """
        Use this to redirecting sys.stdout when running shell commands.
        """
        if self.level >= self.STDOUT:
            self._queue_message(line.rstrip())

    def stderr(self, line):
        """
        Use this to redirecting sys.stderr when running shell commands.
        """
        if self.level >= self.ERROR:
            self._queue_message(line.rstrip())

    def __colorize(self, message, **kwargs):
        return ievv_colorize.colorize(message, **kwargs)

    def __colorprint(self, message, **kwargs):
        self._queue_message(self.__colorize(message, **kwargs))

    def infobox(self, message):
        if self.level >= self.INFO:
            message = textwrap.fill(message, width=70)
            message = '\n{line}\n{message}\n{line}\n'.format(
                message=message,
                line='*' * 70
            )
            self.__colorprint(message, color=ievv_colorize.COLOR_BLUE)

    def info(self, message):
        """
        Log an info message.
        """
        if self.level >= self.INFO:
            self.__colorprint(message, color=ievv_colorize.COLOR_BLUE)

    def success(self, message):
        """
        Log a success message.
        """
        if self.level >= self.INFO:
            self.__colorprint(message, color=ievv_colorize.COLOR_GREEN)

    def warning(self, message):
        """
        Log a warning message.
        """
        if self.level >= self.WARNING:
            self.__colorprint(message, color=ievv_colorize.COLOR_YELLOW)

    def error(self, message):
        """
        Log a warning message.
        """
        if self.level >= self.ERROR:
            self.__colorprint(message, color=ievv_colorize.COLOR_RED)

    def debug(self, message):
        """
        Log a debug message.
        """
        if self.level >= self.DEBUG:
            self.__colorprint(message, color=ievv_colorize.COLOR_GREY)

    def command_start(self, message):
        """
        Log the start of a command. This should be used in the beginning
        of each :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.run`.
        """
        if self.level >= self.DEBUG:
            self._queue_message()
        if self.level >= self.INFO:
            self.__colorprint(message, color=ievv_colorize.COLOR_BLUE, bold=True)

    def __command_end(self, message, **kwargs):
        self.__colorprint(message, **kwargs)
        if self.level >= self.DEBUG:
            self._queue_message()

    def command_error(self, message):
        """
        Log failing end of a command. This should be used in
        :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.run`
        when the task fails.
        """
        self.__command_end(message, color=ievv_colorize.COLOR_RED, bold=True)
        if self.level < self.DEBUG and self.command_error_message:
            self.__colorprint(self.command_error_message,
                              color=ievv_colorize.COLOR_GREY, bold=True)
        desktopnotificationapi.show_message(
            title='ERROR - {}'.format(self.name),
            message=message)

    def command_success(self, message):
        """
        Log successful end of a command. This should be used in
        :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.run`
        when the task succeeds.
        """
        if self.level >= self.INFO:
            self.__command_end(message, color=ievv_colorize.COLOR_GREEN, bold=True)
            desktopnotificationapi.show_message(
                title='SUCCESS - {}'.format(self.name),
                message=message)


class LogMixin(object):
    """
    Mixin class that takes care of logging for all the classes
    in the ``ievvbuildstatic`` package.

    Subclasses must override :meth:`.~LogMixin.get_logger_name`,
    and use :meth:`.~LogMixin.get_logger`.
    """
    def get_logger_name(self):
        """
        Get the name of the logger.
        """
        raise NotImplementedError()

    def get_loglevel(self):
        return Logger.DEBUG

    def get_command_error_message(self):
        return None

    def get_logger(self):
        """
        Get an instance of :meth:`.Logger` with :meth:`.get_logger_name`
        as the logger name.
        """
        return Logger.get_instance(name=self.get_logger_name(), level=self.get_loglevel(),
                                   command_error_message=self.get_command_error_message())


if __name__ == '__main__':
    import time
    import random

    class DemoThread(threading.Thread):
        def __init__(self, *args, **kwargs):
            self.text = kwargs.pop('text')
            self.logger = Logger(name=self.text)
            super(DemoThread, self).__init__(*args, **kwargs)

        def run(self):
            for x in range(30):
                self.logger.info(self.text)
            time.sleep(random.randint(1, 3))

            for x in range(10):
                self.logger.debug(self.text)
            time.sleep(random.randint(1, 3))

            for x in range(10):
                self.logger.warning(self.text)

    threads = [
        DemoThread(text='Hello world'),
        DemoThread(text='A test'),
        DemoThread(text='Yo!'),
    ]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

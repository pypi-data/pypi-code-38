import logging
import sys
from functools import wraps

from pydub import AudioSegment
from pydub.playback import play

"""func"""


def logged(level, name=None, message=None):
    """
    Add logging to a function. If name and message arent specified, they defau
    :param level: logging level, default value is INFO
    :param name: logger name, default value is function's module
    :param message: log message, default value is function's name
    :return:
    """

    def decorate(func):
        log_name = name if name else func.__module__
        log = logging.getLogger(log_name)
        log_msg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            log.log(level, log_msg)
            return func(*args, **kwargs)

        return wrapper

    return decorate


def play_wav(wav_file):
    song = AudioSegment.from_wav(wav_file)
    play(song)


"""class"""


class Program:
    @staticmethod
    def debugging():
        gettrace = getattr(sys, 'gettrace', None)
        return (gettrace is not None) and gettrace()

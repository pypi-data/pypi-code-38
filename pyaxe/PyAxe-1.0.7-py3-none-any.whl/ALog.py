import os
import sys
import time
import ctypes

__all__ = ['LEVEL_FATAL', 'LEVEL_ERROR', 'LEVEL_WARNING', 'LEVEL_INFO', 'LEVEL_DEBUG', 'LEVEL__ALL',
           'fatal', 'error', 'warn', 'info', 'debug',
           'critical', 'warning',
           'enable', 'setLevel', 'enableFileSink', 'enableConsoleSink', 'enableMessageFormattedLeading', 'EnableMessageFormattedLeading'
           'setDateFormat', 'setTimestampFormat'
           'getLogFileObjectForAppend',
           'BLACK', 'BRIGHT_BLACK', 'GRAY',
           'BLUE', 'BRIGHT_BLUE',
           'GREEN', 'BRIGHT_GREEN',
           'AQUA', 'BRIGHT_AQUA',
           'RED', 'BRIGHT_RED',
           'PURPLE', 'BRIGHT_PURPLE',
           'YELLOW', 'BRIGHT_YELLOW',
           'WHITE', 'BRIGHT_WHITE']

LEVEL_FATAL = 50
LEVEL_ERROR = 40
LEVEL_WARN = 30
LEVEL_INFO = 20
LEVEL_DEBUG = 10
LEVEL__ALL = LEVEL_FATAL

_levelFormatTable = {
    LEVEL_FATAL: 'FATAL',
    LEVEL_ERROR: 'ERROR',
    LEVEL_WARN: 'WARN ',
    LEVEL_INFO: 'INFO ',
    LEVEL_DEBUG: 'DEBUG',
}


_level = LEVEL_INFO
_enable = True
_enableFileSink = True
_enableConsoleSink = True
_enableMessageFormattedLeading = True
_logDir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'Log')
_binName = os.path.basename(sys.argv[0])
_hasWriteOpenLog = False
_dateFormat = '%Y_%m_%d'
_timestampFormat = '%H:%M:%S'

def _formatDate():
    return time.strftime(_dateFormat, time.localtime())

def _formatTimestamp():
    return time.strftime(_timestampFormat, time.localtime())

def _formatLevel(level):
    return _levelFormatTable[level]

def _formatMessage(level, msg, args):
    if _enableMessageFormattedLeading:
        return '[' + _formatTimestamp() + ' ' + _formatLevel(level) + '] ' + (msg % args)
    else:
        return (msg % args)

def _ensureLogDir():
    if not os.path.exists(_logDir):
        os.mkdir(_logDir)

def _formatLogFilePath():
    return os.path.join(_logDir, _binName + '-' + _formatDate() + '.log')

def _getLogFileObjectForAppend():
    fileExist = os.path.exists(_formatLogFilePath())
    _ensureLogDir()
    fp = open(_formatLogFilePath(), 'a')
    
    global _hasWriteOpenLog
    if not _hasWriteOpenLog:
        openHintStr = 'Log file was opened at: %s' % _formatTimestamp()

        s = ('\n' if fileExist else '')
        s += '+' + '-'*(len(openHintStr)+2) + '+\n'
        s += '| ' + openHintStr + ' |\n'
        s += '+' + '-'*(len(openHintStr)+2) + '+\n'

        fp.write(s)
        _hasWriteOpenLog = True

    return fp

getLogFileObjectForAppend = _getLogFileObjectForAppend

def _log(level, msg, args):
    rawMsg = msg.msg if isinstance(msg, _ColorMsgPair) else msg
    color = msg.color if isinstance(msg, _ColorMsgPair) else None
    if color is None:
        color = _levelColorTable[level]
        if color is not None:
            color = color.color

    formatStr = _formatMessage(level, rawMsg, args)
    
    if _enableFileSink:
        with _getLogFileObjectForAppend() as fp:
            fp.write(formatStr)
            fp.write('\n')

    if _enableConsoleSink:
        if color is None:
            print(formatStr)
            sys.stdout.flush()
        else:
            _colorPrinterClass.printWithColor(formatStr, color)


def enable(value=True):
    global _enable
    _enable = value

def setLevel(level):
    global _level
    _level = level

def enableFileSink(enable=True):
    global _enableFileSink
    _enableFileSink = enable

def enableConsoleSink(enable=True):
    global _enableConsoleSink
    _enableConsoleSink = enable

def enableMessageFormattedLeading(enable=True):
    global _enableMessageFormattedLeading
    _enableMessageFormattedLeading = enable

class EnableMessageFormattedLeading:
    def __init__(self, enable):
        self.old_enable = _enableMessageFormattedLeading
        self.enable = enable

    def __enter__(self):
        enableMessageFormattedLeading(self.enable)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        enableMessageFormattedLeading(self.old_enable)

def setDateFormat(fmt):
    global _dateFormat
    _dateFormat = fmt

def setTimestampFormat(fmt):
    global _timestampFormat
    _timestampFormat = fmt


def fatal(msg, *args):
    lv = LEVEL_FATAL
    if _enable and lv >= _level:
        _log(lv, msg, args)

def error(msg, *args):
    lv = LEVEL_ERROR
    if _enable and lv >= _level:
        _log(lv, msg, args)

def warn(msg, *args):
    lv = LEVEL_WARN
    if _enable and lv >= _level:
        _log(lv, msg, args)

def info(msg, *args):
    lv = LEVEL_INFO
    if _enable and lv >= _level:
        _log(lv, msg, args)

def debug(msg, *args):
    lv = LEVEL_DEBUG
    if _enable and lv >= _level:
        _log(lv, msg, args)

# keep compatible with system logging module
critical = fatal
warning = warn

class _WindowsColorPrinter:
    BLACK = 0X00
    BRIGHT_BLACK = 0X08

    BLUE = 0X01
    BRIGHT_BLUE = 0X09

    GREEN = 0X02
    BRIGHT_GREEN = 0X0A

    AQUA = 0X03
    BRIGHT_AQUA = 0X0B

    RED = 0X04
    BRIGHT_RED = 0X0C

    PURPLE = 0X05
    BRIGHT_PURPLE = 0X0D

    YELLOW = 0X06
    BRIGHT_YELLOW = 0X0E

    WHITE = 0X07
    BRIGHT_WHITE = 0X0F

    DEFAULT_FORE_COLOR = WHITE
    DEFAULT_BACK_COLOR = BLACK

    if os.name == 'nt':
        _handle = ctypes.windll.kernel32.GetStdHandle(-12)  # STD_ERROR_HANDLE

    @classmethod
    def printWithColor(cls, s, color):
        ctypes.windll.kernel32.SetConsoleTextAttribute(cls._handle, color)
        print(s)
        sys.stdout.flush()
        ctypes.windll.kernel32.SetConsoleTextAttribute(cls._handle, cls.WHITE)


class _LinuxColorPrinter:
    BLACK = '30'
    BRIGHT_BLACK = '1;30'

    BLUE = '34'
    BRIGHT_BLUE = '1;34'

    GREEN = '32'
    BRIGHT_GREEN = '1;32'

    AQUA = '36'
    BRIGHT_AQUA = '1;36'

    RED = '31'
    BRIGHT_RED = '1;31'

    PURPLE = '35'
    BRIGHT_PURPLE = '1;35'

    YELLOW = '33'
    BRIGHT_YELLOW = '1;33'

    WHITE = '37'
    BRIGHT_WHITE = '1;37'

    @classmethod
    def printWithColor(cls, s, color):
        print('\033[%sm%s' % (color, s))
        sys.stdout.write('\033[0m')
        sys.stdout.flush()


class _ColorMsgPair():
    def __init__(self, color, msg):
        self.color = color
        self.msg = msg

class _Color:
    def __init__(self, color):
        self.color = color

    def __add__(self, msg):
        return _ColorMsgPair(self.color, msg)

if os.name == 'nt':
    _colorPrinterClass = _WindowsColorPrinter
else:
    _colorPrinterClass = _LinuxColorPrinter

BLACK = _Color(_colorPrinterClass.BLACK)
BRIGHT_BLACK = _Color(_colorPrinterClass.BRIGHT_BLACK)
GRAY = BRIGHT_BLACK

BLUE = _Color(_colorPrinterClass.BLUE)
BRIGHT_BLUE = _Color(_colorPrinterClass.BRIGHT_BLUE)

GREEN = _Color(_colorPrinterClass.GREEN)
BRIGHT_GREEN = _Color(_colorPrinterClass.BRIGHT_GREEN)

AQUA = _Color(_colorPrinterClass.AQUA)
BRIGHT_AQUA = _Color(_colorPrinterClass.BRIGHT_AQUA)

RED = _Color(_colorPrinterClass.RED)
BRIGHT_RED = _Color(_colorPrinterClass.BRIGHT_RED)

PURPLE = _Color(_colorPrinterClass.PURPLE)
BRIGHT_PURPLE = _Color(_colorPrinterClass.BRIGHT_PURPLE)

YELLOW = _Color(_colorPrinterClass.YELLOW)
BRIGHT_YELLOW = _Color(_colorPrinterClass.BRIGHT_YELLOW)

WHITE = _Color(_colorPrinterClass.WHITE)
BRIGHT_WHITE = _Color(_colorPrinterClass.BRIGHT_WHITE)

_levelColorTable = {
    LEVEL_FATAL:    BRIGHT_RED,
    LEVEL_ERROR:    BRIGHT_RED,
    LEVEL_WARN:  BRIGHT_YELLOW,
    LEVEL_INFO:     None,
    LEVEL_DEBUG:    None,
}

def test():
    info('This is a info message, %s', '这是一条Info消息')
    warn('This is a warn message, %s', '这是一条Warning消息')
    error('This is a error message, %s', '这是一条Error消息')
    info('设置等级为warning')
    setLevel(LEVEL_WARN)
    info('This is a info message, %s', '这是一条Info消息')
    warn('This is a warn message, %s', '这是一条Warning消息')
    error('This is a error message, %s', '这是一条Error消息')
    setLevel(LEVEL_INFO)
    info(RED + 'This is a info message, %s', '这是一条Info消息')

if __name__ == '__main__':
    test()
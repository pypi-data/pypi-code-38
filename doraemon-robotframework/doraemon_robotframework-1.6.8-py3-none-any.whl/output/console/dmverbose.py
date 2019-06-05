import sys
import re

from robot.errors import DataError
from robot.utils import get_console_length, isatty, pad_console_length

from .highlighting import HighlightingStream


class VerboseOutput(object):

    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self._writer = VerboseWriter(88, colors, markers, stdout, stderr)
        self._started = False
        self._started_keywords = 0
        self._running_test = False
        self._str_error = []
        self._multiple_suites = False

    def start_suite(self, suite):
        if not self._started:
            if len(suite.result.name.split('&')) == 1:
                self._writer.info(suite.result.name, suite.doc, start_suite=True, suite_or_test=suite, type=0)
            else:
                self._multiple_suites = True
            self._started = True
            return
        self._writer.info(suite.result.name, suite.doc, start_suite=True, suite_or_test=suite, type=0)

    def end_suite(self, suite):
        self._writer.info(suite.result.name, suite.doc, suite_or_test=suite, type=1)
        self._writer.status(suite.status)
        if self._multiple_suites is True:
            if len(suite.result.name.split('&')) > 1:
                self._writer.result(self._str_error)
        else:
            self._writer.result(self._str_error)
        self._writer.message(suite.full_message)

    def start_test(self, test):
        self._writer.test_separator()
        self._writer.info(test.name, test.doc, suite_or_test=test, type=2)
        self._running_test = True

    def end_test(self, test):
        self._writer.status(test.status, clear=True)
        # self._writer.message(test.message)
        if test.message != '':
            self._str_error.append('\033[31m%d. \033[33m%s\033[0m → \033[31mFAIL : %s\033[0m' % (len(self._str_error)+1, test.name, test.message))
        self._running_test = False

    def start_keyword(self, kw):
        self._started_keywords += 1

    def end_keyword(self, kw):
        self._started_keywords -= 1
        if self._running_test and not self._started_keywords:
            self._writer.keyword_marker(kw.status)

    def message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            # self._writer.error(msg.message, msg.level, clear=self._running_test)
            self._str_error.append('\033[31m%d. \033[0m [\033[31m %s \033[0m] %s' % (len(self._str_error)+1, msg.level, msg.message))

    def output_file(self, name, path):
        self._writer.output(name, path)


class VerboseWriter(object):
    _status_length = len('| PASS |')

    def get_length(self, word):
        length = len(word)
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                length = length + 1
        result = re.findall('\\033\[[0|3][0-9]*m', word)
        for item in result:
            # 长度－1，为真实识别的颜色长度
            color_len = len(item) - 1
            length = length - color_len
            
        return length

    def get_beautiful_log(self, msg, color=34, symbol='='):
        msg_len = self.get_length(msg)
        len_symbol = int((self._width - msg_len) / 2)
        
        str_symbol_left = ''
        str_symbol_right = ''
        if len_symbol > 0:
            for item in range(len_symbol):
                str_symbol_left = symbol + str_symbol_left
            if (self._width - msg_len) % 2 == 1:
                str_symbol_right = str_symbol_left + symbol
            else:
                str_symbol_right = str_symbol_left
        else:
            str_symbol_left = '%s%s' % (symbol, symbol)
            str_symbol_right = str_symbol_left

        return '\033[%sm%s %s %s\033[0m' % (str(color), str_symbol_left, msg, str_symbol_right)

    def __init__(self, width=8, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self._width = width
        self._stdout = HighlightingStream(stdout or sys.__stdout__, colors)
        self._stderr = HighlightingStream(stderr or sys.__stderr__, colors)
        self._keyword_marker = KeywordMarker(self._stdout, markers)
        self._last_info = None
        self._suite_starting = False

    # type: 0 start_suite, 1 end_suite, 2 start_test
    def info(self, name, doc, start_suite=False, suite_or_test=None, type=0):
        width, separator = self._get_info_width_and_separator(start_suite)
        self._last_info = self._get_info(name, doc, width, suite_or_test, type) + separator
        self._write_info()
        self._keyword_marker.reset_count()

    def result(self, result):
        if len(result) < 1:
            return
        self._stdout.write('\033[31m✘ 本次执行发生以下%d个错误: ✘\033[0m\n' % len(result))
        for item in result:
            self._stdout.write('%s\n\n' % (item))

    def _write_info(self):
        self._stdout.write(self._last_info)

    def _get_info_width_and_separator(self, start_suite):
        if start_suite:
            return self._width, '\n'
        return self._width - self._status_length - 1, ' '

    def _get_info(self, name, doc, width, suite_or_test, type=0):
        if type == 0:
            self._suite_starting = True
            return self.get_beautiful_log(name + '.robot')
        elif type == 1:
            self._suite_starting = False
            if len(name.split('&')) > 1:
                return '\n' + self.get_beautiful_log('本次执行包含%d个robot文件' % len(suite_or_test.name.split('&')), color=0, symbol='*')
            return self.get_beautiful_log(name + '.robot')
            # color = 32 if suite_or_test.status == 'PASS' else 31
            # return self.get_beautiful_log(name + '.robot', color)
        else:
            self._suite_starting = False
            return '\033[33m%s\033[0m' % name
            # if get_console_length(name) > width:
            #     return pad_console_length(name, width)
            # info = name if not doc else '%s' % (name)
            # return pad_console_length(info, width)

    def suite_separator(self):
        self._fill('=')

    def test_separator(self):
        if self._suite_starting is False:
            self._fill('-')

    def _fill(self, char):
        self._stdout.write('%s\n' % (char * (self._width + 2)))

    def status(self, status, clear=False):
        if self._should_clear_markers(clear):
            self._clear_status()
        self._stdout.write('| ', flush=False)
        self._stdout.highlight(status, flush=False)
        if clear is False:
            self._stdout.write(' |\n\n')
        else:
            self._stdout.write(' |\n')

    def _should_clear_markers(self, clear):
        return clear and self._keyword_marker.marking_enabled

    def _clear_status(self):
        self._clear_info()
        self._write_info()

    def _clear_info(self):
        self._stdout.write('\r%s\r' % (' ' * self._width))
        self._keyword_marker.reset_count()

    def message(self, message):
        if message:
            self._stdout.write(message.strip() + '\n\n')

    def keyword_marker(self, status):
        if self._keyword_marker.marker_count == self._status_length:
            self._clear_status()
            self._keyword_marker.reset_count()
        self._keyword_marker.mark(status)

    def error(self, message, level, clear=False):
        if self._should_clear_markers(clear):
            self._clear_info()
        self._stderr.error(message, level)
        if self._should_clear_markers(clear):
            self._write_info()

    def output(self, name, path):
        self._stdout.write('%-8s %s\n' % (name+':', path))


class KeywordMarker(object):

    def __init__(self, highlighter, markers):
        self._highlighter = highlighter
        self.marking_enabled = self._marking_enabled(markers, highlighter)
        self.marker_count = 0

    def _marking_enabled(self, markers, highlighter):
        options = {'AUTO': isatty(highlighter.stream),
                   'ON': True,
                   'OFF': False}
        try:
            return options[markers.upper()]
        except KeyError:
            raise DataError("Invalid console marker value '%s'. Available "
                            "'AUTO', 'ON' and 'OFF'." % markers)

    def mark(self, status):
        if self.marking_enabled:
            marker, status = ('.', 'PASS') if status != 'FAIL' else ('F', 'FAIL')
            self._highlighter.highlight(marker, status)
            self.marker_count += 1

    def reset_count(self):
        self.marker_count = 0

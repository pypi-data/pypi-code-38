#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import re
import sys
import time
import json
import threading
import contextlib

import appier

from . import util

COLOR_RESET = "\033[0m"
COLOR_WHITE = "\033[1;37m"
COLOR_BLACK = "\033[0;30m"
COLOR_BLUE = "\033[0;34m"
COLOR_LIGHT_BLUE = "\033[1;34m"
COLOR_GREEN = "\033[0;32m"
COLOR_LIGHT_GREEN = "\033[1;32m"
COLOR_CYAN = "\033[0;36m"
COLOR_LIGHT_CYAN = "\033[1;36m"
COLOR_RED = "\033[0;31m"
COLOR_LIGHT_RED = "\033[1;31m"
COLOR_PURPLE = "\033[0;35m"
COLOR_LIGHT_PURPLE = "\033[1;35m"
COLOR_BROWN = "\033[0;33m"
COLOR_YELLOW = "\033[1;33m"
COLOR_GRAY = "\033[0;30m"
COLOR_LIGHT_GRAY = "\033[0;37m"

CLEAR_LINE = "\033[K"

COLORS = dict(
    white = COLOR_WHITE,
    black = COLOR_BLACK,
    blue = COLOR_BLUE,
    light_blue = COLOR_LIGHT_BLUE,
    green = COLOR_GREEN,
    light_green = COLOR_LIGHT_GREEN,
    cyan = COLOR_CYAN,
    light_cyan = COLOR_LIGHT_CYAN,
    red = COLOR_RED,
    light_red = COLOR_LIGHT_RED,
    purple = COLOR_PURPLE,
    light_purple = COLOR_LIGHT_PURPLE,
    brown = COLOR_BROWN,
    yellow = COLOR_YELLOW,
    gray = COLOR_GRAY,
    light_gray = COLOR_LIGHT_GRAY
)

class LoaderThread(threading.Thread):
    """
    Thread class to be used to display the loader into
    the output stream in an async fashion.
    """

    _spinners = None
    """ The underlying spinners map that will probably be
    loaded from a secondary structure (eg: JSON file) to be
    used as the metadata source of information """

    def __init__(
        self,
        spinner = "point",
        interval = None,
        color = None,
        template = "{{spinner}}",
        stream = sys.stdout,
        single = False,
        flush_s = True,
        max_print = None,
        end_newline = None,
        eol = None,
        *args, **kwargs
    ):
        threading.Thread.__init__(self, *args, **kwargs)
        self.spinner = spinner
        self.interval = interval
        self.color = color
        self.template = template
        self.stream = stream
        self.single = single
        self.flush_s = flush_s
        self.max_print = max_print
        self.end_newline = not self.is_tty if end_newline == None else end_newline
        self.eol = "" if self.is_tty else "\n" if eol == None else eol
        self._condition = threading.Condition()

    @classmethod
    def spinners(cls):
        # in case the spinners dictionary is already loaded returns
        # it immediately to the caller method (no reload)
        if cls._spinners: return cls._spinners

        # builds the path to the JSON based spinners file and the
        # loads into memory to be used in the decoding
        spinners_path = os.path.join(
            os.path.dirname(__file__),
            "res", "spinners.json"
        )
        with open(spinners_path, "rb") as file:
            data = file.read()

        # decodes the binary contents as an UTF-8 unicode string
        # ands feeds its value into the JSON loader
        data = data.decode("utf-8")
        cls._spinners = json.loads(data)

        # returns the now "cached" spinners value to the caller
        # method (further calls avoid the loading)
        return cls._spinners

    def run(self):
        threading.Thread.run(self)

        # retrieves the reference to the class associated with
        # the current instance to be used at the class level
        cls = self.__class__

        # verifies a series of pre-conditions that must be met for
        # the context execution to work properly, if any of them is
        # not met the control flow is returned immediately
        if not self.stream: return

        # sets the running flag for the current instance meaning
        # that the current thread is running
        self.running = True

        # tries to retrieve the color escape sequence from the value
        # of the provided color (provides easy to use interface)
        if self.is_color: color = COLORS.get(self.color, self.color)
        else: color = None

        # retrieves the current spinner map and then uses it to
        # calculate the interval (in seconds) for the spinner sequence
        # and retrieves the list of frame characters for the spinner
        spinner = cls.spinners()[self.spinner]
        interval_s = (spinner["interval"]) / 1000.0
        frames = spinner["frames"]

        if self.has_spinner: interval = min(self.interval_g, interval_s)
        else: interval = self.interval_g

        # retrieves the instance level max print value to be used locally
        # in the control of the print loop
        max_print = self.max_print

        # in case the single print mode is enable and the current output
        # is not a tty one (simple text loading) the no multiple loops
        # should occur, effectively enforcing a single line print, then
        # the value of the max print is set to one
        if self.single and not self.is_tty: max_print = max_print or 1

        initial = time.time()
        next = initial
        is_first = True
        previous_size = 0
        print_count = 0

        # iterates continuously to print the multiple label lines
        # while there's progress in the background operation
        while True:
            # in case the running flag is not longer set breaks
            # the current loop (nothing remaining to be done)
            if not self.running: break

            # in case the maximum number of prints has been reached
            # then the waiting (for condition) must be performed
            if not max_print == None and print_count == max_print:
                # waits for the condition for the associated amount of
                # time and then releases the condition, this will effectively
                # allow external threads to awake this one
                self._condition.acquire()
                self._condition.wait(interval)
                self._condition.release()

                # continues the loop immediately to be able to execute
                # the next iteration
                continue

            # determines the proper character that is going to be used as
            # a prefix for a proper line clearing operation, notice that
            # in case no color support exists the current line is populated
            # with space characters (considered neutral)
            clear_line = "\r" + CLEAR_LINE if self.is_ansi else "\r" + " " * previous_size

            # retrieves the current time and uses it to calculate
            # the current frame index of the spinner
            current = time.time()
            index = int((current - initial) / interval_s)
            value = index % len(frames)

            # determines if this is the first print operation or not
            # and taking that into account sets the proper beginning of
            # line (BOL) and end of line (EOL) characters
            if is_first:
                is_first = False
                bol, eol = ("" if self.is_tty else "", self.eol)
            else:
                bol, eol = (clear_line + "\r" if self.is_tty else "", self.eol)

            # retrieves the value of the current frame of the spinner
            # and in case there's a color selected updates such replacer
            # embedding it into a proper color mask
            replacer = frames[value]
            if color: replacer = color + replacer + COLOR_RESET

            # converts the template into a string so that it can be used
            # safely in the replacement operations
            template = appier.legacy.str(self.template)

            # in case the spinner is active runs a simple string replacement
            # strategy over the template
            if self.has_spinner:
                label = re.sub("\{\{spinner\}\}*", replacer, template)

            # otherwise runs the replace but also removes the adjacent extra
            # spaces to avoid unwanted bad looking
            else:
                label = re.sub("\{\{spinner\}\}\s*", "", template)

            # saves the size of the current label (output text) so that
            # it can be used to calculate the size of the spaces string
            # that would clear its line contents (if required)
            previous_size = len(label)

            # writes the current label (text) to the output stream
            # and runs the flush operation (required to ensure that
            # the data contents are properly set in the stream)
            if label:
                self.stream.write(bol + label + eol)
                if self.flush_s: self.stream.flush()
                print_count += 1

            # waits for the condition for the associated amount of
            # time and then releases the condition, this will effectively
            # allow external threads to awake this one
            self._condition.acquire()
            self._condition.wait(interval)
            self._condition.release()

        # determines the proper character that is going to be used as
        # a prefix for a proper line clearing operation, notice that
        # in case no color support exists the current line is populated
        # with space characters (considered neutral)
        clear_line = "\r" + CLEAR_LINE if self.is_ansi else "\r" + " " * previous_size

        # verifies if the current context should end with a new line
        # or if instead the same line is going to be re-used and write
        # the appropriate string sequence to the output stream
        if self.end_newline: self.stream.write(self.eol)
        else: self.stream.write(clear_line + "\r")
        if self.flush_s: self.stream.flush()

    def stop(self):
        self._condition.acquire()
        self.running = False
        self._condition.notify()
        self._condition.release()

    def set_template(self, value):
        self.template = value

    def flush(self):
        self._condition.acquire()
        self._condition.notify()
        self._condition.release()

    @property
    def interval_g(self):
        if self.interval: return self.interval
        if self.is_tty: return 0.1
        return 0.25

    @property
    def has_spinner(self):
        if not self.is_tty: return False
        if os.name in ("nt",) and not appier.legacy.PYTHON_3: return False
        return True

    @property
    def is_tty(self):
        return util.is_tty(self.stream)

    @property
    def is_ansi(self):
        return util.is_ansi()

    @property
    def is_color(self):
        return util.is_color()

@contextlib.contextmanager
def ctx_loader(*args, **kwargs):
    thread = LoaderThread(*args, **kwargs)
    thread.start()
    try:
        yield thread
    finally:
        thread.stop()
        thread.join()

def colored(value, color = COLOR_RED):
    if not util.is_color(): return value
    color = COLORS.get(color, color)
    return color + value + COLOR_RESET

if __name__ == "__main__":
    spinners = appier.conf("SPINNERS", None, cast = list)
    timeout = appier.conf("TIMEOUT", 3.0, cast = float)
    color = appier.conf("COLOR", "cyan")
    if not spinners:
        spinners = LoaderThread.spinners()
        spinners = appier.legacy.keys(spinners)
        spinners = sorted(spinners)
    for spinner in spinners:
        with ctx_loader(
            spinner = spinner,
            color = color,
            template = "Spinner '%s' {{spinner}}" % spinner
        ) as loader:
            time.sleep(timeout)
else:
    __path__ = []

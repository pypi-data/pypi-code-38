#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import functools
import io
import os
import random
import sys
import threading
import time
from contextlib import contextmanager

try:
    from shutil import get_terminal_size
except ImportError:  # pragma: no cover
    from backports.shutil_get_terminal_size import get_terminal_size  # pragma: no cover


is_py_3 = sys.version_info.major == 3


def _console_dimensions():

    try:
        columns, rows = get_terminal_size((80, 25))
    except OSError:
        return 80, 25
    return columns, rows  # pragma: no cover


def _format_time(t):
    if t is None:
        return "??:??:??.?"
    minutes, seconds = divmod(t, 60)
    hours, minutes = divmod(minutes, 60)
    return "{:02.0f}:{:02.0f}:{:04.1f}".format(hours, minutes, seconds)


def _format_time_part(t_passed, t_left):
    time_str_passed = "passed: " + _format_time(t_passed)
    time_str_left = "left: " + _format_time(t_left)
    return time_str_passed + " " + time_str_left + " - "


class _Formatter(object):
    def __init__(self, bar_size, n_steps, started):
        self.bar_size = bar_size
        self.n_steps = n_steps
        self.started = started
        self.time_left = 0

    def format_progress_line(self, symbol, i, tl=None):
        n = self.bar_size * i // self.n_steps
        time_passed = time.time() - self.started

        progress_symbol = "∣"

        if tl is None:
            time_left_estimate = time_passed / (i + 1) * (self.n_steps - i - 1)

            # exponential smoothing, avoid "flattering" for fast sampling:
            self.time_left = 0.8 * self.time_left + 0.2 * time_left_estimate
        else:
            self.time_left = tl
        time_str = _format_time_part(time_passed, self.time_left)
        return "\r{} {}[{}{}]".format(
            symbol, time_str, progress_symbol * n, " " * (self.bar_size - n)
        )


def _write(what):
    # write to systems stdout directly as sys.stdout might be redirected due to
    # capturing
    if is_py_3:
        os.write(1, what.encode("utf-8"))
    else:
        os.write(1, what)  # pragma: no cover


class _UpdateThread(threading.Thread):
    def __init__(self, symbols, formatter, done_symbol, dt=0.07):
        threading.Thread.__init__(self)
        self.symbols = symbols
        self.formatter = formatter
        self.done_symbol = done_symbol
        self.dt = dt

        self.progress_counter = 0

    def run(self):
        self.iter_running = True
        symbol_idx = 0
        try:
            while self.iter_running:
                time.sleep(self.dt)
                symbol = self.symbols[symbol_idx]
                symbol_idx = (symbol_idx + 1) % len(self.symbols)
                progress_line = self.formatter.format_progress_line(
                    symbol, self.progress_counter
                )
                _write(progress_line)
            progress_line = self.formatter.format_progress_line(
                self.done_symbol, self.progress_counter, 0
            )
            _write(progress_line)
            _write("\n")
        except KeyboardInterrupt:
            pass


def with_progressbar(n_steps, iterable, width=None, delta_t=0.05):

    if width is None:
        width, __ = _console_dimensions()

    symbols = random.choice(
        [
            "◰ ◳ ◲ ◱",
            "▁▂▃▄▅▆▇███▇▆▅▄▃▁▁",
            "▏▎▍▌▋▊███▊▋▌▍▎▏",
            "▏▎▍▌▋▊▉███▏",
            "▖▘▝▗",
            "◐ ◓ ◑ ◒ ",
            "◴ ◷ ◶ ◵",
            "⣾⣽⣻⢿⡿⣟⣯⣷",
            "⠁⠂⠄⡀⢀⠠⠐⠈",
            "◢ ◣ ◤ ◥ ",
            ".oOo",
            "⎺⎻⎼⎽⎼⎻⎺",
            "⎽⎼⎻⎺⎺⎽",
        ]
    ).replace(" ", "")

    done_symbol = "✗"

    time_str = _format_time_part(0, None)
    bar_size = min(n_steps, width - 6 - len(time_str))

    started = time.time()
    formatter = _Formatter(bar_size, n_steps, started)

    thread = _UpdateThread(symbols, formatter, done_symbol)
    thread.start()

    try:
        for result in iterable:
            thread.progress_counter += 1
            yield result
            if not thread.is_alive():
                # usually KeyboardInterrupt happened in update thread
                break
    except KeyboardInterrupt:  # pragma: no cover
        thread.iter_running = False  # pragma: no cover
        thread.join()  # pragma: no cover
        raise  # pragma: no cover

    finally:
        # stop thread:
        thread.iter_running = False
        thread.join()


def with_simple_progress_report(n_steps, iterable, minimum_time_interval=30):
    started = time.time()
    time_left = None

    last_report = started

    for i, result in enumerate(iterable):

        if time.time() > last_report + minimum_time_interval:
            time_left = _print_progress(started, time_left, i, n_steps)
            last_report = time.time()

        yield result


def _print_progress(started, time_left, i, n_steps):
    time_passed = time.time() - started

    time_left_estimate = time_passed / (i + 1) * (n_steps - i - 1)
    if time_left is not None:
        time_left = 0.8 * time_left + 0.2 * time_left_estimate
    else:
        time_left = time_left_estimate

    tp = _format_time(time_passed)
    tl = _format_time(time_left)

    print(
        "time passed: {}  estimated time left: {}  computed {} / {} samples".format(
            tp, tl, i + 1, n_steps
        )
    )
    return time_left


def is_float(x):
    try:
        float(x)
    except ValueError:
        return False
    else:
        return True


def check_range(range_):
    if not isinstance(range_, (list, tuple)) or len(range_) != 2:
        raise ValueError(
            "range_ must be list or tuple of length 2, got {!r}".format(range_)
        )

    min_, max_ = range_

    if not is_float(min_) or not is_float(max_):
        raise ValueError(
            "range_ must be a tuple of 2 float values, got {!r}".format(range_)
        )
    if not min_ < max_:
        raise ValueError(
            "min value {} is not smaller than max value {}".format(min_, max_)
        )


def is_writable(path):

    if os.path.exists(path):
        return os.access(path, os.W_OK)
    try:
        open(path, "w").close()
    except IOError as e:
        print("ERROR", e)
        return False
    try:
        os.unlink(path)
    except FileNotFoundError as e:  # possible race condition when ran in parallel
        print("ERROR", e)
        pass
    return True


class Tee(io.TextIOBase):
    def __init__(self, file_stream, console_stream):
        self.file_stream = file_stream
        self.console_stream = console_stream

    def write(self, *args):
        if self.file_stream is not None:
            self.file_stream.write(*args)
        if self.console_stream is not None:
            self.console_stream.write(*args)

    def close(self):
        pass


@contextmanager
def capture(path, show_output):

    if path is not None:
        fh = open(path, "a")
    else:
        fh = None

    stdout_stream = Tee(fh, sys.stdout if show_output else None)
    stderr_stream = Tee(fh, sys.stderr if show_output else None)

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = stdout_stream
        sys.stderr = stderr_stream
        yield

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        if fh is not None:
            fh.close()


def os_write_works():
    try:
        os.write(1, b"")
    except IOError:
        return False
    else:
        return True


# from https://stackoverflow.com/questions/6796492/temporarily-redirect-stdout-stderr:


@contextmanager
def stdchannel_redirected(stdchannel, dest_filename):
    """
    A context manager to temporarily redirect stdout or stderr

    e.g.:

    with stdchannel_redirected(sys.stderr, os.devnull):
        ...
    """

    oldstdchannel = None
    dest_file = None
    dest_file = open(dest_filename, "w")
    try:
        oldstdchannel = os.dup(stdchannel.fileno())
        os.dup2(dest_file.fileno(), stdchannel.fileno())
        yield
    except IOError:
        # sth with stream handling went wrong, happens e.g. in Jupyter notebooks.
        # In this case we don't redirect:
        yield
    finally:
        if oldstdchannel is not None:
            os.dup2(oldstdchannel, stdchannel.fileno())
        if dest_file is not None:
            dest_file.close()


mute_stderr = functools.partial(stdchannel_redirected, sys.stderr, os.devnull)

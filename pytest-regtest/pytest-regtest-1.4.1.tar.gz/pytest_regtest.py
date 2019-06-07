# encoding: utf-8
from __future__ import absolute_import, division, print_function

import difflib
import functools
import os
import re
import sys
import tempfile

import pkg_resources
import py
import pytest
from _pytest._code.code import ExceptionInfo, TerminalRepr
from _pytest.outcomes import skip

pytest_plugins = ["pytester"]


_version = pkg_resources.require("pytest-regtest")[0].version.split(".")
__version__ = tuple(map(int, _version))
del _version


IS_PY3 = sys.version_info.major == 3
IS_WIN = sys.platform == "win32"

if IS_PY3:
    open = functools.partial(open, encoding="utf-8")
    from io import StringIO

    def ljust(s, *a):
        return s.ljust(*a)


else:
    from cStringIO import StringIO
    from string import ljust


""" the function below is from
http://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
"""

textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})


def is_binary_string(bytes):
    return bool(bytes.translate(None, textchars))


_converters_pre = []
_converters_post = []


def register_converter_pre(function):
    if function not in _converters_pre:
        _converters_pre.append(function)


def register_converter_post(function):
    if function not in _converters_post:
        _converters_post.append(function)


def _std_replacements(request):

    if "tmpdir" in request.fixturenames:
        tmpdir = request.getfixturevalue("tmpdir").strpath
        yield tmpdir, "<tmpdir_from_fixture>"

    regexp = os.path.join(tempfile.gettempdir(), "tmp[_a-zA-Z0-9]+")

    yield regexp, "<tmpdir_from_tempfile_module>"
    yield os.path.realpath(tempfile.gettempdir()), "<tmpdir_from_tempfile_module>"
    yield tempfile.tempdir, "<tmpdir_from_tempfile_module>"
    yield r"var/folders/.*/pytest-of.*/", "<pytest_tempdir>/"

    # replace hex object ids in output by 0x?????????
    yield r" 0x[0-9a-f]+", " 0x?????????"


def _std_conversion(recorded, request):

    fixed = []
    for line in recorded.split("\n"):
        for regex, replacement in _std_replacements(request):
            if IS_WIN:
                # fix windows backwards slashes in regex
                regex = regex.replace("\\", "\\\\")
            line, __ = re.subn(regex, replacement, line)
        fixed.append(line)
    recorded = "\n".join(fixed)

    # recorded = cleanup_hex(recorded)
    return recorded


def _call_converter(converter, recorded, request):
    if converter.__code__.co_argcount == 2:
        #  new api for converters
        return converter(recorded, request)
    # old api for converters
    return converter(recorded)


def cleanup(recorded, request):

    for converter in _converters_pre:
        recorded = _call_converter(converter, recorded, request)

    recorded = _std_conversion(recorded, request)

    for converter in _converters_post:
        recorded = _call_converter(converter, recorded, request)

    # in python 3 a string should not contain binary symbols...:
    if not IS_PY3 and is_binary_string(recorded):
        request.raiseerror(
            "recorded output for regression test contains unprintable characters."
        )

    return recorded


class CollectErrorRepr(TerminalRepr):
    def __init__(self, messages, colors):
        self.messages = messages
        self.colors = colors

    def toterminal(self, out):
        for message, color in zip(self.messages, self.colors):
            out.line(message, **color)


def pytest_addoption(parser):
    """Add options to control the timeout plugin"""
    group = parser.getgroup("regtest", "regression test plugin")
    group.addoption(
        "--regtest-reset",
        action="store_true",
        help="do not run regtest but record current output",
    )
    group.addoption(
        "--regtest-tee",
        action="store_true",
        default=False,
        help="print recorded results to console too",
    )
    group.addoption(
        "--regtest-regard-line-endings",
        action="store_true",
        default=False,
        help="do not strip whitespaces at end of recorded lines",
    )
    group.addoption(
        "--regtest-nodiff",
        action="store_true",
        default=False,
        help="do not show diff output for failed regresson tests",
    )


class Config:

    ignore_line_endings = True
    tee = False
    reset = False
    nodiff = False


def pytest_configure(config):
    Config.tee = config.getvalue("--regtest-tee")
    Config.ignore_line_endings = not config.getvalue("--regtest-regard-line-endings")
    Config.reset = config.getvalue("--regtest-reset")
    Config.nodiff = config.getvalue("--regtest-nodiff")


tw = py.io.TerminalWriter()


class RegTestFixture(object):
    def __init__(self, request, nodeid):
        self.request = request
        self.nodeid = nodeid

        self.test_folder = request.fspath.dirname
        self.buffer = StringIO()
        self.identifier = None

    @property
    def output_file_name(self):
        file_name, __, test_function = self.nodeid.partition("::")
        file_name = os.path.basename(file_name)
        test_function = test_function.replace("/", "--")
        stem, __ = os.path.splitext(file_name)
        if self.identifier is not None:
            return stem + "." + test_function + "__" + self.identifier + ".out"
        else:
            return stem + "." + test_function + ".out"

    @property
    def result_file(self):
        return os.path.join(self.test_folder, "_regtest_outputs", self.output_file_name)

    def write(self, what):
        self.buffer.write(what)

    def flush(self):
        pass

    @property
    def tobe(self):
        if os.path.exists(self.result_file):
            return open(self.result_file).read()
        return ""

    @property
    def current(self):
        return cleanup(self.buffer.getvalue(), self.request)

    def write_current(self):
        folder = os.path.dirname(self.result_file)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(self.result_file, "w") as fh:
            fh.write(self.current)

    def __enter__(self):
        self.stdout = sys.stdout
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.stdout
        return False  # don't suppress exception


@pytest.fixture
def regtest(request):
    item = request.node

    yield RegTestFixture(request, item.nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield

    excinfo = call.excinfo
    when = call.when
    duration = call.stop - call.start
    keywords = dict([(x, 1) for x in item.keywords])

    result = outcome.get_result()
    result.when = when
    result.duration = duration
    result.keywords = keywords

    xfail = item.get_closest_marker("xfail") is not None

    if excinfo:
        if not isinstance(excinfo, ExceptionInfo):
            _outcome = "failed"
            longrepr = excinfo
        elif excinfo.errisinstance(skip.Exception):
            _outcome = "skipped"
            r = excinfo._getreprcrash()
            longrepr = (str(r.path), r.lineno, r.message)
        else:
            _outcome = "failed" if not xfail else "skipped"
            if call.when == "call":
                longrepr = item.repr_failure(excinfo)
            else:  # exception in setup or teardown
                longrepr = item._repr_failure_py(
                    excinfo, style=item.config.option.tbstyle
                )
        result.longrepr = longrepr
        result.outcome = _outcome

    else:
        result.outcome = "passed"
        result.longrepr = None

        if call.when == "call":
            regtest = getattr(item, "funcargs", {}).get("regtest")
            if regtest is not None:
                xfail = item.get_closest_marker("xfail") is not None
                handle_regtest_result(regtest, result, xfail)


def handle_regtest_result(regtest, result, xfail):

    if Config.tee:
        tw.line()
        line = "recorded output to regtest fixture:"
        line = ljust(line, tw.fullwidth, "-")
        tw.line(line, green=True)
        tw.write(regtest.current, cyan=True)
        tw.line("-" * tw.fullwidth, green=True)

    if not Config.reset:

        current = regtest.current.split("\n")
        tobe = regtest.tobe.split("\n")

        if Config.ignore_line_endings:
            current = [l.rstrip() for l in current]
            tobe = [l.rstrip() for l in tobe]

        if current != tobe:

            if xfail:
                result.outcome = "skipped"
            else:
                result.outcome = "failed"

            nodeid = regtest.nodeid + (
                "" if regtest.identifier is None else "__" + regtest.identifier
            )
            if Config.nodiff:
                result.longrepr = CollectErrorRepr(
                    ["regression test for {} failed\n".format(nodeid)],
                    [dict(red=True, bold=True)],
                )
                return

            if not Config.ignore_line_endings:
                # add quotes around lines in diff:
                current = map(repr, current)
                tobe = map(repr, tobe)
            collected = list(
                difflib.unified_diff(current, tobe, "current", "tobe", lineterm="")
            )

            msg = "\nregression test output differences for {}:\n".format(nodeid)
            msg_diff = ">   " + "\n>   ".join(collected)
            result.longrepr = CollectErrorRepr(
                [msg, msg_diff + "\n"], [dict(), dict(red=True, bold=True)]
            )

    else:
        regtest.write_current()

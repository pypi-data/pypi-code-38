# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: test_printer
#         Desc: 测试颜色打印
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-04 20:03
#=============================================================================
"""
import pytest

from plum_tools.utils.printer import get_color
from plum_tools.utils.printer import get_red
from plum_tools.utils.printer import get_green
from plum_tools.utils.printer import get_yellow
from plum_tools.utils.printer import print_error
from plum_tools.utils.printer import print_ok
from plum_tools.utils.printer import print_warn
from plum_tools.utils.printer import print_text

from plum_tools.compat import implements_to_unicode


@pytest.mark.parametrize("c, s", [
    (1, 1),
    (2, 2.02),
    (3, None),
    (4, ""),
    (5, "1"),
    (6, "测试"),
    (7, u"测试"),
])
def test_color(c, s):
    assert get_color(c, s) == "\033[3%sm%s\033[0m" % (c, implements_to_unicode(s))


@pytest.mark.parametrize("s", [
    1,
    2.02,
    None,
    "",
    "1",
    "测试",
    u"测试",
])
def test_get_red(s):
    assert get_red(s) == "\033[3%sm%s\033[0m" % (1, implements_to_unicode(s))


@pytest.mark.parametrize("s", [
    1,
    2.02,
    None,
    "",
    "1",
    "测试",
    u"测试",
])
def test_get_green(s):
    assert get_green(s) == "\033[3%sm%s\033[0m" % (2, implements_to_unicode(s))


@pytest.mark.parametrize("s", [
    1,
    2.02,
    None,
    "",
    "1",
    "测试",
    u"测试",
])
def test_get_yellow(s):
    assert get_yellow(s) == "\033[3%sm%s\033[0m" % (3, implements_to_unicode(s))


@pytest.mark.parametrize("s", [
    1,
    2.02,
    None,
    "",
    "1",
    "测试",
    u"测试",
])
def test_print_text(s, capsys):
    print_text(s)
    captured = capsys.readouterr()
    assert captured.out == implements_to_unicode(s) + "\n"


@pytest.mark.parametrize("s", [
    1,
    2.02,
    None,
    "",
    "1",
    "测试",
    u"测试",
])
def test_print_ok(s, capsys):
    print_ok(s)
    captured = capsys.readouterr()
    assert captured.out == "\033[3%sm%s\033[0m\n" % (2, implements_to_unicode(s))


@pytest.mark.parametrize("s", [
    1,
    2.02,
    None,
    "",
    "1",
    "测试",
    u"测试",
])
def test_print_warn(s, capsys):
    print_warn(s)
    captured = capsys.readouterr()
    assert captured.out == "\033[3%sm%s\033[0m\n" % (3, implements_to_unicode(s))


@pytest.mark.parametrize("s", [
    1,
    2.02,
    None,
    "",
    "1",
    "测试",
    u"测试",
])
def test_pprint_error(s, capsys):
    print_error(s)
    captured = capsys.readouterr()
    assert captured.out == "\033[3%sm%s\033[0m\n" % (1, implements_to_unicode(s))

"""
Tests for qz7.shell.cmdlist module.
"""
#pylint: disable=missing-docstring

import shlex

from qz7.shell.cmdlist import CmdList, command_format

def test_fmt():
    x = command_format('''
        command1
        command2
        command3
        ''')
    y = CmdList(['command1', 'command2', 'command3'])

    assert x == y

def test_fmt_emptylines():
    x = command_format('''
        command1

        command2

        command3
        ''')
    y = CmdList(['command1', 'command2', 'command3'])

    assert x == y

def test_fmt_comment():
    x = command_format('''
        command1
        command2
        command3
        #command4
        ''')
    y = CmdList(['command1', 'command2', 'command3'])

    assert x == y

def test_fmt_line_joining():
    x = command_format('''
        command1
        command2
        command3 \\
            arg1
        ''')
    y = CmdList(['command1', 'command2', 'command3 arg1'])

    assert x == y

def test_str():
    x = CmdList("command", shell="/bin/sh -c", separator=" && ")
    assert str(x) == "/bin/sh -c command"

def test_str2():
    x = CmdList(["command1", "command2"], shell="/bin/sh -c", separator=" && ")
    assert str(x) == "/bin/sh -c 'command1 && command2'"

def test_arg1():
    x = command_format("command {}", "rm -rf /")
    x = str(x)

    x = shlex.split(x)
    assert x[0] == "/bin/bash"
    assert x[1] == "-c"

    y = shlex.split(x[2])
    assert y[0] == "command"
    assert y[1] == "rm -rf /"

import os
import re
from invoke import Context, Config

U_SUCCESS = u"\u2713"
U_FAILURE = u"\u2716"

COLOR_RED = "red"
COLOR_GREEN = "green"
COLOR_YELLOW = "yellow"
COLOR_BLUE = "blue"
COLOR_PURPLE = "purple"
COLOR_LIGHTBLUE = "lightblue"
COLOR_LIGHTGREY = "lightgrey"
COLOR_GREY = "grey"
COLOR_PINK = "pink"


def get_context():
    """
    Get an invoke context object, used to run shell commands.

    :return {invoke.context.Context}: Returns the context object.
    """
    return Context(Config())


def run(cmd, ctx=None, *args, **kwargs):
    if not ctx:
        ctx = get_context()
    return ctx.run(cmd, *args, **kwargs)


def out(msg, color="green", run=True, ctx=None, is_error=False, **kwargs):
    """
    Run an echo command through invoke that prints text in color.

    We will be using the following color codes:

    Black        0;30     Dark Gray     1;30
    Red          0;31     Light Red     1;31
    Green        0;32     Light Green   1;32
    Brown/Orange 0;33     Yellow        1;33
    Blue         0;34     Light Blue    1;34
    Purple       0;35     Light Purple  1;35
    Cyan         0;36     Light Cyan    1;36
    Light Gray   0;37     White         1;37

    :param msg {str}:
    :param color {str}:
    :param run {bool}:
    :param ctx {invoke.context.Context}: Invoke context variable
    :param is_error {bool}:
        If True, echo output to stderr.
    :return {NoneType}:
    """
    if not ctx:
        ctx = get_context()

    if os.environ.get("INVOKE_ASCII", False) == "1":
        msg = msg.replace(U_SUCCESS, "PASS")
        msg = msg.replace(U_FAILURE, "FAIL")
        msg = msg.encode("utf-8").decode("ascii", "ignore")

    if run and os.environ.get("INVOKE_NO_COLOR", False) == "1":
        msg = re.sub(r"\s*\$\(tput[a-z0-9 ]+\)\s*", "", msg)
        ctx.run('echo "{}"'.format(msg), **kwargs)
        return msg

    reset = "\033[0m"
    colors = {
        COLOR_RED: "\033[0;31m",
        COLOR_GREEN: "\033[0;32m",
        COLOR_YELLOW: "\033[0;33m",
        COLOR_BLUE: "\033[0;34m",
        COLOR_PURPLE: "\033[0;35m",
        COLOR_LIGHTBLUE: "\033[1;34m",
        COLOR_LIGHTGREY: "\033[0;37m",
        COLOR_GREY: "\033[1;30m",
        COLOR_PINK: "\033[1;31m",
    }

    color = "" if (not color or color not in colors) else colors[color]
    msg = "{}{}{}".format(color, msg, reset)
    if run:
        # Output to stderr - https://stackoverflow.com/a/23550347/3330552
        prefix = ">&2 " if is_error else ""

        ctx.run('{}echo "{}"'.format(prefix, msg), **kwargs)
    return msg

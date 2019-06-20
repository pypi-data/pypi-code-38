""" Functions for working with command-line interaction """

from .collection import is_collection_like
import sys

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["build_cli_extra", "query_yes_no"]


def build_cli_extra(optargs):
    """
    Render CLI options/args as text to add to base command.

    To specify a flag, map an option to None. Otherwise, map option short or
    long name to value(s). Values that are collection types will be rendered
    with single space between each. All non-string values are converted to
    string.

    :param Mapping | Iterable[(str, object)] optargs: values used as
        options/arguments
    :return str: text to add to base command, based on given opts/args
    :raise TypeError: if an option name isn't a string
    """

    def render(k, v):
        if not isinstance(k, str):
            raise TypeError(
                "Option name isn't a string: {} ({})".format(k, type(k)))
        if v is None:
            return k
        if is_collection_like(v):
            v = " ".join(map(str, v))
        return "{} {}".format(k, v)

    try:
        data_iter = optargs.items()
    except AttributeError:
        data_iter = optargs

    return " ".join(render(*kv) for kv in data_iter)


def query_yes_no(question, default="no"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    :param str question: a string that is presented to the user.
    :param str default: the presumed answer if the user just hits <Enter>.
    :return bool: True for "yes" or False for "no"
    """
    def parse(ans):
        return {"yes": True, "y": True, "ye": True, "no": False, "n": False}[ans.lower()]
    try:
        prompt = {None: "[y/n]", "yes": "[Y/n]",
                  "no": "[y/N]"}[None if default is None else default.lower()]
    except (AttributeError, KeyError):
        raise ValueError("invalid default answer: {}".format(default))
    msg = "{q} {p} ".format(q=question, p=prompt)
    while True:
        sys.stdout.write(msg)
        try:
            return parse(_read_from_user() or default)
        except KeyError:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def _read_from_user():
    import sys
    if sys.version_info.major < 3:
        from __builtin__ import raw_input
        return raw_input()
    return input()

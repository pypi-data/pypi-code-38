"""
Module with helper for shell escaping
"""

import os
import re
import shlex

__all__ = ['quote_argument']


if os.name == 'nt':
    META_CHARS = '()%!^"<>&|'
    META_RE = re.compile('(' + '|'.join(re.escape(char) for char in list(META_CHARS)) + ')')
    META_MAP = {char: f"^{char}" for char in META_CHARS}

    def _escape_meta_chars(m):
        char = m.group(1)
        return META_MAP[char]

    def quote_argument(arg: str) -> str:
        """
        Quote and escape argument properly for use with cmd.exe

        :param arg: argument to quote
        :return: argument with quotes for safe use in a bash-like shell
        """
        # Escape the argument for the cmd.exe shell.
        # See http://blogs.msdn.com/b/twistylittlepassagesallalike/archive/2011/04/23/everyone-quotes-arguments-the-wrong-way.aspx
        #
        # First we escape the quote chars to produce a argument suitable for
        # CommandLineToArgvW. We don't need to do this for simple arguments.

        if not arg or re.search(r'(["\s])', arg):
            arg = '"' + arg.replace('"', r'\"') + '"'

        return META_RE.sub(_escape_meta_chars, arg)
else:
    def quote_argument(arg: str) -> str:
        """
        Use shlex module to quote the argument properly
        :param arg: argument to quote
        :return: argument with quotes for safe use in a bash-like shell
        """
        return shlex.quote(arg)



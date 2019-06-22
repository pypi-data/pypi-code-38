# -*- coding: utf-8 -*-
"""Data structure defining a pype."""

from re import sub


class Pype():
    """Data structure defining a pype."""

    def __init__(self, abspath, filename, plugin):
        """Activate pypes for the provided configuration."""
        self.name = sub(r'\.py$', '', filename)
        self.doc = self.__get_module_docstring(abspath)
        self.abspath = abspath
        self.plugin_name = plugin.name

    def __get_module_docstring(self, filepath):
        co = compile(open(filepath).read(), filepath, 'exec')
        if co.co_consts and isinstance(co.co_consts[0], str):
            return sub(r'[\.]+$', '', co.co_consts[0])
        return 'Not documented yet'

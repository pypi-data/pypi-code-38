# -*- coding: utf-8 -*-

"""Top-level package for clipt."""

__author__ = """Stephen Wasilewski"""
__email__ = 'stephanwaz@gmail.com'
__version__ = '0.1.11'
__all__ = ['plot', 'cl_plot']


def get_root(inside=True, pyenv=False):
    """return root directory of radutil install"""

    import sys

    if pyenv:
        return sys.executable.rsplit("/bin", 1)[0]
    elif inside:
        return __file__.rsplit("radutil", 1)[0] + "radutil"
    else:
        return __file__.rsplit("/radutil", 1)[0]
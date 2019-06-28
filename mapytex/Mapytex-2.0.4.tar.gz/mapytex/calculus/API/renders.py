#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Expression

"""
from ..core import tree2txt, tree2tex


def _txt(mo_tree):
    """ txt render for MOs or Trees"""
    try:
        return tree2txt(mo_tree)
    except ValueError:
        pass

    try:
        return mo_tree.__txt__
    except AttributeError:
        return str(mo_tree)


def _tex(mo_tree):
    """ Tex render for MOs or Trees"""
    try:
        return tree2tex(mo_tree)
    except ValueError:
        pass

    try:
        return mo_tree.__tex__
    except AttributeError:
        return str(mo_tree)


renders = {"txt": _txt, "tex": _tex}

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Exceptions for computing 
"""


class ComputeError(Exception):
    pass


class AddError(ComputeError):
    pass


class MinusError(ComputeError):
    pass


class MultiplyError(ComputeError):
    pass


class DivideError(ComputeError):
    pass


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del

# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Pricing Utilities
"""

from __future__ import unicode_literals, absolute_import


__all__ = ['gross_margin']


def gross_margin(price, cost, percentage=False):
    """
    Calculate and return a gross margin percentage based on ``price`` and
    ``cost``.

    Please note, that for historical reasons, the default behavior is to return
    the margin as a decimal value from 0.0 through 100.0 (or beyond, perhaps).

    However the "industry standard" seems to be to use a decimal value between
    0.000 and 1.000 instead.  Specify ``percentage=True`` for this behavior.

    If ``price`` is empty (or zero), returns ``None``.

    If ``cost`` is empty (or zero), returns ``100`` (or ``1`` if
    ``percentage=True``).
    """
    if not price:
        return None

    if not cost:
        if percentage:
            return 1
        return 100

    margin = (price - cost) / price
    if percentage:
        return margin
    return 100 * margin

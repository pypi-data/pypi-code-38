# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
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
Template Context Helpers
"""

from __future__ import unicode_literals, absolute_import

import datetime
from decimal import Decimal

from rattail.time import localtime, make_utc
from rattail.util import pretty_quantity, pretty_hours, hours_as_decimal

from webhelpers2.html import *
from webhelpers2.html.tags import *

from tailbone.util import csrf_token, pretty_datetime, raw_datetime


def pretty_date(date):
    """
    Render a human-friendly date string.
    """
    if not date:
        return ''
    return date.strftime('%a %d %b %Y')


def render_attrs(**attrs):
    """
    Convenience wrapper to replace the deprecated
    `webhelpers.html.builder.format_attrs()`
    """
    HTML.optimize_attrs(attrs)
    return HTML.render_attrs(attrs)

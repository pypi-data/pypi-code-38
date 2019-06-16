# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Vendor Invoices
"""

from __future__ import unicode_literals, absolute_import

from decimal import Decimal

import six

from rattail.exceptions import RattailError
from rattail.util import load_entry_points


class InvoiceParser(object):
    """
    Base class for all vendor invoice parsers.
    """

    @property
    def key(self):
        """
        Key for the parser.  Must be unique among all invoice parsers.
        """
        raise NotImplementedError("Invoice parser has no key: {0}".format(repr(self)))

    @property
    def vendor_key(self):
        """
        Key for the vendor.  This key will be used to locate an entry in the
        settings table, e.g. ``'rattail.vendor.unfi'`` for a key of ``'unfi'``.
        The value of this setting must be an exact match to either a
        :attr:`rattail.db.model.Vendor.uuid` or
        :attr:`rattail.db.model.Vendor.id` within the system.
        """
        raise NotImplementedError

    def parse_invoice_date(self, path):
        """
        Parse the invoice date from the invoice file.
        """

    def parse_rows(self, data_path):
        """
        Parse the given data file, returning all rows found within it.
        """
        raise NotImplementedError("Invoice parser has no `parse_rows()` method: {0}".format(repr(self.key)))

    def decimal(self, value, scale=4):
        """
        Convert a value to a decimal.
        """
        # No reason to convert integers, really.
        if isinstance(value, (Decimal, int)):
            return value
        if isinstance(value, float):
            return Decimal("{{:0.{}f}}".format(scale).format(value))
        value = value.strip()
        if value:
            return Decimal(value)

    def int_(self, value):
        """
        Convert a value to an integer.
        """
        value = value.strip() or 0
        return int(value)


@six.python_2_unicode_compatible
class InvoiceParserNotFound(RattailError):
    """
    Exception raised when a vendor invoice parser is required, but cannot be
    located.
    """

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "Vendor invoice parser with key {} cannot be located.".format(self.key)


def get_invoice_parsers():
    """
    Returns a dictionary of installed vendor invoice parser classes.
    """
    return load_entry_points('rattail.vendors.invoices.parsers')


def get_invoice_parser(key):
    """
    Fetch a vendor invoice parser by key.  If the parser class can be located,
    this will return an instance thereof; otherwise returns ``None``.
    """
    parser = get_invoice_parsers().get(key)
    if parser:
        return parser()
    return None


def require_invoice_parser(key):
    """
    Fetch a vendor invoice parser by key.  If the parser class can be located,
    this will return an instance thereof; otherwise raises an exception.
    """
    parser = get_invoice_parser(key)
    if not parser:
        raise InvoiceParserNotFound(key)
    return parser


def iter_invoice_parsers():
    """
    Returns an iterator over the installed vendor invoice parsers.
    """
    parsers = get_invoice_parsers()
    return parsers.values()

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
SIL Columns
"""

from __future__ import unicode_literals, absolute_import

import six

from ..core import Object
from .exceptions import SILColumnNotFound
from ..util import load_entry_points


__all__ = ['get_column']


supported_columns = None


@six.python_2_unicode_compatible
class SILColumn(Object):
    """
    Represents a column for use with SIL.
    """

    def __init__(self, name, data_type, description, display_name=None, **kwargs):
        Object.__init__(self, **kwargs)
        self.name = name
        self.data_type = data_type
        self.description = description
        self.display_name = display_name or description

    def __repr__(self):
        return "<SILColumn: %s>" % self.name

    def __str__(self):
        return str(self.name)


def provide_columns():
    """
    Provides all SIL columns natively supported by Rattail.
    """

    SC = SILColumn

    standard = [ # These columns are part of the SIL standard.

        # ITEM_DCT
        SC('F01',       'GPC(14)',      "Primary Item U.P.C. Number (Key)",     "UPC"),
        SC('F02',       'CHAR(20)',     "Descriptor",                           "Description"),
        SC('F04',       'NUMBER(4,0)',  "Sub-Department Number"),
        SC('F22',       'CHAR(30)',     "Size Description"),
        SC('F26',       'CHAR(15)',     "Primary Item Code (User)"),
        SC('F90',       'FLAG(1)',      "Authorized DSD Item"),
        SC('F94',       'NUMBER(2,0)',  "Shelf Tag Quantity"),
        SC('F95',       'CHAR(3)',      "Shelf Tag Type"),
        SC('F155',      'CHAR(30)',     "Brand"),
        SC('F188',      'FLAG(1)',      "POS Valid Item"),

        # PRICE_DCT
        SC('F30',       'NUMBER(8,3)',  "Retail Sell Price"),
        SC('F31',       'NUMBER(3,0)',  "Price Multiple (Quantity/For)"),
        SC('F35',       'DATE(7)',      "Price Start Date"),
        SC('F36',       'TIME(4)',      "Price Start Time"),
        SC('F126',      'NUMBER(2,0)',  "Pricing Level"),
        SC('F129',      'DATE(7)',      "Price End Date"),
        SC('F130',      'TIME(4)',      "Price End Time"),
        SC('F135',      'NUMBER(3,0)',  "Sale Price Multiple (Quantity/For)"),
        SC('F136',      'NUMBER(8,3)',  "Sale Price"),
        SC('F137',      'DATE(7)',      "Sale Price Start Date"),
        SC('F138',      'TIME(4)',      "Sale Price End Date"),
        SC('F139',      'NUMBER(8,3)',  "Sale Package Price"),
        SC('F140',      'NUMBER(8,3)',  "Package Price"),
        SC('F142',      'NUMBER(3,0)',  "Package Price Multiple"),
        SC('F143',      'NUMBER(3,0)',  "Sale Package Price Multiple"),
        SC('F144',      'TIME(4)',      "Sale Price Start Time"),
        SC('F145',      'TIME(4)',      "Sale Price End Time"),
        SC('F181',      'NUMBER(8,3)',  "TPR (Temporary Price Reduction)"),
        SC('F182',      'NUMBER(3,0)',  "TPR Multiple (Quantity/For)"),
        SC('F183',      'DATE(7)',      "TPR Start Date"),
        SC('F184',      'DATE(7)',      "TPR End Date"),
        SC('F387',      'NUMBER(3)',    "Price Type Code"),

        # FCOST_DCT
        SC('F19',       'NUMBER(4,0)',  "Case Pack Size"),
        SC('F20',       'NUMBER(4,0)',  "Receiving Pack Size"),
        SC('F38',       'NUMBER(9,5)',  "Case Receiving Base Cost"),
        SC('F212',      'TIME(4)',      "Cost Change Time"),
        SC('F227',      'DATE(7)',      "Cost Change Date"),

        # DEPT_DCT
        SC('F03',       'NUMBER(4,0)',  "Department Number"),
        SC('F238',      'CHAR(30)',     "Department Description"),

        # VENDOR_DCT
        SC('F27',       'CHAR(9)',      "Vendor Number"),
        SC('F334',      'CHAR(20)',     "Vendor Name"),
        SC('F335',      'CHAR(20)',     "Vendor Contact Name"),
        SC('F341',      'NUMBER(10,0)', "Vendor Phone Number - Voice"),
        SC('F342',      'NUMBER(10,0)', "Vendor Phone Number - Fax"),
        ]

    custom = [ # These columns are Rattail-specific.

        SC('R38',       'NUMBER(9,5)',  "Unit Receiving Base Cost"),
        SC('R49',       'NUMBER(5,3)',  "Gross Margin Percent"),
        SC('R71',       'NUMBER(5,0)',  "Inventory - Units Counted",            "Units"),
        SC('R72',       'NUMBER(5,0)',  "Inventory - Cases Counted",            "Cases"),
        SC('R101',      'NUMBER(9,5)',  "Difference Amount",                    "Difference"),
        SC('R102',      'NUMBER(3,0)',  "Status Code"),
        SC('R103',      'CHAR(30)',     "Status Text"),
        ]

    columns = {}
    for column in standard + custom:
        columns[column.name] = column
    return columns


def get_column(name):
    """
    Returns the :class:`SILColumn` instance named ``name``.
    """

    global supported_columns

    if supported_columns is None:
        supported_columns = {}
        providers = load_entry_points('rattail.sil.column_providers')
        for provider in providers.values():
            supported_columns.update(provider())

    column = supported_columns.get(name)
    if not column:
        raise SILColumnNotFound(name)
    return column

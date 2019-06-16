# -*- coding: utf-8 -*-
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
Models for vendor invoice batches
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, Vendor, FileBatchMixin, ProductBatchRowMixin


class VendorInvoice(FileBatchMixin, Base):
    """
    Vendor invoice, the source data file of which has been provided by a user,
    and may be further processed in some site-specific way.
    """
    __tablename__ = 'vendor_invoice'
    __batchrow_class__ = 'VendorInvoiceRow'

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'],
                                    name='vendor_invoice_fk_vendor'),
            )

    parser_key = sa.Column(sa.String(length=100), nullable=False, doc="""
    The key of the parser used to parse the contents of the data file.
    """)

    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)

    vendor = relationship(Vendor, doc="""
    Reference to the :class:`Vendor` to which the invoice pertains.
    """)

    invoice_date = sa.Column(sa.Date(), nullable=True, doc="""
    Invoice date, as determined by the invoice data file.
    """)

    purchase_order_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Purchase order number, e.g. for cross-reference with another system.  Custom
    batch handlers may populate and leverage this field, but the default handler
    does not.
    """)


class VendorInvoiceRow(ProductBatchRowMixin, Base):
    """
    Row of data within a vendor invoice.
    """
    __tablename__ = 'vendor_invoice_row'
    __batch_class__ = VendorInvoice

    STATUS_OK = 1
    STATUS_NOT_IN_DB = 2
    STATUS_NOT_IN_PURCHASE = 3
    STATUS_NOT_IN_INVOICE = 4
    STATUS_DIFFERS_FROM_PURCHASE = 5
    STATUS_COST_NOT_IN_DB = 6
    STATUS_NO_CASE_QUANTITY = 7

    STATUS = {
        STATUS_OK:                      "as expected",
        STATUS_NOT_IN_DB:               "product not found",
        STATUS_COST_NOT_IN_DB:          "product found but not cost",
        STATUS_NOT_IN_PURCHASE:         "present only in invoice",
        STATUS_NOT_IN_INVOICE:          "present only in PO",
        STATUS_DIFFERS_FROM_PURCHASE:   "invoice and PO differ",
        STATUS_NO_CASE_QUANTITY:        "case quantity not known",
    }

    vendor_code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Vendor's unique code for the product.  The meaning of this corresponds to that
    of the :attr:`ProductCost.code` column.
    """)

    case_quantity = sa.Column(sa.Integer(), nullable=False, default=1, doc="""
    Number of units in a case of product.
    """)

    ordered_cases = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Number of cases of the product which were originally ordered from the vendor.
    """)

    ordered_units = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Number of units of the product which were originally ordered from the vendor.
    """)

    shipped_cases = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Number of cases of the product which were shipped by the vendor.
    """)

    shipped_units = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Number of units of the product which were shipped by the vendor.
    """)

    out_of_stock = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the item was known to be "out of stock" per the
    vendor invoice.
    """)

    case_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Cost per case of the product.
    """)

    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Cost per unit of the product.
    """)

    total_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Total cost for this product line item; should equate to the number of units
    shipped multiplied by the unit cost.
    """)

    line_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Line number of the purchase order with which this invoice row matches.  Custom
    batch handlers may populate and leverage this field, but the default handler
    does not.
    """)

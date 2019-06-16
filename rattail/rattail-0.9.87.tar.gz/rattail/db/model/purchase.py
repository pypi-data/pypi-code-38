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
Data model for purchase orders
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, uuid_column, Store, Department, Vendor, Employee, User, Product
from rattail.db.types import GPCType
from rattail.util import pretty_quantity


@six.python_2_unicode_compatible
class PurchaseBase(object):
    """
    Base class for purchases; defines common fields.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__purchase_table_args__()

    @classmethod
    def __purchase_table_args__(cls):
        return (
            sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='{}_fk_store'.format(cls.__tablename__)),
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'], name='{}_fk_vendor'.format(cls.__tablename__)),
            sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='{}_fk_department'.format(cls.__tablename__)),
            sa.ForeignKeyConstraint(['buyer_uuid'], ['employee.uuid'], name='{}_purchase_fk_buyer'.format(cls.__tablename__)),
        )

    store_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def store(cls):
        return orm.relationship(
            Store,
            doc="""
            Reference to the :class:`Store` for which the purchase was made.
            """)

    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def vendor(cls):
        return orm.relationship(
            Vendor,
            doc="""
            Reference to the :class:`Vendor` to which the purchase was made.
            """)

    department_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def department(cls):
        return orm.relationship(
            Department,
            doc="""
            Reference to the primary :class:`Department` for which the purchase was made.
            """)

    buyer_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def buyer(cls):
        return orm.relationship(
            Employee,
            doc="""
            Reference to the :class:`Employee` who placed the order with the
            vendor, if applicable/known.
            """)

    po_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Purchase order number, e.g. for cross-reference with another system.
    """)

    po_total = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Purchase order total, i.e. expected cost as of order placement.
    """)

    date_ordered = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the purchase order was first submitted to the vendor.
    """)

    ship_method = sa.Column(sa.String(length=50), nullable=True, doc="""
    Code representing the shipping method.
    """)

    notes_to_vendor = sa.Column(sa.Text(), nullable=True, doc="""
    Any arbitrary notes to the vendor, regarding the purchase.
    """)

    date_shipped = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the order was shipped from the vendor.
    """)

    date_received = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the order was received at the store.
    """)

    invoice_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Invoice number, e.g. for cross-reference with another system.
    """)

    invoice_date = sa.Column(sa.Date(), nullable=True, doc="""
    Invoice date, if applicable.
    """)

    invoice_total = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Invoice total, if applicable.
    """)

    def __str__(self):
        if self.vendor and self.date_ordered:
            return "{} ({})".format(self.vendor, self.date_ordered.strftime('%Y-%m-%d'))
        if self.vendor:
            return str(self.vendor)
        return ''


class PurchaseItemBase(object):
    """
    Base class for purchase line items.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__purchaseitem_table_args__()

    @classmethod
    def __purchaseitem_table_args__(cls):
        return (
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='{}_fk_product'.format(cls.__tablename__)),
        )

    sequence = sa.Column(sa.Integer(), nullable=True, doc="""
    Effectively the (internal) line number for the purchase line item, using 1-based indexing.
    """)

    vendor_code = sa.Column(sa.String(length=20), nullable=True, doc="""
    Vendor item code for the product.
    """)

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def product(cls):
        return orm.relationship(
            Product,
            doc="""
            Reference to the :class:`Product` which the line item contains / represents.
            """,
            backref=orm.backref(
                '_{}_records'.format(cls.__tablename__),
                doc="""
                List of ``{}`` records associated with the product.
                """.format(cls.__tablename__)))

    upc = sa.Column(GPCType(), nullable=True, doc="""
    Product UPC for the line item.
    """)

    item_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Generic ID string for the item.
    """)

    brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the line item.
    """)

    description = sa.Column(sa.String(length=60), nullable=False, default='', doc="""
    Product description for the line item.
    """)

    size = sa.Column(sa.String(length=255), nullable=True, doc="""
    Product size for the line item.
    """)

    department_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the department to which the product belongs.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the department to which the product belongs.
    """)

    case_quantity = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Number of units in a single case of product.
    """)

    cases_ordered = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were initially ordered.
    """)

    units_ordered = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were initially ordered.
    """)

    po_line_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Line number from the PO if known, for cross-reference.
    """)

    po_unit_cost = sa.Column(sa.Numeric(precision=7, scale=3), nullable=True, doc="""
    Expected cost per single unit of product, as of initial order placement.
    """)

    po_total = sa.Column(sa.Numeric(precision=7, scale=2), nullable=True, doc="""
    Expected total cost for line item, as of initial order placement.
    """)

    cases_shipped = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were supposedly shipped by/from the vendor.
    """)

    units_shipped = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were supposedly shipped by/from the vendor.
    """)

    cases_received = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were ultimately received.
    """)

    units_received = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were ultimately received.
    """)

    out_of_stock = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the item was known to be "out of stock" per the
    vendor invoice.
    """)

    invoice_line_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Line number from the invoice if known, for cross-reference.
    """)

    invoice_case_cost = sa.Column(sa.Numeric(precision=7, scale=3), nullable=True, doc="""
    Actual cost per case of product, per invoice.
    """)

    invoice_unit_cost = sa.Column(sa.Numeric(precision=7, scale=3), nullable=True, doc="""
    Actual cost per single unit of product, per invoice.
    """)

    invoice_total = sa.Column(sa.Numeric(precision=7, scale=2), nullable=True, doc="""
    Actual total cost for line item, per invoice.
    """)

    cases_damaged = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were shipped damaged.
    """)

    units_damaged = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were shipped damaged.
    """)

    cases_expired = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were shipped expired.
    """)

    units_expired = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were shipped expired.
    """)

    cases_mispick = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product for which mispick was shipped.
    """)

    units_mispick = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product for which mispick was shipped.
    """)


@six.python_2_unicode_compatible
class PurchaseCreditBase(object):
    """
    Base class for purchase credits.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__purchasecredit_table_args__()

    @classmethod
    def __purchasecredit_table_args__(cls):
        return (
            sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='{}_fk_store'.format(cls.__tablename__)),
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'], name='{}_fk_vendor'.format(cls.__tablename__)),
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='{}_fk_product'.format(cls.__tablename__)),
            sa.ForeignKeyConstraint(['mispick_product_uuid'], ['product.uuid'], name='{}_fk_mispick_product'.format(cls.__tablename__)),
        )

    store_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def store(cls):
        return orm.relationship(
            Store,
            doc="""
            Reference to the :class:`Store` for which the purchase was made.
            """)

    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def vendor(cls):
        return orm.relationship(
            Vendor,
            doc="""
            Reference to the :class:`Vendor` to which the purchase was made.
            """)

    date_ordered = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the purchase order was first submitted to the vendor.
    """)

    date_shipped = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the order was shipped from the vendor.
    """)

    date_received = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the order was received at the store.
    """)

    invoice_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Invoice number, e.g. for cross-reference with another system.
    """)

    invoice_date = sa.Column(sa.Date(), nullable=True, doc="""
    Invoice date, if applicable.
    """)

    credit_type = sa.Column(sa.String(length=20), nullable=False, doc="""
    Type of the credit, i.e. damaged/expired/mispick
    """)

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def product(cls):
        return orm.relationship(
            Product,
            primaryjoin='Product.uuid == {}.product_uuid'.format(cls.__name__),
            doc="""
            Reference to the :class:`Product` with which the credit is associated.
            """)

    upc = sa.Column(GPCType(), nullable=True, doc="""
    Product UPC for the credit item.
    """)

    vendor_item_code = sa.Column(sa.String(length=20), nullable=True, doc="""
    Vendor-specific code for the credit item.
    """)

    brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the credit item.
    """)

    description = sa.Column(sa.String(length=60), nullable=False, default='', doc="""
    Product description for the credit item.
    """)

    size = sa.Column(sa.String(length=255), nullable=True, doc="""
    Product size for the credit item.
    """)

    department_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the department to which the product belongs.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the department to which the product belongs.
    """)

    case_quantity = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Number of units in a single case of product.
    """)

    cases_shorted = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were ordered but not received.
    """)

    units_shorted = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were ordered but not received.
    """)

    product_discarded = sa.Column(sa.Boolean(), nullable=True, doc="""
    Indicates the associated product was discarded, and cannot be returned to vendor.
    """)

    expiration_date = sa.Column(sa.Date(), nullable=True, doc="""
    Expiration date marked on expired product, if applicable.
    """)

    invoice_line_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Line number from the invoice if known, for cross-reference.
    """)

    invoice_case_cost = sa.Column(sa.Numeric(precision=7, scale=3), nullable=True, doc="""
    Actual cost per case of product, per invoice.
    """)

    invoice_unit_cost = sa.Column(sa.Numeric(precision=7, scale=3), nullable=True, doc="""
    Actual cost per single unit of product, per invoice.
    """)

    invoice_total = sa.Column(sa.Numeric(precision=7, scale=2), nullable=True, doc="""
    Actual total cost for line item, per invoice.
    """)

    credit_total = sa.Column(sa.Numeric(precision=7, scale=2), nullable=True, doc="""
    Actual total cost for credit, i.e. value of missing/damaged product.
    """)

    mispick_product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def mispick_product(cls):
        return orm.relationship(
            Product,
            primaryjoin='Product.uuid == {}.mispick_product_uuid'.format(cls.__name__),
            doc="""
            Reference to the :class:`Product` which was shipped in place of the
            one which was ordered.
            """)

    mispick_upc = sa.Column(GPCType(), nullable=True, doc="""
    Product UPC for the mispick item.
    """)

    mispick_brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the mispick item.
    """)

    mispick_description = sa.Column(sa.String(length=60), nullable=True, default='', doc="""
    Product description for the mispick item.
    """)

    mispick_size = sa.Column(sa.String(length=255), nullable=True, doc="""
    Product size for the mispick item.
    """)

    def __str__(self):
        if self.cases_shorted is not None and self.units_shorted is not None:
            qty = "{} cases, {} units".format(
                pretty_quantity(self.cases_shorted),
                pretty_quantity(self.units_shorted))
        elif self.cases_shorted is not None:
            qty = "{} cases".format(pretty_quantity(self.cases_shorted))
        elif self.units_shorted is not None:
            qty = "{} units".format(pretty_quantity(self.units_shorted))
        else:
            qty = "??"
        qty += " {}".format(self.credit_type)
        if self.credit_type == 'expired' and self.expiration_date:
            qty += " ({})".format(self.expiration_date)
        if self.credit_type == 'mispick' and self.mispick_product:
            qty += " ({})".format(self.mispick_product)
        if self.invoice_total:
            return "{} = ${:0.2f}".format(qty, self.invoice_total)
        return qty


class Purchase(PurchaseBase, Base):
    """
    Represents a purchase made by a store.
    """
    __tablename__ = 'purchase'

    @declared_attr
    def __table_args__(cls):
        return cls.__purchase_table_args__() + (
            sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='purchase_fk_created_by'),
        )

    uuid = uuid_column()

    status = sa.Column(sa.Integer(), nullable=False, doc="""
    Numeric code used to signify current status for the purchase, e.g. placed
    or paid etc.
    """)

    created = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Timestamp when the purchase was first created within this system.
    """)

    created_by_uuid = sa.Column(sa.String(length=32), nullable=False)

    created_by = orm.relationship(
        User,
        primaryjoin=User.uuid == created_by_uuid,
        foreign_keys=[created_by_uuid],
        doc="""
        Reference to the :class:`User` who first created the purchase within
        this system.
        """)


class PurchaseItem(PurchaseItemBase, Base):
    """
    Represents a line item on a purchase.
    """
    __tablename__ = 'purchase_item'

    @declared_attr
    def __table_args__(cls):
        return cls.__purchaseitem_table_args__() + (
            sa.ForeignKeyConstraint(['purchase_uuid'], ['purchase.uuid'], name='purchase_item_fk_purchase'),
        )

    uuid = uuid_column()

    purchase_uuid = sa.Column(sa.String(length=32), nullable=False)

    purchase = orm.relationship(
        Purchase,
        doc="""
        Reference to the :class:`Purchase` to which the item belongs.
        """,
        backref=orm.backref(
            'items',
            cascade='all',
            doc="""
            List of :class:`PurchaseItem` instances for the purchase.
            """))

    status = sa.Column(sa.Integer(), nullable=True, doc="""
    Numeric code used to signify current status for the line item, e.g. for
    highlighting rows when invoice cost differed from expected/PO cost (?)
    """)


class PurchaseCredit(PurchaseCreditBase, Base):
    """
    Represents a purchase credit item.
    """
    __tablename__ = 'purchase_credit'

    @declared_attr
    def __table_args__(cls):
        return cls.__purchasecredit_table_args__() + (
            sa.ForeignKeyConstraint(['purchase_uuid'], ['purchase.uuid'], name='purchase_credit_fk_purchase'),
            sa.ForeignKeyConstraint(['item_uuid'], ['purchase_item.uuid'], name='purchase_credit_fk_item'),
        )

    uuid = uuid_column()

    purchase_uuid = sa.Column(sa.String(length=32), nullable=True)

    purchase = orm.relationship(
        Purchase,
        doc="""
        Reference to the :class:`Purchase` to which the credit applies.
        """,
        backref=orm.backref(
            'credits',
            doc="""
            List of :class:`PurchaseCredit` instances for the purchase.
            """))

    item_uuid = sa.Column(sa.String(length=32), nullable=True)

    item = orm.relationship(
        PurchaseItem,
        doc="""
        Reference to the purchase item with which the credit is associated.
        """)

    status = sa.Column(sa.Integer(), nullable=True, doc="""
    Numeric code used to signify current status for the credit.
    """)

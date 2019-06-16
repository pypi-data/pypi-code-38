# -*- coding: utf-8; -*-
"""
TrainWreck data models
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

from rattail import enum
from rattail.db.model import uuid_column
from rattail.db.model.core import ModelBase


Base = declarative_base(cls=ModelBase)


@six.python_2_unicode_compatible
class TransactionBase(object):
    """
    Represents a POS (or similar?) transaction.
    """
    __tablename__ = 'transaction'
    __table_args__ = (
        sa.Index('transaction_ix_start_time', 'start_time'),
        sa.Index('transaction_ix_end_time', 'end_time'),
        sa.Index('transaction_ix_upload_time', 'upload_time'),
        sa.Index('transaction_ix_receipt_number', 'receipt_number'),
    )

    uuid = uuid_column()

    system = sa.Column(sa.String(length=50), nullable=True, doc="""
    Unique string representing the system from which transaction originated.
    """)

    system_id = sa.Column(sa.String(length=50), nullable=True, doc="""
    Unique ID string for the transaction within the system.
    """)

    terminal_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Terminal ID from which the transaction originated, if known.
    """)

    receipt_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Receipt number for the transaction, if known.
    """)

    start_time = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp when the transaction began, if known.
    """)

    end_time = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp when the transaction ended, if known.
    """)

    upload_time = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp when the transaction was uploaded to the server, if known.
    """)

    cashier_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Cashier ID string for the transaction, if known.
    """)

    cashier_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    Cashier name for the transaction, if known.
    """)

    customer_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Customer ID string for the transaction, if known.  This should correspond
    to a proper customer account, as opposed to :attr:`shopper_id`.
    """)

    customer_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    Customer name for the transaction, if known.  This should correspond to a
    proper customer account, as opposed to :attr:`shopper_name`.
    """)

    shopper_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Shopper ID string for the transaction, if known.  This should correspond
    to the actual shopper, as opposed to :attr:`customer_id`.
    """)

    shopper_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    Shopper name for the transaction, if known.  This should correspond to the
    actual shopper, as opposed to :attr:`customer_name`.
    """)

    subtotal = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Subtotal for the transaction, before discounts.
    """)

    discounted_subtotal = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Subtotal for the transaction, after discounts.
    """)

    tax = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Tax total (for all tax levels) for the transaction.
    """)

    tax1 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 1" for the transaction.
    """)

    tax2 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 2" for the transaction.
    """)

    tax3 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 3" for the transaction.
    """)

    tax4 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 4" for the transaction.
    """)

    tax5 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 5" for the transaction.
    """)

    tax6 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 6" for the transaction.
    """)

    tax7 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 7" for the transaction.
    """)

    cashback = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Total "cash back" amount for the transaction, if any.
    """)

    total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Total amount for the transaction, i.e. discounted subtotal plus tax.
    """)

    void = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag indicating if the transaction was voided.
    """)

    def __str__(self):
        system = enum.TRAINWRECK_SYSTEM.get(self.system, self.system or "Unknown")
        return "{} {}-{}".format(system, self.terminal_id or "?", self.receipt_number or "??")


@six.python_2_unicode_compatible
class TransactionItemBase(object):
    """
    Represents a line item within a transaction.
    """
    __tablename__ = 'transaction_item'

    @declared_attr
    def __table_args__(cls):
        return cls.__txnitem_table_args__()

    @classmethod
    def __txnitem_table_args__(cls):
        txn_table = cls.__txn_class__.__tablename__
        item_table = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['transaction_uuid'], ['{}.uuid'.format(txn_table)],
                                    name='{}_fk_transaction'.format(item_table)),
            sa.Index('{}_ix_transaction_uuid'.format(item_table), 'transaction_uuid'),
            sa.Index('{}_ix_item_id'.format(item_table), 'item_id'),
        )

    uuid = uuid_column()

    transaction_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def transaction(cls):
        txn_class = cls.__txn_class__
        item_class = cls
        txn_class.item_class = item_class

        # Must establish `Transaction.items` here instead of from within
        # Transaction itself, because the item class doesn't yet exist (really,
        # it can't even be "known") when Transaction is being created.
        txn_class.items = orm.relationship(
            item_class,
            order_by=lambda: item_class.sequence,
            collection_class=ordering_list('sequence', count_from=1),
            cascade='all, delete-orphan',
            doc="""
            Sequence of line items for the transaction.
            """,
            back_populates='transaction')

        # Now, here's the `TransactionItem.transaction` reference.
        return orm.relationship(txn_class, back_populates='items', doc="""
        Reference to the line item's parent transaction.
        """)

    sequence = sa.Column(sa.Integer(), nullable=False, doc="""
    Sequence number for this line item, within the parent transaction.
    """)

    item_type = sa.Column(sa.String(length=50), nullable=True, doc="""
    Type of line item this is, if relevant/known.  Value and interpretation
    thereof are not defined by the schema, but rather the (custom) app logic...
    """)

    item_scancode = sa.Column(sa.String(length=20), nullable=False, doc="""
    Scancode for the item, if applicable / known.
    """)

    item_id = sa.Column(sa.String(length=50), nullable=True, doc="""
    Item ID for the line item.  This is meant to be used to supplement the
    scancode, for systems where multiple items may have the same scancode.
    """)

    department_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Department number for the line item, if known.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Department name for the line item, if known.
    """)

    exempt_from_gross_sales = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether item should (not) contribute to gross sales
    figures.  The SIL book says this about it:

       Dollar sales are not to be included in gross sales. (i.e., Postage
       Stamps, Lottery Tickets, etc.).
    """)

    brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the line item, if known.
    """)

    description = sa.Column(sa.String(length=255), nullable=False, default="", doc="""
    Description for the line item; defaults to empty string.
    """)

    unit_price = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Effective unit price for the item, before discounts.
    """)

    unit_regular_price = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Regular unit price for the item, e.g. as opposed to effective price.
    """)

    unit_discounted_price = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Effective unit price for the item, after discounts.
    """)

    unit_quantity = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Unity quantity for the line item, i.e. how much of product is being sold.
    """)

    subtotal = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Subtotal for the line item, i.e. unit quantity times price, before discounts.
    """)

    discounted_subtotal = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Subtotal for the line item, i.e. quantity times unit price.
    """)

    gross_sales = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Gross sales amount for the line item.  Meaning of this may vary slightly?
    """)

    net_sales = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Net sales amount for the line item.  Meaning of this may vary slightly?
    """)

    tax = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Tax total (for all tax levels) for the line item.
    """)

    tax1 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 1" for the line item.
    """)

    tax2 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 2" for the line item.
    """)

    tax3 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 3" for the line item.
    """)

    tax4 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 4" for the line item.
    """)

    tax5 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 5" for the line item.
    """)

    tax6 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 6" for the line item.
    """)

    tax7 = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Total of "tax level 7" for the line item.
    """)

    total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Total amount for the line item, i.e. discounted subtotal plus tax.
    """)

    void = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag indicating if the line item was voided.
    """)

    error_correct = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag indicating if the line item was error-corrected.
    """)

    def __str__(self):
        return self.description

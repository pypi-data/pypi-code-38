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
Data Models for Customer Orders
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.orderinglist import ordering_list

from rattail.db.model import Base, uuid_column
from rattail.db.model import Customer, Person, Product, User


@six.python_2_unicode_compatible
class CustomerOrder(Base):
    """
    Represents an order placed by the customer.
    """
    __tablename__ = 'custorder'
    __table_args__ = (
        sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'], name='custorder_fk_customer'),
        sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='custorder_fk_person'),
    )

    uuid = uuid_column()

    id = sa.Column(sa.Integer(), doc="""
    Numeric, auto-increment ID for the order.
    """)

    customer_uuid = sa.Column(sa.String(length=32), nullable=True)

    customer = orm.relationship(Customer, doc="""
    Reference to the :class:`Customer` instance for whom the order exists.
    """)

    person_uuid = sa.Column(sa.String(length=32), nullable=True)

    person = orm.relationship(Person, doc="""
    Reference to the :class:`Person` instance for whom the order exists.
    """)

    created = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the order was first created.
    """)

    status_code = sa.Column(sa.Integer(), nullable=False)

    items = orm.relationship('CustomerOrderItem', back_populates='order',
                             collection_class=ordering_list('sequence', count_from=1), doc="""
    Sequence of :class:`CustomerOrderItem` instances which belong to the order.
    """)

    def __str__(self):
        if self.id:
            return "#{}".format(self.id)
        return "(pending)"


@six.python_2_unicode_compatible
class CustomerOrderItem(Base):
    """
    Represents a particular line item (product) within a customer order.
    """
    __tablename__ = 'custorder_item'
    __table_args__ = (
        sa.ForeignKeyConstraint(['order_uuid'], ['custorder.uuid'], name='custorder_item_fk_order'),
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='custorder_item_fk_product'),
    )

    uuid = uuid_column()

    order_uuid = sa.Column(sa.String(length=32), nullable=False)

    order = orm.relationship(CustomerOrder, back_populates='items', doc="""
    Reference to the :class:`CustomerOrder` instance to which the item belongs.
    """)

    sequence = sa.Column(sa.Integer(), nullable=False, doc="""
    Numeric sequence for the item, i.e. its "line number".  These values should
    obviously increment in sequence and be unique within the context of a
    single order.
    """)

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    product = orm.relationship(Product, doc="""
    Reference to the :class:`Product` instance for the item.
    """)

    product_brand = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the product being ordered.  This should be a cache of the
    relevant :attr:`Brand.name`.
    """)

    product_description = sa.Column(sa.String(length=60), nullable=True, doc="""
    Primary description for the product being ordered.  This should be a cache
    of :attr:`Product.description`.
    """)

    product_size = sa.Column(sa.String(length=30), nullable=True, doc="""
    Size of the product being ordered.  This should be a cache of
    :attr:`Product.size`.
    """)

    product_unit_of_measure = sa.Column(sa.String(length=4), nullable=False, doc="""
    Code indicating the unit of measure for the product.  This should be a
    cache of :attr:`Product.unit_of_measure`.
    """)

    department_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the department to which the product belongs.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the department to which the product belongs.
    """)

    case_quantity = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Case pack count for the product being ordered.  This should be a cache of
    :attr:`Product.case_pack`.
    """)

    cases_ordered = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were initially ordered.
    """)

    units_ordered = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were initially ordered.
    """)

    product_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Unit cost of the product being ordered.  This should be a cache of the
    relevant :attr:`rattail.db.model.ProductCost.unit_cost`.
    """)

    unit_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Unit price for the product being ordered.  This is the price which is
    quoted to the customer and/or charged to the customer, but for a unit only
    and *before* any discounts are applied.  It generally will be a cache of
    the relevant :attr:`ProductPrice.price`.
    """)

    discount_percent = sa.Column(sa.Numeric(precision=5, scale=3), nullable=False, default=0, doc="""
    Discount percentage which will be applied to the product's price as part of
    calculating the :attr:`total_price` for the item.
    """)

    total_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Full price (not including tax etc.) which the customer is asked to pay for the item.
    """)

    paid_amount = sa.Column(sa.Numeric(precision=8, scale=3), nullable=False, default=0, doc="""
    Amount which the customer has paid toward the :attr:`total_price` of theitem.
    """)

    payment_transaction_number = sa.Column(sa.String(length=8), nullable=True, doc="""
    Transaction number in which payment for the order was taken, if applicable.
    """)

    status_code = sa.Column(sa.Integer(), nullable=False)

    # TODO
    def __str__(self):
        return str(self.product)


class CustomerOrderItemEvent(Base):
    """
    An event in the life of a customer order item
    """
    __tablename__ = 'custorder_item_event'
    __table_args__ = (
        sa.ForeignKeyConstraint(['item_uuid'], ['custorder_item.uuid'], name='custorder_item_event_fk_item'),
        sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], name='custorder_item_event_fk_user'),
    )

    uuid = uuid_column()

    item_uuid = sa.Column(sa.String(length=32), nullable=False)

    item = orm.relationship(
        CustomerOrderItem,
        doc="""
        Reference to the :class:`CustomerOrder` instance to which the item belongs.
        """,
        backref=orm.backref(
            'events',
            order_by='CustomerOrderItemEvent.occurred'))

    type_code = sa.Column(sa.Integer, nullable=False)

    occurred = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the event occurred.
    """)

    user_uuid = sa.Column(sa.String(length=32), nullable=False)

    user = orm.relationship(
        User,
        doc="""
        User who was the "actor" for the event.
        """)

    note = sa.Column(sa.Text(), nullable=True, doc="""
    Optional note recorded for the event.
    """)

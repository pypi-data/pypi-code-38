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
Products API
"""

from __future__ import unicode_literals, absolute_import

import logging

from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound

from rattail import enum
from rattail.db import model


log = logging.getLogger(__name__)


def get_product_by_upc(session, upc, include_deleted=False):
    """
    Returns the :class:`rattail.Product` associated with ``upc`` (if found), or
    ``None``.
    """
    products = session.query(model.Product)
    if not include_deleted:
        products = products.filter(model.Product.deleted == False)
    try:
        return products.filter(model.Product.upc == upc).one()
    except NoResultFound:
        pass


def get_product_by_item_id(session, item_id, include_deleted=False):
    """
    Returns the :class:`rattail.Product` associated with ``item_id`` (if
    found), or ``None``.
    """
    products = session.query(model.Product)
    if not include_deleted:
        products = products.filter(model.Product.deleted == False)
    try:
        return products.filter(model.Product.item_id == item_id).one()
    except NoResultFound:
        pass


def get_product_by_code(session, code, include_deleted=False):
    """
    Locate a ``Product`` instance using a code value.

    :param session: An open SQLAlchemy session.

    :param code: Product code for which to search.
    :type code: string

    :returns: A :class:`rattail.db.model.Product` instance, or ``None``.

    .. note::
       This function will return the *first* product found, and does not warn
       if multiple products would have matched the search.
    """
    products = session.query(model.Product).join(model.ProductCode)
    if not include_deleted:
        products = products.filter(model.Product.deleted == False)
    return products.filter(model.ProductCode.code == code).first()


def get_product_by_vendor_code(session, code, vendor=None, include_deleted=False):
    """
    Locate a product using a vendor item code, optionally restricted to a
    particular vendor.

    :param session: A SQLAlchemy session.

    :param code: Vendor item code for which to search.
    :type code: string

    :param vendor: Optional vendor instance by which to filter the search.

    :returns: A :class:`rattail.db.model.Product` instance, or ``None``.

    .. note::
       This function will return the *first* product found, and does not warn
       if multiple products would have matched the search.
    """
    products = session.query(model.Product).join(model.ProductCost)
    if vendor:
        products = products.filter(model.ProductCost.vendor == vendor)
    if not include_deleted:
        products = products.filter(model.Product.deleted == False)
    return products.filter(model.ProductCost.code == code).first()


def set_regular_price(product, newprice, **kwargs):
    """
    Simple way to set the regular price for the product, using sane defaults.
    """
    regular = product.regular_price
    if newprice is None:
        if regular:
            product.regular_price = None
        return

    if regular and regular.price == newprice:
        return                  # nothing to do

    price = regular or model.ProductPrice()
    price.type = kwargs.get('type', enum.PRICE_TYPE_REGULAR)
    price.level = kwargs.get('level', 1)
    price.price = newprice
    price.multiple = kwargs.get('multiple', 1)
    price.starts = kwargs.get('starts', None)
    price.ends = kwargs.get('ends', None)
    if price is not regular:
        product.prices.append(price)
    product.regular_price = price
    return price


def set_current_sale_price(product, newprice, starts=None, ends=None, **kwargs):
    """
    Simple way to set the current sale price for the product, using sane
    defaults.  Note that this does not check to confirm that your date range
    encompasses "today".
    """
    current = product.current_price
    if newprice is None:
        if current:
            product.current_price = None
        return
        
    if (current and current.price == newprice
        and current.starts == starts and current.ends == ends):
        return                  # nothing to do

    price = current or model.ProductPrice()
    price.type = kwargs.get('type', enum.PRICE_TYPE_SALE)
    price.level = kwargs.get('level', 1)
    price.price = newprice
    price.multiple = kwargs.get('multiple', 1)
    price.starts = starts
    price.ends = ends
    if price is not current:
        product.prices.append(price)
    product.current_price = price
    return price


future_cost_fieldmap = {
    'order_code': 'code',
    'case_quantity': 'case_size',
    'case_cost': 'case_cost',
    'unit_cost': 'unit_cost',
    'starts': 'effective',
    'discontinued': 'discontinued',
}


def make_future_cost_current(config, future):
    """
    Take the given future cost, and make it current.
    """
    if not future.cost:
        raise NotImplementedError("don't know how to create costs yet")

    cost = future.cost

    if not future.product:
        raise ValueError("future cost does not have product association: {}".format(future))

    if not future.vendor:
        raise ValueError("future cost does not have vendor association: {}".format(future))

    if future.product is not cost.product:
        raise ValueError("product mismatch for future/current costs: {}".format(future))

    if future.vendor is not cost.vendor:
        raise ValueError("vendor mismatch for future/current costs: {}".format(future))

    for field in future_cost_fieldmap:
        setattr(cost, future_cost_fieldmap[field], getattr(future, field))

    session = orm.object_session(future)
    session.delete(future)
    log.debug("future cost became current: %s", cost)

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
Form Schema Types
"""

from __future__ import unicode_literals, absolute_import

import re
import datetime

import six

from rattail.db import model
from rattail.gpc import GPC

import colander

from tailbone.db import Session


class JQueryTime(colander.Time):
    """
    Custom type for jQuery widget Time data.
    """

    def deserialize(self, node, cstruct):
        if not cstruct:
            return colander.null

        formats = [
            '%I:%M %p',
            '%I:%M%p',
            '%I %p',
            '%I%p',
        ]
        for fmt in formats:
            try:
                return datetime.datetime.strptime(cstruct, fmt).time()
            except ValueError:
                pass

        # re-try first format, for "better" error message
        return datetime.datetime.strptime(cstruct, formats[0]).time()


class DateTimeBoolean(colander.Boolean):
    """
    Schema type which presents the user with a "boolean" whereas the underlying
    node is really a datetime (assumed to be "naive" UTC, and allow nulls).
    """

    def deserialize(self, node, cstruct):
        value = super(DateTimeBoolean, self).deserialize(node, cstruct)
        if value: # else return None
            return datetime.datetime.utcnow()


class GPCType(colander.SchemaType):
    """
    Schema type for product GPC data.
    """

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        return six.text_type(appstruct)

    def deserialize(self, node, cstruct):
        if not cstruct:
            return None
        digits = re.sub(r'\D', '', cstruct)
        if not digits:
            return None
        try:
            return GPC(digits)
        except Exception as err:
            raise colander.Invalid(node, six.text_type(err))


class ProductQuantity(colander.MappingSchema):
    """
    Combo schema type for product cases and units; useful for inventory,
    ordering, receiving etc.  Meant to be used with the ``CasesUnitsWidget``.
    """
    cases = colander.SchemaNode(colander.Decimal(), missing=colander.null)

    units = colander.SchemaNode(colander.Decimal(), missing=colander.null)


class ModelType(colander.SchemaType):
    """
    Custom schema type for scalar ORM relationship fields.
    """
    model_class = None
    session = None

    def __init__(self, model_class=None, session=None):
        if model_class:
            self.model_class = model_class
        if session:
            self.session = session
        else:
            self.session = self.make_session()

    def make_session(self):
        return Session()

    @property
    def model_title(self):
        self.model_class.get_model_title()

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        return six.text_type(appstruct)

    def deserialize(self, node, cstruct):
        if not cstruct:
            return None
        obj = self.session.query(self.model_class).get(cstruct)
        if not obj:
            raise colander.Invalid(node, "{} not found".format(self.model_title))
        return obj


# TODO: deprecate / remove this
ObjectType = ModelType


class StoreType(ModelType):
    """
    Custom schema type for store field.
    """
    model_class = model.Store


class CustomerType(ModelType):
    """
    Custom schema type for customer field.
    """
    model_class = model.Customer


class DepartmentType(ModelType):
    """
    Custom schema type for department field.
    """
    model_class = model.Department


class EmployeeType(ModelType):
    """
    Custom schema type for employee field.
    """
    model_class = model.Employee


class VendorType(ModelType):
    """
    Custom schema type for vendor relationship field.
    """
    model_class = model.Vendor


class ProductType(ModelType):
    """
    Custom schema type for product relationship field.
    """
    model_class = model.Product


class UserType(ModelType):
    """
    Custom schema type for user field.
    """
    model_class = model.User

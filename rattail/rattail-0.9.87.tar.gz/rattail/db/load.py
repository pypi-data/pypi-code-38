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
Load Data from Host
"""

from __future__ import unicode_literals

from sqlalchemy.orm import joinedload

from . import model
from . import Session


class LoadProcessor(object):

    def __init__(self, config):
        self.config = config

    def load_all_data(self, host_engine, progress=None):

        self.host_session = Session(bind=host_engine)
        self.session = Session()

        cancel = False
        for cls in self.relevant_classes():
            if not self.load_class_data(cls, progress):
                cancel = True
                break

        self.host_session.close()
        if cancel:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
        return not cancel

    def load_class_data(self, cls, progress=None):
        query = self.host_session.query(cls)
        if hasattr(self, 'query_%s' % cls.__name__):
            query = getattr(self, 'query_%s' % cls.__name__)(query)

        count = query.count()
        if not count:
            return True

        prog = None
        if progress:
            prog = progress("Loading %s data" % cls.__name__, count)

        cancel = False
        for i, instance in enumerate(query, 1):
            if hasattr(self, 'merge_%s' % cls.__name__):
                getattr(self, 'merge_%s' % cls.__name__)(instance)
            else:
                self.session.merge(instance)
            self.session.flush()
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()
        return not cancel

    def relevant_classes(self):
        yield model.Person
        yield model.User
        yield model.Store
        yield model.Department
        yield model.Subdepartment
        yield model.Category
        yield model.Brand
        yield model.Vendor
        yield model.Product
        yield model.CustomerGroup
        yield model.Customer
        yield model.Employee

        classes = self.config.get('rattail.db', 'load.extra_classes')
        if classes:
            for cls in classes.split():
                yield getattr(model, cls)

    def query_Customer(self, q):
        q = q.options(joinedload(model.Customer.phones))
        q = q.options(joinedload(model.Customer.emails))
        q = q.options(joinedload(model.Customer._people))
        q = q.options(joinedload(model.Customer._groups))
        return q

    def query_CustomerPerson(self, q):
        q = q.options(joinedload(model.CustomerPerson.person))
        return q

    def query_Employee(self, q):
        q = q.options(joinedload(model.Employee.phones))
        q = q.options(joinedload(model.Employee.emails))
        return q

    def query_Person(self, q):
        q = q.options(joinedload(model.Person.phones))
        q = q.options(joinedload(model.Person.emails))
        return q

    def query_Product(self, q):
        q = q.options(joinedload(model.Product.costs))
        q = q.options(joinedload(model.Product.prices))
        return q

    def merge_Product(self, host_product):
        # This logic is necessary due to the inter-dependency between Product
        # and ProductPrice tables.  merge() will cause a flush(); however it
        # apparently will not honor the 'post_update=True' flag on the relevant
        # relationships..  I'm unclear whether this is a "bug" with SQLAlchemy,
        # but the workaround is simple enough that I'm leaving it for now.
        product = self.session.merge(host_product)
        product.regular_price_uuid = None
        product.current_price_uuid = None
        if host_product.regular_price_uuid:
            product.regular_price = self.session.merge(host_product.regular_price)
        if host_product.current_price_uuid:
            product.current_price = self.session.merge(host_product.current_price)

    def query_Store(self, q):
        q = q.options(joinedload(model.Store.phones))
        q = q.options(joinedload(model.Store.emails))
        return q

    def query_Vendor(self, q):
        q = q.options(joinedload(model.Vendor._contacts))
        q = q.options(joinedload(model.Vendor.phones))
        q = q.options(joinedload(model.Vendor.emails))
        return q

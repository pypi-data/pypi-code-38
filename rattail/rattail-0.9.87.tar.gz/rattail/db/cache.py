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
Cache Helpers
"""

from __future__ import unicode_literals, absolute_import

import logging

import six
from sqlalchemy.orm import joinedload

from rattail.core import Object
from rattail.db import model


log = logging.getLogger(__name__)


class CacheKeyNotSupported(Exception):
    """
    Special error which a model cacher should raise when generating the cache
    key for a given record/object, but when it is discovered the object does
    not have sufficient data to generate the key.
    """


class ModelCacher(object):
    """
    Generic model data caching class.
    """

    def __init__(self, session, model_class, key='uuid',
                 query=None, order_by=None, query_options=None, normalizer=None,
                 expect_duplicates=False, omit_duplicates=False,
                 use_lists=False):
        self.session = session
        self.model_class = model_class
        self.key = key
        self.duplicate_keys = set()
        self.expect_duplicates = expect_duplicates
        self.omit_duplicates = omit_duplicates
        self._query = query
        self.order_by = order_by
        self.query_options = query_options
        if normalizer is None:
            self.normalize = lambda d: d
        else:
            self.normalize = normalizer
        self.use_lists = use_lists
    
    @property
    def model_name(self):
        return self.model_class.__name__

    def query(self):
        q = self._query or self.session.query(self.model_class)
        if self.order_by:
            q = q.order_by(self.order_by)
        if self.query_options:
            for option in self.query_options:
                q = q.options(option)
        return q

    def get_cache(self, progress):
        self.instances = {}
        query = self.query()
        count = query.count()
        if not count:
            return self.instances
        
        prog = None
        if progress:
            prog = progress("Caching {0} data".format(self.model_name), count)
        for i, instance in enumerate(query, 1):

            self.cache_instance(instance)

            if prog:
                prog.update(i)
        if prog:
            prog.destroy()

        if self.duplicate_keys:
            logger = log.debug if self.expect_duplicates else log.warning
            logger("found %s duplicated keys in cache for %s",
                   len(self.duplicate_keys), self.model_name)
            if self.omit_duplicates:
                for key in self.duplicate_keys:
                    log.debug("removing duplicated key from cache: {}".format(repr(key)))
                    del self.instances[key]

        return self.instances

    def get_key(self, instance, normalized):
        if callable(self.key):
            return self.key(instance, normalized)
        if isinstance(self.key, six.string_types):
            return getattr(instance, self.key)
        return tuple(getattr(instance, k) for k in self.key)

    def cache_instance(self, instance):
        normalized = self.normalize(instance)
        try:
            key = self.get_key(instance, normalized)
        except CacheKeyNotSupported:
            # this means the object doesn't belong in our cache
            return
        if self.use_lists:
            self.instances.setdefault(key, []).append(normalized)
        else:
            if key not in self.instances:
                self.instances[key] = normalized
            else:
                self.duplicate_keys.add(key)
                if not self.omit_duplicates:
                    log.debug("cache already contained key, but overwriting: {}".format(repr(key)))
                    self.instances[key] = normalized


def cache_model(session, model_class, key='uuid', progress=None, **kwargs):
    """
    Convenience function for fetching a cache of data for the given model.
    """
    cacher = ModelCacher(session, model_class, key, **kwargs)
    return cacher.get_cache(progress)


class DataCacher(Object):

    def __init__(self, session=None, **kwargs):
        super(DataCacher, self).__init__(session=session, **kwargs)

    @property
    def class_(self):
        raise NotImplementedError
    
    @property
    def name(self):
        return self.class_.__name__

    def query(self):
        return self.session.query(self.class_)

    def get_cache(self, progress):
        self.instances = {}

        query = self.query()
        count = query.count()
        if not count:
            return self.instances
        
        prog = None
        if progress:
            prog = progress("Caching {0} records".format(self.name), count)

        cancel = False
        for i, instance in enumerate(query, 1):
            self.cache_instance(instance)
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()

        if cancel:
            session.close()
            return None
        return self.instances


class DepartmentCacher(DataCacher):

    class_ = model.Department

    def cache_instance(self, dept):
        self.instances[dept.number] = dept


class SubdepartmentCacher(DataCacher):

    class_ = model.Subdepartment

    def cache_instance(self, subdept):
        self.instances[subdept.number] = subdept


class CategoryCacher(DataCacher):
    class_ = model.Category

    def cache_instance(self, category):
        self.instances[category.code] = category


def cache_categories(session, progress=None):
    """
    Return a dictionary of all :class:`rattail.db.model.Category` instances,
    keyed by :attr:`number`.
    """
    cacher = CategoryCacher(session=session)
    return cacher.get_cache(progress)


class FamilyCacher(DataCacher):

    class_ = model.Family

    def cache_instance(self, family):
        self.instances[family.code] = family


class ReportCodeCacher(DataCacher):

    class_ = model.ReportCode

    def cache_instance(self, report_code):
        self.instances[report_code.code] = report_code


class BrandCacher(DataCacher):

    class_ = model.Brand

    def cache_instance(self, brand):
        self.instances[brand.name] = brand


class VendorCacher(DataCacher):

    class_ = model.Vendor

    def cache_instance(self, vend):
        self.instances[vend.id] = vend


class ProductCacher(DataCacher):

    class_ = model.Product
    with_costs = False

    def query(self):
        q = self.session.query(model.Product)
        if self.with_costs:
            q = q.options(joinedload(model.Product.costs))
            q = q.options(joinedload(model.Product.cost))
        return q

    def cache_instance(self, prod):
        self.instances[prod.upc] = prod


def get_product_cache(session, with_costs=False, progress=None):
    """
    Cache the full product set by UPC.

    Returns a dictionary of all existing products, keyed by
    :attr:`rattail.Product.upc`.
    """

    cacher = ProductCacher(session=session, with_costs=with_costs)
    return cacher.get_cache(progress)


class CustomerGroupCacher(DataCacher):

    class_ = model.CustomerGroup

    def cache_instance(self, group):
        self.instances[group.id] = group


class CustomerCacher(DataCacher):

    class_ = model.Customer

    def cache_instance(self, customer):
        self.instances[customer.id] = customer

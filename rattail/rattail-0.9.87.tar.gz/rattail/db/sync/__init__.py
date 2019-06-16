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
Database Synchronization
"""

from __future__ import unicode_literals, absolute_import

import sys
import time
import logging

if sys.platform == 'win32': # pragma no cover
    import win32api

import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker, class_mapper
from sqlalchemy.exc import OperationalError

from rattail.db import model
from rattail.db.util import get_engines
from rattail.util import load_object


log = logging.getLogger(__name__)


def get_sync_engines(config):
    """
    Fetch the database engines to which data should be synchronized.
    """
    keys = config.get('rattail.db', 'syncs')
    if not keys:
        return None

    engines = get_engines(config)
    sync_engines = {}
    for key in keys.split(','):
        key = key.strip()
        sync_engines[key] = engines[key]
    log.debug("get_sync_engines: found engine keys: {0}".format(','.join(sync_engines.keys())))
    return sync_engines


class Synchronizer(object):
    """
    Default implementation of database synchronization logic.  Subclass this if
    you have special processing needs.
    """

    # This defines the `model` module which will be used to obtain references
    # to model classes (`Product` etc.).  If you need to synchronize custom
    # model classes of which Rattail is not aware, you must override this.
    # Note that the module you specify must be a superset of Rattail.
    model = model

    def __init__(self, local_engine, remote_engines):
        self.Session = sessionmaker()
        self.local_engine = local_engine
        self.remote_engines = remote_engines

    def loop(self):
        log.info("using remote engines: %s",
                 ', '.join(self.remote_engines.keys()))
        while True:
            try:
                self.synchronize()
            except OperationalError as error:
                if error.connection_invalidated:
                    # Presumably a database server restart; give it a moment
                    # and try again.
                    self.sleep(5)
                else:
                    raise
            self.sleep(3)

    def sleep(self, seconds): # pragma no cover
        if sys.platform == 'win32':
            win32api.Sleep(seconds * 1000)
        else:
            time.sleep(seconds)

    def synchronize(self):
        local_session = self.Session(bind=self.local_engine)
        local_changes = local_session.query(model.Change).all()
        if len(local_changes):
            log.debug("Synchronizer.synchronize: found {0} change(s) to synchronize".format(len(local_changes)))

            remote_sessions = {}
            for key, remote_engine in self.remote_engines.items():
                remote_sessions[key] = self.Session(bind=remote_engine)

            self.synchronize_changes(local_changes, local_session, remote_sessions)

            for remote_session in remote_sessions.values():
                remote_session.commit()
                remote_session.close()
            local_session.commit()

            log.debug("Synchronizer.synchronize: synchronization complete")
        local_session.close()

    def synchronize_changes(self, local_changes, local_session, remote_sessions):

        # First we must determine which types of instances are in need of
        # syncing.  The order will matter because of class dependencies.
        # However the dependency_sort() call doesn't *quite* take care of
        # everything - notably the Product/ProductPrice situation.  Since those
        # classes are mutually dependent, we start with a hackish lexical sort
        # and hope for the best...
        class_names = sorted(set([x.class_name for x in local_changes]))
        class_names.sort(cmp=self.dependency_sort)

        for class_name in class_names:
            klass = getattr(self.model, class_name)

            for change in [x for x in local_changes if x.class_name == class_name]:
                log.debug("Synchronizer.synchronize_changes: processing change: {0}".format(repr(change)))

                if change.deleted:
                    for remote_session in remote_sessions.values():
                        remote_instance = remote_session.query(klass).get(change.uuid)
                        if remote_instance:
                            self.delete_instance(remote_session, remote_instance)
                            remote_session.flush()

                else: # new/dirty
                    local_instance = local_session.query(klass).get(change.uuid)
                    if local_instance:
                        for remote_session in remote_sessions.values():
                            self.merge_instance(remote_session, local_instance)
                            remote_session.flush()

                local_session.delete(change)
                local_session.flush()

    def dependency_sort(self, x, y):
        map_x = class_mapper(getattr(self.model, x))
        map_y = class_mapper(getattr(self.model, y))

        dep_x = []
        table_y = map_y.tables[0].name
        for column in map_x.columns:
            for key in column.foreign_keys:
                if key.column.table.name == table_y:
                    return 1
                dep_x.append(key)

        dep_y = []
        table_x = map_x.tables[0].name
        for column in map_y.columns:
            for key in column.foreign_keys:
                if key.column.table.name == table_x:
                    return -1
                dep_y.append(key)

        if dep_x and not dep_y:
            return 1
        if dep_y and not dep_x:
            return -1
        return 0

    def merge_instance(self, session, instance):
        """
        Merge ``instance`` into ``session``.

        This method checks for other "special" methods based on the class of
        ``instance``.  If such a method is found, it is invoked; otherwise a
        simple merge is done.
        """

        cls = instance.__class__.__name__
        if hasattr(self, 'merge_%s' % cls):
            return getattr(self, 'merge_%s' % cls)(session, instance)

        return session.merge(instance)

    def merge_Product(self, session, source_product):
        """
        This method is somewhat of a hack, in order to properly handle
        :class:`rattail.db.model.Product` instances and the interdependent
        nature of the related :class:`rattail.db.model.ProductPrice` instances.
        """

        target_product = session.merge(source_product)

        # I'm not 100% sure I understand this correctly, but here's my
        # thinking: First we clear the price relationships in case they've
        # actually gone away; then we re-establish any which are currently
        # valid.

        # Setting the price relationship attributes to ``None`` isn't enough to
        # force the ORM to notice a change, since the UUID field is ultimately
        # what it's watching.  So we must explicitly use that field here.
        target_product.regular_price_uuid = None
        target_product.current_price_uuid = None

        # If the source instance has currently valid price relationships, then
        # we re-establish them.  We must merge the source price instance in
        # order to be certain it will exist in the target session, and avoid
        # foreign key errors.  However we *still* must also set the UUID fields
        # because again, the ORM is watching those...  This was noticed to be
        # the source of some bugs where successive database syncs were
        # effectively "toggling" the price relationship.  Setting the UUID
        # field explicitly seems to solve it.
        if source_product.regular_price_uuid:
            target_product.regular_price = session.merge(source_product.regular_price)
            target_product.regular_price_uuid = target_product.regular_price.uuid
        if source_product.current_price_uuid:
            target_product.current_price = session.merge(source_product.current_price)
            target_product.current_price_uuid = target_product.current_price.uuid

        return target_product

    def delete_instance(self, session, instance):
        """
        Delete ``instance`` using ``session``.

        This method checks for other "special" methods based on the class of
        ``instance``.  If such a method is found, it is invoked before the
        instance is officially deleted from ``session``.
        """

        cls = instance.__class__.__name__
        if hasattr(self, 'delete_%s' % cls):
            getattr(self, 'delete_%s' % cls)(session, instance)

        session.delete(instance)

    def delete_Department(self, session, department):

        # Remove association from Subdepartment records.
        q = session.query(model.Subdepartment)
        q = q.filter(model.Subdepartment.department == department)
        for subdepartment in q:
            subdepartment.department = None

        # Remove association from Product records.
        q = session.query(model.Product)
        q = q.filter(model.Product.department == department)
        for product in q:
            product.department = None

    def delete_Subdepartment(self, session, subdepartment):

        # Remove association from Product records.
        q = session.query(model.Product)
        q = q.filter(model.Product.subdepartment == subdepartment)
        for product in q:
            product.subdepartment = None

    def delete_Family(self, session, family):

        # Remove Product associations.
        products = session.query(model.Product)\
            .filter(model.Product.family == family)
        for product in products:
            product.family = None

    def delete_Vendor(self, session, vendor):

        # Remove associated ProductCost records.
        q = session.query(model.ProductCost)
        q = q.filter(model.ProductCost.vendor == vendor)
        for cost in q:
            session.delete(cost)

    def delete_CustomerGroup(self, session, group):
        # First remove customer associations.
        q = session.query(model.CustomerGroupAssignment)\
            .filter(model.CustomerGroupAssignment.group == group)
        for assignment in q:
            session.delete(assignment)


def synchronize_changes(config, local_engine, remote_engines):
    """
    This function will instantiate a ``Synchronizer`` class according to
    configuration.  (The default class is :class:`Synchronizer`.)  This
    instance is then responsible for implementing the sync logic.

    .. highlight:: ini

    If you need to override the default synchronizer class, put something like
    the following in your config file::

       [rattail.db]
       sync.synchronizer_class = myapp.sync:MySynchronizer
    """

    factory = config.get('rattail.db', 'sync.synchronizer_class')
    if factory:
        log.debug("synchronize_changes: using custom synchronizer factory: {0}".format(repr(factory)))
        factory = load_object(factory)
    else:
        log.debug("synchronize_changes: using default synchronizer factory")
        factory = Synchronizer

    synchronizer = factory(local_engine, remote_engines)
    synchronizer.loop()

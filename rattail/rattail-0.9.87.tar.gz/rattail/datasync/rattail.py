# -*- coding: utf-8; -*-
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
DataSync for Rattail
"""

from __future__ import unicode_literals, absolute_import

import logging

from sqlalchemy import orm

from rattail.db import Session, model
from rattail.db.util import make_topo_sortkey
from rattail.datasync import DataSyncWatcher, DataSyncConsumer, NewDataSyncImportConsumer
from rattail.config import parse_list


log = logging.getLogger(__name__)


class RattailWatcher(DataSyncWatcher):
    """
    DataSync watcher for Rattail databases.
    """
    prunes_changes = True

    def __init__(self, *args, **kwargs):
        super(RattailWatcher, self).__init__(*args, **kwargs)
        self.engine = self.config.rattail_engines[self.dbkey]

    def get_changes(self, lastrun):
        """
        Checks the :class:`rattail.db.model:Change` table in a Rattail
        database, to see if there are any pending changes for the datasync
        daemon.
        """
        session = Session(bind=self.engine)
        changes = session.query(model.Change).all()
        session.expunge_all()
        session.close()
        if changes:
            return [
                (c.uuid, 
                 model.DataSyncChange(
                     payload_type=c.class_name,
                     payload_key=c.instance_uuid,
                     deletion=c.deleted))
                for c in changes]

    def prune_changes(self, keys):
        deleted = 0
        session = Session(bind=self.engine)
        for key in keys:
            change = session.query(model.Change).get(key)
            if change:
                session.delete(change)
                session.flush()
                deleted += 1
        session.commit()
        session.close()
        return deleted


class RattailConsumer(DataSyncConsumer):
    """
    DataSync consumer for Rattail databases.
    """
    # Set this to a sequence of model names if you wish to *consume* data
    # *only* for those models (and ignore all others).
    consume_models = None

    # Set this to a sequence of model names if you wish to *ignore* data *only*
    # for those models (and consume all others).
    ignore_models = None

    def __init__(self, *args, **kwargs):
        super(RattailConsumer, self).__init__(*args, **kwargs)
        self.engine = self.config.rattail_engines[self.dbkey]
        self.model = self.get_data_model()
        self.topo_sortkey = make_topo_sortkey(self.model)

    def get_data_model(self):
        """
        Subclasses may override this if they have extended the schema.
        Defaults to ``rattail.db.model``.
        """
        return model

    def process_changes(self, host_session, changes):
        """
        Process changes for a Rattail database.
        """
        # First determine which models are represented in the change set.  Some
        # models may be ignored, depending on the subclass logic etc.
        class_names = set([c.payload_type for c in changes])
        if self.consume_models is not None:
            class_names = [c for c in class_names if c in self.consume_models]
        elif self.ignore_models is not None:
            class_names = [c for c in class_names if c not in self.ignore_models]

        # The order will matter because of table foreign key dependencies.  We
        # start with a lexical sort just for kicks maybe...
        class_names = sorted(class_names)
        class_names.sort(key=self.topo_sortkey)

        session = Session(bind=self.engine)
        if self.runas_username:
            session.set_continuum_user(self.runas_username)

        for class_name in class_names:
            cls = getattr(self.model, class_name)

            for change in [c for c in changes if c.payload_type == class_name]:
                log.debug("processing {0} for {1} {2}".format(
                    "deletion" if change.deletion else "change",
                    change.payload_type, change.payload_key))

                if change.deletion:
                    instance = session.query(cls).get(change.payload_key)
                    if instance:
                        self.delete_instance(session, instance)
                        session.flush()
                    else:
                        log.warning("could not find instance to delete")

                else: # add/update
                    host_instance = host_session.query(cls).get(change.payload_key)
                    if host_instance:

                        # if processing a pack item, must process its unit item
                        # first.  this is because both may be "new" in which
                        # case the unit item must exist before the pack may
                        # reference it.
                        if class_name == 'Product' and host_instance.is_pack_item():
                            self.merge_instance(session, host_instance.unit)

                        self.merge_instance(session, host_instance)
                        session.flush()
                    else:
                        log.warning("could not find host instance to merge")

        session.commit()
        session.close()

    def merge_instance(self, session, instance):
        """
        Merge the given model instance into the given database session.

        Subclasses may define model-specific methods instead of or in addition
        to overriding this generic one.
        """
        class_name = instance.__class__.__name__.lower()
        merger = getattr(self, 'merge_{0}'.format(class_name), None)
        if merger:
            return merger(session, instance)

        # Nothing special defined, so just do the normal thing.
        return session.merge(instance)

    def delete_instance(self, session, instance):
        """
        Delete the given model instance from the given database session.

        Subclasses may define model-specific methods instead of or in addition
        to overriding this generic one.
        """
        class_name = instance.__class__.__name__.lower()

        deleter = getattr(self, 'delete_{0}'.format(class_name), None)
        if deleter:
            return deleter(session, instance)

        predeleter = getattr(self, 'predelete_{0}'.format(class_name), None)
        if predeleter:
            predeleter(session, instance)

        session.delete(instance)

    def merge_product(self, session, source_product):
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
        target_product.suggested_price_uuid = None

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
        if source_product.suggested_price_uuid:
            target_product.suggested_price = session.merge(source_product.suggested_price)
            target_product.suggested_price_uuid = target_product.suggested_price.uuid

        return target_product

    def predelete_department(self, session, department):

        # Disconnect from all subdepartments.
        q = session.query(model.Subdepartment).filter(
            model.Subdepartment.department == department)
        for subdept in q:
            subdept.department = None

        # Disconnect from all products.
        q = session.query(model.Product).filter(
            model.Product.department == department)
        for product in q:
            product.department = None

    def predelete_subdepartment(self, session, subdepartment):

        # Disconnect from all products.
        q = session.query(model.Product).filter(
            model.Product.subdepartment == subdepartment)
        for product in q:
            product.subdepartment = None

    def predelete_family(self, session, family):

        # Disconnect from all products.
        q = session.query(model.Product).filter(
            model.Product.family == family)
        for product in q:
            product.family = None

    def predelete_vendor(self, session, vendor):

        # Remove all product costs.
        q = session.query(model.ProductCost).filter(
            model.ProductCost.vendor == vendor)
        for cost in q:
            session.delete(cost)

    def predelete_customergroup(self, session, group):

        # Disconnect from all customers.
        q = session.query(model.CustomerGroupAssignment).filter(
            model.CustomerGroupAssignment.group == group)
        for assignment in q:
            session.delete(assignment)


class FromRattailToRattailExportConsumer(NewDataSyncImportConsumer):
    """
    Export data changes from "local" Rattail to another
    """
    handler_spec = None

    def __init__(self, *args, **kwargs):
        super(FromRattailToRattailExportConsumer, self).__init__(*args, **kwargs)
        self.target_engine = self.config.rattail_engines[self.dbkey]
        self.model = self.config.get_model()

    def setup(self):
        super(FromRattailToRattailExportConsumer, self).setup()
        self.topo_sortkey = make_topo_sortkey(self.model)

    def process_changes(self, session, changes):
        target_session = Session(bind=self.target_engine)

        if self.runas_username:
            target_session.set_continuum_user(self.runas_username)

        # update all importers with current sessions
        for importer in self.importers.values():
            importer.host_session = session
            importer.session = target_session

        # topographically sort changes, i.e. per schema table dependencies.
        # we start with a lexical sort just for kicks maybe...
        class_names = set([c.payload_type for c in changes])
        class_names = sorted(class_names)
        class_names.sort(key=self.topo_sortkey)

        for class_name in class_names:
            cls = getattr(self.model, class_name)
            for change in [c for c in changes if c.payload_type == class_name]:
                self.invoke_importer(session, change)

        target_session.commit()
        target_session.close()

    def get_host_object(self, session, change):
        cls = getattr(self.model, change.payload_type)
        return session.query(cls).get(change.payload_key)


class FromRattailToRattailImportConsumer(NewDataSyncImportConsumer):
    """
    Import data changes from another Rattail to "local"
    """
    handler_spec = None

    def __init__(self, *args, **kwargs):
        super(FromRattailToRattailImportConsumer, self).__init__(*args, **kwargs)
        self.host_engine = self.config.rattail_engines[self.watcher.dbkey]
        self.local_engine = self.config.rattail_engines[self.dbkey]
        self.model = self.config.get_model()

    def setup(self):
        super(FromRattailToRattailImportConsumer, self).setup()
        self.topo_sortkey = make_topo_sortkey(self.model)

    def process_changes(self, session, changes):
        self.host_session = Session(bind=self.host_engine)
        local_session = Session(bind=self.local_engine)
        if self.runas_username:
            local_session.set_continuum_user(self.runas_username)

        # update all importers with current sessions
        for importer in self.importers.values():
            importer.host_session = self.host_session
            importer.session = local_session

        # topographically sort changes, i.e. per schema table dependencies.
        # we start with a lexical sort just for kicks maybe...
        class_names = set([c.payload_type for c in changes])
        class_names = sorted(class_names)
        class_names.sort(key=self.topo_sortkey)

        for class_name in class_names:
            cls = getattr(self.model, class_name)
            for change in [c for c in changes if c.payload_type == class_name]:
                self.invoke_importer(session, change)

        local_session.commit()
        local_session.close()
        # TODO: should we ever commit this..?
        # self.host_session.commit()
        self.host_session.close()

    def get_host_object(self, session, change):
        cls = getattr(self.model, change.payload_type)
        return self.host_session.query(cls).get(change.payload_key)

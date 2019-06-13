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
Data Importers for SQLAlchemy
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound

from rattail.importing import Importer, FromQuery


class FromSQLAlchemy(FromQuery):
    """
    Base class for importers whose external data source is a SQLAlchemy query.
    """
    host_session = None

    # For default behavior, set this to a model class to be used in generating
    # the host data query.
    host_model_class = None

    def query(self):
        """
        Must return the primary query which will define the data set.  Default
        behavior is to leverage :attr:`host_session` and generate a query for
        the class defined by :attr:`host_model_class`.
        """
        return self.host_session.query(self.host_model_class)


class ToSQLAlchemy(Importer):
    """
    Base class for all data importers which support the common use case of
    targeting a SQLAlchemy ORM on the local side.  This is the base class for
    all primary Rattail importers.
    """
    caches_local_data = True

    @property
    def model_mapper(self):
        """
        Reference to the effective SQLAlchemy mapper for the local model class.
        """
        return orm.class_mapper(self.model_class)

    @property
    def model_table(self):
        """
        Reference to the effective SQLAlchemy table for the local model class.
        """
        tables = self.model_mapper.tables
        assert len(tables) == 1
        return tables[0]

    @property
    def simple_fields(self):
        """
        Returns the list of column names on the underlying local model mapper.
        """
        return list(self.model_mapper.columns.keys())

    @property
    def supported_fields(self):
        """
        All/only simple fields are supported by default.
        """
        return self.simple_fields

    def get_single_local_object(self, key):
        """
        Try to fetch the object from the local database, using SA ORM.
        """
        query = self.cache_query()
        for i, k in enumerate(self.key):
            query = query.filter(getattr(self.model_class, k) == key[i])
        try:
            return query.one()
        except NoResultFound:
            pass

    def create_object(self, key, host_data):
        """
        Create and return a new local object for the given key, fully populated
        from the given host data.  This may return ``None`` if no object is
        created.

        Note that this also adds the new object to the local database session.
        """
        with self.session.no_autoflush:
            obj = super(ToSQLAlchemy, self).create_object(key, host_data)
        if obj:
            self.session.add(obj)
            return obj

    def delete_object(self, obj):
        """
        Delete the given object from the local system (or not), and return a
        boolean indicating whether deletion was successful.  Default logic will
        truly delete and expunge the local object from the session.
        """
        self.session.delete(obj)
        return True

    def cache_local_data(self, host_data=None):
        """
        Cache all local objects and data using SA ORM.
        """
        return self.cache_model(self.model_class, key=self.get_cache_key,
                                query=self.cache_query(),
                                # omit_duplicates=True,
                                query_options=self.cache_query_options(),
                                normalizer=self.normalize_cache_object)

    def cache_query(self):
        """
        Return the query to be used when caching "local" data.
        """
        return self.session.query(self.model_class)

    def cache_query_options(self):
        """
        Return a list of options to apply to the cache query, if needed.
        """
        return []

    def flush_create_update(self):
        """
        Flush the database session, to send SQL to the server for all changes
        made thus far.
        """
        self.session.flush()

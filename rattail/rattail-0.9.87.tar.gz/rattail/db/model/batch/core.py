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
Core batch data models

Actually the classes in this module are not true models but rather are mixins,
which provide the common columns etc. for batch tables.
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import shutil

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

from rattail.db.core import uuid_column, filename_column
from rattail.db.types import GPCType
from rattail.db.model import User, Product
from rattail.time import make_utc


@six.python_2_unicode_compatible
class BatchMixin(object):
    """
    Mixin for all (new-style) batch classes.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__()

    @classmethod
    def __batch_table_args__(cls):
        return (
            sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'],
                                    name='{0}_fk_created_by'.format(cls.__tablename__)),
            sa.ForeignKeyConstraint(['cognized_by_uuid'], ['user.uuid'],
                                    name='{0}_fk_cognized_by'.format(cls.__tablename__)), 
            sa.ForeignKeyConstraint(['executed_by_uuid'], ['user.uuid'],
                                    name='{0}_fk_executed_by'.format(cls.__tablename__)),
        )

    @classmethod
    def __default_table_args__(cls):
        return cls.__batch_table_args__()

    @declared_attr
    def batch_key(cls):
        return cls.__tablename__

    uuid = uuid_column()

    id = sa.Column(sa.Integer(), sa.Sequence('batch_id_seq'), nullable=False, doc="""
    Numeric ID for the batch, unique across all "new-style" batches within the
    Rattail database.
    """)

    description = sa.Column(sa.String(length=255), nullable=True, doc="""
    Basic (loosely identifying) description for the batch.
    """)

    created = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the batch was first created.
    """)

    created_by_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def created_by(cls):
        return orm.relationship(
            User,
            primaryjoin=lambda: User.uuid == cls.created_by_uuid,
            foreign_keys=lambda: [cls.created_by_uuid],
            doc="""
            Reference to the :class:`User` who first created the batch.
            """)

    cognized = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the batch data was last cognized.
    """)

    cognized_by_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def cognized_by(cls):
        return orm.relationship(
            User,
            primaryjoin=lambda: User.uuid == cls.cognized_by_uuid,
            foreign_keys=lambda: [cls.cognized_by_uuid],
            doc="""
            Reference to the :class:`User` who last cognized the batch data.
            """)

    rowcount = sa.Column(sa.Integer(), nullable=True, doc="""
    Cached row count for the batch.  No guarantees perhaps, but should be accurate.
    """)

    complete = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag to indicate whether the batch is complete.  This may be used to assist
    with workflow when entering/executing new batches.
    """)

    executed = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the batch was (last) executed.
    """)

    executed_by_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def executed_by(cls):
        return orm.relationship(
            User,
            primaryjoin=lambda: User.uuid == cls.executed_by_uuid,
            foreign_keys=lambda: [cls.executed_by_uuid],
            doc="""
            Reference to the :class:`User` who (last) executed the batch.
            """)

    purge = sa.Column(sa.Date(), nullable=True, doc="""
    Date after which the batch may be purged.
    """)

    notes = sa.Column(sa.Text(), nullable=True, doc="""
    Any arbitrary notes for the batch.
    """)

    extra_data = sa.Column(sa.Text(), nullable=True, doc="""
    Extra field for arbitrary data, useful to the batch handler etc.  Note that
    there is *no* structure assumed here, it can be JSON or whatever is needed.
    """)

    STATUS_OK                   = 1
    STATUS_QUESTIONABLE         = 2

    STATUS = {
        STATUS_OK:              "ok",
        STATUS_QUESTIONABLE:    "questionable",
    }

    status_code = sa.Column(sa.Integer(), nullable=True, doc="""
    Status code for the batch as a whole.  This indicates whether the batch is
    "okay" and ready to execute, or (why) not etc.
    """)

    status_text = sa.Column(sa.String(length=255), nullable=True, doc="""
    Text which may briefly explain the batch status code, if needed.
    """)

    def __repr__(self):
        return "{}(uuid={})".format(
            self.__class__.__name__,
            repr(self.uuid))

    @property
    def id_str(self):
        if self.id:
            return "{:08d}".format(self.id)
        return ''

    def __str__(self):
        return "{} {}".format(
            self.__class__.__name__,
            self.id_str if self.id else "(new)")

    # TODO: deprecate/remove this?
    def add_row(self, row):
        """
        Convenience method for appending a data row, with auto-sequence.
        """
        self.data_rows.append(row)

    def active_rows(self):
        return [row for row in self.data_rows if not row.removed]

    def relative_filedir(self, config):
        """
        Returns the path for batch data file storage, relative to the root
        folder for all batch storage.  This includes the batch key as the first
        segment, e.g. ``'labels/d4/83d6f2aeb011e6afeb3ca9f40bc550'``.
        """
        if not self.uuid:
            orm.object_session(self).flush()
        return os.path.join(self.batch_key, self.uuid[:2], self.uuid[2:])

    # TODO: deprecate / remove this (?)
    relative_filepath = relative_filedir

    def filedir(self, config):
        """
        Returns the absolute path to the folder in which the data file resides.
        The config object determines the root path for such files, e.g.:

        .. code-block:: ini

           [rattail]
           batch.files = /path/to/batch/files

        Within this root path, a more complete path is generated using the
        :attr:`BatchMixin.key` and the :attr:`BatchMixin.uuid` values.
        """
        batchdir = config.batch_filedir()
        return os.path.abspath(os.path.join(batchdir, self.relative_filedir(config)))

    def absolute_filepath(self, config, filename=None, name_attr='filename'):
        """
        Return the absolute path where the data file resides.  This is the path
        returned by :meth:`filedir()` with the batch filename joined to it.
        """
        if filename is None:
            filename = getattr(self, name_attr)
        return os.path.join(self.filedir(config), filename)

    # for convenience
    filepath = absolute_filepath

    def filesize(self, config, name_attr='filename'):
        """
        Returns the size of the data file in bytes.
        """
        path = self.filepath(config, name_attr=name_attr)
        return os.path.getsize(path)

    def delete_data(self, config):
        """
        Delete the data folder for the batch
        """
        # TODO: should this logic be in the handler instead?
        path = config.batch_filepath(self.batch_key, self.uuid)
        if os.path.exists(path):
            shutil.rmtree(path)


class BaseFileBatchMixin(BatchMixin):
    """
    Common mixin for all batches which may involve a data file, either as
    initial data, or perhaps as "export" etc.
    """
    filename_nullable = True

    @declared_attr
    def filename(cls):
        return filename_column(nullable=cls.filename_nullable, doc="""
        Base name of the data file.
        """)


class FileBatchMixin(BaseFileBatchMixin):
    """
    Mixin for all (new-style) batch classes which involve a file upload as
    their first step.
    """
    filename_nullable = False

    def write_file(self, config, contents):
        """
        Save a data file for the batch to the location specified by
        :meth:`filepath()`.
        """
        filedir = self.filedir(config)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        with open(os.path.join(filedir, self.filename), 'wb') as f:
            f.write(contents)


class BatchRowMixin(object):
    """
    Mixin for all (new-style) batch row classes.
    """

    uuid = uuid_column()

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__()

    @classmethod
    def __batchrow_table_args__(cls):
        batch_table = cls.__batch_class__.__tablename__
        row_table = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['batch_uuid'], ['{0}.uuid'.format(batch_table)],
                                    name='{0}_fk_batch_uuid'.format(row_table)),
        )

    @classmethod
    def __default_table_args__(cls):
        return cls.__batchrow_table_args__()

    STATUS = {}

    batch_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def batch(cls):
        batch_class = cls.__batch_class__
        row_class = cls
        batch_class.row_class = row_class

        # Must establish `Batch.data_rows` here instead of from within `Batch`
        # itself, because the row class doesn't yet exist when that happens.
        batch_class.data_rows = orm.relationship(
            row_class,
            order_by=lambda: row_class.sequence,
            collection_class=ordering_list('sequence', count_from=1),
            cascade='all, delete-orphan',
            doc="""
            Collection of data rows for the batch.

            .. note::
               I would prefer for this attribute to simply be named "rows"
               instead of "data_rows", but unfortunately (as of this writing)
               "rows" is essentially a reserved word in FormAlchemy.
            """,
            back_populates='batch')

        # Now, here's the `BatchRow.batch` reference.
        return relationship(batch_class, back_populates='data_rows', doc="""
        Reference to the parent batch to which the row belongs.
        """)

    sequence = sa.Column(sa.Integer(), nullable=False, doc="""
    Sequence number of the row within the batch.  This number should be from 1 to
    the actual number of rows in the batch.
    """)

    status_code = sa.Column(sa.Integer(), nullable=True, doc="""
    Status code for the data row.  This indicates whether the row's product could
    be found in the system, etc.  Ultimately the meaning of this is defined by each
    particular batch type.
    """)

    status_text = sa.Column(sa.String(length=255), nullable=True, doc="""
    Short description of row status.  Ultimately the meaning and use of this is
    defined by each particular batch type.
    """)

    modified = sa.Column(sa.DateTime(), nullable=True, default=make_utc, onupdate=make_utc, doc="""
    Last modification time of the row.  This should be automatically set when
    the row is first created, as well as anytime it's updated thereafter.
    """)

    removed = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag to indicate a row has been removed from the batch.
    """)


class ProductBatchRowMixin(BatchRowMixin):
    """
    Mixin for all row classes of (new-style) batches which pertain to products.
    """

    @classmethod
    def __default_table_args__(cls):
        batch_table = cls.__batch_class__.__tablename__
        row_table = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['batch_uuid'], ['{0}.uuid'.format(batch_table)],
                                    name='{0}_fk_batch'.format(row_table)),
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name='{0}_fk_product'.format(row_table)),
            )

    item_entry = sa.Column(sa.String(length=20), nullable=True, doc="""
    Raw entry value, as obtained from the initial data source, and which is
    used to locate the product within the system.  This raw value is preserved
    in case the initial lookup fails and a refresh must attempt further
    lookup(s) later.  Only used by certain batch handlers in practice.
    """)

    upc = sa.Column(GPCType(), nullable=True, doc="""
    UPC for the product associated with the row.
    """)

    item_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Generic ID string for the product associated with the row.
    """)

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def product(self):
        table_name = self.__batch_class__.__tablename__
        model_title = self.__batch_class__.get_model_title()
        return orm.relationship(
            Product,
            doc="""
            Reference to the product with which the row is associated, if any.
            """,
            backref=orm.backref(
                '_{}_rows'.format(table_name),
                doc="""
                Sequence of all {} rows which reference the product.
                """.format(model_title)))

    brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name of the product.
    """)

    description = sa.Column(sa.String(length=255), nullable=True, doc="""
    Description of the product.
    """)

    size = sa.Column(sa.String(length=255), nullable=True, doc="""
    Size of the product, as string.
    """)

    # TODO: should add this probably, but for now one batch has Integer for this..
    # case_quantity = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True, doc="""
    # Number of units in a case of product.
    # """)

    department_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the department to which the product belongs.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the department to which the product belongs.
    """)

    subdepartment_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the subdepartment to which the product belongs.
    """)

    subdepartment_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the subdepartment to which the product belongs.
    """)

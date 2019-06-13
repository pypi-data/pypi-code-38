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
Data Batch Handlers
"""

from __future__ import unicode_literals, absolute_import

import os
import shutil
import datetime
import warnings

from sqlalchemy import orm

from rattail.db import model, api
from rattail.core import Object
from rattail.gpc import GPC
from rattail.barcodes import upce_to_upca
from rattail.db.cache import cache_model
from rattail.time import localtime, make_utc
from rattail.util import progress_loop, load_object


class BatchHandler(object):
    """
    Base class and partial default implementation for batch handlers.  It is
    expected that all batch handlers will ultimately inherit from this base
    class, therefore it defines the implementation "interface" loosely
    speaking.  Custom batch handlers are welcome to supplement or override this
    as needed, and in fact must do so for certain aspects.

    .. attribute:: populate_batches

       Simple flag to indicate whether any/all batches being handled, will
       require initial population from a relevant data source.  Note that this
       flag should be set to ``True`` if *any* batches may need population.
       Whether or not a given batch actually needs to be populated, is
       ultimately determined by the :meth:`should_populate()` method.

    .. attribute:: populate_with_versioning

       This flag indicates whether it's okay for data versioning to be enabled
       during initial batch population.

       If set to ``True`` (the default), then versioning is allowed and
       therefore the caller need take no special precautions when populating
       the batch.

       If set to ``False`` then versioning is *not* allowed; if versioning is
       not enabled for the current process, the caller may populate the batch
       with no special precautions.  However if versioning *is* enabled, the
       caller must launch a separate process with versioning disabled, in order
       to populate the batch.

    .. attribute:: refresh_with_versioning

       This flag indicates whether it's okay for data versioning to be enabled
       during batch refresh.

       If set to ``True`` (the default), then versioning is allowed and
       therefore the caller need take no special precautions when populating
       the batch.

       If set to ``False`` then versioning is *not* allowed; if versioning is
       not enabled for the current process, the caller may populate the batch
       with no special precautions.  However if versioning *is* enabled, the
       caller must launch a separate process with versioning disabled, in order
       to refresh the batch.

    .. attribute:: execute_with_versioning

       This flag indicates whether it's okay for data versioning to be enabled
       during batch execution.

       If set to ``True`` (the default), then versioning is allowed and
       therefore the caller need take no special precautions when populating
       the batch.

       If set to ``False`` then versioning is *not* allowed; if versioning is
       not enabled for the current process, the caller may populate the batch
       with no special precautions.  However if versioning *is* enabled, the
       caller must launch a separate process with versioning disabled, in order
       to execute the batch.

    .. attribute:: repopulate_when_refresh

       Flag to indicate that when a batch is refreshed, the first step of that
       should be to re-populate the batch.  The flag is ``False`` by default,
       in which case the batch is *not* repopulated, i.e. the refresh will work
       with existing batch rows.
    """
    populate_batches = False
    populate_with_versioning = True

    refresh_with_versioning = True
    repopulate_when_refresh = False

    execute_with_versioning = True

    def __init__(self, config):
        self.config = config
        self.enum = config.get_enum()

    @property
    def batch_model_class(self):
        """
        Reference to the data model class of the batch type for which this
        handler is responsible, e.g. :class:`rattail.db.model.LabelBatch`.
        Each handler must define this (or inherit from one that does).
        """
        raise NotImplementedError("You must set the 'batch_model_class' attribute "
                                  "for class '{}'".format(self.__class__.__name__))

    @property
    def batch_key(self):
        """
        The "batch type key" for the handler, e.g. ``'labels'``.  This isn't
        necessarily unique among handlers, but instead refers to a unique key
        for the type of batch being handled.  The handler needn't define this,
        as it is borrowed from :attr:`batch_model_class`.
        """
        return self.batch_model_class.batch_key

    def get_model_title(self):
        return self.batch_model_class.get_model_title()

    def allow_versioning(self, action):
        if action == 'populate':
            return self.populate_with_versioning
        if action == 'refresh':
            return self.refresh_with_versioning
        if action == 'execute':
            return self.execute_with_versioning
        raise NotImplementedError("unknown batch action: {}".format(action))

    def make_basic_batch(self, session, progress=None, **kwargs):
        """
        Make a new "basic" batch, with no customization beyond what is provided
        by ``kwargs``, which are passed directly to the batch class constructor.
        """
        kwargs.setdefault('rowcount', 0)
        kwargs.setdefault('complete', False)
        batch = self.batch_model_class(**kwargs)
        session.add(batch)
        session.flush()
        return batch

    def make_batch(self, session, progress=None, **kwargs):
        """
        Make a new batch, with initial rows if applicable.
        """
        batch = self.make_basic_batch(session, progress=progress, **kwargs)
        self.init_batch(batch, progress=progress, **kwargs)
        return batch

    def init_batch(self, batch, progress=None, **kwargs):
        """
        Initialize the batch in whatever way might make sense.  Whether this is
        required at all is up to the batch handler etc.
        """

    def add_row(self, batch, row):
        """
        (Try to) Add the given row to the given batch.  This assumes it is a
        *new* row, perhaps along with other assumptions?
        """
        session = orm.object_session(batch)
        with session.no_autoflush:
            batch.data_rows.append(row)
            self.refresh_row(row)
        if not row.removed:
            batch.rowcount += 1
            self.after_add_row(batch, row)

    def after_add_row(self, batch, row):
        """
        Event hook, called immediately after the given row has been "properly"
        added to the batch.  This is a good place to update totals for the
        batch, to account for the new row, etc.
        """

    def purge_batches(self, session, before=None, before_days=90,
                      delete_all_data=True, progress=None, **kwargs):
        """
        Purge all batches which were executed prior to a given date.

        :param before: If provided, must be a timezone-aware datetime object.
           If not provided, it will be calculated from the current date, using
           ``before_days``.

        :param before_days: Number of days before the current date, to be used
           as the cutoff date if ``before`` is not specified.

        :param delete_all_data: Flag indicating whether *all* data should be
           deleted for each batch being purged.  This flag is passed along to
           :meth:`delete()`; see that for more info.

        :returns: Integer indicating the number of batches purged.
        """
        if not before:
            before = localtime(self.config).date() - datetime.timedelta(days=before_days)
            before = datetime.datetime.combine(before, datetime.time(0))
            before = localtime(self.config, before)

        old_batches = session.query(self.batch_model_class)\
                             .filter(self.batch_model_class.executed < before)\
                             .options(orm.joinedload(self.batch_model_class.data_rows))
        result = Object()
        result.purged = 0

        def purge(batch, i):
            self.delete(batch, delete_all_data=delete_all_data, progress=progress)
            session.delete(batch)
            result.purged += 1
            if i % 5 == 0:
                session.flush()

        self.progress_loop(purge, old_batches, progress,
                           message="Purging old batches")

        session.flush()
        return result.purged

    @property
    def root_datadir(self):
        """
        The absolute path of the root folder in which data for this particular
        type of batch is stored.  The structure of this path is as follows:

        .. code-block:: none

           /{root_batch_data_dir}/{batch_type_key}

        * ``{root_batch_data_dir}`` - Value of the 'batch.files' option in the
          [rattail] section of config file.
        * ``{batch_type_key}`` - Unique key for the type of batch it is.

        .. note::
           While it is likely that the data folder returned by this method
           already exists, this method does not guarantee it.
        """
        return self.config.batch_filedir(self.batch_key)

    def datadir(self, batch):
        """
        Returns the absolute path of the folder in which the batch's source
        data file(s) resides.  Note that the batch must already have been
        persisted to the database.  The structure of the path returned is as
        follows:

        .. code-block:: none

           /{root_datadir}/{uuid[:2]}/{uuid[2:]}

        * ``{root_datadir}`` - Value returned by :meth:`root_datadir()`.
        * ``{uuid[:2]}`` - First two characters of batch UUID.
        * ``{uuid[2:]}`` - All batch UUID characters *after* the first two.

        .. note::
           While it is likely that the data folder returned by this method
           already exists, this method does not guarantee any such thing.  It
           is typically assumed that the path will have been created by a
           previous call to :meth:`make_batch()` however.
        """
        return os.path.join(self.root_datadir, batch.uuid[:2], batch.uuid[2:])

    def make_datadir(self, batch):
        """
        Returns the data folder specific to the given batch, creating if necessary.
        """
        datadir = self.datadir(batch)
        os.makedirs(datadir)
        return datadir

    # TODO: remove default attr?
    def set_input_file(self, batch, path, attr='filename'):
        """
        Assign the data file found at ``path`` to the batch.  This overwrites
        the given attribute (``attr``) of the batch and places a copy of the
        data file in the batch's data folder.
        """
        datadir = self.make_datadir(batch)
        filename = os.path.basename(path)
        shutil.copyfile(path, os.path.join(datadir, filename))
        setattr(batch, attr, filename)

    def should_populate(self, batch):
        """
        Must return a boolean indicating whether the given batch should be
        populated from an initial data source, i.e. at time of batch creation.
        Override this method if you need to inspect the batch in order to
        determine whether the populate step is needed.  Default behavior is to
        simply return the value of :attr:`populate_batches`.
        """
        return self.populate_batches

    def setup_populate(self, batch, progress=None):
        """
        Perform any setup (caching etc.) necessary for populating a batch.
        """

    def teardown_populate(self, batch, progress=None):
        """
        Perform any teardown (cleanup etc.) necessary after populating a batch.
        """

    def do_populate(self, batch, user, progress=None):
        """
        Perform initial population for the batch, i.e. fill it with data rows.
        Where the handler obtains the data to do this, will vary greatly.

        Note that callers *should* use this method, but custom batch handlers
        should *not* override this method.  Conversely, custom handlers
        *should* override the :meth:`~populate()` method, but callers should
        *not* use that one directly.
        """
        self.setup_populate(batch, progress=progress)
        self.populate(batch, progress=progress)
        self.teardown_populate(batch, progress=progress)
        self.refresh_batch_status(batch)
        return True

    def populate(self, batch, progress=None):
        """
        Populate the batch with initial data rows.  It is assumed that the data
        source to be used will be known by inspecting various properties of the
        batch itself.

        Note that callers should *not* use this method, but custom batch
        handlers *should* override this method.  Conversely, custom handlers
        should *not* override the :meth:`~do_populate()` method, but callers
        *should* use that one directly.
        """
        raise NotImplementedError("Please implement `{}.populate()` method".format(batch.__class__.__name__))

    def refreshable(self, batch):
        """
        This method should return a boolean indicating whether or not the
        handler supports a "refresh" operation for the batch, given its current
        condition.  The default assumes a refresh is allowed unless the batch
        is executed.

        Note that this (currently) only affects the enabled/disabled state of
        the Refresh button within the Tailbone batch view.
        """
        if batch.executed:
            return False
        return True

    def progress_loop(self, *args, **kwargs):
        return progress_loop(*args, **kwargs)

    def setup_refresh(self, batch, progress=None):
        """
        Perform any setup (caching etc.) necessary for refreshing a batch.
        """

    def teardown_refresh(self, batch, progress=None):
        """
        Perform any teardown (cleanup etc.) necessary after refreshing a batch.
        """

    def do_refresh(self, batch, user, progress=None):
        self.refresh(batch, progress=progress)
        return True

    def refresh(self, batch, progress=None):
        """
        Perform a full data refresh for the batch.  What exactly this means will
        depend on the type of batch, and specific handler logic.

        Generally speaking this refresh is meant to use queries etc. to obtain
        "fresh" data for the batch (header) and all its rows.  In most cases
        certain data is expected to be "core" to the batch and/or rows, and
        such data will be left intact, with all *other* data values being
        re-calculated and/or reset etc.
        """
        session = orm.object_session(batch)
        self.setup_refresh(batch, progress=progress)
        if self.repopulate_when_refresh:
            del batch.data_rows[:]
            batch.rowcount = 0
            session.flush()
            self.populate(batch, progress=progress)
        else:
            batch.rowcount = 0

            def refresh(row, i):
                with session.no_autoflush:
                    self.refresh_row(row)
                if not row.removed:
                    batch.rowcount += 1

            self.progress_loop(refresh, batch.active_rows(), progress,
                               message="Refreshing batch data rows")
        self.refresh_batch_status(batch)
        self.teardown_refresh(batch, progress=progress)
        return True

    def refresh_row(self, row):
        """
        This method will be passed a row object which has already been properly
        added to a batch, and which has basic required fields already
        populated.  This method is then responsible for further populating all
        applicable fields for the row, based on current data within the
        relevant system(s).

        Note that in some cases this method may be called multiple times for
        the same row, e.g. once when first creating the batch and then later
        when a user explicitly refreshes the batch.  The method logic must
        account for this possibility.
        """

    def locate_product_for_entry(self, session, entry, **kwargs):
        """
        This method aims to provide sane default logic for locating a
        :class:`~rattail.db.model.products.Product` record for the given
        "entry" - which is assumed to be a string, i.e. "as-is" from whatever
        data source.

        Note that any batch handler is free to override this, and certainly
        some batches will never need it anyway.  The goal is more to establish
        a good API pattern, but the handler logic itself can vary.

        Also, this default logic will try to honor the "configured" product key
        field, and prefer that when attempting the lookup.
        """
        # try to locate product by uuid before other, more specific key
        # if kwargs.get('try_uuid', True):
        product = session.query(model.Product).get(entry)
        if product:
            return product

        product_key = self.config.product_key()
        if product_key == 'upc':

            if entry.isdigit():

                # we first assume the user entry *does* include check digit
                provided = GPC(entry, calc_check_digit=False)
                product = api.get_product_by_upc(session, provided)
                if product:
                    return product

                # but we can also calculate a check digit and try that
                checked = GPC(entry, calc_check_digit='upc')
                product = api.get_product_by_upc(session, checked)
                if product:
                    return product

                # one last trick is to expand UPC-E to UPC-A and then reattempt
                # the lookup, *with* check digit (since it would be known)
                if len(entry) in (6, 8):
                    checked = GPC(upce_to_upca(entry), calc_check_digit='upc')
                    product = api.get_product_by_upc(session, checked)
                    if product:
                        return product

        elif product_key == 'item_id':

            # try to locate product by item_id
            product = api.get_product_by_item_id(session, entry)
            if product:
                return product

        # if we made it this far, lookup by product key failed.

        # okay then, let's maybe attempt lookup by "alternate" code
        if kwargs.get('lookup_by_code'):
            product = api.get_product_by_code(session, entry)
            if product:
                return product

    def remove_row(self, row):
        """
        Remove the given row from its batch, and update the batch accordingly.
        How exactly the row is "removed" is up to this method.  Default is to
        set the row's :attr:`~rattail.db.model.batch.BatchRowMixin.removed`
        flag, then invoke the :meth:`~refresh_batch_status()` method.

        Execute the given batch, with given progress and kwargs.  That is an
        intentionally generic statement, the meaning of which must be further
        defined by the handler subclass since default is ``NotImplementedError``.

        Note that callers should *not* use this method, but custom batch
        handlers *should* override this method.  Conversely, custom handlers
        should *not* override the :meth:`~do_remove_row()` method, but callers
        *should* use that one directly.
        """
        batch = row.batch
        row.removed = True
        self.refresh_batch_status(batch)

    def do_remove_row(self, row):
        """
        Remove the given row from its batch, and update the batch accordingly.

        Note that callers *should* use this method, but custom batch handlers
        should *not* override this method.  Conversely, custom handlers
        *should* override the :meth:`~remove_row()` method, but callers should
        *not* use that one directly.
        """
        if row.removed:
            return
        self.remove_row(row)
        batch = row.batch
        if batch.rowcount is not None:
            batch.rowcount -= 1

    def refresh_batch_status(self, batch):
        """
        Update the batch status, as needed...
        """

    def mark_complete(self, batch, progress=None):
        """
        Mark the given batch as "complete".  This usually is just a matter of
        setting the :attr:`~rattail.db.model.batch.BatchMixin.complete` flag
        for the batch, with the idea that this should "freeze" the batch so
        that another user can verify its state before finally executing it.

        Each handler is of course free to expound on this idea, or to add extra
        logic to this "event" of marking a batch complete.
        """
        batch.complete = True

    def mark_incomplete(self, batch, progress=None):
        """
        Mark the given batch as "incomplete" (aka. pending).  This usually is
        just a matter of clearing the
        :attr:`~rattail.db.model.batch.BatchMixin.complete` flag for the batch,
        with the idea that this should "thaw" the batch so that it may be
        further updated, i.e. it's not yet ready to execute.

        Each handler is of course free to expound on this idea, or to add extra
        logic to this "event" of marking a batch incomplete.
        """
        batch.complete = False

    def why_not_execute(self, batch):
        """
        This method should return a string indicating the reason why the given
        batch should not be considered executable.  By default it returns
        ``None`` which means the batch *is* to be considered executable.

        Note that it is assumed the batch has not already been executed, since
        execution is globally prevented for such batches.
        """

    def executable(self, batch):
        """
        This method should return a boolean indicating whether or not execution
        should be allowed for the batch, given its current condition.  The
        default simply returns ``True`` but you may override as needed.

        Note that this (currently) only affects the enabled/disabled state of
        the Execute button within the Tailbone batch view.
        """
        if batch is None:
            return True
        if batch.executed:
            return False
        if self.why_not_execute(batch):
            return False
        return True

    def auto_executable(self, batch):
        """
        Must return a boolean indicating whether the given bath is eligible for
        "automatic" execution, i.e. immediately after batch is created.
        """
        return False

    def do_execute(self, batch, user, progress=None, **kwargs):
        """
        Perform final execution for the batch.  What that means for any given
        batch, will vary greatly.

        Note that callers *should* use this method, but custom batch handlers
        should *not* override this method.  Conversely, custom handlers
        *should* override the :meth:`~execute()` method, but callers should
        *not* use that one directly.
        """
        # make sure we declare who's responsible, if we can
        session = orm.object_session(batch)
        session.set_continuum_user(user)

        result = self.execute(batch, user=user, progress=progress, **kwargs)
        if not result:
            return False
        batch.executed = make_utc()
        batch.executed_by = user
        return result

    def execute(self, batch, progress=None, **kwargs):
        """
        Execute the given batch, with given progress and kwargs.  That is an
        intentionally generic statement, the meaning of which must be further
        defined by the handler subclass since default is ``NotImplementedError``.

        Note that callers should *not* use this method, but custom batch
        handlers *should* override this method.  Conversely, custom handlers
        should *not* override the :meth:`~do_execute()` method, but callers
        *should* use that one directly.
        """
        raise NotImplementedError

    def execute_many(self, batches, progress=None, **kwargs):
        """
        Execute a set of batches, with given progress and kwargs.  Default
        behavior is to simply execute each batch in succession.  Any batches
        which are already executed are skipped.
        """
        now = make_utc()
        for batch in batches:
            if not batch.executed:
                self.execute(batch, progress=progress, **kwargs)
                batch.executed = now
                batch.executed_by = kwargs['user']
        return True

    def delete(self, batch, delete_all_data=True, progress=None, **kwargs):
        """
        Delete all data for the batch, including any related (e.g. row)
        records, as well as files on disk etc.  This method should *not* delete
        the batch itself however.

        :param delete_all_data: Flag indicating whether *all* data should be
           deleted.  You should probably set this to ``False`` if in dry-run
           mode, since deleting *all* data often implies deleting files from
           disk, which is not transactional and therefore can't be rolled back.
        """
        if delete_all_data:
            if hasattr(batch, 'delete_data'):
                batch.delete_data(self.config)
        if hasattr(batch, 'data_rows'):
            del batch.data_rows[:]

    def setup_clone(self, oldbatch, progress=None):
        """
        Perform any setup (caching etc.) necessary for cloning batch.  Note
        that the ``oldbatch`` arg is the "old" batch, i.e. the one from which a
        clone is to be created.
        """

    def teardown_clone(self, newbatch, progress=None):
        """
        Perform any teardown (cleanup etc.) necessary after cloning a batch.
        Note that the ``newbatch`` arg is the "new" batch, i.e. the one which
        was just created by cloning the old batch.
        """

    def clone(self, oldbatch, created_by, progress=None):
        """
        Clone the given batch as a new batch, and return the new batch.
        """
        self.setup_clone(oldbatch, progress=progress)
        batch_class = self.batch_model_class
        batch_mapper = orm.class_mapper(batch_class)

        newbatch = batch_class()
        newbatch.created_by = created_by
        newbatch.rowcount = 0
        for name in batch_mapper.columns.keys():
            if name not in ('uuid', 'id', 'created', 'created_by_uuid', 'rowcount', 'executed', 'executed_by_uuid'):
                setattr(newbatch, name, getattr(oldbatch, name))

        session = orm.object_session(oldbatch)
        session.add(newbatch)
        session.flush()

        row_class = newbatch.row_class
        row_mapper = orm.class_mapper(row_class)

        def clone_row(oldrow, i):
            newrow = self.clone_row(oldrow)
            self.add_row(newbatch, newrow)

        self.progress_loop(clone_row, oldbatch.data_rows, progress,
                           message="Cloning data rows for new batch")

        self.refresh_batch_status(newbatch)
        self.teardown_clone(newbatch, progress=progress)
        return newbatch

    def clone_row(self, oldrow):
        row_class = self.batch_model_class.row_class
        row_mapper = orm.class_mapper(row_class)
        newrow = row_class()
        for name in row_mapper.columns.keys():
            if name not in ('uuid', 'batch_uuid', 'sequence'):
                setattr(newrow, name, getattr(oldrow, name))
        return newrow

    def cache_model(self, session, model, **kwargs):
        return cache_model(session, model, **kwargs)


def get_batch_types(config):
    """
    Returns the list of available batch type keys.
    """
    model = config.get_model()

    keys = []
    for name in dir(model):
        if name == 'BatchMixin':
            continue
        obj = getattr(model, name)
        if isinstance(obj, type):
            if issubclass(obj, model.Base):
                if issubclass(obj, model.BatchMixin):
                    keys.append(obj.batch_key)

    keys.sort()
    return keys


def get_batch_handler(config, batch_key, default=None, error=True):
    """
    Returns a batch handler object corresponding to the given batch key.
    """
    spec = config.get('rattail.batch', '{}.handler'.format(batch_key), default=default)
    if error and not spec:
        raise ValueError("handler spec not found for batch type: {}".format(batch_key))
    handler = load_object(spec)(config)
    return handler

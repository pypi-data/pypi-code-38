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
Model Master View
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import tempfile
import logging

import six
import sqlalchemy as sa
from sqlalchemy import orm

import sqlalchemy_continuum as continuum

from rattail.db import model, Session as RattailSession
from rattail.db.continuum import model_transaction_query
from rattail.core import Object
from rattail.util import prettify
from rattail.time import localtime
from rattail.threads import Thread
from rattail.csvutil import UnicodeDictWriter
from rattail.files import temp_path
from rattail.excel import ExcelWriter
from rattail.gpc import GPC

import colander
import deform
from pyramid import httpexceptions
from pyramid.renderers import get_renderer, render_to_response, render
from pyramid.response import FileResponse
from webhelpers2.html import HTML, tags

from tailbone import forms, grids, diffs
from tailbone.views import View
from tailbone.progress import SessionProgress


log = logging.getLogger(__name__)


class MasterView(View):
    """
    Base "master" view class.  All model master views should derive from this.
    """
    filterable = True
    pageable = True
    checkboxes = False

    # set to True in order to encode search values as utf-8
    use_byte_string_filters = False

    listable = True
    sortable = True
    results_downloadable_csv = False
    results_downloadable_xlsx = False
    creatable = True
    show_create_link = True
    viewable = True
    editable = True
    deletable = True
    delete_confirm = 'full'
    bulk_deletable = False
    set_deletable = False
    supports_set_enabled_toggle = False
    populatable = False
    mergeable = False
    downloadable = False
    cloneable = False
    touchable = False
    executable = False
    execute_progress_template = None
    execute_progress_initial_msg = None
    supports_prev_next = False
    supports_import_batch_from_file = False

    # quickie (search)
    supports_quickie_search = False
    expose_quickie_search = False

    # set to True to declare model as "contact"
    is_contact = False

    supports_mobile = False
    mobile_creatable = False
    mobile_editable = False
    mobile_pageable = True
    mobile_filterable = False
    mobile_executable = False

    mobile = False
    listing = False
    creating = False
    creates_multiple = False
    viewing = False
    editing = False
    deleting = False
    executing = False
    has_pk_fields = False
    has_image = False
    has_thumbnail = False

    row_attrs = {}
    cell_attrs = {}

    grid_index = None
    use_index_links = False

    has_versions = False
    help_url = None

    labels = {'uuid': "UUID"}

    # ROW-RELATED ATTRS FOLLOW:

    has_rows = False
    model_row_class = None
    rows_pageable = True
    rows_sortable = True
    rows_filterable = True
    rows_viewable = True
    rows_creatable = False
    rows_editable = False
    rows_deletable = False
    rows_deletable_speedbump = True
    rows_bulk_deletable = False
    rows_default_pagesize = 20
    rows_downloadable_csv = False
    rows_downloadable_xlsx = False

    mobile_rows_creatable = False
    mobile_rows_creatable_via_browse = False
    mobile_rows_quickable = False
    mobile_rows_filterable = False
    mobile_rows_viewable = False
    mobile_rows_editable = False
    mobile_rows_deletable = False

    row_labels = {}

    @property
    def Session(self):
        """
        SQLAlchemy scoped session to use when querying the database.  Defaults
        to ``tailbone.db.Session``.
        """
        from tailbone.db import Session
        return Session

    @classmethod
    def get_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        grid instances.
        """
        return getattr(cls, 'grid_factory', grids.Grid)

    @classmethod
    def get_row_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        row grid instances.
        """
        return getattr(cls, 'row_grid_factory', grids.Grid)

    @classmethod
    def get_version_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        version grid instances.
        """
        return getattr(cls, 'version_grid_factory', grids.Grid)

    @classmethod
    def get_mobile_grid_factory(cls):
        """
        Must return a callable to be used when creating new mobile grid
        instances.  Instead of overriding this, you can set
        :attr:`mobile_grid_factory`.  Default factory is :class:`MobileGrid`.
        """
        return getattr(cls, 'mobile_grid_factory', grids.MobileGrid)

    @classmethod
    def get_mobile_row_grid_factory(cls):
        """
        Must return a callable to be used when creating new mobile row grid
        instances.  Instead of overriding this, you can set
        :attr:`mobile_row_grid_factory`.  Default factory is :class:`MobileGrid`.
        """
        return getattr(cls, 'mobile_row_grid_factory', grids.MobileGrid)

    def set_labels(self, obj):
        labels = self.collect_labels()
        for key, label in six.iteritems(labels):
            obj.set_label(key, label)

    def collect_labels(self):
        """
        Collect all labels defined within the master class hierarchy.
        """
        labels = {}
        hierarchy = self.get_class_hierarchy()
        for cls in hierarchy:
            if hasattr(cls, 'labels'):
                labels.update(cls.labels)
        return labels

    def get_class_hierarchy(self):
        hierarchy = []

        def traverse(cls):
            if cls is not object:
                hierarchy.append(cls)
                for parent in cls.__bases__:
                    traverse(parent)

        traverse(self.__class__)
        hierarchy.reverse()
        return hierarchy

    def set_row_labels(self, obj):
        labels = self.collect_row_labels()
        for key, label in six.iteritems(labels):
            obj.set_label(key, label)

    def collect_row_labels(self):
        """
        Collect all row labels defined within the master class hierarchy.
        """
        labels = {}
        hierarchy = self.get_class_hierarchy()
        for cls in hierarchy:
            if hasattr(cls, 'row_labels'):
                labels.update(cls.row_labels)
        return labels

    ##############################
    # Available Views
    ##############################

    def index(self):
        """
        View to list/filter/sort the model data.

        If this view receives a non-empty 'partial' parameter in the query
        string, then the view will return the rendered grid only.  Otherwise
        returns the full page.
        """
        self.listing = True
        grid = self.make_grid()
        use_buefy = self.get_use_buefy()

        # If user just refreshed the page with a reset instruction, issue a
        # redirect in order to clear out the query string.
        if self.request.GET.get('reset-to-default-filters') == 'true':
            return self.redirect(self.request.current_route_url(_query=None))

        # Stash some grid stats, for possible use when generating URLs.
        if grid.pageable and hasattr(grid, 'pager'):
            self.first_visible_grid_index = grid.pager.first_item

        # return grid only, if partial page was requested
        if self.request.params.get('partial'):
            if use_buefy:
                # render grid data only, as JSON
                return render_to_response('json', grid.get_buefy_data(),
                                          request=self.request)
            else: # just do traditional thing, render grid HTML
                self.request.response.content_type = str('text/html')
                self.request.response.text = grid.render_grid()
                return self.request.response

        context = {
            'grid': grid,
        }
        return self.render_to_response('index', context)

    def make_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Creates a new grid instance
        """
        if factory is None:
            factory = self.get_grid_factory()
        if key is None:
            key = self.get_grid_key()
        if data is None:
            data = self.get_data(session=kwargs.get('session'))
        if columns is None:
            columns = self.get_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_grid(grid)
        grid.load_settings()
        return grid

    def get_effective_data(self, session=None, **kwargs):
        """
        Convenience method which returns the "effective" data for the master
        grid, filtered and sorted to match what would show on the UI, but not
        paged etc.
        """
        if session is None:
            session = self.Session()
        kwargs.setdefault('pageable', False)
        grid = self.make_grid(session=session, **kwargs)
        return grid.make_visible_data()

    def get_grid_columns(self):
        """
        Returns the default list of grid column names.  This may return
        ``None``, in which case the grid will generate its own default list.
        """
        if hasattr(self, 'grid_columns'):
            return self.grid_columns

    def make_grid_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new grid instances.
        """
        permission_prefix = self.get_permission_prefix()

        checkboxes = self.checkboxes
        if not checkboxes and self.mergeable and self.request.has_perm('{}.merge'.format(permission_prefix)):
            checkboxes = True
        if not checkboxes and self.supports_set_enabled_toggle and self.request.has_perm('{}.enable_disable_set'.format(permission_prefix)):
            checkboxes = True
        if not checkboxes and self.set_deletable and self.request.has_perm('{}.delete_set'.format(permission_prefix)):
            checkboxes = True

        defaults = {
            'model_class': getattr(self, 'model_class', None),
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'width': 'full',
            'filterable': self.filterable,
            'use_byte_string_filters': self.use_byte_string_filters,
            'sortable': self.sortable,
            'pageable': self.pageable,
            'extra_row_class': self.grid_extra_class,
            'url': lambda obj: self.get_action_url('view', obj),
            'checkboxes': checkboxes,
            'checked': self.checked,
        }
        if 'main_actions' not in kwargs and 'more_actions' not in kwargs:
            main, more = self.get_grid_actions()
            defaults['main_actions'] = main
            defaults['more_actions'] = more
        defaults.update(kwargs)
        return defaults

    def configure_grid(self, grid):
        self.set_labels(grid)

    def grid_extra_class(self, obj, i):
        """
        Returns string of extra class(es) for the table row corresponding to
        the given object, or ``None``.
        """

    def quickie(self):
        raise NotImplementedError

    def get_quickie_url(self):
        route_prefix = self.get_route_prefix()
        return self.request.route_url('{}.quickie'.format(route_prefix))

    def get_quickie_perm(self):
        permission_prefix = self.get_permission_prefix()
        return '{}.quickie'.format(permission_prefix)

    def get_quickie_placeholder(self):
        pass

    def make_row_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Make and return a new (configured) rows grid instance.
        """
        instance = kwargs.pop('instance', None)
        if not instance:
            instance = self.get_instance()

        if factory is None:
            factory = self.get_row_grid_factory()
        if key is None:
            key = self.get_row_grid_key()
        if data is None:
            data = self.get_row_data(instance)
        if columns is None:
            columns = self.get_row_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_row_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_row_grid(grid)
        grid.load_settings()
        return grid

    def get_row_grid_columns(self):
        if hasattr(self, 'row_grid_columns'):
            return self.row_grid_columns
        # TODO
        raise NotImplementedError

    def make_row_grid_kwargs(self, **kwargs):
        """
        Return a dict of kwargs to be used when constructing a new rows grid.
        """
        permission_prefix = self.get_permission_prefix()

        defaults = {
            'model_class': self.model_row_class,
            'width': 'full',
            'filterable': self.rows_filterable,
            'sortable': self.rows_sortable,
            'pageable': self.rows_pageable,
            'default_pagesize': self.rows_default_pagesize,
            'extra_row_class': self.row_grid_extra_class,
            'url': lambda obj: self.get_row_action_url('view', obj),
        }

        if self.has_rows and 'main_actions' not in defaults:
            actions = []
            use_buefy = self.get_use_buefy()

            # view action
            if self.rows_viewable:
                view = lambda r, i: self.get_row_action_url('view', r)
                icon = 'eye' if use_buefy else 'zoomin'
                actions.append(self.make_action('view', icon=icon, url=view))

            # edit action
            if self.rows_editable:
                icon = 'edit' if use_buefy else 'pencil'
                actions.append(self.make_action('edit', icon=icon, url=self.row_edit_action_url))

            # delete action
            if self.rows_deletable and self.request.has_perm('{}.delete_row'.format(permission_prefix)):
                actions.append(self.make_action('delete', icon='trash', url=self.row_delete_action_url))
                defaults['delete_speedbump'] = self.rows_deletable_speedbump

            defaults['main_actions'] = actions

        defaults.update(kwargs)
        return defaults

    def configure_row_grid(self, grid):
        # super(MasterView, self).configure_row_grid(grid)
        self.set_row_labels(grid)

    def row_grid_extra_class(self, obj, i):
        """
        Returns string of extra class(es) for the table row corresponding to
        the given row object, or ``None``.
        """

    def make_version_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Creates a new version grid instance
        """
        instance = kwargs.pop('instance', None)
        if not instance:
            instance = self.get_instance()

        if factory is None:
            factory = self.get_version_grid_factory()
        if key is None:
            key = self.get_version_grid_key()
        if data is None:
            data = self.get_version_data(instance)
        if columns is None:
            columns = self.get_version_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_version_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_version_grid(grid)
        grid.load_settings()
        return grid

    def get_version_grid_columns(self):
        if hasattr(self, 'version_grid_columns'):
            return self.version_grid_columns
        # TODO
        return [
            'issued_at',
            'user',
            'remote_addr',
            'comment',
        ]

    def make_version_grid_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when
        constructing a new version grid.
        """
        defaults = {
            'model_class': continuum.transaction_class(self.get_model_class()),
            'width': 'full',
            'pageable': True,
        }
        if 'main_actions' not in kwargs:
            route = '{}.version'.format(self.get_route_prefix())
            instance = kwargs.get('instance') or self.get_instance()
            url = lambda txn, i: self.request.route_url(route, uuid=instance.uuid, txnid=txn.id)
            defaults['main_actions'] = [
                self.make_action('view', icon='zoomin', url=url),
            ]
        defaults.update(kwargs)
        return defaults

    def configure_version_grid(self, g):
        g.set_sort_defaults('issued_at', 'desc')
        g.set_renderer('comment', self.render_version_comment)
        g.set_label('issued_at', "Changed")
        g.set_label('user', "Changed by")
        g.set_label('remote_addr', "IP Address")
        # TODO: why does this render '#' as url?
        # g.set_link('issued_at')

    def render_version_comment(self, transaction, column):
        return transaction.meta.get('comment', "")

    def mobile_index(self):
        """
        Mobile "home" page for the data model
        """
        self.mobile = True
        self.listing = True
        grid = self.make_mobile_grid()
        return self.render_to_response('index', {'grid': grid}, mobile=True)

    @classmethod
    def get_mobile_grid_key(cls):
        """
        Must return a unique "config key" for the mobile grid, for sort/filter
        purposes etc.  (It need only be unique among *mobile* grids.)  Instead
        of overriding this, you can set :attr:`mobile_grid_key`.  Default is
        the value returned by :meth:`get_route_prefix()`.
        """
        if hasattr(cls, 'mobile_grid_key'):
            return cls.mobile_grid_key
        return 'mobile.{}'.format(cls.get_route_prefix())

    def make_mobile_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Creates a new mobile grid instance
        """
        if factory is None:
            factory = self.get_mobile_grid_factory()
        if key is None:
            key = self.get_mobile_grid_key()
        if data is None:
            data = self.get_mobile_data(session=kwargs.get('session'))
        if columns is None:
            columns = self.get_mobile_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs.setdefault('mobile', True)
        kwargs = self.make_mobile_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_mobile_grid(grid)
        grid.load_settings()
        return grid

    def get_mobile_grid_columns(self):
        if hasattr(self, 'mobile_grid_columns'):
            return self.mobile_grid_columns
        # TODO
        return ['listitem']

    def get_mobile_data(self, session=None):
        """
        Must return the "raw" / full data set for the mobile grid.  This data
        should *not* yet be sorted or filtered in any way; that happens later.
        Default is the value returned by :meth:`get_data()`, in which case all
        records visible in the traditional view, are visible in mobile too.
        """
        return self.get_data(session=session)

    def make_mobile_grid_kwargs(self, **kwargs):
        """
        Must return a dictionary of kwargs to be passed to the factory when
        creating new mobile grid instances.
        """
        defaults = {
            'model_class': getattr(self, 'model_class', None),
            'pageable': self.mobile_pageable,
            'sortable': False,
            'filterable': self.mobile_filterable,
            'renderers': self.make_mobile_grid_renderers(),
            'url': lambda obj: self.get_action_url('view', obj, mobile=True),
        }
        # TODO: this seems wrong..
        if self.mobile_filterable:
            defaults['filters'] = self.make_mobile_filters()
        defaults.update(kwargs)
        return defaults

    def make_mobile_grid_renderers(self):
        return {
            'listitem': self.render_mobile_listitem,
        }

    def render_mobile_listitem(self, obj, i):
        return obj

    def configure_mobile_grid(self, grid):
        pass

    def make_mobile_row_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Make a new (configured) rows grid instance for mobile.
        """
        instance = kwargs.pop('instance', self.get_instance())

        if factory is None:
            factory = self.get_mobile_row_grid_factory()
        if key is None:
            key = 'mobile.{}.{}'.format(self.get_grid_key(), self.request.matchdict[self.get_model_key()])
        if data is None:
            data = self.get_mobile_row_data(instance)
        if columns is None:
            columns = self.get_mobile_row_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs.setdefault('mobile', True)
        kwargs = self.make_mobile_row_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_mobile_row_grid(grid)
        grid.load_settings()
        return grid

    def get_mobile_row_grid_columns(self):
        if hasattr(self, 'mobile_row_grid_columns'):
            return self.mobile_row_grid_columns
        # TODO
        return ['listitem']

    def make_mobile_row_grid_kwargs(self, **kwargs):
        """
        Must return a dictionary of kwargs to be passed to the factory when
        creating new mobile *row* grid instances.
        """
        defaults = {
            'model_class': self.model_row_class,
            # TODO
            'pageable': self.pageable,
            'sortable': False,
            'filterable': self.mobile_rows_filterable,
            'renderers': self.make_mobile_row_grid_renderers(),
            'url': lambda obj: self.get_row_action_url('view', obj, mobile=True),
        }
        # TODO: this seems wrong..
        if self.mobile_rows_filterable:
            defaults['filters'] = self.make_mobile_row_filters()
        defaults.update(kwargs)
        return defaults

    def make_mobile_row_grid_renderers(self):
        return {
            'listitem': self.render_mobile_row_listitem,
        }

    def configure_mobile_row_grid(self, grid):
        pass

    def make_mobile_filters(self):
        """
        Returns a set of filters for the mobile grid, if applicable.
        """

    def make_mobile_row_filters(self):
        """
        Returns a set of filters for the mobile row grid, if applicable.
        """

    def render_mobile_row_listitem(self, obj, i):
        return obj

    def create(self, form=None, template='create'):
        """
        View for creating a new model record.
        """
        self.creating = True
        if form is None:
            form = self.make_form(self.get_model_class())
        if self.request.method == 'POST':
            if self.validate_form(form):
                # let save_create_form() return alternate object if necessary
                obj = self.save_create_form(form)
                self.after_create(obj)
                self.flash_after_create(obj)
                return self.redirect_after_create(obj)
        context = {'form': form}
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response(template, context)

    def mobile_create(self):
        """
        Mobile view for creating a new primary object
        """
        self.mobile = True
        self.creating = True
        form = self.make_mobile_form(self.get_model_class())
        if self.request.method == 'POST':
            if self.validate_mobile_form(form):
                # let save_create_form() return alternate object if necessary
                obj = self.save_mobile_create_form(form)
                self.after_create(obj)
                self.flash_after_create(obj)
                return self.redirect_after_create(obj, mobile=True)
        return self.render_to_response('create', {'form': form}, mobile=True)

    def save_create_form(self, form):
        uploads = self.normalize_uploads(form)
        self.before_create(form)
        with self.Session().no_autoflush:
            obj = self.objectify(form, self.form_deserialized)
            self.before_create_flush(obj, form)
        self.Session.add(obj)
        self.Session.flush()
        self.process_uploads(obj, form, uploads)
        return obj

    def normalize_uploads(self, form, skip=None):
        uploads = {}
        for node in form.schema:
            if isinstance(node.typ, deform.FileData):
                if skip and node.name in skip:
                    continue
                # TODO: does form ever *not* have 'validated' attr here?
                if hasattr(form, 'validated'):
                    filedict = form.validated.get(node.name)
                else:
                    filedict = self.form_deserialized.get(node.name)
                if filedict:
                    tempdir = tempfile.mkdtemp()
                    filepath = os.path.join(tempdir, filedict['filename'])
                    tmpinfo = form.deform_form[node.name].widget.tmpstore.get(filedict['uid'])
                    tmpdata = tmpinfo['fp'].read()
                    with open(filepath, 'wb') as f:
                        f.write(tmpdata)
                    uploads[node.name] = {
                        'tempdir': tempdir,
                        'temp_path': filepath,
                    }
        return uploads

    def process_uploads(self, obj, form, uploads):
        pass

    def import_batch_from_file(self, handler_factory, model_name,
                               delete=False, schema=None, importer_host_title=None):

        handler = handler_factory(self.rattail_config)

        if not schema:
            schema = forms.SimpleFileImport().bind(request=self.request)
        form = forms.Form(schema=schema, request=self.request)
        form.save_label = "Upload"
        form.cancel_url = self.get_index_url()
        if form.validate(newstyle=True):

            uploads = self.normalize_uploads(form)
            filepath = uploads['filename']['temp_path']
            batches = handler.make_batches(model_name,
                                           delete=delete,
                                           # tdc_input_path=filepath,
                                           # source_csv_path=filepath,
                                           source_data_path=filepath,
                                           runas_user=self.request.user)
            batch = batches[0]
            return self.redirect(self.request.route_url('batch.importer.view', uuid=batch.uuid))

        if not importer_host_title:
            importer_host_title = handler.host_title

        return self.render_to_response('import_file', {
            'form': form,
            'dform': form.make_deform_form(),
            'importer_host_title': importer_host_title,
        })

    def render_product_key_value(self, obj):
        """
        Render the "canonical" product key value for the given object.
        """
        product_key = self.rattail_config.product_key()
        if product_key == 'upc':
            return obj.upc.pretty() if obj.upc else ''
        return getattr(obj, product_key)

    def render_product(self, obj, field):
        product = getattr(obj, field)
        if not product:
            return ""
        text = six.text_type(product)
        url = self.request.route_url('products.view', uuid=product.uuid)
        return tags.link_to(text, url)

    def render_vendor(self, obj, field):
        vendor = getattr(obj, field)
        if not vendor:
            return ""
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def render_department(self, obj, field):
        department = getattr(obj, field)
        if not department:
            return ""
        text = "({}) {}".format(department.number, department.name)
        url = self.request.route_url('departments.view', uuid=department.uuid)
        return tags.link_to(text, url)

    def render_subdepartment(self, obj, field):
        subdepartment = getattr(obj, field)
        if not subdepartment:
            return ""
        text = "({}) {}".format(subdepartment.number, subdepartment.name)
        url = self.request.route_url('subdepartments.view', uuid=subdepartment.uuid)
        return tags.link_to(text, url)

    def render_category(self, obj, field):
        category = getattr(obj, field)
        if not category:
            return ""
        text = "({}) {}".format(category.code, category.name)
        url = self.request.route_url('categories.view', uuid=category.uuid)
        return tags.link_to(text, url)

    def render_family(self, obj, field):
        family = getattr(obj, field)
        if not family:
            return ""
        text = "({}) {}".format(family.code, family.name)
        url = self.request.route_url('families.view', uuid=family.uuid)
        return tags.link_to(text, url)

    def render_report(self, obj, field):
        report = getattr(obj, field)
        if not report:
            return ""
        text = "({}) {}".format(report.code, report.name)
        url = self.request.route_url('reportcodes.view', uuid=report.uuid)
        return tags.link_to(text, url)

    def render_person(self, obj, field):
        person = getattr(obj, field)
        if not person:
            return ""
        text = six.text_type(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def render_user(self, obj, field):
        user = getattr(obj, field)
        if not user:
            return ""
        text = six.text_type(user)
        url = self.request.route_url('users.view', uuid=user.uuid)
        return tags.link_to(text, url)

    def before_create_flush(self, obj, form):
        pass

    def flash_after_create(self, obj):
        self.request.session.flash("{} has been created: {}".format(
            self.get_model_title(), self.get_instance_title(obj)))

    def save_mobile_create_form(self, form):
        self.before_create(form)
        with self.Session.no_autoflush:
            obj = self.objectify(form, self.form_deserialized)
            self.before_create_flush(obj, form)
        self.Session.add(obj)
        self.Session.flush()
        return obj

    def redirect_after_create(self, instance, mobile=False):
        if self.populatable and self.should_populate(instance):
            return self.redirect(self.get_action_url('populate', instance, mobile=mobile))
        return self.redirect(self.get_action_url('view', instance, mobile=mobile))

    def should_populate(self, obj):
        return True

    def populate(self):
        """
        View for populating a new object.  What exactly this means / does will
        depend on the logic in :meth:`populate_object()`.
        """
        obj = self.get_instance()
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        # showing progress requires a separate thread; start that first
        key = '{}.populate'.format(route_prefix)
        progress = SessionProgress(self.request, key)
        thread = Thread(target=self.populate_thread, args=(obj.uuid, progress)) # TODO: uuid?
        thread.start()

        # Send user to progress page.
        kwargs = {
            'cancel_url': self.get_action_url('view', obj),
            'cancel_msg': "{} population was canceled.".format(self.get_model_title()),
        }

        return self.render_progress(progress, kwargs)

    def populate_thread(self, uuid, progress): # TODO: uuid?
        """
        Thread target for populating new object with progress indicator.
        """
        # mustn't use tailbone web session here
        session = RattailSession()
        obj = session.query(self.model_class).get(uuid)
        try:
            self.populate_object(session, obj, progress=progress)
        except Exception as error:
            session.rollback()
            msg = "{} population failed".format(self.get_model_title())
            log.warning("{}: {}".format(msg, obj), exc_info=True)
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "{}: {} {}".format(msg, error.__class__.__name__, error)
                progress.session.save()
            return

        session.commit()
        session.refresh(obj)
        session.close()

        # finalize progress
        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = self.get_action_url('view', obj)
            progress.session.save()

    def populate_object(self, session, obj, progress=None):
        """
        You must define this if new objects require population.
        """
        raise NotImplementedError

    def view(self, instance=None):
        """
        View for viewing details of an existing model record.
        """
        self.viewing = True
        use_buefy = self.get_use_buefy()
        if instance is None:
            instance = self.get_instance()
        form = self.make_form(instance)
        if self.has_rows:

            # must make grid prior to redirecting from filter reset, b/c the
            # grid will detect the filter reset request and store defaults in
            # the session, that way redirect will then show The Right Thing
            grid = self.make_row_grid(instance=instance)

            # If user just refreshed the page with a reset instruction, issue a
            # redirect in order to clear out the query string.
            if self.request.GET.get('reset-to-default-filters') == 'true':
                return self.redirect(self.request.current_route_url(_query=None))

            # return grid only, if partial page was requested
            if self.request.params.get('partial'):
                if use_buefy:
                    # render grid data only, as JSON
                    return render_to_response('json', grid.get_buefy_data(),
                                              request=self.request)
                else: # just do traditional thing, render grid HTML
                    self.request.response.content_type = str('text/html')
                    self.request.response.text = grid.render_grid()
                    return self.request.response

        context = {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_editable': self.editable_instance(instance),
            'instance_deletable': self.deletable_instance(instance),
            'form': form,
        }
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()

        if self.has_rows:
            if use_buefy:
                context['rows_grid'] = grid
                context['rows_grid_tools'] = HTML(self.make_row_grid_tools(instance) or '').strip()
            else:
                context['rows_grid'] = grid.render_complete(allow_save_defaults=False,
                                                            tools=self.make_row_grid_tools(instance))

        return self.render_to_response('view', context)

    def image(self):
        """
        View which renders the object's image as a response.
        """
        obj = self.get_instance()
        image_bytes = self.get_image_bytes(obj)
        if not image_bytes:
            raise self.notfound()
        # TODO: how to properly detect image type?
        self.request.response.content_type = str('image/jpeg')
        self.request.response.body = image_bytes
        return self.request.response

    def get_image_bytes(self, obj):
        raise NotImplementedError

    def thumbnail(self):
        """
        View which renders the object's thumbnail image as a response.
        """
        obj = self.get_instance()
        image_bytes = self.get_thumbnail_bytes(obj)
        if not image_bytes:
            raise self.notfound()
        # TODO: how to properly detect image type?
        self.request.response.content_type = str('image/jpeg')
        self.request.response.body = image_bytes
        return self.request.response

    def get_thumbnail_bytes(self, obj):
        raise NotImplementedError

    def clone(self):
        """
        View for cloning an object's data into a new object.
        """
        self.viewing = True
        instance = self.get_instance()
        form = self.make_form(instance)
        self.configure_clone_form(form)
        if self.request.method == 'POST' and self.request.POST.get('clone') == 'clone':
            cloned = self.clone_instance(instance)
            return self.redirect(self.get_action_url('view', cloned))
        return self.render_to_response('clone', {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_url': self.get_action_url('view', instance),
            'form': form,
        })

    def configure_clone_form(self, form):
        pass

    def clone_instance(self, instance):
        raise NotImplementedError

    def touch(self):
        """
        View for "touching" an object so as to trigger datasync logic for it.
        Useful instead of actually "editing" the object, which is generally the
        alternative.
        """
        obj = self.get_instance()
        change = self.touch_instance(obj)
        self.request.session.flash("{} has been touched: {}".format(
            self.get_model_title(), self.get_instance_title(obj)))
        return self.redirect(self.get_action_url('view', obj))

    def touch_instance(self, obj):
        """
        Perform actual "touch" logic for the given object.  Must return the
        :class:`rattail:~rattail.db.model.Change` record involved.
        """
        change = model.Change()
        change.class_name = obj.__class__.__name__
        change.instance_uuid = obj.uuid
        change = self.Session.merge(change)
        change.deleted = False
        return change

    def versions(self):
        """
        View to list version history for an object.
        """
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)
        grid = self.make_version_grid(instance=instance)

        # return grid only, if partial page was requested
        if self.request.params.get('partial'):
            self.request.response.content_type = b'text/html'
            self.request.response.text = grid.render_grid()
            return self.request.response

        return self.render_to_response('versions', {
            'instance': instance,
            'instance_title': instance_title,
            'instance_url': self.get_action_url('view', instance),
            'grid': grid,
        })

    @classmethod
    def get_version_grid_key(cls):
        """
        Returns the unique key to be used for the version grid, for caching
        sort/filter options etc.
        """
        if hasattr(cls, 'version_grid_key'):
            return cls.version_grid_key
        return '{}.history'.format(cls.get_route_prefix())

    def get_version_data(self, instance):
        """
        Generate the base data set for the version grid.
        """
        model_class = self.get_model_class()
        transaction_class = continuum.transaction_class(model_class)
        query = model_transaction_query(self.Session(), instance, model_class,
                                        child_classes=self.normalize_version_child_classes())
        return query.order_by(transaction_class.issued_at.desc())

    def get_version_child_classes(self):
        """
        If applicable, should return a list of child classes which should be
        considered when querying for version history of an object.
        """
        return []

    def normalize_version_child_classes(self):
        classes = []
        for cls in self.get_version_child_classes():
            if not isinstance(cls, tuple):
                cls = (cls, 'uuid', 'uuid')
            elif len(cls) == 2:
                cls = tuple([cls[0], cls[1], 'uuid'])
            classes.append(cls)
        return classes

    def view_version(self):
        """
        View showing diff details of a particular object version.
        """
        instance = self.get_instance()
        model_class = self.get_model_class()
        route_prefix = self.get_route_prefix()
        Transaction = continuum.transaction_class(model_class)
        transactions = model_transaction_query(self.Session(), instance, model_class,
                                               child_classes=self.normalize_version_child_classes())
        transaction_id = self.request.matchdict['txnid']
        transaction = transactions.filter(Transaction.id == transaction_id).first()
        if not transaction:
            return self.notfound()
        older = transactions.filter(Transaction.issued_at <= transaction.issued_at)\
                            .filter(Transaction.id != transaction_id)\
                            .order_by(Transaction.issued_at.desc())\
                            .first()
        newer = transactions.filter(Transaction.issued_at >= transaction.issued_at)\
                            .filter(Transaction.id != transaction_id)\
                            .order_by(Transaction.issued_at)\
                            .first()

        instance_title = self.get_instance_title(instance)

        prev_url = next_url = None
        if older:
            prev_url = self.request.route_url('{}.version'.format(route_prefix), uuid=instance.uuid, txnid=older.id)
        if newer:
            next_url = self.request.route_url('{}.version'.format(route_prefix), uuid=instance.uuid, txnid=newer.id)

        return self.render_to_response('view_version', {
            'instance': instance,
            'instance_title': "{} (history)".format(instance_title),
            'instance_title_normal': instance_title,
            'instance_url': self.get_action_url('versions', instance),
            'transaction': transaction,
            'changed': localtime(self.rattail_config, transaction.issued_at, from_utc=True),
            'versions': self.get_relevant_versions(transaction, instance),
            'show_prev_next': True,
            'prev_url': prev_url,
            'next_url': next_url,
            'previous_transaction': older,
            'next_transaction': newer,
            'title_for_version': self.title_for_version,
            'fields_for_version': self.fields_for_version,
            'continuum': continuum,
        })

    def title_for_version(self, version):
        cls = continuum.parent_class(version.__class__)
        return cls.get_model_title()

    def fields_for_version(self, version):
        mapper = orm.class_mapper(version.__class__)
        fields = sorted(mapper.columns.keys())
        fields.remove('transaction_id')
        fields.remove('end_transaction_id')
        fields.remove('operation_type')
        return fields

    def get_relevant_versions(self, transaction, instance):
        versions = []
        version_cls = self.get_model_version_class()
        query = self.Session.query(version_cls)\
                            .filter(version_cls.transaction == transaction)\
                            .filter(version_cls.uuid == instance.uuid)
        versions.extend(query.all())
        for cls, foreign_attr, primary_attr in self.normalize_version_child_classes():
            version_cls = continuum.version_class(cls)
            query = self.Session.query(version_cls)\
                                .filter(version_cls.transaction == transaction)\
                                .filter(getattr(version_cls, foreign_attr) == getattr(instance, primary_attr))
            versions.extend(query.all())
        return versions

    def mobile_view(self):
        """
        Mobile view for displaying a single object's details
        """
        self.mobile = True
        self.viewing = True
        instance = self.get_instance()
        form = self.make_mobile_form(instance)

        context = {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_editable': self.editable_instance(instance),
            # 'instance_deletable': self.deletable_instance(instance),
            'form': form,
        }
        if self.has_rows:
            context['model_row_class'] = self.model_row_class
            context['grid'] = self.make_mobile_row_grid(instance=instance)
        return self.render_to_response('view', context, mobile=True)

    def make_mobile_form(self, instance=None, factory=None, fields=None, schema=None, **kwargs):
        """
        Creates a new mobile form for the given model class/instance.
        """
        if factory is None:
            factory = self.get_mobile_form_factory()
        if fields is None:
            fields = self.get_mobile_form_fields()
        if schema is None:
            schema = self.make_mobile_form_schema()

        if not self.creating:
            kwargs['model_instance'] = instance
        kwargs = self.make_mobile_form_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        self.configure_mobile_form(form)
        return form

    def get_mobile_form_fields(self):
        if hasattr(self, 'mobile_form_fields'):
            return self.mobile_form_fields
        # TODO
        # raise NotImplementedError

    def make_mobile_form_schema(self):
        if not self.model_class:
            # TODO
            raise NotImplementedError

    def make_mobile_form_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new mobile forms.
        """
        defaults = {
            'request': self.request,
            'readonly': self.viewing,
            'model_class': getattr(self, 'model_class', None),
            'action_url': self.request.current_route_url(_query=None),
        }
        if self.creating:
            defaults['cancel_url'] = self.get_index_url(mobile=True)
        else:
            instance = kwargs['model_instance']
            defaults['cancel_url'] = self.get_action_url('view', instance, mobile=True)
        defaults.update(kwargs)
        return defaults

    def configure_common_form(self, form):
        """
        Configure the form in whatever way is deemed "common" - i.e. where
        configuration should be done the same for desktop and mobile.

        By default this removes the 'uuid' field (if present), sets any primary
        key fields to be readonly (if we have a :attr:`model_class` and are in
        edit mode), and sets labels as defined by the master class hierarchy.
        """
        form.remove_field('uuid')

        if self.editing:
            model_class = self.get_model_class(error=False)
            if model_class:
                # set readonly for all primary key fields
                mapper = orm.class_mapper(model_class)
                for key in mapper.primary_key:
                    for field in form.fields:
                        if field == key.name:
                            form.set_readonly(field)
                            break

        self.set_labels(form)

    def configure_mobile_form(self, form):
        """
        Configure the main "mobile" form for the view's data model.
        """
        self.configure_common_form(form)

    def validate_mobile_form(self, form):
        if form.validate(newstyle=True):
            # TODO: deprecate / remove self.form_deserialized
            self.form_deserialized = form.validated
            return True
        else:
            return False

    def make_mobile_row_form(self, instance=None, factory=None, fields=None, schema=None, **kwargs):
        """
        Creates a new mobile form for the given model class/instance.
        """
        if factory is None:
            factory = self.get_mobile_row_form_factory()
        if fields is None:
            fields = self.get_mobile_row_form_fields()
        if schema is None:
            schema = self.make_mobile_row_form_schema()

        if not self.creating:
            kwargs['model_instance'] = instance
        kwargs = self.make_mobile_row_form_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        self.configure_mobile_row_form(form)
        return form

    def make_quick_row_form(self, instance=None, factory=None, fields=None, schema=None, mobile=False, **kwargs):
        """
        Creates a "quick" form for adding a new row to the given instance.
        """
        if factory is None:
            factory = self.get_quick_row_form_factory(mobile=mobile)
        if fields is None:
            fields = self.get_quick_row_form_fields(mobile=mobile)
        if schema is None:
            schema = self.make_quick_row_form_schema(mobile=mobile)

        kwargs['mobile'] = mobile
        kwargs = self.make_quick_row_form_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        self.configure_quick_row_form(form, mobile=mobile)
        return form

    def get_quick_row_form_factory(self, mobile=False):
        return forms.Form

    def get_quick_row_form_fields(self, mobile=False):
        pass

    def make_quick_row_form_schema(self, mobile=False):
        schema = colander.MappingSchema()
        schema.add(colander.SchemaNode(colander.String(), name='quick_entry'))
        return schema

    def make_quick_row_form_kwargs(self, **kwargs):
        defaults = {
            'request': self.request,
            'model_class': getattr(self, 'model_row_class', None),
            'cancel_url': self.request.get_referrer(),
        }
        defaults.update(kwargs)
        return defaults

    def configure_quick_row_form(self, form, mobile=False):
        pass

    def get_mobile_row_form_fields(self):
        if hasattr(self, 'mobile_row_form_fields'):
            return self.mobile_row_form_fields
        # TODO
        # raise NotImplementedError

    def make_mobile_row_form_schema(self):
        if not self.model_row_class:
            # TODO
            raise NotImplementedError

    def make_mobile_row_form_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new mobile row forms.
        """
        defaults = {
            'request': self.request,
            'mobile': True,
            'readonly': self.viewing,
            'model_class': getattr(self, 'model_row_class', None),
            'action_url': self.request.current_route_url(_query=None),
        }
        if self.creating:
            defaults['cancel_url'] = self.request.get_referrer()
        else:
            instance = kwargs['model_instance']
            defaults['cancel_url'] = self.get_row_action_url('view', instance, mobile=True)
        defaults.update(kwargs)
        return defaults

    def configure_mobile_row_form(self, form):
        """
        Configure the mobile row form.
        """
        # TODO: is any of this stuff from configure_form() needed?
        # if self.editing:
        #     model_class = self.get_model_class(error=False)
        #     if model_class:
        #         mapper = orm.class_mapper(model_class)
        #         for key in mapper.primary_key:
        #             for field in form.fields:
        #                 if field == key.name:
        #                     form.set_readonly(field)
        #                     break
        # form.remove_field('uuid')

        self.set_row_labels(form)

    def validate_mobile_row_form(self, form):
        controls = self.request.POST.items()
        try:
            self.form_deserialized = form.validate(controls)
        except deform.ValidationFailure:
            return False
        return True

    def validate_quick_row_form(self, form):
        return form.validate(newstyle=True)

    def get_mobile_row_data(self, parent):
        query = self.get_row_data(parent)
        return self.sort_mobile_row_data(query)

    def sort_mobile_row_data(self, query):
        return query

    def mobile_row_route_url(self, route_name, **kwargs):
        route_name = 'mobile.{}.{}_row'.format(self.get_route_prefix(), route_name)
        return self.request.route_url(route_name, **kwargs)

    def mobile_view_row(self):
        """
        Mobile view for row items
        """
        self.mobile = True
        self.viewing = True
        row = self.get_row_instance()
        parent = self.get_parent(row)
        form = self.make_mobile_row_form(row)
        context = {
            'row': row,
            'parent_instance': parent,
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent, mobile=True),
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'instance_editable': self.row_editable(row),
            'parent_model_title': self.get_model_title(),
            'form': form,
        }
        return self.render_to_response('view_row', context, mobile=True)
        
    def make_default_row_grid_tools(self, obj):
        if self.rows_creatable:
            link = tags.link_to("Create a new {}".format(self.get_row_model_title()),
                                self.get_action_url('create_row', obj))
            return HTML.tag('p', c=[link])

    def make_row_grid_tools(self, obj):
        return self.make_default_row_grid_tools(obj)

    # TODO: depracate / remove this
    def get_effective_row_query(self):
        """
        Convenience method which returns the "effective" query for the master
        grid, filtered and sorted to match what would show on the UI, but not
        paged etc.
        """
        return self.get_effective_row_data(sort=False)

    def get_row_data(self, instance):
        """
        Generate the base data set for a rows grid.
        """
        raise NotImplementedError

    def get_effective_row_data(self, session=None, sort=False, **kwargs):
        """
        Convenience method which returns the "effective" data for the row grid,
        filtered (and optionally sorted) to match what would show on the UI,
        but not paged.
        """
        if session is None:
            session = self.Session()
        kwargs.setdefault('pageable', False)
        kwargs.setdefault('sortable', sort)
        grid = self.make_row_grid(session=session, **kwargs)
        return grid.make_visible_data()

    @classmethod
    def get_row_url_prefix(cls):
        """
        Returns a prefix which (by default) applies to all URLs provided by the
        master view class, for "row" views, e.g. '/products/rows'.
        """
        return getattr(cls, 'row_url_prefix', '{}/rows'.format(cls.get_url_prefix()))

    @classmethod
    def get_row_permission_prefix(cls):
        """
        Permission prefix specific to the row-level data for this batch type,
        e.g. ``'vendorcatalogs.rows'``.
        """
        return "{}.rows".format(cls.get_permission_prefix())

    def row_editable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def row_edit_action_url(self, row, i):
        if self.row_editable(row):
            return self.get_row_action_url('edit', row)

    def row_delete_action_url(self, row, i):
        if self.row_deletable(row):
            return self.get_row_action_url('delete', row)

    def row_grid_row_attrs(self, row, i):
        return {}

    @classmethod
    def get_row_model_title(cls):
        if hasattr(cls, 'row_model_title'):
            return cls.row_model_title
        return "{} Row".format(cls.get_model_title())

    @classmethod
    def get_row_model_title_plural(cls):
        if hasattr(cls, 'row_model_title_plural'):
            return cls.row_model_title_plural
        return "{} Rows".format(cls.get_model_title())

    def view_index(self):
        """
        View a record according to its grid index.
        """
        try:
            index = int(self.request.GET['index'])
        except (KeyError, ValueError):
            return self.redirect(self.get_index_url())
        if index < 1:
            return self.redirect(self.get_index_url())
        data = self.get_effective_data()
        try:
            instance = data[index-1]
        except IndexError:
            return self.redirect(self.get_index_url())
        self.grid_index = index
        if hasattr(data, 'count'):
            self.grid_count = data.count()
        else:
            self.grid_count = len(data)
        return self.view(instance)

    def download(self):
        """
        View for downloading a data file.
        """
        obj = self.get_instance()
        filename = self.request.GET.get('filename', None)
        if not filename:
            raise self.notfound()
        path = self.download_path(obj, filename)
        response = FileResponse(path, request=self.request)
        response.content_length = os.path.getsize(path)
        content_type = self.download_content_type(path, filename)
        if content_type:
            if six.PY3:
                response.content_type = content_type
            else:
                response.content_type = six.binary_type(content_type)

        # content-disposition
        filename = os.path.basename(path)
        if six.PY2:
            filename = filename.encode('ascii', 'replace')
        response.content_disposition = str('attachment; filename="{}"'.format(filename))

        return response

    def download_content_type(self, path, filename):
        """
        Return a content type for a file download, if known.
        """

    def edit(self):
        """
        View for editing an existing model record.
        """
        self.editing = True
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)

        if not self.editable_instance(instance):
            self.request.session.flash("Edit is not permitted for {}: {}".format(
                self.get_model_title(), instance_title), 'error')
            return self.redirect(self.get_action_url('view', instance))

        form = self.make_form(instance)

        if self.request.method == 'POST':
            if self.validate_form(form):
                self.save_edit_form(form)
                # note we must fetch new instance title, in case it changed
                self.request.session.flash("{} has been updated: {}".format(
                    self.get_model_title(), self.get_instance_title(instance)))
                return self.redirect_after_edit(instance)

        context = {
            'instance': instance,
            'instance_title': instance_title,
            'instance_deletable': self.deletable_instance(instance),
            'form': form,
        }
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response('edit', context)

    def mobile_edit(self):
        """
        Mobile view for editing an existing model record.
        """
        self.mobile = True
        self.editing = True
        obj = self.get_instance()

        if not self.editable_instance(obj):
            msg = "Edit is not permitted for {}: {}".format(
                self.get_model_title(),
                self.get_instance_title(obj))
            self.request.session.flash(msg, 'error')
            return self.redirect(self.get_action_url('view', obj))

        form = self.make_mobile_form(obj)

        if self.request.method == 'POST':
            if self.validate_mobile_form(form):

                # note that save_form() may return alternate object
                obj = self.save_mobile_edit_form(form)

                msg = "{} has been updated: {}".format(
                    self.get_model_title(),
                    self.get_instance_title(obj))
                self.request.session.flash(msg)
                return self.redirect_after_edit(obj, mobile=True)

        context = {
            'instance': obj,
            'instance_title': self.get_instance_title(obj),
            'instance_deletable': self.deletable_instance(obj),
            'instance_url': self.get_action_url('view', obj, mobile=True),
            'form': form,
        }
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response('edit', context, mobile=True)

    def save_edit_form(self, form):
        if not self.mobile:
            uploads = self.normalize_uploads(form)
        obj = self.objectify(form)
        if not self.mobile:
            self.process_uploads(obj, form, uploads)
        self.after_edit(obj)
        self.Session.flush()
        return obj

    def save_mobile_edit_form(self, form):
        return self.save_edit_form(form)

    def redirect_after_edit(self, instance, mobile=False):
        return self.redirect(self.get_action_url('view', instance, mobile=mobile))

    def delete(self):
        """
        View for deleting an existing model record.
        """
        if not self.deletable:
            raise httpexceptions.HTTPForbidden()

        self.deleting = True
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)

        if not self.deletable_instance(instance):
            self.request.session.flash("Deletion is not permitted for {}: {}".format(
                self.get_model_title(), instance_title), 'error')
            return self.redirect(self.get_action_url('view', instance))

        form = self.make_form(instance)

        # TODO: Add better validation, ideally CSRF etc.
        if self.request.method == 'POST':

            # Let derived classes prep for (or cancel) deletion.
            result = self.before_delete(instance)
            if isinstance(result, httpexceptions.HTTPException):
                return result

            self.delete_instance(instance)
            self.request.session.flash("{} has been deleted: {}".format(
                self.get_model_title(), instance_title))
            return self.redirect(self.get_after_delete_url(instance))

        form.readonly = True
        return self.render_to_response('delete', {
            'instance': instance,
            'instance_title': instance_title,
            'form': form})

    def bulk_delete(self):
        """
        Delete all records matching the current grid query
        """
        objects = self.get_effective_data()
        key = '{}.bulk_delete'.format(self.model_class.__tablename__)
        progress = SessionProgress(self.request, key)
        thread = Thread(target=self.bulk_delete_thread, args=(objects, progress))
        thread.start()
        return self.render_progress(progress, {
            'cancel_url': self.get_index_url(),
            'cancel_msg': "Bulk deletion was canceled",
        })

    def bulk_delete_objects(self, session, objects, progress=None):

        def delete(obj, i):
            session.delete(obj)
            if i % 1000 == 0:
                session.flush()

        self.progress_loop(delete, objects, progress,
                           message="Deleting objects")

    def get_bulk_delete_session(self):
        return RattailSession()

    def bulk_delete_thread(self, objects, progress):
        """
        Thread target for bulk-deleting current results, with progress.
        """
        session = self.get_bulk_delete_session()
        objects = objects.with_session(session).all()
        try:
            self.bulk_delete_objects(session, objects, progress=progress)

        # If anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("execution failed for batch results")
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Bulk deletion failed: {}: {}".format(type(error).__name__, error)
                progress.session.save()

        # If no error, check result flag (false means user canceled).
        else:
            session.commit()
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = self.get_index_url()
                progress.session.save()

    def obtain_set(self):
        """
        Obtain the effective "set" (selection) of records from POST data.
        """
        # TODO: should have a cleaner way to parse object uuids?
        uuids = self.request.POST.get('uuids')
        if uuids:
            uuids = uuids.split(',')
            # TODO: probably need to allow override of fetcher callable
            fetcher = lambda uuid: self.Session.query(self.model_class).get(uuid)
            objects = []
            for uuid in uuids:
                obj = fetcher(uuid)
                if obj:
                    objects.append(obj)
            return objects

    def enable_set(self):
        """
        View which can turn ON the 'enabled' flag for a specific set of records.
        """
        objects = self.obtain_set()
        if objects:
            enabled = 0
            for obj in objects:
                if not obj.enabled:
                    obj.enabled = True
                    enabled += 1
            model_title_plural = self.get_model_title_plural()
            self.request.session.flash("Enabled {} {}".format(enabled, model_title_plural))
        return self.redirect(self.get_index_url())

    def disable_set(self):
        """
        View which can turn OFF the 'enabled' flag for a specific set of records.
        """
        objects = self.obtain_set()
        if objects:
            disabled = 0
            for obj in objects:
                if obj.enabled:
                    obj.enabled = False
                    disabled += 1
            model_title_plural = self.get_model_title_plural()
            self.request.session.flash("Disabled {} {}".format(disabled, model_title_plural))
        return self.redirect(self.get_index_url())

    def delete_set(self):
        """
        View which can delete a specific set of records.
        """
        objects = self.obtain_set()
        if objects:
            for obj in objects:
                self.delete_instance(obj)
            model_title_plural = self.get_model_title_plural()
            self.request.session.flash("Deleted {} {}".format(len(objects), model_title_plural))
        return self.redirect(self.get_index_url())

    def oneoff_import(self, importer, host_object=None):
        """
        Basic helper method, to do a one-off import (or export, depending on
        perspective) of the "current instance" object.  Where the data "goes"
        depends on the importer you provide.
        """
        if not host_object:
            host_object = self.get_instance()

        host_data = importer.normalize_host_object(host_object)
        if not host_data:
            return

        key = importer.get_key(host_data)
        local_object = importer.get_local_object(key)
        if local_object:
            if importer.allow_update:
                local_data = importer.normalize_local_object(local_object)
                if importer.data_diffs(local_data, host_data) and importer.allow_update:
                    local_object = importer.update_object(local_object, host_data, local_data)
            return local_object
        elif importer.allow_create:
            return importer.create_object(key, host_data)

    def execute(self):
        """
        Execute an object.
        """
        obj = self.get_instance()
        model_title = self.get_model_title()
        if self.request.method == 'POST':

            progress = self.make_execute_progress(obj)
            kwargs = {'progress': progress}
            thread = Thread(target=self.execute_thread, args=(obj.uuid, self.request.user.uuid), kwargs=kwargs)
            thread.start()

            return self.render_progress(progress, {
                'instance': obj,
                'initial_msg': self.execute_progress_initial_msg,
                'cancel_url': self.get_action_url('view', obj),
                'cancel_msg': "{} execution was canceled".format(model_title),
            }, template=self.execute_progress_template)

        self.request.session.flash("Sorry, you must POST to execute a {}.".format(model_title), 'error')
        return self.redirect(self.get_action_url('view', obj))

    def make_execute_progress(self, obj):
        key = '{}.execute'.format(self.get_grid_key())
        return SessionProgress(self.request, key)

    def execute_thread(self, uuid, user_uuid, progress=None, **kwargs):
        """
        Thread target for executing an object.
        """
        session = RattailSession()
        obj = session.query(self.model_class).get(uuid)
        user = session.query(model.User).get(user_uuid)
        try:
            self.execute_instance(obj, user, progress=progress, **kwargs)

        # If anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("{} failed to execute: {}".format(self.get_model_title(), obj))
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = self.execute_error_message(error)
                progress.session.save()

        # If no error, check result flag (false means user canceled).
        else:
            session.commit()
            session.refresh(obj)
            success_url = self.get_execute_success_url(obj)
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = success_url
                progress.session.save()

    def execute_error_message(self, error):
        return "Execution of {} failed: {}: {}".format(self.get_model_title(),
                                                       type(error).__name__, error)

    def get_execute_success_url(self, obj, **kwargs):
        return self.get_action_url('view', obj, **kwargs)

    def get_merge_fields(self):
        if hasattr(self, 'merge_fields'):
            return self.merge_fields
        mapper = orm.class_mapper(self.get_model_class())
        return mapper.columns.keys()

    def get_merge_coalesce_fields(self):
        if hasattr(self, 'merge_coalesce_fields'):
            return self.merge_coalesce_fields
        return []

    def get_merge_additive_fields(self):
        if hasattr(self, 'merge_additive_fields'):
            return self.merge_additive_fields
        return []

    def merge(self):
        """
        Preview and execute a merge of two records.
        """
        object_to_remove = object_to_keep = None
        if self.request.method == 'POST':
            uuids = self.request.POST.get('uuids', '').split(',')
            if len(uuids) == 2:
                object_to_remove = self.Session.query(self.get_model_class()).get(uuids[0])
                object_to_keep = self.Session.query(self.get_model_class()).get(uuids[1])

                if object_to_remove and object_to_keep and self.request.POST.get('commit-merge') == 'yes':
                    msg = six.text_type(object_to_remove)
                    try:
                        self.validate_merge(object_to_remove, object_to_keep)
                    except Exception as error:
                        self.request.session.flash("Requested merge cannot proceed (maybe swap kept/removed and try again?): {}".format(error), 'error')
                    else:
                        self.merge_objects(object_to_remove, object_to_keep)
                        self.request.session.flash("{} has been merged into {}".format(msg, object_to_keep))
                        return self.redirect(self.get_action_url('view', object_to_keep))

        if not object_to_remove or not object_to_keep or object_to_remove is object_to_keep:
            return self.redirect(self.get_index_url())

        remove = self.get_merge_data(object_to_remove)
        keep = self.get_merge_data(object_to_keep)
        return self.render_to_response('merge', {'object_to_remove': object_to_remove,
                                                 'object_to_keep': object_to_keep,
                                                 'view_url': lambda obj: self.get_action_url('view', obj),
                                                 'merge_fields': self.get_merge_fields(),
                                                 'remove_data': remove,
                                                 'keep_data': keep,
                                                 'resulting_data': self.get_merge_resulting_data(remove, keep)})

    def validate_merge(self, removing, keeping):
        """
        If applicable, your view should override this in order to confirm that
        the requested merge is valid, in your context.  If it is not - for *any
        reason* - you should raise an exception; the type does not matter.
        """

    def get_merge_data(self, obj):
        raise NotImplementedError("please implement `{}.get_merge_data()`".format(self.__class__.__name__))

    def get_merge_resulting_data(self, remove, keep):
        result = dict(keep)
        for field in self.get_merge_coalesce_fields():
            if remove[field] and not keep[field]:
                result[field] = remove[field]
        for field in self.get_merge_additive_fields():
            if isinstance(keep[field], (list, tuple)):
                result[field] = sorted(set(remove[field] + keep[field]))
            else:
                result[field] = remove[field] + keep[field]
        return result

    def merge_objects(self, removing, keeping):
        """
        Merge the two given objects.  You should probably override this;
        default behavior is merely to delete the 'removing' object.
        """
        self.Session.delete(removing)

    ##############################
    # Core Stuff
    ##############################

    @classmethod
    def get_model_class(cls, error=True):
        """
        Returns the data model class for which the master view exists.
        """
        if not hasattr(cls, 'model_class') and error:
            raise NotImplementedError("You must define the `model_class` for: {}".format(cls))
        return getattr(cls, 'model_class', None)

    @classmethod
    def get_model_version_class(cls):
        """
        Returns the version class for the master model class.
        """
        return continuum.version_class(cls.get_model_class())

    @classmethod
    def get_normalized_model_name(cls):
        """
        Returns the "normalized" name for the view's model class.  This will be
        the value of the :attr:`normalized_model_name` attribute if defined;
        otherwise it will be a simple lower-cased version of the associated
        model class name.
        """
        if hasattr(cls, 'normalized_model_name'):
            return cls.normalized_model_name
        return cls.get_model_class().__name__.lower()

    @classmethod
    def get_model_key(cls):
        """
        Return a string name for the primary key of the model class.
        """
        if hasattr(cls, 'model_key'):
            return cls.model_key
        mapper = orm.class_mapper(cls.get_model_class())
        return ','.join([k.key for k in mapper.primary_key])

    @classmethod
    def get_model_title(cls):
        """
        Return a "humanized" version of the model name, for display in templates.
        """
        if hasattr(cls, 'model_title'):
            return cls.model_title

        # model class itself may provide title
        model_class = cls.get_model_class()
        if hasattr(model_class, 'get_model_title'):
            return model_class.get_model_title()

        # otherwise just use model class name
        return model_class.__name__

    @classmethod
    def get_model_title_plural(cls):
        """
        Return a "humanized" (and plural) version of the model name, for
        display in templates.
        """
        if hasattr(cls, 'model_title_plural'):
            return cls.model_title_plural
        try:
            return cls.get_model_class().get_model_title_plural()
        except (NotImplementedError, AttributeError):
            return '{}s'.format(cls.get_model_title())

    @classmethod
    def get_route_prefix(cls):
        """
        Returns a prefix which (by default) applies to all routes provided by
        the master view class.  This is the plural, lower-cased name of the
        model class by default, e.g. 'products'.
        """
        model_name = cls.get_normalized_model_name()
        return getattr(cls, 'route_prefix', '{0}s'.format(model_name))

    @classmethod
    def get_url_prefix(cls):
        """
        Returns a prefix which (by default) applies to all URLs provided by the
        master view class.  By default this is the route prefix, preceded by a
        slash, e.g. '/products'.
        """
        return getattr(cls, 'url_prefix', '/{0}'.format(cls.get_route_prefix()))

    @classmethod
    def get_template_prefix(cls):
        """
        Returns a prefix which (by default) applies to all templates required by
        the master view class.  This uses the URL prefix by default.
        """
        return getattr(cls, 'template_prefix', cls.get_url_prefix())

    @classmethod
    def get_permission_prefix(cls):
        """
        Returns a prefix which (by default) applies to all permissions leveraged by
        the master view class.  This uses the route prefix by default.
        """
        return getattr(cls, 'permission_prefix', cls.get_route_prefix())

    def get_index_url(self, mobile=False, **kwargs):
        """
        Returns the master view's index URL.
        """
        route = self.get_route_prefix()
        if mobile:
            route = 'mobile.{}'.format(route)
        return self.request.route_url(route)

    @classmethod
    def get_index_title(cls):
        """
        Returns the title for the index page.
        """
        return getattr(cls, 'index_title', cls.get_model_title_plural())

    def get_action_url(self, action, instance, mobile=False, **kwargs):
        """
        Generate a URL for the given action on the given instance
        """
        kw = self.get_action_route_kwargs(instance)
        kw.update(kwargs)
        route_prefix = self.get_route_prefix()
        if mobile:
            route_prefix = 'mobile.{}'.format(route_prefix)
        return self.request.route_url('{}.{}'.format(route_prefix, action), **kw)

    def get_help_url(self):
        """
        May return a "help URL" if applicable.  Default behavior is to simply
        return the value of :attr:`help_url` (regardless of which view is in
        effect), which in turn defaults to ``None``.  If an actual URL is
        returned, then a Help button will be shown in the page header;
        otherwise it is not shown.

        This method is invoked whenever a template is rendered for a response,
        so if you like you can return a different help URL depending on which
        type of CRUD view is in effect, etc.
        """
        return self.help_url

    def render_to_response(self, template, data, mobile=False):
        """
        Return a response with the given template rendered with the given data.
        Note that ``template`` must only be a "key" (e.g. 'index' or 'view').
        First an attempt will be made to render using the :attr:`template_prefix`.
        If that doesn't work, another attempt will be made using '/master' as
        the template prefix.
        """
        context = {
            'master': self,
            'use_buefy': self.get_use_buefy(),
            'mobile': mobile,
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'route_prefix': self.get_route_prefix(),
            'permission_prefix': self.get_permission_prefix(),
            'index_title': self.get_index_title(),
            'index_url': self.get_index_url(mobile=mobile),
            'action_url': self.get_action_url,
            'grid_index': self.grid_index,
            'help_url': self.get_help_url(),
            'quickie': None,
        }

        if self.expose_quickie_search:
            context['quickie'] = Object(
                url=self.get_quickie_url(),
                perm=self.get_quickie_perm(),
                placeholder=self.get_quickie_placeholder(),
            )

        if self.grid_index:
            context['grid_count'] = self.grid_count

        if self.has_rows:
            context['row_permission_prefix'] = self.get_row_permission_prefix()
            context['row_model_title'] = self.get_row_model_title()
            context['row_model_title_plural'] = self.get_row_model_title_plural()
            context['row_action_url'] = self.get_row_action_url

            if mobile and self.viewing and self.mobile_rows_quickable:

                # quick row does *not* mimic keyboard wedge by default, but can
                context['quick_row_keyboard_wedge'] = False

                # quick row does *not* use autocomplete by default, but can
                context['quick_row_autocomplete'] = False
                context['quick_row_autocomplete_url'] = '#'

        context.update(data)
        context.update(self.template_kwargs(**context))
        if hasattr(self, 'template_kwargs_{}'.format(template)):
            context.update(getattr(self, 'template_kwargs_{}'.format(template))(**context))
        if mobile and hasattr(self, 'mobile_template_kwargs_{}'.format(template)):
            context.update(getattr(self, 'mobile_template_kwargs_{}'.format(template))(**context))

        # First try the template path most specific to the view.
        if mobile:
            mako_path = '/mobile{}/{}.mako'.format(self.get_template_prefix(), template)
        else:
            mako_path = '{}/{}.mako'.format(self.get_template_prefix(), template)
        try:
            return render_to_response(mako_path, context, request=self.request)

        except IOError:

            # Failing that, try one or more fallback templates.
            for fallback in self.get_fallback_templates(template, mobile=mobile):
                try:
                    return render_to_response(fallback, context, request=self.request)
                except IOError:
                    pass

            # If we made it all the way here, we found no templates at all, in
            # which case re-attempt the first and let that error raise on up.
            return render_to_response('{}/{}.mako'.format(self.get_template_prefix(), template),
                                      context, request=self.request)

    # TODO: merge this logic with render_to_response()
    def render(self, template, data):
        """
        Render the given template with the given context data.
        """
        context = {
            'master': self,
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'route_prefix': self.get_route_prefix(),
            'permission_prefix': self.get_permission_prefix(),
            'index_title': self.get_index_title(),
            'index_url': self.get_index_url(),
            'action_url': self.get_action_url,
        }
        context.update(data)

        # First try the template path most specific to the view.
        try:
            return render('{}/{}.mako'.format(self.get_template_prefix(), template),
                          context, request=self.request)

        except IOError:

            # Failing that, try one or more fallback templates.
            for fallback in self.get_fallback_templates(template):
                try:
                    return render(fallback, context, request=self.request)
                except IOError:
                    pass

            # If we made it all the way here, we found no templates at all, in
            # which case re-attempt the first and let that error raise on up.
            return render('{}/{}.mako'.format(self.get_template_prefix(), template),
                          context, request=self.request)

    def get_fallback_templates(self, template, mobile=False):
        if mobile:
            return ['/mobile/master/{}.mako'.format(template)]
        return ['/master/{}.mako'.format(template)]

    def template_kwargs(self, **kwargs):
        """
        Supplement the template context, for all views.
        """
        return kwargs

    ##############################
    # Grid Stuff
    ##############################

    @classmethod
    def get_grid_key(cls):
        """
        Returns the unique key to be used for the grid, for caching sort/filter
        options etc.
        """
        if hasattr(cls, 'grid_key'):
            return cls.grid_key
        # default previously came from cls.get_normalized_model_name() but this is hopefully better
        return cls.get_route_prefix()

    def get_row_grid_key(self):
        return '{}.{}'.format(self.get_grid_key(), self.request.matchdict[self.get_model_key()])

    def get_grid_actions(self):
        main, more = self.get_main_actions(), self.get_more_actions()
        if len(more) == 1:
            main, more = main + more, []
        if len(main + more) <= 3:
            main, more = main + more, []
        return main, more

    def get_row_attrs(self, row, i):
        """
        Returns a dict of HTML attributes which is to be applied to the row's
        ``<tr>`` element.  Note that ``i`` will be a 1-based index value for
        the row within its table.  The meaning of ``row`` is basically not
        defined; it depends on the type of data the grid deals with.
        """
        if callable(self.row_attrs):
            attrs = self.row_attrs(row, i)
        else:
            attrs = dict(self.row_attrs)
        if self.mergeable:
            attrs['data-uuid'] = row.uuid
        return attrs

    def get_cell_attrs(self, row, column):
        """
        Returns a dictionary of HTML attributes which should be applied to the
        ``<td>`` element in which the given row and column "intersect".
        """
        if callable(self.cell_attrs):
            return self.cell_attrs(row, column)
        return self.cell_attrs

    def get_main_actions(self):
        """
        Return a list of 'main' actions for the grid.
        """
        actions = []
        prefix = self.get_permission_prefix()
        use_buefy = self.get_use_buefy()
        if self.viewable and self.request.has_perm('{}.view'.format(prefix)):
            url = self.get_view_index_url if self.use_index_links else None
            icon = 'eye' if use_buefy else 'zoomin'
            actions.append(self.make_action('view', icon=icon, url=url))
        return actions

    def get_view_index_url(self, row, i):
        route = '{}.view_index'.format(self.get_route_prefix())
        return '{}?index={}'.format(self.request.route_url(route), self.first_visible_grid_index + i - 1)

    def get_more_actions(self):
        """
        Return a list of 'more' actions for the grid.
        """
        actions = []
        prefix = self.get_permission_prefix()
        use_buefy = self.get_use_buefy()

        # Edit
        if self.editable and self.request.has_perm('{}.edit'.format(prefix)):
            icon = 'edit' if use_buefy else 'pencil'
            actions.append(self.make_action('edit', icon=icon, url=self.default_edit_url))

        # Delete
        if self.deletable and self.request.has_perm('{}.delete'.format(prefix)):
            kwargs = {}
            if use_buefy and self.delete_confirm == 'simple':
                kwargs['click_handler'] = 'deleteObject'
            actions.append(self.make_action('delete', icon='trash', url=self.default_delete_url, **kwargs))

        return actions

    def default_edit_url(self, row, i=None):
        if self.editable_instance(row):
            return self.request.route_url('{}.edit'.format(self.get_route_prefix()),
                                          **self.get_action_route_kwargs(row))

    def default_delete_url(self, row, i=None):
        if self.deletable_instance(row):
            return self.request.route_url('{}.delete'.format(self.get_route_prefix()),
                                          **self.get_action_route_kwargs(row))

    def make_action(self, key, url=None, **kwargs):
        """
        Make a new :class:`GridAction` instance for the current grid.
        """
        if url is None:
            route = '{}.{}'.format(self.get_route_prefix(), key)
            url = lambda r, i: self.request.route_url(route, **self.get_action_route_kwargs(r))
        return grids.GridAction(key, url=url, **kwargs)

    def get_action_route_kwargs(self, row):
        """
        Hopefully generic kwarg generator for basic action routes.
        """
        try:
            mapper = orm.object_mapper(row)
        except orm.exc.UnmappedInstanceError:
            return {self.model_key: row[self.model_key]}
        else:
            keys = [k.key for k in mapper.primary_key]
            values = [getattr(row, k) for k in keys]
            return dict(zip(keys, values))

    def get_data(self, session=None):
        """
        Generate the base data set for the grid.  This typically will be a
        SQLAlchemy query against the view's model class, but subclasses may
        override this to support arbitrary data sets.

        Note that if your view is typical and uses a SA model, you should not
        override this methid, but override :meth:`query()` instead.
        """
        if session is None:
            session = self.Session()
        return self.query(session)

    def query(self, session):
        """
        Produce the initial/base query for the master grid.  By default this is
        simply a query against the model class, but you may override as
        necessary to apply any sort of pre-filtering etc.  This is useful if
        say, you don't ever want to show records of a certain type to non-admin
        users.  You would modify the base query to hide what you wanted,
        regardless of the user's filter selections.
        """
        return session.query(self.get_model_class())

    def get_effective_query(self, session=None, **kwargs):
        return self.get_effective_data(session=session, **kwargs)

    def checkbox(self, instance):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        rendererd for the given row.  Default implementation returns ``True``
        in all cases.
        """
        return True

    def checked(self, instance):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        checked by default, for the given row.  Default implementation returns
        ``False`` in all cases.
        """
        return False

    def results_csv(self):
        """
        Download current list results as CSV
        """
        results = self.get_effective_data()
        fields = self.get_csv_fields()
        data = six.StringIO()
        writer = UnicodeDictWriter(data, fields)
        writer.writeheader()
        for obj in results:
            writer.writerow(self.get_csv_row(obj, fields))
        response = self.request.response
        if six.PY3:
            response.text = data.getvalue()
            response.content_type = 'text/csv'
            response.content_disposition = 'attachment; filename={}.csv'.format(self.get_grid_key())
        else:
            response.body = data.getvalue()
            response.content_type = b'text/csv'
            response.content_disposition = b'attachment; filename={}.csv'.format(self.get_grid_key())
        data.close()
        response.content_length = len(response.body)
        return response

    def results_xlsx(self):
        """
        Download current list results as XLSX.
        """
        results = self.get_effective_data()
        fields = self.get_xlsx_fields()
        path = temp_path(suffix='.xlsx')
        writer = ExcelWriter(path, fields, sheet_title=self.get_model_title_plural())
        writer.write_header()

        rows = []
        for obj in results:
            data = self.get_xlsx_row(obj, fields)
            row = [data[field] for field in fields]
            rows.append(row)

        writer.write_rows(rows)
        writer.auto_freeze()
        writer.auto_filter()
        writer.auto_resize()
        writer.save()

        response = self.request.response
        with open(path, 'rb') as f:
            response.body = f.read()
        os.remove(path)

        response.content_length = len(response.body)
        response.content_type = str('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response.content_disposition = str('attachment; filename={}.xlsx').format(self.get_grid_key())
        return response

    def get_xlsx_fields(self):
        """
        Return the list of fields to be written to XLSX download.
        """
        fields = []
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def get_xlsx_row(self, obj, fields):
        """
        Return a dict for use when writing the row's data to CSV download.
        """
        row = {}
        for field in fields:
            row[field] = getattr(obj, field, None)
        return row

    def row_results_xlsx(self):
        """
        Download current *row* results as XLSX.
        """
        obj = self.get_instance()
        results = self.get_effective_row_data(sort=True)
        fields = self.get_row_xlsx_fields()
        path = temp_path(suffix='.xlsx')
        writer = ExcelWriter(path, fields, sheet_title=self.get_row_model_title_plural())
        writer.write_header()

        rows = []
        for row_obj in results:
            data = self.get_row_xlsx_row(row_obj, fields)
            row = [data[field] for field in fields]
            rows.append(row)

        writer.write_rows(rows)
        writer.auto_freeze()
        writer.auto_filter()
        writer.auto_resize()
        writer.save()

        response = self.request.response
        with open(path, 'rb') as f:
            response.body = f.read()
        os.remove(path)

        response.content_length = len(response.body)
        response.content_type = str('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = self.get_row_results_xlsx_filename(obj)
        response.content_disposition = str('attachment; filename={}'.format(filename))
        return response

    def get_row_xlsx_fields(self):
        """
        Return the list of row fields to be written to XLSX download.
        """
        # TODO: should this be shared at all? in a better way?
        return self.get_row_csv_fields()

    def get_row_xlsx_row(self, row, fields):
        """
        Return a dict for use when writing the row's data to XLSX download.
        """
        xlrow = {}
        for field in fields:
            value = getattr(row, field, None)

            if isinstance(value, GPC):
                value = six.text_type(value)

            elif isinstance(value, datetime.datetime):
                # datetime values we provide to Excel must *not* have time zone info,
                # but we should make sure they're in "local" time zone effectively.
                # note however, this assumes a "naive" time value is in UTC zone!
                if value.tzinfo:
                    value = localtime(self.rattail_config, value, tzinfo=False)
                else:
                    value = localtime(self.rattail_config, value, from_utc=True, tzinfo=False)

            xlrow[field] = value
        return xlrow

    def get_row_results_xlsx_filename(self, obj):
        return '{}.xlsx'.format(self.get_row_grid_key())

    def row_results_csv(self):
        """
        Download current row results data for an object, as CSV
        """
        obj = self.get_instance()
        fields = self.get_row_csv_fields()
        data = six.StringIO()
        writer = UnicodeDictWriter(data, fields)
        writer.writeheader()
        for row in self.get_effective_row_data(sort=True):
            writer.writerow(self.get_row_csv_row(row, fields))
        response = self.request.response
        filename = self.get_row_results_csv_filename(obj)
        if six.PY3:
            response.text = data.getvalue()
            response.content_type = 'text/csv'
            response.content_disposition = 'attachment; filename={}'.format(filename)
        else:
            response.body = data.getvalue()
            response.content_type = b'text/csv'
            response.content_disposition = b'attachment; filename={}'.format(filename)
        data.close()
        response.content_length = len(response.body)
        return response

    def get_row_results_csv_filename(self, instance):
        return '{}.csv'.format(self.get_row_grid_key())

    def get_csv_fields(self):
        """
        Return the list of fields to be written to CSV download.  Default field
        list will be constructed from the underlying table columns.
        """
        fields = []
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def get_row_csv_fields(self):
        """
        Return the list of row fields to be written to CSV download.
        """
        fields = []
        mapper = orm.class_mapper(self.model_row_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def get_csv_row(self, obj, fields):
        """
        Return a dict for use when writing the row's data to CSV download.
        """
        csvrow = {}
        for field in fields:
            value = getattr(obj, field, None)
            if isinstance(value, datetime.datetime):
                # TODO: this assumes value is *always* naive UTC
                value = localtime(self.rattail_config, value, from_utc=True)
            csvrow[field] = '' if value is None else six.text_type(value)
        return csvrow

    def get_row_csv_row(self, row, fields):
        """
        Return a dict for use when writing the row's data to CSV download.
        """
        csvrow = {}
        for field in fields:
            value = getattr(row, field, None)
            if isinstance(value, datetime.datetime):
                # TODO: this assumes value is *always* naive UTC
                value = localtime(self.rattail_config, value, from_utc=True)
            csvrow[field] = '' if value is None else six.text_type(value)
        return csvrow

    ##############################
    # CRUD Stuff
    ##############################

    def get_instance(self):
        """
        Fetch the current model instance by inspecting the route kwargs and
        doing a database lookup.  If the instance cannot be found, raises 404.
        """
        # TODO: this can't handle composite model key..is that needed?
        key = self.request.matchdict[self.get_model_key()]
        instance = self.Session.query(self.get_model_class()).get(key)
        if not instance:
            raise httpexceptions.HTTPNotFound()
        return instance

    def get_instance_title(self, instance):
        """
        Return a "pretty" title for the instance, to be used in the page title etc.
        """
        return six.text_type(instance)

    @classmethod
    def get_form_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        grid instances.
        """
        return getattr(cls, 'form_factory', forms.Form)

    @classmethod
    def get_mobile_form_factory(cls):
        """
        Returns the factory or class which is to be used when creating new
        mobile forms.
        """
        return getattr(cls, 'mobile_form_factory', forms.Form)

    @classmethod
    def get_row_form_factory(cls):
        """
        Returns the factory or class which is to be used when creating new row
        forms.
        """
        return getattr(cls, 'row_form_factory', forms.Form)

    @classmethod
    def get_mobile_row_form_factory(cls):
        """
        Returns the factory or class which is to be used when creating new
        mobile row forms.
        """
        return getattr(cls, 'mobile_row_form_factory', forms.Form)

    def render_downloadable_file(self, obj, field):
        filename = getattr(obj, field)
        if not filename:
            return ""
        path = self.download_path(obj, filename)
        url = self.get_action_url('download', obj, _query={'filename': filename})
        return self.render_file_field(path, url)

    def render_file_field(self, path, url=None, filename=None):
        """
        Convenience for rendering a file with optional download link
        """
        if not filename:
            filename = os.path.basename(path)
        content = "{} ({})".format(filename, self.readable_size(path))
        if url:
            return tags.link_to(content, url)
        return content

    def readable_size(self, path):
        # TODO: this was shamelessly copied from FormAlchemy ...
        length = self.get_size(path)
        if length == 0:
            return '0 KB'
        if length <= 1024:
            return '1 KB'
        if length > 1048576:
            return '%0.02f MB' % (length / 1048576.0)
        return '%0.02f KB' % (length / 1024.0)

    def get_size(self, path):
        try:
            return os.path.getsize(path)
        except os.error:
            return 0

    def make_form(self, instance=None, factory=None, fields=None, schema=None, make_kwargs=None, configure=None, **kwargs):
        """
        Creates a new form for the given model class/instance
        """
        if factory is None:
            factory = self.get_form_factory()
        if fields is None:
            fields = self.get_form_fields()
        if schema is None:
            schema = self.make_form_schema()
        if make_kwargs is None:
            make_kwargs = self.make_form_kwargs
        if configure is None:
            configure = self.configure_form

        # TODO: SQLAlchemy class instance is assumed *unless* we get a dict
        # (seems like we should be smarter about this somehow)
        # if not self.creating and not isinstance(instance, dict):
        if not self.creating:
            kwargs['model_instance'] = instance
        kwargs = make_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        configure(form)
        return form

    def get_form_fields(self):
        if hasattr(self, 'form_fields'):
            return self.form_fields
        # TODO
        # raise NotImplementedError

    def make_form_schema(self):
        if not self.model_class:
            # TODO
            raise NotImplementedError

    def make_form_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new form instances.
        """
        defaults = {
            'request': self.request,
            'readonly': self.viewing,
            'model_class': getattr(self, 'model_class', None),
            'action_url': self.request.current_route_url(_query=None),
            'use_buefy': self.get_use_buefy(),
        }
        if self.creating:
            kwargs.setdefault('cancel_url', self.get_index_url())
        else:
            instance = kwargs['model_instance']
            kwargs.setdefault('cancel_url', self.get_action_url('view', instance))
        defaults.update(kwargs)
        return defaults

    def configure_form(self, form):
        """
        Configure the main "desktop" form for the view's data model.
        """
        self.configure_common_form(form)

    def validate_form(self, form):
        if form.validate(newstyle=True):
            self.form_deserialized = form.validated
            return True
        return False

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        obj = form.schema.objectify(data, context=form.model_instance)
        if self.is_contact:
            obj = self.objectify_contact(obj, data)
        return obj

    def objectify_contact(self, contact, data):

        if 'default_email' in data:
            address = data['default_email']
            if contact.emails:
                if address:
                    email = contact.emails[0]
                    email.address = address
                else:
                    contact.emails.pop(0)
            elif address:
                contact.add_email_address(address)

        if 'default_phone' in data:
            number = data['default_phone']
            if contact.phones:
                if number:
                    phone = contact.phones[0]
                    phone.number = number
                else:
                    contact.phones.pop(0)
            elif number:
                contact.add_phone_number(number)

        address_fields = ('address_street',
                          'address_street2',
                          'address_city',
                          'address_state',
                          'address_zipcode')

        addr = dict([(field, data[field])
                     for field in address_fields
                     if field in data])

        if any(addr.values()):
            # we strip 'address_' prefix from fields
            addr = dict([(field[8:], value)
                         for field, value in addr.items()])
            if contact.addresses:
                address = contact.addresses[0]
                for field, value in addr.items():
                    setattr(address, field, value)
            else:
                contact.add_mailing_address(**addr)

        elif any([field in data for field in address_fields]) and contact.addresses:
            contact.addresses.pop()

        return contact

    def save_form(self, form):
        form.save()

    def before_create(self, form):
        """
        Event hook, called just after the form to create a new instance has
        been validated, but prior to the form itself being saved.
        """

    def after_create(self, instance):
        """
        Event hook, called just after a new instance is saved.
        """

    def editable_instance(self, instance):
        """
        Returns boolean indicating whether or not the given instance can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def after_edit(self, instance):
        """
        Event hook, called just after an existing instance is saved.
        """

    def deletable_instance(self, instance):
        """
        Returns boolean indicating whether or not the given instance can be
        considered "deletable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def before_delete(self, instance):
        """
        Event hook, called just before deletion is attempted.
        """

    def delete_instance(self, instance):
        """
        Delete the instance, or mark it as deleted, or whatever you need to do.
        """
        # Flush immediately to force any pending integrity errors etc.; that
        # way we don't set flash message until we know we have success.
        self.Session.delete(instance)
        self.Session.flush()

    def get_after_delete_url(self, instance):
        """
        Returns the URL to which the user should be redirected after
        successfully "deleting" the given instance.
        """
        if hasattr(self, 'after_delete_url'):
            if callable(self.after_delete_url):
                return self.after_delete_url(instance)
            return self.after_delete_url
        return self.get_index_url()

    ##############################
    # Associated Rows Stuff
    ##############################

    def create_row(self):
        """
        View for creating a new row record.
        """
        self.creating = True
        parent = self.get_instance()
        index_url = self.get_action_url('view', parent)
        form = self.make_row_form(self.model_row_class, cancel_url=index_url)
        if self.request.method == 'POST':
            if self.validate_row_form(form):
                self.before_create_row(form)
                obj = self.save_create_row_form(form)
                self.after_create_row(obj)
                return self.redirect_after_create_row(obj)
        return self.render_to_response('create_row', {
            'index_url': index_url,
            'index_title': '{} {}'.format(
                self.get_model_title(),
                self.get_instance_title(parent)),
            'form': form})

    # TODO: still need to verify this logic
    def save_create_row_form(self, form):
        # self.before_create(form)
        # with self.Session().no_autoflush:
        #     obj = self.objectify(form, self.form_deserialized)
        #     self.before_create_flush(obj, form)
        obj = self.objectify(form, self.form_deserialized)
        self.Session.add(obj)
        self.Session.flush()
        return obj

    # def save_create_row_form(self, form):
    #     self.save_row_form(form)

    def before_create_row(self, form):
        pass

    def after_create_row(self, row_object):
        pass

    def redirect_after_create_row(self, row, mobile=False):
        return self.redirect(self.get_row_action_url('view', row, mobile=mobile))

    def mobile_create_row(self):
        """
        Mobile view for creating a new row object
        """
        self.mobile = True
        self.creating = True
        parent = self.get_instance()
        instance_url = self.get_action_url('view', parent, mobile=True)
        form = self.make_mobile_row_form(self.model_row_class, cancel_url=instance_url)
        if self.request.method == 'POST':
            if self.validate_mobile_row_form(form):
                self.before_create_row(form)
                # let save() return alternate object if necessary
                obj = self.save_create_row_form(form)
                self.after_create_row(obj)
                return self.redirect_after_create_row(obj, mobile=True)
        return self.render_to_response('create_row', {
            'instance_title': self.get_instance_title(parent),
            'instance_url': instance_url,
            'parent_object': parent,
            'form': form,
        }, mobile=True)

    def mobile_quick_row(self):
        """
        Mobile view for "quick" location or creation of a row object
        """
        parent = self.get_instance()
        parent_url = self.get_action_url('view', parent, mobile=True)
        form = self.make_quick_row_form(self.model_row_class, mobile=True, cancel_url=parent_url)
        if self.request.method == 'POST':
            if self.validate_quick_row_form(form):
                row = self.save_quick_row_form(form)
                if not row:
                    self.request.session.flash("Could not locate/create row for entry: "
                                               "{}".format(form.validated['quick_entry']),
                                               'error')
                    return self.redirect(parent_url)
                return self.redirect_after_quick_row(row, mobile=True)
        return self.redirect(parent_url)

    def save_quick_row_form(self, form):
        raise NotImplementedError("You must define `{}:{}.save_quick_row_form()` "
                                  "in order to process quick row forms".format(
                                      self.__class__.__module__,
                                      self.__class__.__name__))

    def redirect_after_quick_row(self, row, mobile=False):
        return self.redirect(self.get_row_action_url('edit', row, mobile=mobile))

    def view_row(self):
        """
        View for viewing details of a single data row.
        """
        self.viewing = True
        row = self.get_row_instance()
        form = self.make_row_form(row)
        parent = self.get_parent(row)
        return self.render_to_response('view_row', {
            'instance': row,
            'instance_title': self.get_instance_title(parent),
            'row_title': self.get_row_instance_title(row),
            'instance_url': self.get_action_url('view', parent),
            'instance_editable': self.row_editable(row),
            'instance_deletable': self.row_deletable(row),
            'rows_creatable': self.rows_creatable and self.rows_creatable_for(parent),
            'model_title': self.get_row_model_title(),
            'model_title_plural': self.get_row_model_title_plural(),
            'parent_instance': parent,
            'parent_model_title': self.get_model_title(),
            'action_url': self.get_row_action_url,
            'form': form})

    def rows_creatable_for(self, instance):
        """
        Returns boolean indicating whether or not the given instance should
        allow new rows to be added to it.
        """
        return True

    def rows_quickable_for(self, instance):
        """
        Must return boolean indicating whether the "quick row" feature should
        be allowed for the given instance.  Returns ``True`` by default.
        """
        return True

    def row_editable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def edit_row(self):
        """
        View for editing an existing model record.
        """
        self.editing = True
        row = self.get_row_instance()
        form = self.make_row_form(row)

        if self.request.method == 'POST':
            if self.validate_row_form(form):
                self.save_edit_row_form(form)
                return self.redirect_after_edit_row(row)

        parent = self.get_parent(row)
        return self.render_to_response('edit_row', {
            'instance': row,
            'row_parent': parent,
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent),
            'parent_instance': parent,
            'instance_title': self.get_row_instance_title(row),
            'instance_deletable': self.row_deletable(row),
            'form': form,
            'dform': form.make_deform_form(),
        })

    def mobile_edit_row(self):
        """
        Mobile view for editing a row object
        """
        self.mobile = True
        self.editing = True
        row = self.get_row_instance()
        instance_url = self.get_row_action_url('view', row, mobile=True)
        form = self.make_mobile_row_form(row)

        if self.request.method == 'POST':
            if self.validate_mobile_row_form(form):
                self.save_edit_row_form(form)
                return self.redirect_after_edit_row(row, mobile=True)

        parent = self.get_parent(row)
        return self.render_to_response('edit_row', {
            'row': row,
            'instance': row,
            'parent_instance': parent,
            'instance_title': self.get_row_instance_title(row),
            'instance_url': instance_url,
            'instance_deletable': self.row_deletable(row),
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent, mobile=True),
            'form': form},
        mobile=True)

    def save_edit_row_form(self, form):
        obj = self.objectify(form, self.form_deserialized)
        self.after_edit_row(obj)
        self.Session.flush()
        return obj

    # def save_row_form(self, form):
    #     form.save()

    def after_edit_row(self, row):
        """
        Event hook, called just after an existing row object is saved.
        """

    def redirect_after_edit_row(self, row, mobile=False):
        return self.redirect(self.get_row_action_url('view', row, mobile=mobile))

    def row_deletable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "deletable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def delete_row_object(self, row):
        """
        Perform the actual deletion of given row object.
        """
        self.Session.delete(row)

    def delete_row(self):
        """
        Desktop view which can "delete" a sub-row from the parent.
        """
        row = self.Session.query(self.model_row_class).get(self.request.matchdict['row_uuid'])
        if not row:
            raise self.notfound()
        self.delete_row_object(row)
        return self.redirect(self.get_action_url('view', self.get_parent(row)))

    def mobile_delete_row(self):
        """
        Mobile view which can "delete" a sub-row from the parent.
        """
        if self.request.method == 'POST':
            parent = self.get_instance()
            row = self.get_row_instance()
            if self.get_parent(row) is not parent:
                raise RuntimeError("Can only delete rows which belong to current object")

            self.delete_row_object(row)
            return self.redirect(self.get_action_url('view', parent, mobile=True))

        self.session.flash("Must POST to delete a row", 'error')
        return self.redirect(self.request.get_referrer(mobile=True))

    def get_parent(self, row):
        raise NotImplementedError

    def get_row_instance_title(self, instance):
        return self.get_row_model_title()

    def get_row_instance(self):
        # TODO: is this right..?
        # key = self.request.matchdict[self.get_model_key()]
        key = self.request.matchdict['row_uuid']
        instance = self.Session.query(self.model_row_class).get(key)
        if not instance:
            raise httpexceptions.HTTPNotFound()
        return instance

    def make_row_form(self, instance=None, factory=None, fields=None, schema=None, **kwargs):
        """
        Creates a new row form for the given model class/instance.
        """
        if factory is None:
            factory = self.get_row_form_factory()
        if fields is None:
            fields = self.get_row_form_fields()
        if schema is None:
            schema = self.make_row_form_schema()

        if not self.creating:
            kwargs['model_instance'] = instance
        kwargs = self.make_row_form_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        self.configure_row_form(form)
        return form

    def get_row_form_fields(self):
        if hasattr(self, 'row_form_fields'):
            return self.row_form_fields
        # TODO
        # raise NotImplementedError

    def make_row_form_schema(self):
        if not self.model_row_class:
            # TODO
            raise NotImplementedError

    def make_row_form_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new row forms.
        """
        defaults = {
            'request': self.request,
            'readonly': self.viewing,
            'model_class': getattr(self, 'model_row_class', None),
            'action_url': self.request.current_route_url(_query=None),
            'use_buefy': self.get_use_buefy(),
        }
        if self.creating:
            kwargs.setdefault('cancel_url', self.request.get_referrer())
        else:
            instance = kwargs['model_instance']
            if 'cancel_url' not in kwargs:
                kwargs['cancel_url'] = self.get_row_action_url('view', instance)
        defaults.update(kwargs)
        return defaults

    def configure_row_form(self, form):
        """
        Configure a row form.
        """
        # TODO: is any of this stuff from configure_form() needed?
        # if self.editing:
        #     model_class = self.get_model_class(error=False)
        #     if model_class:
        #         mapper = orm.class_mapper(model_class)
        #         for key in mapper.primary_key:
        #             for field in form.fields:
        #                 if field == key.name:
        #                     form.set_readonly(field)
        #                     break
        # form.remove_field('uuid')

        self.set_row_labels(form)

    def validate_row_form(self, form):
        if form.validate(newstyle=True):
            self.form_deserialized = form.validated
            return True
        return False

    def get_row_action_url(self, action, row, mobile=False):
        """
        Generate a URL for the given action on the given row.
        """
        route_name = '{}.{}_row'.format(self.get_route_prefix(), action)
        if mobile:
            route_name = 'mobile.{}'.format(route_name)
        return self.request.route_url(route_name, **self.get_row_action_route_kwargs(row))

    def get_row_action_route_kwargs(self, row):
        """
        Hopefully generic kwarg generator for basic action routes.
        """
        # TODO: make this smarter?
        parent = self.get_parent(row)
        return {
            'uuid': parent.uuid,
            'row_uuid': row.uuid,
        }

    def make_diff(self, old_data, new_data, **kwargs):
        return diffs.Diff(old_data, new_data, **kwargs)

    ##############################
    # Config Stuff
    ##############################

    @classmethod
    def defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        rattail_config = config.registry.settings.get('rattail_config')
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()
        if cls.has_rows:
            row_model_title = cls.get_row_model_title()

        config.add_tailbone_permission_group(permission_prefix, model_title_plural, overwrite=False)

        # list/search
        if cls.listable:
            config.add_tailbone_permission(permission_prefix, '{}.list'.format(permission_prefix),
                                           "List / search {}".format(model_title_plural))
            config.add_route(route_prefix, '{}/'.format(url_prefix))
            config.add_view(cls, attr='index', route_name=route_prefix,
                            permission='{}.list'.format(permission_prefix))
            if cls.supports_mobile:
                config.add_route('mobile.{}'.format(route_prefix), '/mobile{}/'.format(url_prefix))
                config.add_view(cls, attr='mobile_index', route_name='mobile.{}'.format(route_prefix),
                                permission='{}.list'.format(permission_prefix))

            if cls.results_downloadable_csv:
                config.add_tailbone_permission(permission_prefix, '{}.results_csv'.format(permission_prefix),
                                               "Download {} as CSV".format(model_title_plural))
                config.add_route('{}.results_csv'.format(route_prefix), '{}/csv'.format(url_prefix))
                config.add_view(cls, attr='results_csv', route_name='{}.results_csv'.format(route_prefix),
                                permission='{}.results_csv'.format(permission_prefix))

            if cls.results_downloadable_xlsx:
                config.add_tailbone_permission(permission_prefix, '{}.results_xlsx'.format(permission_prefix),
                                               "Download {} as XLSX".format(model_title_plural))
                config.add_route('{}.results_xlsx'.format(route_prefix), '{}/xlsx'.format(url_prefix))
                config.add_view(cls, attr='results_xlsx', route_name='{}.results_xlsx'.format(route_prefix),
                                permission='{}.results_xlsx'.format(permission_prefix))

        # quickie (search)
        if cls.supports_quickie_search:
            config.add_tailbone_permission(permission_prefix, '{}.quickie'.format(permission_prefix),
                                           "Do a \"quickie search\" for {}".format(model_title_plural))
            config.add_route('{}.quickie'.format(route_prefix), '{}/quickie'.format(route_prefix),
                             request_method='GET')
            config.add_view(cls, attr='quickie', route_name='{}.quickie'.format(route_prefix),
                            permission='{}.quickie'.format(permission_prefix))

        # create
        if cls.creatable or cls.mobile_creatable:
            config.add_tailbone_permission(permission_prefix, '{}.create'.format(permission_prefix),
                                           "Create new {}".format(model_title))
        if cls.creatable:
            config.add_route('{}.create'.format(route_prefix), '{}/new'.format(url_prefix))
            config.add_view(cls, attr='create', route_name='{}.create'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))
        if cls.mobile_creatable:
            config.add_route('mobile.{}.create'.format(route_prefix), '/mobile{}/new'.format(url_prefix))
            config.add_view(cls, attr='mobile_create', route_name='mobile.{}.create'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

        # populate new object
        if cls.populatable:
            config.add_route('{}.populate'.format(route_prefix), '{}/{{uuid}}/populate'.format(url_prefix))
            config.add_view(cls, attr='populate', route_name='{}.populate'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

        # enable/disable set
        if cls.supports_set_enabled_toggle:
            config.add_tailbone_permission(permission_prefix, '{}.enable_disable_set'.format(permission_prefix),
                                           "Enable / disable set (selection) of {}".format(model_title_plural))
            config.add_route('{}.enable_set'.format(route_prefix), '{}/enable-set'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='enable_set', route_name='{}.enable_set'.format(route_prefix),
                            permission='{}.enable_disable_set'.format(permission_prefix))
            config.add_route('{}.disable_set'.format(route_prefix), '{}/disable-set'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='disable_set', route_name='{}.disable_set'.format(route_prefix),
                            permission='{}.enable_disable_set'.format(permission_prefix))

        # delete set
        if cls.set_deletable:
            config.add_tailbone_permission(permission_prefix, '{}.delete_set'.format(permission_prefix),
                                           "Delete set (selection) of {}".format(model_title_plural))
            config.add_route('{}.delete_set'.format(route_prefix), '{}/delete-set'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='delete_set', route_name='{}.delete_set'.format(route_prefix),
                            permission='{}.delete_set'.format(permission_prefix))

        # bulk delete
        if cls.bulk_deletable:
            config.add_route('{}.bulk_delete'.format(route_prefix), '{}/bulk-delete'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='bulk_delete', route_name='{}.bulk_delete'.format(route_prefix),
                            permission='{}.bulk_delete'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.bulk_delete'.format(permission_prefix),
                                           "Bulk delete {}".format(model_title_plural))

        # merge
        if cls.mergeable:
            config.add_route('{}.merge'.format(route_prefix), '{}/merge'.format(url_prefix))
            config.add_view(cls, attr='merge', route_name='{}.merge'.format(route_prefix),
                            permission='{}.merge'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.merge'.format(permission_prefix),
                                           "Merge 2 {}".format(model_title_plural))

        # view
        if cls.viewable:
            config.add_tailbone_permission(permission_prefix, '{}.view'.format(permission_prefix),
                                           "View details for {}".format(model_title))
            if cls.has_pk_fields:
                config.add_tailbone_permission(permission_prefix, '{}.view_pk_fields'.format(permission_prefix),
                                               "View all PK-type fields for {}".format(model_title_plural))

            # view by grid index
            config.add_route('{}.view_index'.format(route_prefix), '{}/view'.format(url_prefix))
            config.add_view(cls, attr='view_index', route_name='{}.view_index'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

            # view by record key
            config.add_route('{}.view'.format(route_prefix), '{}/{{{}}}'.format(url_prefix, model_key))
            config.add_view(cls, attr='view', route_name='{}.view'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))
            if cls.supports_mobile:
                config.add_route('mobile.{}.view'.format(route_prefix), '/mobile{}/{{{}}}'.format(url_prefix, model_key))
                config.add_view(cls, attr='mobile_view', route_name='mobile.{}.view'.format(route_prefix),
                                permission='{}.view'.format(permission_prefix))

            # version history
            if cls.has_versions and rattail_config and rattail_config.versioning_enabled():
                config.add_tailbone_permission(permission_prefix, '{}.versions'.format(permission_prefix),
                                               "View version history for {}".format(model_title))
                config.add_route('{}.versions'.format(route_prefix), '{}/{{{}}}/versions/'.format(url_prefix, model_key))
                config.add_view(cls, attr='versions', route_name='{}.versions'.format(route_prefix),
                                permission='{}.versions'.format(permission_prefix))
                config.add_route('{}.version'.format(route_prefix), '{}/{{{}}}/versions/{{txnid}}'.format(url_prefix, model_key))
                config.add_view(cls, attr='view_version', route_name='{}.version'.format(route_prefix),
                                permission='{}.versions'.format(permission_prefix))

        # image
        if cls.has_image:
            config.add_route('{}.image'.format(route_prefix), '{}/{{{}}}/image'.format(url_prefix, model_key))
            config.add_view(cls, attr='image', route_name='{}.image'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

        # thumbnail
        if cls.has_thumbnail:
            config.add_route('{}.thumbnail'.format(route_prefix), '{}/{{{}}}/thumbnail'.format(url_prefix, model_key))
            config.add_view(cls, attr='thumbnail', route_name='{}.thumbnail'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

        # clone
        if cls.cloneable:
            config.add_tailbone_permission(permission_prefix, '{}.clone'.format(permission_prefix),
                                           "Clone an existing {0} as a new {0}".format(model_title))
            config.add_route('{}.clone'.format(route_prefix), '{}/{{{}}}/clone'.format(url_prefix, model_key))
            config.add_view(cls, attr='clone', route_name='{}.clone'.format(route_prefix),
                            permission='{}.clone'.format(permission_prefix))

        # touch
        if cls.touchable:
            config.add_tailbone_permission(permission_prefix, '{}.touch'.format(permission_prefix),
                                           "\"Touch\" a {} to trigger datasync for it".format(model_title))
            config.add_route('{}.touch'.format(route_prefix), '{}/{{{}}}/touch'.format(url_prefix, model_key))
            config.add_view(cls, attr='touch', route_name='{}.touch'.format(route_prefix),
                            permission='{}.touch'.format(permission_prefix))

        # download
        if cls.downloadable:
            config.add_route('{}.download'.format(route_prefix), '{}/{{{}}}/download'.format(url_prefix, model_key))
            config.add_view(cls, attr='download', route_name='{}.download'.format(route_prefix),
                            permission='{}.download'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.download'.format(permission_prefix),
                                           "Download associated data for {}".format(model_title))

        # edit
        if cls.editable or cls.mobile_editable:
            config.add_tailbone_permission(permission_prefix, '{}.edit'.format(permission_prefix),
                                           "Edit {}".format(model_title))
        if cls.editable:
            config.add_route('{}.edit'.format(route_prefix), '{}/{{{}}}/edit'.format(url_prefix, model_key))
            config.add_view(cls, attr='edit', route_name='{}.edit'.format(route_prefix),
                            permission='{}.edit'.format(permission_prefix))
        if cls.mobile_editable:
            config.add_route('mobile.{}.edit'.format(route_prefix), '/mobile{}/{{{}}}/edit'.format(url_prefix, model_key))
            config.add_view(cls, attr='mobile_edit', route_name='mobile.{}.edit'.format(route_prefix),
                            permission='{}.edit'.format(permission_prefix))

        # execute
        if cls.executable or cls.mobile_executable:
            config.add_tailbone_permission(permission_prefix, '{}.execute'.format(permission_prefix),
                                           "Execute {}".format(model_title))
        if cls.executable:
            config.add_route('{}.execute'.format(route_prefix), '{}/{{{}}}/execute'.format(url_prefix, model_key))
            config.add_view(cls, attr='execute', route_name='{}.execute'.format(route_prefix),
                            permission='{}.execute'.format(permission_prefix))
        if cls.mobile_executable:
            config.add_route('mobile.{}.execute'.format(route_prefix), '/mobile{}/{{{}}}/execute'.format(url_prefix, model_key))
            config.add_view(cls, attr='mobile_execute', route_name='mobile.{}.execute'.format(route_prefix),
                            permission='{}.execute'.format(permission_prefix))

        # delete
        if cls.deletable:
            config.add_route('{0}.delete'.format(route_prefix), '{0}/{{{1}}}/delete'.format(url_prefix, model_key))
            config.add_view(cls, attr='delete', route_name='{0}.delete'.format(route_prefix),
                            permission='{0}.delete'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{0}.delete'.format(permission_prefix),
                                           "Delete {0}".format(model_title))

        # import batch from file
        if cls.supports_import_batch_from_file:
            config.add_tailbone_permission(permission_prefix, '{}.import_file'.format(permission_prefix),
                                           "Create a new import batch from data file")

        ### sub-rows stuff follows

        # download row results as CSV
        if cls.has_rows and cls.rows_downloadable_csv:
            config.add_tailbone_permission(permission_prefix, '{}.row_results_csv'.format(permission_prefix),
                                           "Download {} results as CSV".format(row_model_title))
            config.add_route('{}.row_results_csv'.format(route_prefix), '{}/{{uuid}}/rows-csv'.format(url_prefix))
            config.add_view(cls, attr='row_results_csv', route_name='{}.row_results_csv'.format(route_prefix),
                            permission='{}.row_results_csv'.format(permission_prefix))

        # download row results as Excel
        if cls.has_rows and cls.rows_downloadable_xlsx:
            config.add_tailbone_permission(permission_prefix, '{}.row_results_xlsx'.format(permission_prefix),
                                           "Download {} results as XLSX".format(row_model_title))
            config.add_route('{}.row_results_xlsx'.format(route_prefix), '{}/{{uuid}}/rows-xlsx'.format(url_prefix))
            config.add_view(cls, attr='row_results_xlsx', route_name='{}.row_results_xlsx'.format(route_prefix),
                            permission='{}.row_results_xlsx'.format(permission_prefix))

        # create row
        if cls.has_rows:
            if cls.rows_creatable or cls.mobile_rows_creatable:
                config.add_tailbone_permission(permission_prefix, '{}.create_row'.format(permission_prefix),
                                               "Create new {} rows".format(model_title))
            if cls.rows_creatable:
                config.add_route('{}.create_row'.format(route_prefix), '{}/{{{}}}/new-row'.format(url_prefix, model_key))
                config.add_view(cls, attr='create_row', route_name='{}.create_row'.format(route_prefix),
                                permission='{}.create_row'.format(permission_prefix))
            if cls.mobile_rows_creatable:
                config.add_route('mobile.{}.create_row'.format(route_prefix), '/mobile{}/{{{}}}/new-row'.format(url_prefix, model_key))
                config.add_view(cls, attr='mobile_create_row', route_name='mobile.{}.create_row'.format(route_prefix),
                                permission='{}.create_row'.format(permission_prefix))
                if cls.mobile_rows_quickable:
                    config.add_route('mobile.{}.quick_row'.format(route_prefix), '/mobile{}/{{{}}}/quick-row'.format(url_prefix, model_key))
                    config.add_view(cls, attr='mobile_quick_row', route_name='mobile.{}.quick_row'.format(route_prefix),
                                    permission='{}.create_row'.format(permission_prefix))

        # view row
        if cls.has_rows:
            if cls.rows_viewable:
                config.add_route('{}.view_row'.format(route_prefix), '{}/{{uuid}}/rows/{{row_uuid}}'.format(url_prefix))
                config.add_view(cls, attr='view_row', route_name='{}.view_row'.format(route_prefix),
                                permission='{}.view'.format(permission_prefix))
            if cls.mobile_rows_viewable:
                config.add_route('mobile.{}.view_row'.format(route_prefix), '/mobile{}/{{uuid}}/rows/{{row_uuid}}'.format(url_prefix))
                config.add_view(cls, attr='mobile_view_row', route_name='mobile.{}.view_row'.format(route_prefix),
                                permission='{}.view'.format(permission_prefix))

        # edit row
        if cls.has_rows:
            if cls.rows_editable or cls.mobile_rows_editable:
                config.add_tailbone_permission(permission_prefix, '{}.edit_row'.format(permission_prefix),
                                               "Edit individual {} rows".format(model_title))
            if cls.rows_editable:
                config.add_route('{}.edit_row'.format(route_prefix), '{}/{{uuid}}/rows/{{row_uuid}}/edit'.format(url_prefix))
                config.add_view(cls, attr='edit_row', route_name='{}.edit_row'.format(route_prefix),
                                permission='{}.edit_row'.format(permission_prefix))
            if cls.mobile_rows_editable:
                config.add_route('mobile.{}.edit_row'.format(route_prefix), '/mobile{}/{{uuid}}/rows/{{row_uuid}}/edit'.format(url_prefix))
                config.add_view(cls, attr='mobile_edit_row', route_name='mobile.{}.edit_row'.format(route_prefix),
                                permission='{}.edit_row'.format(permission_prefix))

        # delete row
        if cls.has_rows:
            if cls.rows_deletable or cls.mobile_rows_deletable:
                config.add_tailbone_permission(permission_prefix, '{}.delete_row'.format(permission_prefix),
                                               "Delete individual {} rows".format(model_title))
            if cls.rows_deletable:
                config.add_route('{}.delete_row'.format(route_prefix), '{}/{{uuid}}/rows/{{row_uuid}}/delete'.format(url_prefix))
                config.add_view(cls, attr='delete_row', route_name='{}.delete_row'.format(route_prefix),
                                permission='{}.delete_row'.format(permission_prefix))
            if cls.mobile_rows_deletable:
                config.add_route('mobile.{}.delete_row'.format(route_prefix), '/mobile{}/{{uuid}}/rows/{{row_uuid}}/delete'.format(url_prefix))
                config.add_view(cls, attr='mobile_delete_row', route_name='mobile.{}.delete_row'.format(route_prefix),
                                permission='{}.delete_row'.format(permission_prefix))

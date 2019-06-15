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
Core Grid Classes
"""

from __future__ import unicode_literals, absolute_import

import datetime
from six.moves import urllib

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import api
from rattail.db.types import GPCType
from rattail.util import prettify, pretty_boolean, pretty_quantity, pretty_hours
from rattail.time import localtime

import webhelpers2_grid
from pyramid.renderers import render
from webhelpers2.html import HTML, tags
from paginate_sqlalchemy import SqlalchemyOrmPage

from . import filters as gridfilters
from tailbone.db import Session
from tailbone.util import raw_datetime


class FieldList(list):
    """
    Convenience wrapper for a field list.
    """

    def insert_before(self, field, newfield):
        i = self.index(field)
        self.insert(i, newfield)

    def insert_after(self, field, newfield):
        i = self.index(field)
        self.insert(i + 1, newfield)


class Grid(object):
    """
    Core grid class.  In sore need of documentation.
    """

    def __init__(self, key, data, columns=None, width='auto', request=None, mobile=False,
                 model_class=None, model_title=None, model_title_plural=None,
                 enums={}, labels={}, renderers={}, extra_row_class=None, linked_columns=[], url='#',
                 joiners={}, filterable=False, filters={}, use_byte_string_filters=False,
                 sortable=False, sorters={}, default_sortkey=None, default_sortdir='asc',
                 pageable=False, default_pagesize=20, default_page=1,
                 checkboxes=False, checked=None, main_actions=[], more_actions=[], delete_speedbump=False,
                 **kwargs):

        self.key = key
        self.data = data
        self.columns = FieldList(columns) if columns is not None else None
        self.width = width
        self.request = request
        self.mobile = mobile
        self.model_class = model_class
        if self.model_class and self.columns is None:
            self.columns = self.make_columns()

        self.model_title = model_title
        if not self.model_title and self.model_class and hasattr(self.model_class, 'get_model_title'):
            self.model_title = self.model_class.get_model_title()

        self.model_title_plural = model_title_plural
        if not self.model_title_plural:
            if self.model_class and hasattr(self.model_class, 'get_model_title_plural'):
                self.model_title_plural = self.model_class.get_model_title_plural()
            if not self.model_title_plural:
                self.model_title_plural = '{}s'.format(self.model_title)

        self.enums = enums or {}

        self.labels = labels or {}
        self.renderers = self.make_default_renderers(renderers or {})
        self.extra_row_class = extra_row_class
        self.linked_columns = linked_columns or []
        self.url = url
        self.joiners = joiners or {}

        self.filterable = filterable
        self.use_byte_string_filters = use_byte_string_filters
        self.filters = self.make_filters(filters)

        self.sortable = sortable
        self.sorters = self.make_sorters(sorters)
        self.default_sortkey = default_sortkey
        self.default_sortdir = default_sortdir

        self.pageable = pageable
        self.default_pagesize = default_pagesize
        self.default_page = default_page

        self.checkboxes = checkboxes
        self.checked = checked
        if self.checked is None:
            self.checked = lambda item: False
        self.main_actions = main_actions or []
        self.more_actions = more_actions or []
        self.delete_speedbump = delete_speedbump

        self._whgrid_kwargs = kwargs

    def make_columns(self):
        """
        Return a default list of columns, based on :attr:`model_class`.
        """
        if not self.model_class:
            raise ValueError("Must define model_class to use make_columns()")

        mapper = orm.class_mapper(self.model_class)
        return [prop.key for prop in mapper.iterate_properties]

    def hide_column(self, key):
        if key in self.columns:
            self.columns.remove(key)

    def hide_columns(self, *keys):
        for key in keys:
            self.hide_column(key)

    def append(self, field):
        self.columns.append(field)

    def insert_before(self, field, newfield):
        self.columns.insert_before(field, newfield)

    def insert_after(self, field, newfield):
        self.columns.insert_after(field, newfield)

    def replace(self, oldfield, newfield):
        self.insert_after(oldfield, newfield)
        self.hide_column(oldfield)

    def set_joiner(self, key, joiner):
        if joiner is None:
            self.joiners.pop(key, None)
        else:
            self.joiners[key] = joiner

    def set_sorter(self, key, *args, **kwargs):
        self.sorters[key] = self.make_sorter(*args, **kwargs)

    def set_sort_defaults(self, sortkey, sortdir='asc'):
        self.default_sortkey = sortkey
        self.default_sortdir = sortdir

    def set_filter(self, key, *args, **kwargs):
        if len(args) == 1 and args[0] is None:
            self.remove_filter(key)
        else:
            if 'label' not in kwargs and key in self.labels:
                kwargs['label'] = self.labels[key]
            self.filters[key] = self.make_filter(key, *args, **kwargs)

    def remove_filter(self, key):
        self.filters.pop(key, None)

    def set_label(self, key, label):
        self.labels[key] = label
        if key in self.filters:
            self.filters[key].label = label

    def get_label(self, key):
        """
        Returns the label text for given field key.
        """
        return self.labels.get(key, prettify(key))

    def set_link(self, key, link=True):
        if link:
            if key not in self.linked_columns:
                self.linked_columns.append(key)
        else: # unlink
            if self.linked_columns and key in self.linked_columns:
                self.linked_columns.remove(key)

    def set_renderer(self, key, renderer):
        self.renderers[key] = renderer

    def set_type(self, key, type_):
        if type_ == 'boolean':
            self.set_renderer(key, self.render_boolean)
        elif type_ == 'currency':
            self.set_renderer(key, self.render_currency)
        elif type_ == 'datetime':
            self.set_renderer(key, self.render_datetime)
        elif type_ == 'datetime_local':
            self.set_renderer(key, self.render_datetime_local)
        elif type_ == 'enum':
            self.set_renderer(key, self.render_enum)
        elif type_ == 'gpc':
            self.set_renderer(key, self.render_gpc)
        elif type_ == 'percent':
            self.set_renderer(key, self.render_percent)
        elif type_ == 'quantity':
            self.set_renderer(key, self.render_quantity)
        elif type_ == 'duration':
            self.set_renderer(key, self.render_duration)
        else:
            raise ValueError("Unsupported type for column '{}': {}".format(key, type_))

    def set_enum(self, key, enum):
        if enum:
            self.enums[key] = enum
            self.set_type(key, 'enum')
            if key in self.filters:
                self.filters[key].set_value_renderer(gridfilters.EnumValueRenderer(enum))
        else:
            self.enums.pop(key, None)

    def render_generic(self, obj, column_name):
        return self.obtain_value(obj, column_name)

    def render_boolean(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        return pretty_boolean(value)

    def obtain_value(self, obj, column_name):
        try:
            return obj[column_name]
        except TypeError:
            return getattr(obj, column_name)

    def render_currency(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        if value < 0:
            return "(${:0,.2f})".format(0 - value)
        return "${:0,.2f}".format(value)

    def render_datetime(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        return raw_datetime(self.request.rattail_config, value)

    def render_datetime_local(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        value = localtime(self.request.rattail_config, value)
        return raw_datetime(self.request.rattail_config, value)

    def render_enum(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        enum = self.enums.get(column_name)
        if enum and value in enum:
            return six.text_type(enum[value])
        return six.text_type(value)

    def render_gpc(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        return value.pretty()

    def render_percent(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        return "{:0.3f} %".format(value * 100)

    def render_quantity(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        return pretty_quantity(value)

    def render_duration(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        return pretty_hours(datetime.timedelta(seconds=value))

    def set_url(self, url):
        self.url = url

    def make_url(self, obj, i=None):
        if callable(self.url):
            return self.url(obj)
        return self.url

    def make_webhelpers_grid(self):
        kwargs = dict(self._whgrid_kwargs)
        kwargs['request'] = self.request
        kwargs['mobile'] = self.mobile
        kwargs['url'] = self.make_url

        columns = list(self.columns)
        column_labels = kwargs.setdefault('column_labels', {})
        column_formats = kwargs.setdefault('column_formats', {})

        for key, value in self.labels.items():
            column_labels.setdefault(key, value)

        if self.checkboxes:
            columns.insert(0, 'checkbox')
            column_labels['checkbox'] = tags.checkbox('check-all')
            column_formats['checkbox'] = self.checkbox_column_format

        if self.renderers:
            kwargs['renderers'] = self.renderers
        if self.extra_row_class:
            kwargs['extra_record_class'] = self.extra_row_class
        if self.linked_columns:
            kwargs['linked_columns'] = list(self.linked_columns)

        if self.main_actions or self.more_actions:
            columns.append('actions')
            column_formats['actions'] = self.actions_column_format

        # TODO: pretty sure this factory doesn't serve all use cases yet?
        factory = CustomWebhelpersGrid
        # factory = webhelpers2_grid.Grid
        if self.sortable:
            # factory = CustomWebhelpersGrid
            kwargs['order_column'] = self.sortkey
            kwargs['order_direction'] = 'dsc' if self.sortdir == 'desc' else 'asc'

        grid = factory(self.make_visible_data(), columns, **kwargs)
        if self.sortable:
            grid.exclude_ordering = list([key for key in grid.exclude_ordering
                                          if key not in self.sorters])
        return grid

    def make_default_renderers(self, renderers):
        """
        Make the default set of column renderers for the grid.

        We honor any existing renderers which have already been set, but then
        we also try to supplement that by auto-assigning renderers based on
        underlying column type.  Note that this special logic only applies to
        grids with a valid :attr:`model_class`.
        """
        if self.model_class:
            mapper = orm.class_mapper(self.model_class)
            for prop in mapper.iterate_properties:
                if isinstance(prop, orm.ColumnProperty) and not prop.key.endswith('uuid'):
                    if prop.key in self.columns and prop.key not in renderers:
                        if len(prop.columns) == 1:
                            coltype = prop.columns[0].type
                            renderers[prop.key] = self.get_renderer_for_column_type(coltype)

        return renderers

    def get_renderer_for_column_type(self, coltype):
        """
        Returns an appropriate renderer according to the given SA column type.
        """
        if isinstance(coltype, sa.Boolean):
            return self.render_boolean

        if isinstance(coltype, sa.DateTime):
            return self.render_datetime

        if isinstance(coltype, GPCType):
            return self.render_gpc

        return self.render_generic

    def checkbox_column_format(self, column_number, row_number, item):
        return HTML.td(self.render_checkbox(item), class_='checkbox')

    def actions_column_format(self, column_number, row_number, item):
        return HTML.td(self.render_actions(item, row_number), class_='actions')

    def render_grid(self, template='/grids/grid.mako', **kwargs):
        context = kwargs
        context['grid'] = self
        context['request'] = self.request
        grid_class = ''
        if self.width == 'full':
            grid_class = 'full'
        elif self.width == 'half':
            grid_class = 'half'
        context['grid_class'] = '{} {}'.format(grid_class, context.get('grid_class', ''))
        context.setdefault('grid_attrs', {})
        return render(template, context)

    def get_default_filters(self):
        """
        Returns the default set of filters provided by the grid.
        """
        if hasattr(self, 'default_filters'):
            if callable(self.default_filters):
                return self.default_filters()
            return self.default_filters
        filters = gridfilters.GridFilterSet()
        if self.model_class:
            mapper = orm.class_mapper(self.model_class)
            for prop in mapper.iterate_properties:
                if not isinstance(prop, orm.ColumnProperty):
                    continue
                if prop.key.endswith('uuid'):
                    continue
                if len(prop.columns) != 1:
                    continue
                column = prop.columns[0]
                if isinstance(column.type, sa.LargeBinary):
                    continue
                filters[prop.key] = self.make_filter(prop.key, column)
        return filters

    def make_filters(self, filters=None):
        """
        Returns an initial set of filters which will be available to the grid.
        The grid itself may or may not provide some default filters, and the
        ``filters`` kwarg may contain additions and/or overrides.
        """
        if filters:
            return filters
        return self.get_default_filters()

    def make_filter(self, key, column, **kwargs):
        """
        Make a filter suitable for use with the given column.
        """
        factory = kwargs.pop('factory', None)
        if not factory:
            factory = gridfilters.AlchemyGridFilter
            if isinstance(column.type, sa.String):
                factory = gridfilters.AlchemyStringFilter
            elif isinstance(column.type, sa.Numeric):
                factory = gridfilters.AlchemyNumericFilter
            elif isinstance(column.type, sa.Integer):
                factory = gridfilters.AlchemyIntegerFilter
            elif isinstance(column.type, sa.Boolean):
                # TODO: check column for nullable here?
                factory = gridfilters.AlchemyNullableBooleanFilter
            elif isinstance(column.type, sa.Date):
                factory = gridfilters.AlchemyDateFilter
            elif isinstance(column.type, sa.DateTime):
                factory = gridfilters.AlchemyDateTimeFilter
            elif isinstance(column.type, GPCType):
                factory = gridfilters.AlchemyGPCFilter
        kwargs.setdefault('encode_values', self.use_byte_string_filters)
        return factory(key, column=column, config=self.request.rattail_config, **kwargs)

    def iter_filters(self):
        """
        Iterate over all filters available to the grid.
        """
        return six.itervalues(self.filters)

    def iter_active_filters(self):
        """
        Iterate over all *active* filters for the grid.  Whether a filter is
        active is determined by current grid settings.
        """
        for filtr in self.iter_filters():
            if filtr.active:
                yield filtr

    def make_sorters(self, sorters=None):
        """
        Returns an initial set of sorters which will be available to the grid.
        The grid itself may or may not provide some default sorters, and the
        ``sorters`` kwarg may contain additions and/or overrides.
        """
        sorters, updates = {}, sorters
        if self.model_class:
            mapper = orm.class_mapper(self.model_class)
            for prop in mapper.iterate_properties:
                if isinstance(prop, orm.ColumnProperty) and not prop.key.endswith('uuid'):
                    sorters[prop.key] = self.make_sorter(prop)
        if updates:
            sorters.update(updates)
        return sorters

    def make_sorter(self, model_property):
        """
        Returns a function suitable for a sort map callable, with typical logic
        built in for sorting applied to ``field``.
        """
        class_ = getattr(model_property, 'class_', self.model_class)
        column = getattr(class_, model_property.key)
        return lambda q, d: q.order_by(getattr(column, d)())

    def make_simple_sorter(self, key, foldcase=False):
        """
        Returns a function suitable for a sort map callable, with typical logic
        built in for sorting a data set comprised of dicts, on the given key.
        """
        if foldcase:
            keyfunc = lambda v: v[key].lower()
        else:
            keyfunc = lambda v: v[key]
        return lambda q, d: sorted(q, key=keyfunc, reverse=d == 'desc')

    def load_settings(self, store=True):
        """
        Load current/effective settings for the grid, from the request query
        string and/or session storage.  If ``store`` is true, then once
        settings have been fully read, they are stored in current session for
        next time.  Finally, various instance attributes of the grid and its
        filters are updated in-place to reflect the settings; this is so code
        needn't access the settings dict directly, but the more Pythonic
        instance attributes.
        """

        # initial default settings
        settings = {}
        if self.sortable:
            settings['sortkey'] = self.default_sortkey
            settings['sortdir'] = self.default_sortdir
        if self.pageable:
            settings['pagesize'] = self.default_pagesize
            settings['page'] = self.default_page
        if self.filterable:
            for filtr in self.iter_filters():
                settings['filter.{}.active'.format(filtr.key)] = filtr.default_active
                settings['filter.{}.verb'.format(filtr.key)] = filtr.default_verb
                settings['filter.{}.value'.format(filtr.key)] = filtr.default_value

        # If user has default settings on file, apply those first.
        if self.user_has_defaults():
            self.apply_user_defaults(settings)

        # If request contains instruction to reset to default filters, then we
        # can skip the rest of the request/session checks.
        if self.request.GET.get('reset-to-default-filters') == 'true':
            pass

        # If request has filter settings, grab those, then grab sort/pager
        # settings from request or session.
        elif self.filterable and self.request_has_settings('filter'):
            self.update_filter_settings(settings, 'request')
            if self.request_has_settings('sort'):
                self.update_sort_settings(settings, 'request')
            else:
                self.update_sort_settings(settings, 'session')
            self.update_page_settings(settings)

        # If request has no filter settings but does have sort settings, grab
        # those, then grab filter settings from session, then grab pager
        # settings from request or session.
        elif self.request_has_settings('sort'):
            self.update_sort_settings(settings, 'request')
            self.update_filter_settings(settings, 'session')
            self.update_page_settings(settings)

        # NOTE: These next two are functionally equivalent, but are kept
        # separate to maintain the narrative...

        # If request has no filter/sort settings but does have pager settings,
        # grab those, then grab filter/sort settings from session.
        elif self.request_has_settings('page'):
            self.update_page_settings(settings)
            self.update_filter_settings(settings, 'session')
            self.update_sort_settings(settings, 'session')

        # If request has no settings, grab all from session.
        elif self.session_has_settings():
            self.update_filter_settings(settings, 'session')
            self.update_sort_settings(settings, 'session')
            self.update_page_settings(settings)

        # If no settings were found in request or session, don't store result.
        else:
            store = False
            
        # Maybe store settings for next time.
        if store:
            self.persist_settings(settings, 'session')

        # If request contained instruction to save current settings as defaults
        # for the current user, then do that.
        if self.request.GET.get('save-current-filters-as-defaults') == 'true':
            self.persist_settings(settings, 'defaults')

        # update ourself to reflect settings
        if self.filterable:
            for filtr in self.iter_filters():
                filtr.active = settings['filter.{}.active'.format(filtr.key)]
                filtr.verb = settings['filter.{}.verb'.format(filtr.key)]
                filtr.value = settings['filter.{}.value'.format(filtr.key)]
        if self.sortable:
            self.sortkey = settings['sortkey']
            self.sortdir = settings['sortdir']
        if self.pageable:
            self.pagesize = settings['pagesize']
            self.page = settings['page']

    def user_has_defaults(self):
        """
        Check to see if the current user has default settings on file for this grid.
        """
        user = self.request.user
        if not user:
            return False

        # NOTE: we used to leverage `self.session` here, but sometimes we might
        # be showing a grid of data from another system...so always use
        # Tailbone Session now, for the settings.  hopefully that didn't break
        # anything...
        session = Session()
        if user not in session:
            user = session.merge(user)

        # User defaults should have all or nothing, so just check one key.
        key = 'tailbone.{}.grid.{}.sortkey'.format(user.uuid, self.key)
        return api.get_setting(session, key) is not None

    def apply_user_defaults(self, settings):
        """
        Update the given settings dict with user defaults, if any exist.
        """
        def merge(key, normalize=lambda v: v):
            skey = 'tailbone.{}.grid.{}.{}'.format(self.request.user.uuid, self.key, key)
            value = api.get_setting(Session(), skey)
            settings[key] = normalize(value)

        if self.filterable:
            for filtr in self.iter_filters():
                merge('filter.{}.active'.format(filtr.key), lambda v: v == 'true')
                merge('filter.{}.verb'.format(filtr.key))
                merge('filter.{}.value'.format(filtr.key))

        if self.sortable:
            merge('sortkey')
            merge('sortdir')

        if self.pageable:
            merge('pagesize', int)
            merge('page', int)

    def request_has_settings(self, type_):
        """
        Determine if the current request (GET query string) contains any
        filter/sort settings for the grid.
        """
        if type_ == 'filter':
            for filtr in self.iter_filters():
                if filtr.key in self.request.GET:
                    return True
            if 'filter' in self.request.GET: # user may be applying empty filters
                return True

        elif type_ == 'sort':
            for key in ['sortkey', 'sortdir']:
                if key in self.request.GET:
                    return True

        elif type_ == 'page':
            for key in ['pagesize', 'page']:
                if key in self.request.GET:
                    return True

        return False

    def session_has_settings(self):
        """
        Determine if the current session contains any settings for the grid.
        """
        # session should have all or nothing, so just check a few keys which
        # should be guaranteed present if anything has been stashed
        for key in ['page', 'sortkey']:
            if 'grid.{}.{}'.format(self.key, key) in self.request.session:
                return True
        return any([key.startswith('grid.{}.filter'.format(self.key)) for key in self.request.session])

    def get_setting(self, source, settings, key, normalize=lambda v: v, default=None):
        """
        Get the effective value for a particular setting, preferring ``source``
        but falling back to existing ``settings`` and finally the ``default``.
        """
        if source not in ('request', 'session'):
            raise ValueError("Invalid source identifier: {}".format(source))

        # If source is query string, try that first.
        if source == 'request':
            value = self.request.GET.get(key)
            if value is not None:
                try:
                    value = normalize(value)
                except ValueError:
                    pass
                else:
                    return value

        # Or, if source is session, try that first.
        else:
            value = self.request.session.get('grid.{}.{}'.format(self.key, key))
            if value is not None:
                return normalize(value)

        # If source had nothing, try default/existing settings.
        value = settings.get(key)
        if value is not None:
            try:
                value = normalize(value)
            except ValueError:
                pass
            else:
                return value

        # Okay then, default it is.
        return default

    def update_filter_settings(self, settings, source):
        """
        Updates a settings dictionary according to filter settings data found
        in either the GET query string, or session storage.

        :param settings: Dictionary of initial settings, which is to be updated.

        :param source: String identifying the source to consult for settings
           data.  Must be one of: ``('request', 'session')``.
        """
        if not self.filterable:
            return

        for filtr in self.iter_filters():
            prefix = 'filter.{}'.format(filtr.key)

            if source == 'request':
                # consider filter active if query string contains a value for it
                settings['{}.active'.format(prefix)] = filtr.key in self.request.GET
                settings['{}.verb'.format(prefix)] = self.get_setting(
                    source, settings, '{}.verb'.format(filtr.key), default='')
                settings['{}.value'.format(prefix)] = self.get_setting(
                    source, settings, filtr.key, default='')

            else: # source = session
                settings['{}.active'.format(prefix)] = self.get_setting(
                    source, settings, '{}.active'.format(prefix),
                    normalize=lambda v: six.text_type(v).lower() == 'true', default=False)
                settings['{}.verb'.format(prefix)] = self.get_setting(
                    source, settings, '{}.verb'.format(prefix), default='')
                settings['{}.value'.format(prefix)] = self.get_setting(
                    source, settings, '{}.value'.format(prefix), default='')

    def update_sort_settings(self, settings, source):
        """
        Updates a settings dictionary according to sort settings data found in
        either the GET query string, or session storage.

        :param settings: Dictionary of initial settings, which is to be updated.

        :param source: String identifying the source to consult for settings
           data.  Must be one of: ``('request', 'session')``.
        """
        if not self.sortable:
            return
        settings['sortkey'] = self.get_setting(source, settings, 'sortkey')
        settings['sortdir'] = self.get_setting(source, settings, 'sortdir')

    def update_page_settings(self, settings):
        """
        Updates a settings dictionary according to pager settings data found in
        either the GET query string, or session storage.

        Note that due to how the actual pager functions, the effective settings
        will often come from *both* the request and session.  This is so that
        e.g. the page size will remain constant (coming from the session) while
        the user jumps between pages (which only provides the single setting).

        :param settings: Dictionary of initial settings, which is to be updated.
        """
        if not self.pageable:
            return

        pagesize = self.request.GET.get('pagesize')
        if pagesize is not None:
            if pagesize.isdigit():
                settings['pagesize'] = int(pagesize)
        else:
            pagesize = self.request.session.get('grid.{}.pagesize'.format(self.key))
            if pagesize is not None:
                settings['pagesize'] = pagesize

        page = self.request.GET.get('page')
        if page is not None:
            if page.isdigit():
                settings['page'] = int(page)
        else:
            page = self.request.session.get('grid.{}.page'.format(self.key))
            if page is not None:
                settings['page'] = int(page)

    def persist_settings(self, settings, to='session'):
        """
        Persist the given settings in some way, as defined by ``func``.
        """
        def persist(key, value=lambda k: settings[k]):
            if to == 'defaults':
                skey = 'tailbone.{}.grid.{}.{}'.format(self.request.user.uuid, self.key, key)
                api.save_setting(Session(), skey, value(key))
            else: # to == session
                skey = 'grid.{}.{}'.format(self.key, key)
                self.request.session[skey] = value(key)

        if self.filterable:
            for filtr in self.iter_filters():
                persist('filter.{}.active'.format(filtr.key), value=lambda k: six.text_type(settings[k]).lower())
                persist('filter.{}.verb'.format(filtr.key))
                persist('filter.{}.value'.format(filtr.key))

        if self.sortable:
            persist('sortkey')
            persist('sortdir')

        if self.pageable:
            persist('pagesize')
            persist('page')

    def filter_data(self, data):
        """
        Filter and return the given data set, according to current settings.
        """
        for filtr in self.iter_active_filters():

            # apply filter to data but save reference to original; if data is a
            # SQLAlchemy query and wasn't modified, we don't need to bother
            # with the underlying join (if there is one)
            original = data
            data = filtr.filter(data)
            if filtr.key in self.joiners and filtr.key not in self.joined and (
                    not isinstance(data, orm.Query) or data is not original):

                # this filter requires a join; apply that
                data = self.joiners[filtr.key](data)
                self.joined.add(filtr.key)

        return data

    def sort_data(self, data):
        """
        Sort the given query according to current settings, and return the result.
        """
        # Cannot sort unless we know which column to sort by.
        if not self.sortkey:
            return data

        # Cannot sort unless we have a sort function.
        sortfunc = self.sorters.get(self.sortkey)
        if not sortfunc:
            return data

        # We can provide a default sort direction though.
        sortdir = getattr(self, 'sortdir', 'asc')
        if self.sortkey in self.joiners and self.sortkey not in self.joined:
            data = self.joiners[self.sortkey](data)
            self.joined.add(self.sortkey)
        return sortfunc(data, sortdir)

    def paginate_data(self, data):
        """
        Paginate the given data set according to current settings, and return
        the result.
        """
        # we of course assume our current page is correct, at first
        pager = self.make_pager(data)

        # if pager has detected that our current page is outside the valid
        # range, we must re-orient ourself around the "new" (valid) page
        if pager.page != self.page:
            self.page = pager.page
            self.request.session['grid.{}.page'.format(self.key)] = self.page
            pager = self.make_pager(data)

        return pager

    def make_pager(self, data):
        return SqlalchemyOrmPage(data,
                                 items_per_page=self.pagesize,
                                 page=self.page,
                                 url_maker=URLMaker(self.request))

    def make_visible_data(self):
        """
        Apply various settings to the raw data set, to produce a final data
        set.  This will page / sort / filter as necessary, according to the
        grid's defaults and the current request etc.
        """
        self.joined = set()
        data = self.data
        if self.filterable:
            data = self.filter_data(data)
        if self.sortable:
            data = self.sort_data(data)
        if self.pageable:
            self.pager = self.paginate_data(data)
            data = self.pager
        return data

    def render_complete(self, template='/grids/complete.mako', **kwargs):
        """
        Render the complete grid, including filters.
        """
        context = kwargs
        context['grid'] = self
        context['request'] = self.request
        context.setdefault('allow_save_defaults', True)
        return render(template, context)

    def render_buefy(self, template='/grids/buefy.mako', **kwargs):
        """
        Render the Buefy grid, complete with filters.  Note that this also
        includes the context menu items and grid tools.
        """
        if 'grid_columns' not in kwargs:
            kwargs['grid_columns'] = self.get_buefy_columns()

        if 'grid_data' not in kwargs:
            kwargs['grid_data'] = self.get_buefy_data()

        if 'static_data' not in kwargs:
            kwargs['static_data'] = self.has_static_data()

        if self.filterable and 'filters_data' not in kwargs:
            kwargs['filters_data'] = self.get_filters_data()

        if self.filterable and 'filters_sequence' not in kwargs:
            kwargs['filters_sequence'] = self.get_filters_sequence()

        return self.render_complete(template=template, **kwargs)

    def render_buefy_table_element(self, template='/grids/b-table.mako', data_prop='gridData', **kwargs):
        """
        This is intended for ad-hoc "small" grids with static data.  Renders
        just a ``<b-table>`` element instead of the typical "full" grid.
        """
        context = dict(kwargs)
        context['grid'] = self
        context['data_prop'] = data_prop
        if 'grid_columns' not in context:
            context['grid_columns'] = self.get_buefy_columns()
        return render(template, context)

    def get_filters_sequence(self):
        """
        Returns a list of filter keys (strings) in the sequence with which they
        should be displayed in the UI.
        """
        return list(self.filters)

    def get_filters_data(self):
        """
        Returns a dict of current filters data, for use with Buefy grid view.
        """
        data = {}
        for filtr in self.filters.values():

            valueless = [v for v in filtr.valueless_verbs
                         if v in filtr.verbs]

            choices = []
            choice_labels = {}
            if self.enums and filtr.key in self.enums:
                choices = list(self.enums[filtr.key])
                choice_labels = self.enums[filtr.key]

            data[filtr.key] = {
                'key': filtr.key,
                'label': filtr.label,
                'active': filtr.active,
                'visible': filtr.active,
                'verbs': filtr.verbs,
                'valueless_verbs': valueless,
                'verb_labels': filtr.verb_labels,
                'verb': filtr.verb or filtr.default_verb or filtr.verbs[0],
                'value': six.text_type(filtr.value) if filtr.value is not None else "",
                'data_type': filtr.data_type,
                'choices': choices,
                'choice_labels': choice_labels,
            }

        return data

    def render_filters(self, template='/grids/filters.mako', **kwargs):
        """
        Render the filters to a Unicode string, using the specified template.
        Additional kwargs are passed along as context to the template.
        """
        # Provide default data to filters form, so renderer can do some of the
        # work for us.
        data = {}
        for filtr in self.iter_active_filters():
            data['{}.active'.format(filtr.key)] = filtr.active
            data['{}.verb'.format(filtr.key)] = filtr.verb
            data[filtr.key] = filtr.value

        form = gridfilters.GridFiltersForm(self.filters,
                                           request=self.request,
                                           defaults=data)

        kwargs['request'] = self.request
        kwargs['grid'] = self
        kwargs['form'] = form
        return render(template, kwargs)

    def render_actions(self, row, i):
        """
        Returns the rendered contents of the 'actions' column for a given row.
        """
        main_actions = [self.render_action(a, row, i)
                        for a in self.main_actions]
        main_actions = [a for a in main_actions if a]
        more_actions = [self.render_action(a, row, i)
                        for a in self.more_actions]
        more_actions = [a for a in more_actions if a]
        if more_actions:
            icon = HTML.tag('span', class_='ui-icon ui-icon-carat-1-e')
            link = tags.link_to("More" + icon, '#', class_='more')
            main_actions.append(HTML.literal('&nbsp; ') + link + HTML.tag('div', class_='more', c=more_actions))
        return HTML.literal('').join(main_actions)

    def render_action(self, action, row, i):
        """
        Renders an action menu item (link) for the given row.
        """
        url = action.get_url(row, i)
        if url:
            kwargs = {'class_': action.key, 'target': action.target}
            if action.icon:
                icon = HTML.tag('span', class_='ui-icon ui-icon-{}'.format(action.icon))
                return tags.link_to(icon + action.label, url, **kwargs)
            return tags.link_to(action.label, url, **kwargs)

    def get_row_key(self, item):
        """
        Must return a unique key for the given data item's row.
        """
        mapper = orm.object_mapper(item)
        if len(mapper.primary_key) == 1:
            return getattr(item, mapper.primary_key[0].key)
        raise NotImplementedError

    def checkbox(self, item):
        """
        Returns boolean indicating whether a checkbox should be rendererd for
        the given data item's row.
        """
        return True

    def render_checkbox(self, item):
        """
        Renders a checkbox cell for the given item, if applicable.
        """
        if not self.checkbox(item):
            return ''
        return tags.checkbox('checkbox-{}-{}'.format(self.key, self.get_row_key(item)),
                             checked=self.checked(item))

    def get_pagesize_options(self):

        # use values from config, if defined
        options = self.request.rattail_config.getlist('tailbone', 'grid.pagesize_options')
        if options:
            options = [int(size) for size in options
                       if size.isdigit()]
            if options:
                return options

        return [5, 10, 20, 50, 100, 200]

    def has_static_data(self):
        """
        Should return ``True`` if the grid data can be considered "static"
        (i.e. a list of values).  Will return ``False`` otherwise, e.g. if the
        data is represented as a SQLAlchemy query.
        """
        # TODO: should make this smarter?
        if isinstance(self.data, list):
            return True
        return False

    def get_buefy_columns(self):
        """
        Return a list of dicts representing all grid columns.  Meant for use
        with Buefy table.
        """
        columns = []
        for name in self.columns:
            columns.append({
                'field': name,
                'label': self.get_label(name),
                'sortable': self.sortable and name in self.sorters,
            })
        return columns

    def get_buefy_data(self):
        """
        Returns a list of data rows for the grid, for use with Buefy table.
        """
        # filter / sort / paginate to get "visible" data
        raw_data = self.make_visible_data()
        data = []
        status_map = {}

        # iterate over data rows
        for i in range(len(raw_data)):
            rowobj = raw_data[i]
            row = {}

            # iterate over data fields
            for name in self.columns:

                # leverage configured rendering logic where applicable;
                # otherwise use "raw" data value as string
                if self.renderers and name in self.renderers:
                    value = self.renderers[name](rowobj, name)
                else:
                    value = self.obtain_value(rowobj, name)
                if value is None:
                    value = ""
                row[name] = six.text_type(value)

            # maybe add UUID for convenience
            if 'uuid' not in self.columns:
                if hasattr(rowobj, 'uuid'):
                    row['uuid'] = rowobj.uuid

            # set action URL(s) for row, as needed
            self.set_action_urls(row, rowobj, i)

            # set extra row class if applicable
            if self.extra_row_class:
                status = self.extra_row_class(rowobj, i)
                if status:
                    status_map[i] = status

            data.append(row)

        results = {
            'data': data,
            'row_status_map': status_map,
        }

        if self.pageable and self.pager is not None:
            results['total_items'] = self.pager.item_count
            results['per_page'] = self.pager.items_per_page
            results['page'] = self.pager.page
            results['pages'] = self.pager.page_count
            results['first_item'] = self.pager.first_item
            results['last_item'] = self.pager.last_item

        return results

    def set_action_urls(self, row, rowobj, i):
        """
        Pre-generate all action URLs for the given data row.  Meant for use
        with Buefy table, since we can't generate URLs from JS.
        """
        for action in (self.main_actions + self.more_actions):
            url = action.get_url(rowobj, i)
            row['_action_url_{}'.format(action.key)] = url

    def is_linked(self, name):
        """
        Should return ``True`` if the given column name is configured to be
        "linked" (i.e. table cell should contain a link to "view object"),
        otherwise ``False``.
        """
        if self.linked_columns:
            if name in self.linked_columns:
                return True
        return False


class CustomWebhelpersGrid(webhelpers2_grid.Grid):
    """
    Implement column sorting links etc. for webhelpers2_grid
    """

    def __init__(self, itemlist, columns, **kwargs):
        self.mobile = kwargs.pop('mobile', False)
        self.renderers = kwargs.pop('renderers', {})
        self.linked_columns = kwargs.pop('linked_columns', [])
        self.extra_record_class = kwargs.pop('extra_record_class', None)
        super(CustomWebhelpersGrid, self).__init__(itemlist, columns, **kwargs)

    def default_header_record_format(self, headers):
        if self.mobile:
            return HTML('')
        return super(CustomWebhelpersGrid, self).default_header_record_format(headers)

    def generate_header_link(self, column_number, column, label_text):

        # display column header as simple no-op link; client-side JS takes care
        # of the rest for us
        label_text = tags.link_to(label_text, '#', data_sortkey=column)

        # Is the current column the one we're ordering on?
        if (column == self.order_column):
            return self.default_header_ordered_column_format(column_number,
                                                             column,
                                                             label_text)
        else:
            return self.default_header_column_format(column_number, column,
                                                     label_text)            

    def default_record_format(self, i, record, columns):
        if self.mobile:
            return columns
        kwargs = {
            'class_': self.get_record_class(i, record, columns),
        }
        if hasattr(record, 'uuid'):
            kwargs['data_uuid'] = record.uuid
        return HTML.tag('tr', columns, **kwargs)

    def get_record_class(self, i, record, columns):
        if i % 2 == 0:
            cls = 'even r{}'.format(i)
        else:
            cls = 'odd r{}'.format(i)
        if self.extra_record_class:
            extra = self.extra_record_class(record, i)
            if extra:
                cls = '{} {}'.format(cls, extra)
        return cls

    def get_column_value(self, column_number, i, record, column_name):
        if self.renderers and column_name in self.renderers:
            return self.renderers[column_name](record, column_name)
        try:
            return record[column_name]
        except TypeError:
            return getattr(record, column_name)

    def default_column_format(self, column_number, i, record, column_name):
        value = self.get_column_value(column_number, i, record, column_name)
        if self.mobile:
            url = self.url_generator(record, i)
            attrs = {}
            if hasattr(record, 'uuid'):
                attrs['data_uuid'] = record.uuid
            return HTML.tag('li', tags.link_to(value, url), **attrs)
        if self.linked_columns and column_name in self.linked_columns and (
                value is not None and value != ''):
            url = self.url_generator(record, i)
            value = tags.link_to(value, url)
        class_name = 'c{} {}'.format(column_number, column_name)
        return HTML.tag('td', value, class_=class_name)


class GridAction(object):
    """
    Represents an action available to a grid.  This is used to construct the
    'actions' column when rendering the grid.
    """

    def __init__(self, key, label=None, url='#', icon=None, target=None,
                 click_handler=None):
        self.key = key
        self.label = label or prettify(key)
        self.icon = icon
        self.url = url
        self.target = target
        self.click_handler = click_handler

    def get_url(self, row, i):
        """
        Returns an action URL for the given row.
        """
        if callable(self.url):
            return self.url(row, i)
        return self.url


class URLMaker(object):
    """
    URL constructor for use with SQLAlchemy grid pagers.  Logic for this was
    basically copied from the old `webhelpers.paginate` module
    """

    def __init__(self, request):
        self.request = request

    def __call__(self, page):
        params = self.request.GET.copy()
        params["page"] = page
        params["partial"] = "1"
        qs = urllib.parse.urlencode(params, True)
        return '{}?{}'.format(self.request.path, qs)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from congo.templatetags.models import field_name
from copy import copy
from django.core.paginator import InvalidPage, Paginator
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import timesince
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
import json
from django.utils import formats


@python_2_unicode_compatible
class Cell(object):
    row = None

    def __init__(self, column, data, raw_data):
        self.column = column
        self.data = data
        self.raw_data = raw_data

    def __str__(self):
        return self.data

    def as_dict(self):
        data_dict = {
            'column_id': self.column.id,
            'data': self.data,
        }

        if self.column.as_html:
            data_dict['as_html'] = self.column.as_html

        if self.column.hidden:
            data_dict['is_hidden'] = self.column.hidden

        if isinstance(self.raw_data, models.Model):
            data_dict['raw_data'] = self.raw_data.id
        else:
            data_dict['raw_data'] = self.raw_data

        return data_dict

class Row(object):
    datagrid = None

    def __init__(self, datagrid, obj, cells):
        self.datagrid = datagrid
        self.obj = obj
        self.cells = cells
        self.cell_map = {}

        for cell in self.cells:
            cell.row = self
            self.cell_map[cell.column.id] = cell

    def __getattr__(self, field):
        return self.cell_map[field]

    def __iter__(self):
        for cell in self.cells:
            yield cell

    def as_dict(self):
        return {
            'obj_id': self.obj.id,
            'cells': [c.as_dict() for c in self.cells]
        }

class Column(object):
    """
    A column in a data grid.

    The column is the primary component of the data grid. It is used to
    display not only the column header but the HTML for the cell as well.

    Columns can be tied to database fields and can be used for sorting.
    Not all columns have to allow for this, though.

    Columns can have an image, text, or both in the column header. The
    contents of the cells can be instructed to link to the object on the
    row or the data in the cell.
    """

    SORT_DESC = 0
    SORT_ASC = 1

    creation_counter = 0

    def __init__(self, label = None, field_name = None, db_field = None, param_name = None,
                 sort_field = None, sortable = False, default_sort_dir = SORT_ASC,
                 link = False, link_func = None, render_func = None, data_func = None,
                 icon_name = None, width = '', column_css_class = '', header_css_class = '',
                 cell_css_class = '', as_html = False, hidden = False):

        self.id = None
        self.datagrid = None

        self.label = label # etykieta
        self.field_name = field_name # nazwa atrybutu modelu
        self.db_field = db_field # nazwa pola bazy danych
        self.param_name = param_name # nazwa parametru GET

        self.sort_field = sort_field # nazwa pola, po którym realizowane jest sortowanie, np. role__translations__name
        self.sortable = sortable # czy możliwe sortowanie?
        self.default_sort_dir = default_sort_dir # kierunek sortowania, domyślnie SORT_ASC

        self.link = link # czy wartość komórki ma być linkiem?
        self.link_func = link_func # własna f-cja generująca link, przyjmuje obiekt z queryset'u, domyślnie wywołuje get_absolute_url na atrybucie lub obiekcie
        self.render_func = render_func # f-cja generująca link, przyjmuje obiekt źródłowy
        self.data_func = data_func # f-cja generująca dane, przyjmuje obiekt źródłowy

        self.icon_name = icon_name # nazwa ikony, np. account
        self.width = width
        self.column_css_class = column_css_class
        self.header_css_class = header_css_class
        self.cell_css_class = cell_css_class

        self.as_html = as_html # renderować html'a
        self.hidden = hidden # ukryć kolumne, np. gdy chcemy pobrac dane, ale nie wyświetlac ich w grid tylko np. w dialogu.

        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

        # State
        self.sort_priority = None
        self.sort_dir = None

    def get_column_css_style(self):
        if not hasattr(self, '_column_css_style'):
            self._column_css_style = "width: %s" % self.width if self.width else ""
        return self._column_css_style


    def get_column_css_class(self):
        if not hasattr(self, '_column_css_class'):
            column_id = "datagrid-column-%s" % str(self.id).replace('_', '-')
            self._column_css_class = ' '.join([css_class for css_class in [column_id, self.column_css_class] if css_class])
        return self._column_css_class


    def get_header_css_class(self):
        if not hasattr(self, '_header_css_class'):
            column_id = "datagrid-header-%s" % str(self.id).replace('_', '-')
            self._header_css_class = ' '.join([css_class for css_class in [column_id, self.header_css_class] if css_class])
        return self._header_css_class


    def get_cell_css_class(self):
        if not hasattr(self, '_cell_css_class'):
            column_id = "datagrid-cell-%s" % str(self.id).replace('_', '-')
            self._cell_css_class = ' '.join([css_class for css_class in [column_id, self.cell_css_class] if css_class])
        return self._cell_css_class


    def get_sort_cols(self):
        if self.sortable:
            sort_list = copy(self.datagrid.param_name_sort_list)

            if self.sort_priority:
                del sort_list[self.sort_priority - 1]
                sort_col = self.param_name if self.sort_dir == self.SORT_DESC else "-%s" % self.param_name
            else:
                sort_col = self.param_name if self.default_sort_dir == self.SORT_ASC else "-%s" % self.param_name

            sort_list.insert(0, sort_col)
            return sort_list
        else:
            return []


    def get_sort_url(self):
        sort_param_name = self.datagrid.sort_param_name
        url_params = self.datagrid.get_url_params_except(sort_param_name)
        return "?%s%s=%s" % (url_params, sort_param_name, ','.join(self.get_sort_cols()))


    def get_unsort_cols(self):
        if self.sortable:
            sort_list = copy(self.datagrid.param_name_sort_list)

            if self.sort_priority:
                del sort_list[self.sort_priority - 1]

            return sort_list
        else:
            return []


    def get_unsort_url(self):
        sort_param_name = self.datagrid.sort_param_name
        url_params = self.datagrid.get_url_params_except(sort_param_name)
        url = "?"
        if url_params:
            url += url_params
        unsort_cols = ','.join(self.get_unsort_cols())
        if unsort_cols:
            url += "%s=%s" % (sort_param_name, unsort_cols)
        return url


    @mark_safe
    def render_header(self):
        """
        Displays a sortable column header.

        The column header will include the current sort indicator, if it
        belongs in the sort list. It will also be made clickable in order
        to modify the sort order appropriately, if sortable.
        """

        return render_to_string(self.datagrid.column_header_template, {'column': self})

    def as_dict(self):
        return {
            'column_id': self.id,
            'label': self.label,
            'param_name': self.param_name,
            'icon_name': self.icon_name,

            'is_sortable': self.sortable,
            'is_hidden': self.hidden,
            'sort_priority': self.sort_priority,
            'sort_dir': self.sort_dir,

            'column_css_style': self.get_column_css_style(),
            'column_css_class': self.get_column_css_class(),
            'header_css_class': self.get_header_css_class(),
            'cell_css_class': self.get_cell_css_class(),

            'sort_cols': self.get_sort_cols(),
            'unsort_cols': self.get_unsort_cols(),
        }

    def get_cell_data(self, obj):
        """
        Zwraca obiekt lub wartość dla komórki danych. Jeśli zdefiniowano funkcję,
        która pobierze dane z obiektu queryset’u użyjemy jej. W innym wypadku
        staramy się pobrać dane automatycznie.
        """

        if self.data_func:
            # Jeśli podano funkcję, która pobiera dane dla komórki, użyjmy jej
            return self.data_func(obj)
        else:
            # W przeciwnym razie spróbujmy zewaluować dane automatycznie
            field_names = self.field_name.split('.')
            if len(field_names) > 1:
                field_name = field_names.pop(0)
                value = getattr(obj, field_name)
                if callable(value):
                    value = value()
                if value is None:
                    return value

                while field_names:
                    field_name = field_names.pop(0)
                    value = getattr(value, field_name)
                    if callable(value):
                        value = value()
                    if value is None:
                        return value
            else:
                value = getattr(obj, self.db_field)
            if self.data_func:
                value = self.data_func(value)

            if callable(value):
                return value()
            else:
                return value

    @mark_safe
    def render_cell(self, obj, cell_data = None):
        """
        Renderuje wartość dla komórki danych. Jeśli zdefiniowano funkcję renderującą, 
        użyjemy jej. W przeciwnym razie wyrenderujemy wartość automatycznie. Wynik 
        zostanie przekazany do funkcji generującej link, jeśli link ma zostać stworzony.
        """

        # Jeśli podano cell_data, nie wyliczamy ponownie
        if cell_data is None:
            cell_data = self.get_cell_data(obj)

        if self.render_func:
            # Jeśli podano funkcję, która wyświetla dane dla komórki, użyjmy jej; f-cja działa na obiekcie źródłowym
            rendered_cell = self.render_func(obj)
        else:
            get_displayed = 'get_%s_displayed' % self.field_name
            if hasattr(obj, get_displayed):
                # Sprawdzamy, czy uda się pobrać etykietę dla danych z obiektu cell_data
                rendered_cell = getattr(cell_data, get_displayed)()
            else:
                # Wpp próbujmy wyrenderować komórkę automatycznie na podst. cell_data
                rendered_cell = cell_data

        url = None
        if self.link:
            if self.link_func:
                # Wykonujemy f-cję link_func na obiekcie źródłowym, aby mieć większą kotrolę
                url = self.link_func(obj)
            elif hasattr(cell_data, 'get_absolute_url'):
                # Wpp wykonujemy f-cję get_absolute_url na obiekcie cell_data
                url = cell_data.get_absolute_url()
            elif hasattr(obj, 'get_absolute_url'):
                # Wpp wykonujemy f-cję get_absolute_url na obiekcie źródłowym
                url = obj.get_absolute_url()

        if rendered_cell is None:
            rendered_cell = _("(Brak)")

        if url:
            return u"""<a href="%s">%s</a>""" % (url, force_text(rendered_cell))
        else:
            return force_text(rendered_cell)

class NonDatabaseColumn(Column):
    """
    NonDatabaseColumn pozwala na renderowanie column niezwiązanych z modelem.
    """
    def __init__(self, label, *args, **kwargs):
        Column.__init__(self, label, sortable = False, *args, **kwargs)

        def _data_func(obj):
            return self.label

        # jesli nie ma data func, zwracamy label
        if not self.data_func:
            self.data_func = _data_func

class DateColumn(Column):
    """
    DateColumn renderuje datę lub czas. Domyślnie format = DATE_FORMAT
    Strefa czasowa (self.tz) musi przyjmowac obj i nie moze byc naive.
    """

    def __init__(self, label = None, format = None, tz = None, *args, **kwargs):
        Column.__init__(self, label, *args, **kwargs)
        self.format = format
        self.tz = tz

        def _render_func(obj):
            # get date
            date = getattr(obj, self.db_field)

            # normalize
            if self.tz:
                date = self.tz(obj).normalize(date)

            return formats.date_format(date, self.format)

        if not self.render_func:
            self.render_func = _render_func

class DateTimeSinceColumn(Column):
    """
    A column that renders a date or time relative to now.
    """
    def __init__(self, label, sortable = True, *args, **kwargs):
        Column.__init__(self, label, sortable = sortable, *args, **kwargs)

    def render_data(self, obj):
        return _("%s ago") % timesince(getattr(obj, self.db_field))

class DataGrid(object):
    def __init__(self, request, queryset, optimize_sorts = True, **kwargs):

        self.request = request
        self.queryset = queryset

        self.rows = []
        self.columns = []
        self.param_name_sort_map = {} # key: param_name, val: id
        self.param_name_sort_list = [] # lista parametrów usera do sortowania - lub default_sort_list
        self.sort_field_sort_list = [] # lista pól bd do sortowania - uwzględnia extra_sort_list
        self.paginator = None
        self.page = None
        self.optimize_sorts = optimize_sorts

        self.id = "datagrid-%s" % get_random_string(5, 'abcdefghijklmnopqrstuvwxyz0123456789')
        self.params = {}

        # Ustawiamy domyślne parametry z meta lub kwargs
        self.set_meta_data(**kwargs)

        # Ustawiamy kolumny dla klasy
        for attr in dir(self):
            column = getattr(self, attr)
            if isinstance(column, Column):
                self.columns.append(column)
                column.datagrid = self
                column.id = attr

                if column.id in self.columns_kwargs:
                    for key, value in self.columns_kwargs[column.id].items():
                        setattr(column, key, value)

                # Resetujemy...
                column.sort_priority = None
                column.sort_dir = None

                if not column.field_name:
                    column.field_name = column.id

                if column.label is None:
                    # jeśli label = "", to nie nadpisujemy!
                    column.label = field_name(self.queryset.model, column.field_name)

                if not column.db_field:
                    column.db_field = column.field_name

                if not column.param_name:
                    column.param_name = column.id

                if not column.sort_field:
                    column.sort_field = column.db_field

                if column.sortable:
                    self.param_name_sort_map[column.param_name] = column.id

        self.columns.sort(key = lambda x: x.creation_counter)

        # Ustawiamy parametry z requst'a
        self.set_params()

        # Obsługujemy szukanie, filtrowanie, sortowanie
#        self.handle_search()
#        self.handle_filter()
        self.handle_sorting()

        # Wczytujemy obiekty z queryset'a
        self.precompute_objects()

#        self.filtering_options = {}
#        if self.filter_fields:
#            filtering_options = {}
#
#            # @og do zmiany na raw query...
#            for field in self.filter_fields:
#                filtering_options[field] = set([getattr(el, field) for el in queryset])
#            self.filtering_options = filtering_options

    def set_meta_data(self, **kwargs):
        meta = getattr(self, 'Meta', None)

#        self.pagination_control_widget = getattr(meta, 'pagination_control_widget', False)
#        self.filter_fields = getattr(meta, 'filter_fields', [])
#        self.search_fields = getattr(meta, 'search_fields', [])

        def get_from_kwargs_or_meta(key, default = None):
            return kwargs.get(key, getattr(meta, key, default))

        # auto_related_fields
        self.auto_related_fields = get_from_kwargs_or_meta('auto_related_fields', True)

        # page_num_param_name
        self.page_num_param_name = get_from_kwargs_or_meta('page_num_param_name', 'p')

        # page_size_param_name
        self.page_size_param_name = get_from_kwargs_or_meta('page_size_param_name', 'ps')

        # default_page_size
        self.default_page_size = get_from_kwargs_or_meta('default_page_size', 10)

        # page_size_list
        self.page_size_list = get_from_kwargs_or_meta('page_size_param_name', [10, 20, 50, 100])

        if self.default_page_size not in self.page_size_list:
            self.page_size_list.append(self.default_page_size)
            self.page_size_list.sort()

        # sort_param_name
        self.sort_param_name = get_from_kwargs_or_meta('sort_param_name', 's')

        # default_sort_list - lista pól jako param_name, bo trzeba zainicjować
        self.default_sort_list = get_from_kwargs_or_meta('default_sort_list', [])

        # extra_sort_list - lista pól jako sort_field, bo można sortować wg pól spoza listy kolumn
        self.extra_sort_list = get_from_kwargs_or_meta('extra_sort_list', [])

        # szablony
        # @og dopracować...
        self.listview_template = get_from_kwargs_or_meta('listview_template', 'utils/datagrid/listview.html')
        self.column_header_template = get_from_kwargs_or_meta('column_header_template', 'utils/datagrid/column_header.html')
        self.cell_template = get_from_kwargs_or_meta('cell_template', 'utils/datagrid/cell.html')

        # nadpisywanie parametrów kolumn
        self.columns_kwargs = get_from_kwargs_or_meta('columns_kwargs', {})

    def set_params(self):

        if hasattr(self.request, 'data'):
            self.params = self.request.data
        elif 'application/json' in self.request.META['CONTENT_TYPE']:
            self.params = json.loads(self.request.body)
        else:
            self.params = self.request.GET

        # page_num
        page_num = self.params.get(self.page_num_param_name, 1)
        try:
            self.page_num = int(page_num)
        except ValueError:
            self.page_num = 1

        # page_size
        page_size = self.params.get(self.page_size_param_name, self.default_page_size)
        try:
            self.page_size = int(page_size)
        except ValueError:
            self.page_size = self.default_page_size

    def precompute_objects(self):
        """
        Builds the queryset and stores the list of objects for use in
        rendering the datagrid.
        """
        query = self.queryset

        if self.sort_field_sort_list:
            query = query.order_by(*self.sort_field_sort_list)

        self.paginator = Paginator(query, self.page_size)

        try:
            self.page = self.paginator.page(self.page_num)
        except InvalidPage:
            self.page = self.paginator.page(1)

        self.rows = []
        id_list = None

        if self.optimize_sorts and len(self.sort_field_sort_list) > 0:
            # This can be slow when sorting by multiple columns. If we
            # have multiple items in the sort list, we'll request just the
            # IDs and then fetch the actual details from that.
            id_list = list(self.page.object_list.values_list('pk', flat = True))

            # Make sure to unset the order. We can't meaningfully order these
            # results in the query, as what we really want is to keep it in
            # the order specified in id_list, and we certainly don't want
            # the database to do any special ordering (possibly slowing things
            # down). We'll set the order properly in a minute.
            self.page.object_list = self.post_process_queryset(
                self.queryset.model.objects.filter(pk__in = id_list).order_by()
            )

        if self.auto_related_fields:
            # Jeśli występuje relacja, od razu pobierzmy powiązane obiekty.
            related_fields = []
            for column in self.columns:
                fields = column.db_field.split('__', 1)
                if len(fields) > 1:
                    related_fields.append(fields[0])

            if related_fields:
                self.page.object_list = self.page.object_list.select_related(*related_fields)

        if id_list:
            # The database will give us the items in a more or less random
            # order, since it doesn't know to keep it in the order provided by
            # the ID list. This will place the results back in the order we
            # expect.
            index = dict([(obj_id, pos) for (pos, obj_id) in enumerate(id_list)])
            object_list = [None] * len(id_list)

            for obj in list(self.page.object_list):
                object_list[index[obj.id]] = obj

        else:
            # Grab the whole list at once. We know it won't be too large,
            # and it will prevent one query per row.
            object_list = list(self.page.object_list)

        for obj in object_list:
            cells = []

            for column in self.columns:
                cell_data = column.get_cell_data(obj)
                cells.append(Cell(column, column.render_cell(obj, cell_data), cell_data))

            self.rows.append(Row(self, obj, cells))

    def post_process_queryset(self, queryset):
        """
        Processes a QuerySet after the initial query has been built and
        pagination applied. This is only used when optimizing a sort.

        By default, this just returns the existing queryset. Custom datagrid
        subclasses can override this to add additional queries (such as
        subqueries in an extra() call) for use in the cell renderers.

        When optimize_sorts is True, subqueries (using extra()) on the initial
        QuerySet passed to the datagrid will be stripped from the final
        result. This function can be used to re-add those subqueries.
        """
        return queryset

    def handle_search(self):
        # słabe...

        if not self.search_fields:
            return
        query = self.params.get('q', None)
        if not query:
            return
        query_criteria = Q()
        for field in self.search_fields:
            field = field + "__icontains"
            query_criteria = query_criteria | Q(**{field: query})
        self.queryset = self.queryset.filter(query_criteria)

    def handle_filter(self):
        # słabe... a co ze statusami jako int?

        queryset = self.queryset
        if not self.filter_fields:
            return
        for field in self.filter_fields:
            query = self.params.get(field, None)
            if query:
                self.queryset = queryset.filter(**{field: query})

    def handle_sorting(self):

        self.param_name_sort_list = []
        self.sort_field_sort_list = []

        param_name_sort_list = self.params.get(self.sort_param_name, [])
        i = 1

        if param_name_sort_list:
            # sortujemy wg parametrów usera
            if isinstance(param_name_sort_list, unicode):
                param_name_sort_list = param_name_sort_list.split(',')
        elif self.default_sort_list:
            # albo wg domyślnych
            param_name_sort_list = self.default_sort_list

        # kolejno wyliczamy param_name i sort_field
        # i dodajemy wartości do list
        for param_name in param_name_sort_list:

            if param_name[0] == '-':
                param_name = param_name[1:]
                sort_dir = Column.SORT_DESC
                prefix = '-'
            else:
                sort_dir = Column.SORT_ASC
                prefix = ''

            if param_name in self.param_name_sort_map:
                col = getattr(self, self.param_name_sort_map[param_name])
                col.sort_priority = i
                col.sort_dir = sort_dir
                i += 1

                prefixed_param_name = "%s%s" % (prefix, param_name)
                self.param_name_sort_list.append(prefixed_param_name)

                prefixed_sort_field = "%s%s" % (prefix, col.sort_field)
                if prefixed_sort_field not in self.sort_field_sort_list:
                    self.sort_field_sort_list.append(prefixed_sort_field)

        # aktualizujemy parametry sortowania
#        self.params[self.sort_param_name] = self.sort_field_sort_list

        # ustawiamy dodatkowe sortowanie, ale nie ma tu jak kontrolować
        # poprawności, więc przy pomyłce dostaniemy błąd
        for sort_field in self.extra_sort_list:
            if sort_field not in self.sort_field_sort_list:
                self.sort_field_sort_list.append(sort_field)

    def get_first_page_num(self):
        if self.page.has_previous() and self.page.previous_page_number() > 1:
            return 1
        return None

    def get_first_page_url(self):
        first_page_num = self.get_first_page_num()
        if first_page_num:
            url_params = self.get_url_params_except(self.page_num_param_name)
            return "?%s%s=%s" % (url_params, self.page_num_param_name, first_page_num)
        return None

    def get_last_page_num(self):
        if self.page.has_next() and self.page.next_page_number() < self.paginator.num_pages:
            return self.paginator.num_pages
        return None

    def get_last_page_url(self):
        last_page_num = self.get_last_page_num()
        if last_page_num:
            url_params = self.get_url_params_except(self.page_num_param_name)
            return "?%s%s=%s" % (url_params, self.page_num_param_name, last_page_num)
        return None

    def get_prev_page_num(self):
        if self.page.has_previous():
            return self.page.previous_page_number()
        return None

    def get_prev_page_url(self):
        prev_page_num = self.get_prev_page_num()
        if prev_page_num:
            url_params = self.get_url_params_except(self.page_num_param_name)
            return "?%s%s=%s" % (url_params, self.page_num_param_name, prev_page_num)
        return None

    def get_next_page_num(self):
        if self.page.has_next():
            return self.page.next_page_number()
        return None

    def get_next_page_url(self):
        next_page_num = self.get_next_page_num()
        if next_page_num:
            url_params = self.get_url_params_except(self.page_num_param_name)
            return "?%s%s=%s" % (url_params, self.page_num_param_name, next_page_num)
        return None

    def get_paginator(self):
        return {
            'start_index': self.page.start_index(),
            'end_index': self.page.end_index(),
            'items': self.paginator.count,

            'page': self.page.number,
            'pages': self.paginator.num_pages,
            # 'page_range': [i for i in self.paginator.page_range], # potrzebne?

            'first_page': self.get_first_page_num(),
            'last_page': self.get_last_page_num(),
            'prev_page': self.get_prev_page_num(),
            'next_page': self.get_next_page_num(),

            'page_size': self.page_size,
            'page_size_list': self.page_size_list,
        }

    def get_sort(self):
        return {
            'current': self.param_name_sort_list,
            'default': self.default_sort_list,
        }

    def get_url_params_except(self, *params):
        """
        Utility function to return a string containing URL parameters to
        this page with the specified parameter filtered out.
        """

        s = ""
        for key, value in self.params.items():
            if key not in params and value:
                s += "%s=%s&" % (key, value)
        return s

    @mark_safe
    def render_data(self):

        context = {
            'datagrid': self,
            'request': self.request,
        }

        return render_to_string(self.listview_template, context)

    def as_dict(self):
        data_dict = {
            'grid_id': self.id,
            'columns': [c.as_dict() for c in self.columns],
            # 'column_map': dict([(c.id, index) for index, c in enumerate(self.columns)]), # potrzebne?
            'rows': [r.as_dict() for r in self.rows],
            'paginator': self.get_paginator(),
            'params': self.params,
            'sort': {
                'current': self.param_name_sort_list,
                'default': self.default_sort_list,
            },
        }

        return data_dict

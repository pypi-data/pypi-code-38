# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime
import json

from django.core.paginator import InvalidPage, Paginator
from django.db import models
from django.db.models import Q
from django.forms.fields import NullBooleanField
from django.utils import formats
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_filters.filters import DateFromToRangeFilter, DateTimeFromToRangeFilter, TimeRangeFilter, MultipleChoiceFilter, RangeFilter, DateFilter, DateTimeFilter, TimeFilter, ChoiceFilter, BooleanFilter, NumericRangeFilter

from congo.templatetags.common import or_blank
from congo.templatetags.models import field_name
from congo.utils.date_time import parse_datetime, datetime_to_str, normalize_tz


class Cell(object):
    row = None

    def __init__(self, column, data, raw_data):
        self.column = column
        self.data = data
        self.raw_data = raw_data

    def __str__(self):
        return self.data


class Row(object):
    datagrid = None

    def __init__(self, datagrid, obj, cells, extra_params):
        self.datagrid = datagrid
        self.obj = obj
        self.cells = cells
        self.cell_map = {}
        self.extra_params = extra_params

        for cell in self.cells:
            cell.row = self
            self.cell_map[cell.column.id] = cell

    def __getattr__(self, field):
        return self.cell_map[field]

    def __iter__(self):
        for cell in self.cells:
            yield cell


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
                 sort_field = None, is_sortable = False, default_sort_dir = SORT_ASC,
                 link = False, link_func = None, render_func = None, data_func = None,
                 localize = True, normalize_tz = True, header_css_class = '', cell_css_class = '',
                 as_html = False, is_hidden = False, is_visible = None):

        self.id = None
        self.datagrid = None

        self.label = label # etykieta
        self.field_name = field_name # nazwa atrybutu modelu
        self.db_field = db_field # nazwa pola bazy danych
        self.param_name = param_name # nazwa parametru GET

        self.sort_field = sort_field # nazwa pola, po którym realizowane jest sortowanie, np. role__translations__name
        self.is_sortable = is_sortable # czy możliwe sortowanie?
        self.default_sort_dir = default_sort_dir # kierunek sortowania, domyślnie SORT_ASC

        self.link = link # czy wartość komórki ma być linkiem?
        self.link_func = link_func # własna f-cja generująca link, przyjmuje obiekt z queryset'u, domyślnie wywołuje get_absolute_url na atrybucie lub obiekcie
        self.render_func = render_func # f-cja generująca link, przyjmuje obiekt źródłowy
        self.data_func = data_func # f-cja generująca dane, przyjmuje obiekt źródłowy
        self.localize = localize # czy lokalizować wartość?
        self.normalize_tz = normalize_tz # czy normalizować strefę czasową?

        self.header_css_class = header_css_class
        self.cell_css_class = cell_css_class

        self.as_html = as_html # renderować html'a
        self.is_hidden = is_hidden # czy ukryć kolumne, np. gdy chcemy pobrac dane, ale nie wyświetlac ich w grid tylko np. w dialogu.
        self.is_visible = is_visible # czy pokazywac kolumne? True > pokazywac, False > ukrywac, None > zawsze pokazywac bez mozliwosci ukrycia

        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

        # State
        self.sort_priority = None
        self.sort_dir = None

        if self.is_hidden:
            self.is_visible = False

    def get_sort_cols(self):
        if self.is_sortable:
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

    def get_unsort_cols(self):
        if self.is_sortable:
            sort_list = copy(self.datagrid.param_name_sort_list)

            if self.sort_priority:
                del sort_list[self.sort_priority - 1]

            return sort_list
        else:
            return []

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
                value = getattr(obj, self.field_name)

            if isinstance(value, datetime) and self.normalize_tz:
                value = normalize_tz(value)

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
            get_display = 'get_%s_display' % self.field_name
            if hasattr(obj, get_display):
                # Sprawdzamy, czy uda się pobrać etykietę dla danych z obiektu cell_data
                rendered_cell = or_blank(getattr(obj, get_display)(), use_html = False)
            else:
                # Wpp próbujmy wyrenderować komórkę automatycznie na podst. cell_data
                rendered_cell = or_blank(cell_data, use_html = False)

            if isinstance(rendered_cell, datetime) and self.normalize_tz:
                # Próbujemy normalizować strefę czasową
                rendered_cell = normalize_tz(rendered_cell)

            if self.localize:
                # Próbujemy lokalizować wartość
                rendered_cell = str(formats.localize(rendered_cell))

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
            return mark_safe("""<a href="%s">%s</a>""" % (url, force_text(rendered_cell)))
        else:
            return force_text(rendered_cell)


class NonDatabaseColumn(Column):
    """
    NonDatabaseColumn pozwala na renderowanie column niezwiązanych z modelem.
    """

    def __init__(self, *args, **kwargs):
        kwargs['is_sortable'] = False
        Column.__init__(self, *args, **kwargs)

        if not self.data_func:
            raise NotImplementedError("data_func() method must be implemented in NonDatabaseColumn")


class DataGrid(object):

    def __init__(self, request, queryset, **kwargs):
        self.request = request
        self.queryset = queryset

        self.rows = []
        self.columns = []
        self.param_name_sort_map = {} # key: param_name, val: id
        self.param_name_sort_list = [] # lista parametrów usera do sortowania - lub default_sort_list
        self.sort_field_sort_list = [] # lista pól bd do sortowania - uwzględnia extra_sort_list
        self.paginator = None
        self.page = None

        self.params = {}

        # Ustawiamy domyślne parametry z meta lub kwargs
        self.set_meta_data()

        # Ustawiamy kolumny dla klasy
        for attr in dir(self):
            column = getattr(self, attr)
            if isinstance(column, Column):
                self.columns.append(column)
                column.datagrid = self
                column.id = attr

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

                if column.is_sortable:
                    self.param_name_sort_map[column.param_name] = column.id

        self.columns.sort(key = lambda x: x.creation_counter)

        # Ustawiamy parametry z requst'a
        self.set_params()

        # Obsługujemy szukanie, filtrowanie, sortowanie
        self.handle_search() # must be before filtering in order to work well with fulltext / elastic search
        self.handle_filters()
        self.handle_sorting()

        # Wczytujemy obiekty z queryset'a
        self.precompute_objects()

    def get_from_kwargs_or_meta(self, kwargs, key, default = None):
        meta = getattr(self, 'Meta', None)
        return kwargs.get(key, getattr(meta, key, default))

    def set_meta_data(self, **kwargs):
        random_id = "datagrid-%s" % get_random_string(5, 'abcdefghijklmnopqrstuvwxyz0123456789')
        self.id = self.get_from_kwargs_or_meta(kwargs, 'id', random_id)

        # userconfig_class - klasa ustawień usera z pakietu congo
        self.userconfig_class = self.get_from_kwargs_or_meta(kwargs, 'userconfig_class', None)

        # prefetch_fields - lista pól do pobrania w odrębnym selecie i "podjoinowania" na poziomie Django - używać dla relacji many-to-many i many-to-one
        self.prefetch_fields = self.get_from_kwargs_or_meta(kwargs, 'prefetch_fields', None)

        # related_fields - lista pól do pobrania w tym samym selecie i "podjoinowania" na poziomie BD - używać dla relacji foreign key i one-to-one
        self.related_fields = self.get_from_kwargs_or_meta(kwargs, 'related_fields', None)

        # auto_related_fields - domyślnie True, szuka relacji, jeśli w nazwie pola znajdzie __, chyba, że podano related_fields ręcznie
        self.auto_related_fields = self.get_from_kwargs_or_meta(kwargs, 'auto_related_fields', True)

        # search_fields - lista pól do przeszukania za pomoca Django ORM (o ile nie ma indeksu fulltext lub elasticsearch)
        self.search_fields = self.get_from_kwargs_or_meta(kwargs, 'search_fields', None)

        # filterset_class - klasa zestawu filtrow z pakiedu django-filters
        self.filterset_class = self.get_from_kwargs_or_meta(kwargs, 'filterset_class', None)

        # default_page_size
        self.default_page_size = self.get_from_kwargs_or_meta(kwargs, 'default_page_size', 10)

        # page_size_list
        self.page_size_list = self.get_from_kwargs_or_meta(kwargs, 'page_size_list', [10, 20, 50, 100])

        if self.default_page_size not in self.page_size_list:
            self.page_size_list.append(self.default_page_size)
            self.page_size_list.sort()

        # default_sort_list - lista pól jako param_name, bo trzeba zainicjować
        self.default_sort_list = self.get_from_kwargs_or_meta(kwargs, 'default_sort_list', [])

        # extra_sort_list - lista pól jako sort_field, bo można sortować wg pól spoza listy kolumn
        self.extra_sort_list = self.get_from_kwargs_or_meta(kwargs, 'extra_sort_list', [])

    def set_params(self):
        if 'application/json' in self.request.META.get('CONTENT_TYPE', ''):
            self.params = self.request.data
        else:
            self.params = self.request.GET

        # force_filters
        # this parameters forces filter dict to be returned in a grid's JSON
        # this is needed ex on grid init
        self.force_filters = self.params.get('force_filters', False)
        self.default_filters = self.params.get('default_filters', False)

        # paginator
        paginator = self.params.get('paginator', {})

        # page_num
        page_num = paginator.get('page', 1)
        try:
            self.page_num = int(page_num)
        except ValueError:
            self.page_num = 1

        # page_size
        page_size = paginator.get('size', self.default_page_size)
        try:
            self.page_size = int(page_size)
        except ValueError:
            self.page_size = self.default_page_size

        # visible_cols
        self.set_visible_cols()

    def set_visible_cols(self):
        """
        This function sets visible column list by sent params or stored user config.
        In order to make this function work you need to set unique grid ID and define a userconfig_class.
        """

        if not self.userconfig_class:
            return

        key = '%s-vc' % self.id
        default_visible_cols = [c.param_name for c in self.columns if c.is_visible]
        visible_cols = self.params.get('visible_cols', None)
        reset_cols = self.params.get('reset_visible_cols', False)

        if reset_cols:
            self.userconfig_class.set_value(self.request, key, ','.join(default_visible_cols))

        elif visible_cols is None:
            user_visible_cols = self.userconfig_class.get_value(self.request, key)
            if user_visible_cols is not None:
                user_visible_cols = user_visible_cols.split(',')

                for c in self.columns:
                    if not (c.is_visible is None or c.is_hidden):
                        c.is_visible = c.param_name in user_visible_cols

            else:
                self.userconfig_class.set_value(self.request, key, ','.join(default_visible_cols))

        else:
            user_visible_cols = []

            for c in self.columns:
                if not (c.is_visible is None or c.is_hidden):
                    c.is_visible = c.param_name in visible_cols
                    if c.is_visible:
                        user_visible_cols.append(c.param_name)

            self.userconfig_class.set_value(self.request, key, ','.join(user_visible_cols))

    def precompute_objects(self):
        """
        Builds the queryset and stores the list of objects for use in
        rendering the datagrid.
        """
        queryset = self.queryset

        # prefetch_fields
        if self.prefetch_fields is not None:
            queryset = queryset.prefetch_related(*self.prefetch_fields)

        # related_fields
        if self.related_fields is not None:
            queryset = queryset.select_related(*self.related_fields)

        # auto_related_fields
        elif self.auto_related_fields:
            # Jeśli występuje relacja, od razu pobierzmy powiązane obiekty.
            # Aby zapobiec temu zachowaniu, ustaw auto_related_fields = False lub related_fields = []
            related_fields = []

            for column in self.columns:
                fields = column.db_field.split('__', 1)
                if len(fields) > 1:
                    related_fields.append(fields[0])

            if related_fields:
                queryset = queryset.select_related(*related_fields)

        # sort_field_sort_list
        if self.sort_field_sort_list:
            queryset = queryset.order_by(*self.sort_field_sort_list)

        # paginator
        self.paginator = Paginator(queryset, self.page_size)

        try:
            self.page = self.paginator.page(self.page_num)
        except InvalidPage:
            self.page = self.paginator.page(1)

        # rows
        self.rows = []

        for obj in self.page.object_list:
            cells = []

            for column in self.columns:
                if column.is_visible != False:
                    cell_data = column.get_cell_data(obj)
                    cells.append(Cell(column, column.render_cell(obj, cell_data), cell_data))

            self.rows.append(Row(self, obj, cells, self.extra_row_params(obj)))

    def extra_row_params(self, row_object):
        """
        Daje mozliwosc dodania dodatkowych parametrow na row w koncekscie obj.

        Usage:

        return {
            'css_class': "my-custom-id-%s" %s row_object.id,
        }

        """

        return {}

    def handle_search(self):
        """
        Here you can search your queryset. Use classic Django ORM or use fulltext.
        More about fulltext search here: https://blog.confirm.ch/django-1-8-mysql-mariadb-full-text-search/, eg:

        if self.search_fields:
            query = self.params.get('q', None)
            if query:
                self.queryset = self.queryset.search(query)

        But you'd better use elasticsearch, eg:

        if query:
            s = CarDocument.search().filter("term", content=query)[:10]
            qs = s.to_queryset()

        Start with elasticsearch here: https://github.com/sabricot/django-elasticsearch-dsl
        and here: https://www.merixstudio.com/blog/elasticsearch-django-rest-framework/
        """
        if self.search_fields:
            query = self.params.get('q', None)
            if query:
                q = Q()
                for f in self.search_fields:
                    q = q | Q(**{"%s__icontains" % f: query})
                self.queryset = self.queryset.filter(q)

    def handle_filters(self):
        """
        You can filter your queryset here...
        """

        if self.filterset_class:
            data = {}

            if hasattr(self.filterset_class.Meta, 'defaults') and self.default_filters:
                _filters = self.filterset_class.Meta.defaults
            else:
                _filters = self.params.get('filters', {})

            if _filters:
                for name, f in self.filterset_class.get_filters().items():

                    if name in _filters:

                            # @og 4 debug
#                            print()
#                            print(_filters[name])
#                            print('name', name)
#                            print('clss', f.__class__.__name__)
#                            print('field_name', f.field_name)
#                            print('lookup_expr', f.lookup_expr)
#                            print('label', f.label)
#                            print('method', f.method)
#                            print('distinct', f.distinct)
#                            print()

                        # DateFromToRangeFilter, TimeRangeFilter
                        if isinstance(f, (DateFromToRangeFilter, TimeRangeFilter)):
                            if not _filters[name].get('is_initial', False):
                                if 'raw_min' in _filters[name]:
                                    data['%s_after' % name] = _filters[name]['raw_min']
                                if 'raw_max' in _filters[name]:
                                    data['%s_before' % name] = _filters[name]['raw_max']

                        # DateTimeFromToRangeFilter
                        elif isinstance(f, DateTimeFromToRangeFilter):
                            if not _filters[name].get('is_initial', False):
                                if 'raw_min' in _filters[name]:
                                    data['%s_after' % name] = _filters[name]['raw_min']
                                if 'raw_max' in _filters[name]:
                                    val = _filters[name]['raw_max']

                                    # profesjonalny drut: jeśli nie wskazano czasu, określamy godzinę 23:59:59
                                    _val = parse_datetime(val)
                                    if _val and not any([_val.hour, _val.minute, _val.second]):
                                        _val = _val.replace(hour = 23, minute = 59, second = 59)
                                        val = datetime_to_str(_val, '%Y-%m-%d %H:%M:%S')

                                    data['%s_before' % name] = val

                        # DateFilter, DateTimeFilter, TimeFilter
                        elif isinstance(f, (DateFilter, DateTimeFilter, TimeFilter)):
                            if not _filters[name].get('is_initial', False):
                                if 'raw_val' in _filters[name]:
    #                                key = '%s_%s' % (name, f.lookup_expr)
                                    data[name] = _filters[name]['raw_val']

                        # NumericRangeFilter, RangeFilter
                        elif isinstance(f, (NumericRangeFilter, RangeFilter)):
                            if not _filters[name].get('is_initial', False):
                                if 'min' in _filters[name]:
                                    data['%s_min' % name] = _filters[name]['min']
                                if 'max' in _filters[name]:
                                    data['%s_max' % name] = _filters[name]['max']

                        else:
                            data[name] = _filters[name]

            # @og 4 debug
#             print()
#             print('_filters', _filters)
#             print()
#             print('data', data)
#             print()

            self.filterset = self.filterset_class(data, queryset = self.queryset)
            self.queryset = self.filterset.qs

            # @og 4 debug
            # print('query', self.queryset.query)

    @classmethod
    def _format_value(cls, f, value):
        if isinstance(f, (DateFilter, DateFromToRangeFilter)):
            value = value.strftime('%Y-%m-%d')
        elif isinstance(f, (DateTimeFilter, DateTimeFromToRangeFilter)):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(f, (TimeFilter, TimeRangeFilter)):
            value = value.strftime('%H:%M:%S')
        return value

    def get_filters(self, force_filters = None):
        filters = {}

        if self.filterset_class:
            if hasattr(self, 'filterset'):
                filterset = self.filterset
            else:
                filterset = self.filterset_class(self.params, queryset = self.queryset)

            fields = filterset.form.fields
            cleaned_data = self.filterset.form.cleaned_data
            errors = self.filterset.errors.get_json_data()

            has_filters = any(cleaned_data.values()) or bool(errors)
            force_filters = force_filters or self.force_filters

            # @og 4 debug
#            print()
#            print('params', self.params)
#            print('fields', fields)
#            print('cleaned_data', cleaned_data)
#            print()
#            print('errors', errors)
#            print('has_filters', has_filters)
#            print('force_filters', force_filters)
#            print()

            if not (has_filters or force_filters):
                return None

            for name, f in filterset.get_filters().items():
                field = fields[name]

                filters[name] = {
                    'label': field.label,
                    'field_name': f.field_name,
#                     'lookup_expr': f.lookup_expr,
                    'filter_type': f.__class__.__name__,
#                     'field_type': field.__class__.__name__,
                }

                if hasattr(field, 'choices'):
                    filters[name]['choices'] = [{'id': k, 'label': v} for k, v in field.choices]

                if hasattr(self.filterset_class.Meta, 'defaults'):
                    if name in self.filterset_class.Meta.defaults:
                        filters[name]['defaults'] = self.filterset_class.Meta.defaults[name]

                if hasattr(self.filterset_class.Meta, 'initials'):
                    if name in self.filterset_class.Meta.initials:
                        filters[name]['initials'] = self.filterset_class.Meta.initials[name]

                if name in cleaned_data:
                    cleaned_value = cleaned_data[name]
                    value = None

                    # NumericRangeFilter, RangeFilter (2x input)
                    # DateFromToRangeFilter, DateTimeFromToRangeFilter, TimeRangeFilter (2x input + cal widget)
                    if isinstance(f, RangeFilter):
                        if cleaned_value:
                            value_min = getattr(cleaned_value, 'start')
                            value_max = getattr(cleaned_value, 'stop')

                            value = {}
                            if value_min:
                                value['min'] = self._format_value(f, value_min)
                            if value_max:
                                value['max'] = self._format_value(f, value_max)

                    # DateFilter, TimeFilter, DateTimeFilter (input + cal widget)
                    elif isinstance(f, (DateFilter, TimeFilter, DateTimeFilter)):
                        if cleaned_value:
                            value = {}
                            value['val'] = self._format_value(f, cleaned_value)

                    # MultipleChoiceFilter, ModelMultipleChoiceFilter (multiselect)
                    elif isinstance(f, MultipleChoiceFilter):
                        value = []
                        for obj in cleaned_value:
                            if isinstance(obj, models.Model):
                                value.append(obj.id)
                            else:
                                value.append(obj)

                    # ChoiceFilter, ModelChoiceFilter (select)
                    elif isinstance(f, ChoiceFilter):
                        if isinstance(cleaned_value, models.Model):
                            value = cleaned_value.id
                        else:
                            value = cleaned_value

                    # BooleanFilter (select)
                    elif isinstance(f, BooleanFilter):
                        choices = [
                            (True, _('Tak')),
                            (False, _('Nie')),
                        ]
                        if isinstance(field, NullBooleanField):
                            choices.append((None, _('(Brak)')))

                        filters[name]['choices'] = [{'id': k, 'label': v} for k, v in choices]

                    # NumberFilter, CharFilter (input)
                    else:
                        value = cleaned_value

                    filters[name]['value'] = value

                if name in errors:
                    filters[name]['errors'] = errors[name]

        # @og 4 debug
#         print()
#         print('filters')
#         print(filters)
#         print()

        return filters

    def handle_sorting(self):

        self.param_name_sort_list = []
        self.sort_field_sort_list = []

        param_name_sort_list = self.params.get('sort', [])
        i = 1

        if param_name_sort_list:
            # sortujemy wg parametrów usera
            if isinstance(param_name_sort_list, str):
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

        # ustawiamy dodatkowe sortowanie, ale nie ma tu jak kontrolować
        # poprawności, więc przy pomyłce dostaniemy błąd
        for sort_field in self.extra_sort_list:
            if sort_field not in self.sort_field_sort_list:
                self.sort_field_sort_list.append(sort_field)

    def get_first_page_num(self):
        if self.page.has_previous() and self.page.previous_page_number() > 1:
            return 1
        return None

    def get_last_page_num(self):
        if self.page.has_next() and self.page.next_page_number() < self.paginator.num_pages:
            return self.paginator.num_pages
        return None

    def get_prev_page_num(self):
        if self.page.has_previous():
            return self.page.previous_page_number()
        return None

    def get_next_page_num(self):
        if self.page.has_next():
            return self.page.next_page_number()
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

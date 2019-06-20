# -*- coding: utf-8 -*-
from collections import OrderedDict
from copy import copy
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.db.models import Q
from django.db.models.aggregates import Count
from django.db.models.fields.related import RelatedField
from django.http.request import QueryDict
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.db.models.fields import DateTimeField, DateField
from django.utils.timezone import make_aware

@python_2_unicode_compatible
class SearchOrdering(object):
    def __init__(self, filterset, ordering_name, **kwargs):
        self.filterset = filterset
        self.ordering_name = ordering_name

        self._attr_name = kwargs.get('attr_name', None)
        self._label = kwargs.get('label', None)

        self._asc_desc_label = kwargs.get('asc_desc_label', "[A-Z],[Z-A]").split(',')
        self.allow_asc = kwargs.get('allow_asc', True)
        self.allow_desc = kwargs.get('allow_desc', True)
        self.set_asc(kwargs.get('is_asc', True))
        self.is_active = False

    def __str__(self):
        return "%s.%s" % (self.model.__name__, self.attr_name)

    @property
    def model(self):
        return self.filterset.model

    @property
    def attr_name(self):
        if self._attr_name is None:
            self._attr_name = self.ordering_name
        return self._attr_name

    @property
    def field(self):
        if not hasattr(self, '_field'):
            try:
                self._field = self.model._meta.get_field(self.attr_name)
            except FieldDoesNotExist:
                self._field = None
        return self._field

    @property
    def label(self):
        if self._label is None:
            self._label = self.field.verbose_name if self.field else self.ordering_name
        return self._label

    @property
    def asc_desc_label(self):
        return self._asc_desc_label[0] if self.is_asc else self._asc_desc_label[1]

    @property
    def asc_label(self):
        return self._asc_desc_label[0]

    @property
    def desc_label(self):
        return self._asc_desc_label[1]

    def set_asc(self, is_asc):
        if is_asc:
            self.is_asc = True if self.allow_asc else False
        else:
            self.is_asc = False if self.allow_desc else True

    @property
    def asc_ordering_name(self):
        return self.ordering_name if self.allow_asc else None

    @property
    def desc_ordering_name(self):
        return "-%s" % self.ordering_name if self.allow_desc else None

    @classmethod
    def parse_ordering(cls, ordering_name):
        if ordering_name[0] == '-':
            return (ordering_name[1:], False)
        return (ordering_name, True)

    def get_query_dict(self, value, query_dict = None):
        if query_dict is None:
            query_dict = self.filterset.query_dict

        new_dict = copy(query_dict)
        new_dict[self.filterset.ordering_param] = value

        return new_dict

@python_2_unicode_compatible
class SearchFilter(object):
    OPERATORS = ['exact', 'eq', 'lt', 'lte', 'gte', 'gt', 'in']

    LIST = 'LIST'
    SELECT = 'SELECT'
    INPUT = 'INPUT'
    WIDGETS = [LIST, SELECT, INPUT]

    def __init__(self, filterset, filter_name, **kwargs):
        self.filterset = filterset
        self.filter_name = filter_name

        self._attr_name = kwargs.get('attr_name', None)
        self._param = kwargs.get('param', None)
        self._label = kwargs.get('label', None)

        self._to_python = kwargs.get('to_python', None)
        self._to_string = kwargs.get('to_string', None)

        operator = kwargs.get('operator', None)
        self.operator = operator if operator in self.OPERATORS else self.OPERATORS[0]

        self.mapped_values = dict([(unicode(v), m) for v, m in kwargs.get('mapped_values', [])])
        self.valid_values = [self.to_python(value) for value in kwargs.get('valid_values', [])]
        self.valid_format = kwargs.get('valid_format', None)
        self.ignore_none_value = kwargs.get('ignore_none_value', True)

        widget = kwargs.get('widget', None)
        self.widget = widget if widget in self.WIDGETS else self.WIDGETS[0]
        self.css_class = kwargs.get('css_class', None)
        self.placeholder = kwargs.get('placeholder', None)

    def __str__(self):
        return "%s.%s (%s)" % (self.model.__name__, self.filter_name, self.operator)

    @property
    def model(self):
        return self.filterset.model

    @property
    def attr_name(self):
        if self._attr_name is None:
            self._attr_name = self.filter_name
        return self._attr_name

    @property
    def field(self):
        if not hasattr(self, '_field'):
            self._field = self.model._meta.get_field(self.attr_name)
        return self._field

    def to_python(self, value):
        if self._to_python:
            return self._to_python(value)
        else:
            value = self.field.to_python(value)
            if isinstance(self.field, RelatedField):
                try:
                    value = long(value)
                except (TypeError, ValueError):
                    value = None
            elif isinstance(self.field, (DateTimeField, DateField)):
                value = make_aware(value)
            return value

    def to_string(self, value):
        if self._to_string:
            return self._to_string(value)
        else:
            return smart_text(value)

    @property
    def label(self):
        if self._label is None:
            self._label = self.field.verbose_name
        return self._label

    @property
    def param(self):
        if self._param is None:
            self._param = self.filter_name
        return self._param

    def get_value(self, query_dict = None):
        if query_dict is None:
            query_dict = self.filterset.query_dict
        value = query_dict.get(self.param)
        try:
            return self.to_python(value)
        except:
            return None

    def map_value(self, value):
        try:
            return self.mapped_values[unicode(value)]
        except KeyError:
            return value

    def get_string(self, query_dict = None):
        value = self.get_value(query_dict)
        if value is None:
            return ''
        return self.to_string(value)

    def get_value_list(self, query_dict = None):
        if query_dict is None:
            query_dict = self.filterset.query_dict

        value_list = []

        for value in query_dict.getlist(self.param):
            try:
                value_list.append(self.to_python(value))
            except:
                pass

        return value_list

    def get_string_list(self, query_dict = None):
        string_list = []

        for value in self.get_value_list(query_dict):
            string_list.append(self.to_string(value))

        return string_list

    def get_values(self, queryset):
        return queryset.values_list(self.attr_name, flat = True).distinct().order_by(self.attr_name)

    def count_values(self, queryset = None, values_to_count = [], sort_values = True):
        if queryset is None:
            queryset = self.filterset.queryset

        set_values = self.get_value_list()
        values = []

        values_to_count = [self.to_python(value) for value in values_to_count]
        if self.valid_values:
            if values_to_count:
                values_to_count = [v for v in values_to_count if v in self.valid_values]
            else:
                values_to_count = self.valid_values


        if self.operator == 'exact':
            if values_to_count:
                field = "%s__in" % self.attr_name
                queryset = queryset.filter(**{field: values_to_count})

            for value_dict in queryset.values(self.attr_name).annotate(count = Count(self.attr_name)).order_by():
                value = self.to_python(value_dict[self.attr_name])
                if value is None:
                    if self.ignore_none_value:
                        continue
                    else:
                        field = "%s__isnull" % self.attr_name
                        count = queryset.filter(**{field: True}).count()
                else:
                    count = value_dict['count']
                is_set = value in set_values
                values.append((self.to_string(value), count, is_set))
        else:
            for value in values_to_count:
                if value is None:
                    if self.ignore_none_value:
                        continue
                    else:
                        field = "%s__isnull" % self.attr_name
                        count = queryset.filter(**{field: True}).count()
                else:
                    field = "%s__%s" % (self.attr_name, self.operator)
                    count = queryset.filter(**{field: value}).count()
                is_set = value in set_values
                if count:
                    values.append((self.to_string(value), count, is_set))
        if sort_values:
            values.sort(key = lambda v: v[1], reverse = True)

        return values

    def filter(self, queryset, query_dict):
        field = "%s__%s" % (self.attr_name, self.operator)
        query = Q()

        for value in self.get_value_list(query_dict):
            if value is None:
                if self.ignore_none_value:
                    continue
                else:
                    field = "%s__isnull" % self.attr_name
                    value = True
            query = query | Q(**{field: value})
        return queryset.filter(query)

    def get_query_dict(self, add_values = [], del_values = [], query_dict = None):
        if query_dict is None:
            query_dict = self.filterset.query_dict

        new_dict = copy(query_dict)
        string_list = self.get_string_list(new_dict)

        for value in add_values:
            if isinstance(value, list):
                value_list = value
            else:
                value_list = [value]
            for v in value_list:
                try:
                    v = self.to_string(v)
                    if v not in string_list:
                        string_list.append(v)
                except ValidationError:
                    pass

        for value in del_values:
            if isinstance(value, list):
                value_list = value
            else:
                value_list = [value]
            for v in value_list:
                try:
                    v = self.to_string(v)
                    string_list.remove(v)
                except (ValueError, ValidationError):
                    pass

        if string_list:
            new_dict.setlist(self.param, string_list)
        elif self.param in new_dict:
            del new_dict[self.param]

        return new_dict

@python_2_unicode_compatible
class SearchFilterSet(object):
    def __init__(self, queryset, query_dict = None, *args, **kwargs):
        self.queryset = queryset
        self.query_dict = query_dict

        self.page_param = kwargs.get('page_param', 'page')
        self.ordering_param = kwargs.get('ordering_param', 'sort')
        self.default_ordering = []
        self.extra_ordering = []

        self._filters = OrderedDict()
        self._ordering = OrderedDict()

    def __str__(self):
        return [unicode(f) for f in self.filters]

    def __iter__(self):
        for f in self.filters:
            yield  f

    @property
    def model(self):
        return self._queryset.model

    @property
    def queryset(self):
        return self._queryset.all()

    @queryset.setter
    def queryset(self, value):
        self._queryset = value

    @property
    def query_dict(self):
        return copy(self._query_dict)

    @query_dict.setter
    def query_dict(self, value):
        self._query_dict = QueryDict(mutable = True) if value is None else value

    # filters

    @property
    def filters(self):
        return self._filters.values()

    def add_filter(self, filter_name, *args, **kwargs):
        self._filters[filter_name] = SearchFilter(self, filter_name, *args, **kwargs)

    def get_filter(self, filter_name):
        if filter_name in self._filters:
            return self._filters[filter_name]
        return None

    def filter(self, queryset = None, query_dict = None, exclude = [], update_queryset = True):
        if queryset is None:
            queryset = self.queryset

        if query_dict is None:
            query_dict = self.query_dict

        for filter_name, f in self._filters.items():
            if filter_name not in exclude:
                queryset = f.filter(queryset, query_dict)

        if update_queryset:
            self.queryset = queryset.all()

        return queryset

    def has_set_filters(self, query_dict = None):
        if query_dict is None:
            query_dict = self.query_dict

        for f in self.filters:
            if f.get_value_list():
                return True

        return False

    def get_set_filters(self, query_dict = None):
        if query_dict is None:
            query_dict = self.query_dict

        return [f for f in self.filters if f.get_value_list()]

    # ordering

    def add_ordering(self, ordering_name, *args, **kwargs):
        self._ordering[ordering_name] = SearchOrdering(self, ordering_name, *args, **kwargs)

    def add_default_ordering(self, ordering_name, asc = True):
        ordering = self._ordering.get(ordering_name, None)
        if ordering:
            if asc and ordering.allow_asc:
                self.default_ordering.append((ordering_name, asc))
            elif not asc and ordering.allow_desc:
                self.default_ordering.append((ordering_name, asc))

    def add_extra_ordering(self, ordering_name, asc = True):
        ordering = self._ordering.get(ordering_name, None)
        if ordering:
            if asc and ordering.allow_asc:
                self.extra_ordering.append((ordering_name, asc))
            elif not asc and ordering.allow_desc:
                self.extra_ordering.append((ordering_name, asc))

    def get_ordering(self):
        ordering_list = copy(self._ordering)
        active_ordering = self.get_active_ordering()

        for ordering_name, ordering in ordering_list.items():
            if ordering_name == active_ordering.ordering_name:
                ordering.is_active = True
                ordering.set_asc(active_ordering.is_asc)
            else:
                ordering.is_active = False

        return ordering_list.values()

    def get_active_ordering(self, query_dict = None):
        if query_dict is None:
            query_dict = self.query_dict

        ordering_dict = copy(self._ordering)

        for ordering_name_asc in query_dict.getlist(self.ordering_param):
            ordering_name, is_asc = SearchOrdering.parse_ordering(ordering_name_asc)

            if ordering_name in ordering_dict:
                ordering = ordering_dict[ordering_name]
                ordering.set_asc(is_asc)
                return ordering

        for ordering_name, is_asc in self.default_ordering:
            ordering = ordering_dict[ordering_name]
            ordering.set_asc(is_asc)
            return ordering

        for ordering in ordering_dict.values():
            return ordering

    def get_order_by(self, query_dict = None):
        if query_dict is None:
            query_dict = self.query_dict

        ordering_dict = copy(self._ordering)
        order_by_dict = OrderedDict()

        for ordering_name_asc in query_dict.getlist(self.ordering_param):
            ordering_name, is_asc = SearchOrdering.parse_ordering(ordering_name_asc)

            if ordering_name in ordering_dict:
                ordering = ordering_dict[ordering_name]
                ordering.set_asc(is_asc)
                order_by_dict[ordering_name] = ordering

        if not order_by_dict:
            for ordering_name, is_asc in self.default_ordering:
                ordering = ordering_dict[ordering_name]
                ordering.set_asc(is_asc)
                order_by_dict[ordering_name] = ordering

        for ordering_name, is_asc in self.extra_ordering:
            if ordering_name not in order_by_dict:
                ordering = ordering_dict[ordering_name]
                ordering.set_asc(is_asc)
                order_by_dict[ordering_name] = ordering

        return [(ordering.attr_name if ordering.is_asc else "-%s" % ordering.attr_name) for ordering in order_by_dict.values()]

    # query_dict

    def get_query_dict(self, query_dict = None, exclude = []):
        if query_dict is None:
            query_dict = self.query_dict

        new_dict = copy(query_dict)

        for filter_name, f in self._filters.items():
            if filter_name in exclude:
                if f.param in new_dict:
                    del new_dict[f.param]
            else:
                value = f.get_string_list(query_dict)
                if value:
                    new_dict.setlist(f.param, value)

        return new_dict

    def get_clear_query_dict(self, query_dict = None):
        query_dict = self.get_query_dict(query_dict, exclude = self._filters.keys())
        if self.page_param in query_dict:
            del query_dict[self.page_param]
        return query_dict

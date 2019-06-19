import inspect
import re
import urllib.parse
from typing import Mapping, List, Any
import collections

import django.db.models as db_models
import django.db.models.aggregates as db_aggregates


class QuerySpec:
    """Parse and handle several kinds of queries for the charts

    The query language is pretty similar to Django's regular queries, with
    two additions:

    * keys & values are urlencoded, and multiple filters can be joined with '&'
    * query + ":" + function name can be used to specify an aggregate function
      to add to the filter

    Examples (is_filter=False):

    ``page__category:count`` (group views by their page's category count)
        ``query.values(x=Count('page__category')).annotate(F('x')

    Examples (is_filter=True):

    ``group__name__contains=Foo%20Bar``
        query.filter(group__name__contains='Foo Bar')
    ``group__users:count__lt=6``
        ``query.annotate(x=Count(group__users)).filter(x__lt=6)``


    Invalid text strings

    ``group__name__contains``
        invalid because ``__contains`` needs to be compared with a value
    ``page__category``
        invalid because category many-to-many to many relationship
    """

    # nb. make range work right
    def __init__(self, axis_text: str, group_text: str, filter_text: str):
        """
        :param axis_text: Text for the y axis query
        :param group_text: Text for the group by query
        :param filter_text: Text for the filter query
        """
        if not axis_text:
            axis_text = 'id:count'
        self.axis_parts = [QuerySpecPart(part, is_filter=False)
                           for part in axis_text.split('&')
                           if part != '']
        self.group_parts = [QuerySpecPart(part, is_filter=False)
                            for part in group_text.split('&')
                            if part != '']
        self.filter_parts = [QuerySpecPart(part, is_filter=True)
                             for part in filter_text.split('&')
                             if part != '']

    def update_queryset(self, qs, x_annotations, x_value):
        annotations = dict(('_django_adminstats_x_{}'.format(k), v) for k, v
                           in x_annotations.items())
        filters = {}
        values = {}
        axis_values = {}
        axis_annotations = {
            '_django_adminstats_x': db_models.F(
                '_django_adminstats_x_{}'.format(x_value))
        }
        final_values = ['_django_adminstats_x']

        for index, qsp in enumerate(self.filter_parts):
            if qsp.func is None:
                filters[qsp.col] = qsp.value
            else:
                key = '_django_adminstats_f_{}'.format(index)
                annotations[key] = qsp.expression_col()
                if qsp.func_lookup:
                    key = key + '__' + qsp.func_lookup
                filters[key] = qs.value
        for index, qsp in enumerate(self.axis_parts):
            value_key = '_django_adminstats_a_{}'.format(index)
            annotate_key = '_django_adminstats_axis_{}'.format(index)
            axis_values[value_key] = qsp.expression_col()
            axis_annotations[annotate_key] = db_models.F(value_key)
            final_values.append(annotate_key)
        for index, qsp in enumerate(self.group_parts):
            value_key = '_django_adminstats_gv_{}'.format(index)
            annotate_key = '_django_adminstats_group_{}'.format(index)
            axis_values[value_key] = qsp.expression_col()
            axis_annotations[annotate_key] = db_models.F(value_key)
            final_values.append(annotate_key)
        if filters:
            qs = qs.filter(**filters)
        return qs.values(**values).annotate(**annotations).values(
            **axis_values).annotate(**axis_annotations).values(*final_values)


class QuerySpecPart:

    FUNCS = collections.OrderedDict((
        ('count', db_aggregates.Count),
        ('sum', db_aggregates.Sum),
        ('avg', db_aggregates.Avg),
        ('min', db_aggregates.Min),
        ('max', db_aggregates.Max),
        ('stddev', db_aggregates.StdDev),
        ('variance', db_aggregates.Variance),
    ))
    FIELD_LOOKUPS = [
        'exact', 'iexact', 'contains', 'icontains', 'in', 'gt', 'gte', 'lt',
        'lte', 'startswith', 'endswith', 'range', 'date', 'month', 'day',
        'week', 'weekday', 'quarter', 'time', 'hour', 'minute', 'second',
        'isnull', 'regex', 'iregex']

    def __init__(self, text: str, *, is_filter: bool):
        self.is_filter = is_filter
        if not is_filter:
            parts = (text, '')
        else:
            parts = text.split('=', 1) if '=' in text else (text, '')
        col_func, self.value = (urllib.parse.unquote(p) for p in parts)

        if ':' in col_func:
            self.col, func = col_func.split(':', 1)
        else:
            self.col, func = col_func, None

        if func is None:
            self.func_name, self.func_lookup = None, None
        elif '__' in func:
            self.func_name, self.func_lookup = func.split('__', 1)
        else:
            self.func_name, self.func_lookup = func, None

    @property
    def func(self):
        if self.func_name not in self.FUNCS:
            return None
        return self.FUNCS[self.func_name]

    def expression_col(self):
        """Used with not filter lookups, gets the expression to query.

        This will normally return an F() value or an aggregate function
        like Count(field)
        """
        exp = self.func if self.func else db_models.F
        return exp(self.col)

    @staticmethod
    def _model_options(model: type) -> Mapping[str, db_models.Field]:
        meta = getattr(model, '_meta')
        return getattr(meta, '_forward_fields_map').copy()
        # note: _forward_fields_map is a dict, which currently (in Python
        # 3.6 & 3.7) maintains insertion order, If this is no longer the
        # case in the future, we can get the fields with
        # return collections.OrderedDict((f.name, f) for f in meta.fields)
        # but that won't include the *_id fields :-/

    @staticmethod
    def _field_options(field: db_models.Field) -> Mapping[str, Any]:
        return field.get_lookups()

    @staticmethod
    def _is_field_or_lookup(obj: Any) -> bool:
        return (issubclass(obj, db_models.Lookup)
                if inspect.isclass(obj) else
                isinstance(obj, db_models.Field))

    def options(self, model: type) -> List[str]:
        """Given a filter string, return the next options"""
        options = self._model_options(model)
        query_startswith = ''
        top_key = ''
        last_key = ''
        last_obj = model

        for match in re.finditer(r'(^|__)(\w*?)(?=__|$)', self.col):
            # add last item
            part = match.group(2)
            if part == '':
                continue
            elif part in options:
                last_obj = options[part]
                last_key = self.col[:match.end()]
                query_startswith = ''
                key = self.col[:match.end()]
                top_key = key
                if isinstance(last_obj, db_models.Field):
                    if last_obj.related_model is not None:
                        last_obj = last_obj.related_model
                        options = self._model_options(last_obj)
                    elif self.is_filter:
                        options = self._field_options(last_obj)
                    else:
                        options = {}
                else:
                    options = {}
                continue
            query_startswith = part
            break
        result = []
        if top_key != '':
            result = [top_key]

        if self.value == '':
            if query_startswith == '':
                if self._is_field_or_lookup(last_obj):
                    if self.func_name is None:
                        result.append(last_key + ':count')
                    else:
                        result += [
                            last_key + ':' + fn for fn in self.FUNCS.keys()
                            if fn.startswith(self.func_name)]

            duplicate_keys = set()
            # clear out duplicate fkey_id field
            for key, field in options.items():
                if (getattr(field, 'related_model', None) is not None
                        and field.name != key
                        and options[field.name] is field):
                    duplicate_keys.add(key)
            for key in duplicate_keys:
                del options[key]
            keys = options.keys()
            if query_startswith != '':
                keys = (key for key in keys
                        if key.startswith(query_startswith))
            if last_key != '':
                keys = (last_key + '__' + key for key in keys)
            result = result + list(keys)

        # see if we need to add query stuff
        if self.is_filter:
            result = [item + '=' + self.value for item in result]
        return result

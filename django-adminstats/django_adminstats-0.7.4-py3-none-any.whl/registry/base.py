import abc
import collections
import typing
from datetime import date

import django.db.models as db_models
import django.db.models.functions as db_functions

from django_adminstats import Step
from django_adminstats.qs import QuerySpec


class Registration(metaclass=abc.ABCMeta):

    date_field = 'date'

    @property
    @abc.abstractmethod
    def key(self) -> str:
        """A unique string for this statistics registration"""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def label(self) -> str:
        """A human-readable name for these statistics"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_queryset(self):
        raise NotImplementedError

    def get_span_queryset(self, start, end, _period_step):
        qs = self.get_queryset().annotate(
            _date_field=db_functions.Cast(self.date_field,
                                          db_models.DateField()))
        kwargs = {'_date_field__gte': start, '_date_field__lt': end}
        return qs.filter(**kwargs)

    def get_x_parameters(self, period_step: Step):
        args = {}
        if period_step == Step.DAY:
            args['date'] = db_functions.TruncDay(
                self.date_field, output_field=db_models.DateField())
            args['month'] = db_functions.TruncMonth(self.date_field)
            args['year'] = db_functions.TruncYear(self.date_field)
        if period_step == Step.MONTH:
            args['date'] = db_functions.TruncMonth(
                self.date_field, output_field=db_models.DateField())
            args['year'] = db_functions.TruncYear(self.date_field)
        if period_step == Step.YEAR:
            args['date'] = db_functions.TruncYear(
                self.date_field, output_field=db_models.DateField())
        return args, 'date'

    def query(self, start: date, end: date,
              period_step: Step, query_spec: QuerySpec):
        qs = self.get_span_queryset(start, end, period_step)
        x_annotations, x_value = self.get_x_parameters(period_step)
        return query_spec.update_queryset(
            qs, x_annotations=x_annotations, x_value=x_value)

    def get_data(self, start: date, end: date,
                 period_step: Step, filter_text: str, group_text: str,
                 axis_text: str) -> typing.Mapping[
                    str, typing.Mapping[date, str]]:
        query_spec = QuerySpec(axis_text=axis_text, group_text=group_text,
                               filter_text=filter_text)
        qs = self.query(start, end, period_step, query_spec)
        result = {}  # type: typing.Dict[str, typing.Dict[date, str]]
        group_fields = ['_django_adminstats_group_{}'.format(index)
                        for index in range(len(query_spec.group_parts))]
        axis_fields = ['_django_adminstats_axis_{}'.format(index)
                       for index in range(len(query_spec.axis_parts))]
        for item in qs:
            group_key = ' / '.join(str(item[field]) for field in group_fields)
            value = ' / '.join(str(item[field]) for field in axis_fields)
            if group_key not in result:
                result[group_key] = {}
            result[group_key][item['_django_adminstats_x']] = value
        return result

    @abc.abstractmethod
    def query_options(self, text: str, *, is_filter: bool = False) -> list:
        """Given a filter string, return the next options"""


class Registry(collections.OrderedDict):

    def register(self, reg: Registration):
        self[reg.key] = reg

    def __getitem__(self, key: str) -> Registration:
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: Registration):
        super().__setitem__(key, value)

    def choices(self):
        for key, value in self.items():
            yield key, value.label

    def query(self, criteria):
        stats = self[criteria.stats_key]
        start, end = criteria.chart.span()
        return stats.get_data(start, end, Step(criteria.chart.period_step),
                              criteria.filter_query, criteria.group_query,
                              criteria.axis_query)

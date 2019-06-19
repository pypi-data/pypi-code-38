
from datetime import date
from typing import Mapping

import django.apps
import django.db.models as models
import trackstats.models
from django.contrib.contenttypes.models import ContentType

from django_adminstats import Step
from django_adminstats import qs

from .base import Registration


class MetricRegistration(Registration):

    def __init__(self, metric, model=None):
        # metric is probably a lazy object
        self.metric = metric
        self.model = model
        lazy_func = getattr(metric, '_setupfunc')
        contents = lazy_func.__closure__[1].cell_contents
        self.ref = contents['ref']
        domain = contents['domain']
        lazy_func = getattr(domain, '_setupfunc')
        contents = lazy_func.__closure__[1].cell_contents
        self.domain_ref = contents['ref']

    @property
    def key(self):
        if self.model is None:
            return 'trackstats:{}.{}'.format(self.domain_ref, self.ref)
        meta = getattr(self.model, '_meta')
        return 'trackstats:{}.{}:{}'.format(self.domain_ref, self.ref,
                                            meta.label_lower)

    @property
    def label(self):
        if self.model is None:
            return '{} {} Stats'.format(
                self.domain_ref, self.ref).title()
        meta = getattr(self.model, '_meta')
        return '{} {} ({}) Stats'.format(
            self.domain_ref, self.ref, meta.verbose_name).title()

    def get_queryset(self):
        if self.model is None:
            return trackstats.models.StatisticByDate.objects.filter(
                metric=self.metric)
        object_type = ContentType.objects.get_for_model(self.model)

        meta = getattr(trackstats.models.StatisticByDateAndObject, '_meta')

        cls_name = '_fake_StatisticByDateAndObject_{}'.format(
            self.model.__name__).lower()
        all_models = django.apps.apps.all_models['django_adminstats']
        if cls_name in all_models:
            new_class = all_models[cls_name]
        else:
            class FakeMeta:
                app_label = 'django_adminstats'
                # app_label = meta.app_label
                db_table = meta.db_table
                verbose_name = meta.verbose_name
                verbose_name_plural = meta.verbose_name_plural

            new_class = type(cls_name, (
                    trackstats.models.ByDateMixin,
                    trackstats.models.AbstractStatistic),
                {
                    '__module__': '__ignore__',
                    'Meta': FakeMeta,
                    'object_type': models.ForeignKey(
                        ContentType, on_delete=models.PROTECT),
                    'object_id': models.PositiveIntegerField(),
                    'object': models.ForeignKey(
                        to=self.model, on_delete=models.PROTECT)
                })
        qs = new_class.objects.filter(
            metric=self.metric, object_type=object_type)
        return qs

    def get_span_queryset(self, start: date, end: date,
                          period_step: Step):
        kwargs = {self.date_field + '__gte': start,
                  self.date_field + '__lt': end}
        if period_step == Step.DAY:
            kwargs['period'] = trackstats.models.Period.DAY
        elif period_step == Step.MONTH:
            kwargs['period'] = trackstats.models.Period.MONTH
        else:
            # trackstats doesn't actually support year
            kwargs['period'] = trackstats.models.Period.LIFETIME
        return self.get_queryset().filter(**kwargs)

    def query(self, start: date, end: date,
              period_step: Step, query_spec: qs.QuerySpec):
        qs = self.get_span_queryset(start, end, period_step)
        if self.model:
            x_annotations, x_value = self.get_x_parameters(period_step)
            return query_spec.update_queryset(
                qs, x_annotations=x_annotations, x_value=x_value)
        x_annotations, x_value = self.get_x_parameters(period_step)
        return query_spec.update_queryset(
            qs, x_annotations=x_annotations, x_value=x_value)

    def get_data(self, start: date, end: date,
                 period_step: Step, filter_text: str, group_text: str,
                 axis_text: str) -> Mapping[str, Mapping[date, str]]:
        if axis_text != '':
            raise ValueError('Axis not supported for tracstats')
        if not group_text:
            group_text = 'object_id' if self.model else ''
        return super().get_data(start, end, period_step, filter_text,
                                group_text, 'value')

    def query_options(self, text: str, *, is_filter: bool = False) -> list:
        """Given a filter string, return the next options"""
        if self.model is None:
            return []
        if text.startswith('object'):
            text = text[len('object')+2:]
            part = qs.QuerySpecPart(text, is_filter=is_filter)
            return ['object__' + item for item in part.options(self.model)]
        else:
            part = qs.QuerySpecPart(text, is_filter=is_filter)
            return part.options(trackstats.models.StatisticByDateAndObject)

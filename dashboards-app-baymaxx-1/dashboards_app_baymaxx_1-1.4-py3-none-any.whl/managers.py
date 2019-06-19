# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from collections import Counter
except ImportError:
    from backport_collections import Counter

import datetime
from operator import attrgetter

from django.db import models
from django.utils.timezone import now

from aldryn_apphooks_config.managers.base import ManagerMixin, QuerySetMixin
from aldryn_people.models import Person
from parler.managers import TranslatableManager, TranslatableQuerySet
from taggit.models import Tag, TaggedItem


class DashboardQuerySet(QuerySetMixin, TranslatableQuerySet):
    def published(self):
        """
        Returns dashboards that are published AND have a publishing_date that
        has actually passed.
        """
        return self.filter(is_published=True, publishing_date__lte=now())


class RelatedManager(ManagerMixin, TranslatableManager):
    def get_queryset(self):
        qs = DashboardQuerySet(self.model, using=self.db)
        return qs.select_related('featured_image')

    def published(self):
        return self.get_queryset().published()

    def get_months(self, request, namespace):
        """
        Get months and years with dashboards count for given request and namespace
        string. This means how many dashboards there are in each month.

        The request is required, because logged-in content managers may get
        different counts.

        Return list of dictionaries ordered by dashboard publishing date of the
        following format:
        [
            {
                'date': date(YEAR, MONTH, ARBITRARY_DAY),
                'num_dashboards': NUM_ARTICLES
            },
            ...
        ]
        """

        # TODO: check if this limitation still exists in Django 1.6+
        # This is done in a naive way as Django is having tough time while
        # aggregating on date fields
        if (request and hasattr(request, 'toolbar') and
                request.toolbar and request.toolbar.edit_mode):
            dashboards = self.namespace(namespace)
        else:
            dashboards = self.published().namespace(namespace)
        dates = dashboards.values_list('publishing_date', flat=True)
        dates = [(x.year, x.month) for x in dates]
        date_counter = Counter(dates)
        dates = set(dates)
        dates = sorted(dates, reverse=True)
        months = [
            # Use day=3 to make sure timezone won't affect this hacks'
            # month value. There are UTC+14 and UTC-12 timezones!
            {'date': datetime.date(year=year, month=month, day=3),
             'num_dashboards': date_counter[(year, month)]}
            for year, month in dates]
        return months

    def get_authors(self, namespace):
        """
        Get authors with dashboards count for given namespace string.

        Return Person queryset annotated with and ordered by 'num_dashboards'.
        """

        # This methods relies on the fact that Dashboard.app_config.namespace
        # is effectively unique for Dashboard models
        return Person.objects.filter(
            dashboard__app_config__namespace=namespace,
            dashboard__is_published=True).annotate(
                num_dashboards=models.Count('dashboard')).order_by('-num_dashboards')

    def get_tags(self, request, namespace):
        """
        Get tags with dashboards count for given namespace string.

        Return list of Tag objects ordered by custom 'num_dashboards' attribute.
        """
        if (request and hasattr(request, 'toolbar') and
                request.toolbar and request.toolbar.edit_mode):
            dashboards = self.namespace(namespace)
        else:
            dashboards = self.published().namespace(namespace)
        if not dashboards:
            # return empty iterable early not to perform useless requests
            return []
        kwargs = TaggedItem.bulk_lookup_kwargs(dashboards)

        # aggregate and sort
        counted_tags = dict(TaggedItem.objects
                            .filter(**kwargs)
                            .values('tag')
                            .annotate(tag_count=models.Count('tag'))
                            .values_list('tag', 'tag_count'))

        # and finally get the results
        tags = Tag.objects.filter(pk__in=counted_tags.keys())
        for tag in tags:
            tag.num_dashboards = counted_tags[tag.pk]
        return sorted(tags, key=attrgetter('num_dashboards'), reverse=True)

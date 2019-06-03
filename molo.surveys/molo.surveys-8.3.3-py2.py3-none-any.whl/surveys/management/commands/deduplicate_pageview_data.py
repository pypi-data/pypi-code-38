from __future__ import unicode_literals

from datetime import timedelta

from django.core.management.base import BaseCommand

from molo.surveys.models import MoloSurveyPageView


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_duplicates = []

        for pageview in MoloSurveyPageView.objects.all():
            params = {
                'page': pageview.page,
                'user': pageview.user,
                'visited_at__gt': pageview.visited_at,
                'visited_at__lte': pageview.visited_at + timedelta(minutes=1),
            }
            duplicates = MoloSurveyPageView.objects.filter(
                **params).values_list('id')
            for duplicate in duplicates:
                all_duplicates.extend(duplicate)

        MoloSurveyPageView.objects.filter(id__in=set(all_duplicates)).delete()

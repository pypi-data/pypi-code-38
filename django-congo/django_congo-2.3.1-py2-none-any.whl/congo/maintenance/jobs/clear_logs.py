# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.maintenance.jobs import BaseJob
from congo.utils.date_time import years_ago
from django.apps import apps
from django.contrib.admin.models import LogEntry
from django.core.exceptions import ImproperlyConfigured

class Job(BaseJob):
    description = "Removing admin and system logs older than 1 year"

    def __init__(self):
        super(Job, self).__init__()

    def _run(self, user, *args, **kwargs):
        result = {}

        # LogEntry
        queryset = LogEntry.objects.filter(action_time__lte = years_ago(1))
        result['LogEntry'] = queryset.count()
        queryset.delete()

        # Log
        model_name = settings.CONGO_LOG_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use Log model, configure settings.CONGO_LOG_MODEL first.")
        model = apps.get_model(*model_name.split('.', 1))

        queryset = model.objects.filter(date__lte = years_ago(1))
        result['Log'] = queryset.count()
        queryset.delete()

        return result

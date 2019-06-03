# -*- coding: utf-8
from django.apps import AppConfig


class GenomixWorkflowsConfig(AppConfig):
    name = 'genomix_workflows'

    def ready(self):
        from . import signals  # noqa NOTE: This is to setup signals

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BooksConfig(AppConfig):
    name = 'aparnik.packages.educations.books'
    verbose_name = _('Book')

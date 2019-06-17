# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BooksConfig(AppConfig):
    name = 'aparnik.packages.educations.books'
    verbose_name = _('Book')

# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BookmarkConfig(AppConfig):
    name = 'aparnik.contrib.bookmarks'
    verbose_name = _('Bookmarks')



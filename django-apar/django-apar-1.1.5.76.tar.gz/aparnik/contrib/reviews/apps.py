# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ReviewsConfig(AppConfig):
    name = 'aparnik.contrib.reviews'
    verbose_name = _('reviews')

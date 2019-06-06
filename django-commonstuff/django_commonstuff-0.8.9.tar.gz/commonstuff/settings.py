# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf import settings


MINIFY_CSS = bool(getattr(settings, 'DJANGO_COMMONSTUFF_MINIFY_CSS', True))
MINIFY_JS = bool(getattr(settings, 'DJANGO_COMMONSTUFF_MINIFY_JS', True))

CKEDITOR_MODELS = getattr(settings, 'DJANGO_COMMONSTUFF_CKEDITOR_MODELS', [])
CKEDITOR_MAX_IMAGE_SIZE = int(getattr(settings, 'DJANGO_COMMONSTUFF_CKEDITOR_MAX_IMAGE_SIZE', 512))  # kb
CKEDITOR_MAX_IMAGE_W = int(getattr(settings, 'DJANGO_COMMONSTUFF_CKEDITOR_MAX_IMAGE_W', 1000))  # px
CKEDITOR_MAX_IMAGE_H = int(getattr(settings, 'DJANGO_COMMONSTUFF_CKEDITOR_MAX_IMAGE_H', 1000))  # px


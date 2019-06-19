"""
Django settings for django_vox tests
"""
# based of django-debug-toolbar
# https://github.com/jazzband/django-debug-toolbar/blob/master/tests/settings.py
import os
from .settings import SECRET_KEY, TEMPLATES, MIDDLEWARE  # noqa: F401

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_vox",
]

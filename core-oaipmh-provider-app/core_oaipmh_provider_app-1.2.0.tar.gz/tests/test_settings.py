import os
from os.path import dirname, realpath, join

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',

    # Extra apps
    "password_policies",

    # Local apps
    "tests",
]

OAI_PROVIDER_ROOT = dirname(realpath(__file__))

ALLOWED_HOSTS = ['testserver']

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        join(
            dirname(dirname(os.path.realpath(__file__))),
            'core_oaipmh_provider_app',
            'templates'
        )
    ],
    'OPTIONS': {
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
        ]
    }
}]

ROOT_URLCONF = 'core_oaipmh_provider_app.urls'

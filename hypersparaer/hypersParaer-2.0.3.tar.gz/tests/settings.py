# encoding: utf-8

from django.conf.urls import url
from django.http import HttpResponse
from django.urls import path

DEBUG = True
_name = 'test.sqlite3'
DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': _name,
            'TEST': {'NAME': _name}
        }
}
SECRET_KEY = "4l0ngs3cr3tstr1ngw3lln0ts0l0ngw41tn0w1tsl0ng3n0ugh"
ROOT_URLCONF = __name__
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    "rest_framework",
    "rest_framework_swagger",
]
STATIC_URL = "/static/"
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": True,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]


def get_url_patterns():
    from paraer.para import para_ok_or_400
    from paraer.vendor import APIView
    from rest_framework.response import Response
    from rest_framework_swagger.views import get_swagger_view

    class HomeView(APIView):
        permission_classes = []

        @para_ok_or_400(
            [
                {"name": "name", "required": True},
                {"name": "tags", "type": "array"},
                {"name": "type", "description": {'a': 'A', 'b': 'B', 'c': 'C'}},
                {"name": "identify", "type": "integer", 'method': lambda x: isinstance(x, int)},
            ]
        )
        def get(self, request, **kwargs):
            """
            test
            """
            return Response(dict(data=kwargs))

        post = get

    urlpatterns = [
        path("home", HomeView.as_view()),
        path("", get_swagger_view(title="test1 API Doc")),
    ]
    return urlpatterns


urlpatterns = get_url_patterns()

import os
import random
import logging

from django.conf import settings
from json_dict import JsonDict

preamble = ""
#if manage.py is called directly
if len(__name__.split(".")) == 2:
    from manage import logger,CONFIG
else:
    from ..manage import logger,CONFIG
    preamble = __name__.replace(".controll_server.settings",".")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if CONFIG is None:
    CONFIG = JsonDict(os.path.join(BASE_DIR, "serverconfig.json"))


SECRET_KEY = CONFIG.get(
    "django_settings",
    "security",
    "key",
    default="".join(
        random.SystemRandom().choice(
            "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        )
        for i in range(50)
    ),
)

DEBUG = CONFIG.get("django_settings", "debug", default=False)

ALLOWED_HOSTS = CONFIG.get("django_settings", "security", "allowed_hosts", default=[])


LANGUAGE_CODE = CONFIG.get("public", "language_time", "language_code", default="en-us")

TIME_ZONE = CONFIG.get("public", "language_time", "time_zone", default="UTC")

USE_I18N = CONFIG.get("django_settings", "language_time", "use_I18N", default=True)

USE_L10N = CONFIG.get("django_settings", "language_time", "use_L10N", default=True)

USE_TZ = CONFIG.get("django_settings", "language_time", "use_TZ", default=True)

STATIC_URL = CONFIG.get("django_settings", "static_files", "url", default="/static/")


INSTALLED_APPS = []

# APP_DIR=os.path.join(BASE_DIR, 'django_apps')
# if CONFIG.get("django_settings","apps","load_local",default=True):
#    for dir in [f for f in os.listdir(APP_DIR) if os.path.isdir(os.path.join(APP_DIR, f))]:
#        INSTALLED_APPS.append(os.path.basename(APP_DIR)+"."+dir)


if CONFIG.get("django_settings", "apps", "load_defaults", default=True):
    INSTALLED_APPS += [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        'bootstrap4',
    ]

INSTALLED_APPS += CONFIG.get("django_settings", "apps", "additional", default=[])

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), "/var/www/static/"] + CONFIG.get(
    "django_settings", "static_files", "dirs", default=[]
)


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "global_login_required.GlobalLoginRequiredMiddleware",
]

PUBLIC_PATHS = [r"^/accounts/.*"]  # allow public access to all django-allauth views
ROOT_URLCONF = preamble + "controll_server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                preamble + "templatetags.installed_apps.get_apps_context",
            ],
            "libraries": {"public_dict": preamble + "templatetags.public_dict"},
        },
    }
]

WSGI_APPLICATION = preamble + "controll_server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":  CONFIG.get(
            "django_settings",
            "database",
            "name",
            default=os.path.abspath(os.path.join(os.path.dirname(CONFIG.file), "db.sqlite3")),
        )
    }
}
logger.debug("use db:"+str(DATABASES['default']))


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

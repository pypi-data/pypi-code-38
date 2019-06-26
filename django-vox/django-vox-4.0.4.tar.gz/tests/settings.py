"""
Django settings for django_vox tests
"""
# based of django-debug-toolbar
# https://github.com/jazzband/django-debug-toolbar/blob/master/tests/settings.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production

SECRET_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

SITE_DOMAIN = "127.0.0.1:8000"
INTERNAL_IPS = ALLOWED_HOSTS = ["127.0.0.1"]
SITE_SSL = False

LOGGING_CONFIG = None  # avoids spurious output in tests
DEBUG = True

# Application definition

BASE_INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_vox",
]

INSTALLED_APPS = BASE_INSTALLED_APPS + ["background_task", "tests"]


FIXTURE_DIRS = ["fixtures"]

MEDIA_URL = "/media/"  # Avoids https://code.djangoproject.com/ticket/21451

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_vox.middleware.activity_inbox_middleware",
]

ROOT_URLCONF = "tests.root_urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

STATIC_ROOT = os.path.join(BASE_DIR, "tests", "static")

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "tests", "additional_static"),
    ("prefix", os.path.join(BASE_DIR, "tests", "additional_static")),
]

# Cache and database

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "second": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

DJANGO_VOX_BACKENDS = [
    # we can specify class or module
    "django_vox.backends.activity.Backend",
    "django_vox.backends.html_email",
    "django_vox.backends.markdown_email",
    "django_vox.backends.postmark_email",
    "django_vox.backends.template_email",
    "django_vox.backends.twilio",
    # "django_vox.backends.twitter",
    # "django_vox.backends.slack",
    "django_vox.backends.json_webhook",
    # "django_vox.backends.xmpp",
]
DJANGO_VOX_VIEW_INBOX = False
DEFAULT_FROM_EMAIL = "admin@example.test"

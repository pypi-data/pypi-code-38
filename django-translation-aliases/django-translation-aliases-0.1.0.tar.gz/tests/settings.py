import os

SECRET_KEY = "roverdotcom"
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin.apps.SimpleAdminConfig",
    "django.contrib.staticfiles",
    "django_translation_aliases",
]
ROOT_URLCONF = []

MIGRATION_MODULES = {
    # This lets us skip creating migrations for the test models as many of
    # them depend on one of the following contrib applications.
    "auth": None,
    "contenttypes": None,
    "sessions": None,
}


DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

RUNTESTS_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(RUNTESTS_DIR, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

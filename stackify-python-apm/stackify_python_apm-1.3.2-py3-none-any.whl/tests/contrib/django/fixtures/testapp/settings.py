import django

settings = dict(
    BASE_DIR="tests.contrib.django.fixtures.testapp",
    CONFIG_FILE="stackify.json",
    SECRET_KEY="some_secret",
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "test",
            "TEST_NAME": "test",
            "TEST": {"NAME": "test"},
        }
    },
    TEST_DATABASE_NAME="test",
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.admin",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.redirects",
        "django.contrib.contenttypes",
        "stackifyapm.contrib.django",

        "tests.contrib.django.fixtures.testapp",
    ],
    ROOT_URLCONF="tests.contrib.django.fixtures.testapp.urls",
    DEBUG=True,
    SITE_ID=1,
    BROKER_HOST="localhost",
    BROKER_PORT=5672,
    BROKER_USER="user",
    BROKER_PASSWORD="password",
    BROKER_VHOST="/",
    CELERY_ALWAYS_EAGER=True,
    TEMPLATE_DEBUG=False,
    TEMPLATE_DIRS=["tests.contrib.django.fixtures.testapp.templates"],
    ALLOWED_HOSTS=["*"],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["tests.contrib.django.fixtures.testapp.templates"],
            "OPTIONS": {
                "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "stackifyapm.contrib.django.context_processors.rum_tracing"
                ],
                "loaders": ["django.template.loaders.filesystem.Loader"],
                "debug": False,
            },
        }
    ],
    ENVIRONMENT="test",
)

middleware_list = [
    "stackifyapm.contrib.django.middleware.TracingMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

if django.VERSION < (1, 10):
    settings.update({"MIDDLEWARE_CLASSES": middleware_list})
else:
    settings.update({"MIDDLEWARE": middleware_list, "MIDDLEWARE_CLASSES": None})

TEST_SETTINGS = settings

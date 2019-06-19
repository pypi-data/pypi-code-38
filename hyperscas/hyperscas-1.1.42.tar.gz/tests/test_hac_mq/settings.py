SECRET_KEY = 'foobar'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": 'test.db',
        "TEST": {"NAME": 'test.db'},
    }
}

INSTALLED_APPS = (
                     'django.contrib.contenttypes',
                     'django.contrib.auth',
                     # 'cas',
                     'test_hac_mq',
                 )

AUTH_USER_MODEL = 'test_hac_mq.User'

USER_GROUP_MODEL = 'test_hac_mq.UserGroup'

RABBITMQ = 'localhost'
HAC_LISTEN_MQ = ''
HAC_PUBLISH_MQ = ''
SERVICE = ''
DOMAIN = ''
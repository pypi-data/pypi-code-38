# -*- coding: utf-8 -*-

"""
Django settings for bigtree project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.utils.encoding import smart_unicode, DEFAULT_LOCALE_ENCODING

BASE_DIR = smart_unicode(
    os.path.dirname(os.path.dirname(__file__)), DEFAULT_LOCALE_ENCODING)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7&cu(g#x8s$@*b^b7pah+23jdwbrll_4x7l%3nfcic+a9!sqtu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'bigtiger.contrib.conf',
    'bigtiger.contrib.log',
    'bigtiger.contrib.admin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sqlalchemy_django.middleware.SqlAlchemyMiddleware',
)

ROOT_URLCONF = 'bigtiger_test.urls'

WSGI_APPLICATION = 'bigtiger_test.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SQLALCHEMY_DATABASES = {
    'auth': {
        'SQLALCHEMY_DATABASE_URI': 'postgresql+psycopg2://postgres:linkeddt.c0m@106.13.40.217:9501/bigtree',
        'SQLALCHEMY_NATIVE_UNICODE': None,
        'SQLALCHEMY_ECHO': False,
        'SQLALCHEMY_RECORD_QUERIES': None,
        'SQLALCHEMY_POOL_SIZE': 20,
        'SQLALCHEMY_POOL_TIMEOUT': None,
        'SQLALCHEMY_POOL_RECYCLE': None,
        'SQLALCHEMY_MAX_OVERFLOW': None,
        'SQLALCHEMY_COMMIT_ON_TEARDOWN': True
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'cn-zh'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'bower_components')

BIGTIGER_ROOT = os.path.join(BASE_DIR, 'bigtiger')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "bigtiger/contrib/admin/static"),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "bigtiger/contrib/admin/templates"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

############
# SESSIONS #
############

# Cookie name. This can be whatever you want.
SESSION_COOKIE_NAME = 'sessionid'
# Age of cookie, in seconds (default: 2 weeks).
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2
# A string like ".lawrence.com", or None for standard domain cookie.
SESSION_COOKIE_DOMAIN = None
# Whether the session cookie should be secure (https:// only).
SESSION_COOKIE_SECURE = False
# The path of the session cookie.
SESSION_COOKIE_PATH = '/'
# Whether to use the non-RFC standard httpOnly flag (IE, FF3+, others)
SESSION_COOKIE_HTTPONLY = True
# Whether to save the session data on every request.
SESSION_SAVE_EVERY_REQUEST = False
# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# The module to store session data
SESSION_ENGINE = 'django_sae.session.backends.db'
SESSION_FILE_PATH = None

PERMISSIONS_SESSION_KEY = '_auth_user_permissions'

##################
# AUTHENTICATION #
##################

AUTHENTICATION_BACKENDS = ('django_sae.auth.backends.ModelBackend',)
AUTHENTICATION_MODE = 'remote'

LOGIN_URL = '/admin/'

LOGOUT_URL = '/admin/logout/'

LOGIN_REDIRECT_URL = '/admin/main/'

# The number of days a password reset link is valid for
PASSWORD_RESET_TIMEOUT_DAYS = 3

# the first hasher in this list is the preferred algorithm.  any
# password using different algorithms will be converted automatically
# upon login
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

BIGTREE_API_ACCESS_TOKEN_SECRET = 'linkeddt.com'
BIGTREE_API_BASE_URI = 'http://127.0.0.1:8000/admin/api/'
USER_LOG_BACKEND = 'bigtree_log.backends.ModelBackend'
SYS_CONFIG_BACKEND = 'bigtree_config.backends.ModelBackend'

#######################
# SESSION AUTH ENGINE #
#######################
SAE_SESSION_SERVICE_URL = 'http://127.0.0.1:8000/admin/sae/session/'
SAE_AUTHENTICATE_SERVICE_URL = 'http://127.0.0.1:8000/admin/sae/user/'
SAE_ACCESS_TOKEN_SECRET = 'linkeddt.com'


SYS_CONFIG = {
    'company': '成都领数云科技有限公司',
    'version': '0.1',
}

BAIDU_WEATHER_AK = 'HXUVN5E30f33NoHGvdtqjtbM'
BAIDU_WEATHER_LOCATION = '成都市'

PAGESIZE = 50
EXPORT_PAGESIZE = 1000
XLS_TEMPLATE = os.path.join(BASE_DIR, 'xlstemplate')

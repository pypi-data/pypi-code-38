'''
Django settings for Trosnoth server.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
'''

from configparser import ConfigParser
import logging
import os
import socket

from django.core.management.utils import get_random_secret_key
from trosnoth import data


log = logging.getLogger(__name__)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data.makeDirs(data.getPath(data.user, 'authserver'))
CONFIG_PATH = data.getPath(data.user, 'authserver', 'config')
config = ConfigParser(interpolation=None)
config.add_section('security')
config.add_section('web')
config.read(CONFIG_PATH)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('security', 'key', fallback=None)
if not SECRET_KEY:
    SECRET_KEY = get_random_secret_key().replace('%', '-')
    config.set('security', 'key', SECRET_KEY)
    with open(CONFIG_PATH, 'w') as f:
        config.write(f)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.getboolean('security', 'debug', fallback=False)
if DEBUG:
    os.environ['PYTHONASYNCIODEBUG'] = '1'


def build_allowed_hosts():
    result = {'localhost', '[::1]'}
    result.update(socket.gethostbyname_ex(socket.gethostname())[2])
    result.update(socket.gethostbyname_ex('localhost')[2])
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(('10.1.1.1', 1))
        except OSError:
            log.warning('Could not get server IP address')
        else:
            result.add(s.getsockname()[0])
    extra = config.get('web', 'hosts', fallback=None)
    if extra:
        result.update(extra.split(','))
    return list(result)


ALLOWED_HOSTS = build_allowed_hosts()

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'trosnoth.djangoapp.apps.TrosnothConfig',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'trosnoth.server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]


WSGI_APPLICATION = 'trosnoth.server.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': data.getPath(data.user, 'authserver', 'db.sqlite3'),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-au'

USE_I18N = True

USE_L10N = True

USE_TZ = False

TIME_ZONE = 'UTC'


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    data.getPath(data.user, 'authserver', 'public'),
]

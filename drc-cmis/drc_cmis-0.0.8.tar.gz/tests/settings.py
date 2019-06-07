import os

PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = PROJECT_DIR  # setting present in new startproject

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SITE_ID = 1

IS_HTTPS = False

INSTALLED_APPS = [
    'drc_cmis',
    'tests.app',
    'vng_api_common',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_DIR = 'reports'
TEST_OUTPUT_FILE_NAME = 'junit.xml'

ROOT_URLCONF = 'tests.urls'

DEBUG = True
SECRET_KEY = 'this-is-really-not-a-secret'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

STATIC_URL = '/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'database.db'),
    }
}


STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

#
# CMIS SETTINGS
#
DRC_CMIS_CLIENT_URL = 'http://localhost:8082/alfresco/cmisatom'
DRC_CMIS_CLIENT_USER = 'admin'
DRC_CMIS_CLIENT_USER_PASSWORD = 'admin'
ENKELVOUDIGINFORMATIEOBJECT_MODEL = 'app.EnkelvoudigInformatieObject'
ABSTRACT_BASE_CLASS = 'tests.app.utils.BaseDRCStorageBackend'
TEMP_DOCUMENT_CLASS = 'tests.app.utils.TempDocument'
HOST_URL = 'testserver'
ABSTRACT_BASE_CLASS = 'tests.app.backend.AbstractStorageBackend'
BASE_FOLDER_LOCATION = 'TEST_DRC'

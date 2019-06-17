
from steelscript.appfwk.project.settings import *

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATAHOME = os.getenv('DATAHOME', PROJECT_ROOT)
PCAP_STORE = os.path.join(DATAHOME, 'data', 'pcap')
DATA_CACHE = os.path.join(DATAHOME, 'data', 'datacache')
INITIAL_DATA = os.path.join(DATAHOME, 'data', 'initial_data')
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')
LOG_DIR = os.path.join(DATAHOME, 'logs')

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
MEDIA_ROOT = DATA_CACHE

# Task model specific configs
APPFWK_TASK_MODEL = 'async'
#APPFWK_TASK_MODEL = 'celery'

if APPFWK_TASK_MODEL == 'celery':
    LOCAL_APPS = (
        'djcelery',
    )
    INSTALLED_APPS += LOCAL_APPS

    # redis for broker and backend
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_ACKS_LATE = True

    import djcelery
    djcelery.setup_loader()

    #CELERY_ALWAYS_EAGER = True
    TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

# Optionally add additional applications specific to this project instance
LOCAL_APPS = (
    # additional apps can be listed here
)
INSTALLED_APPS += LOCAL_APPS

# Optionally enable Guest read-only access to reports
GUEST_USER_ENABLED = False
GUEST_USER_TIME_ZONE = 'US/Eastern'

if GUEST_USER_ENABLED:
    # adjust authentication parameters
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ['rest_framework.permissions.AllowAny']
    REST_FRAMEWORK.pop('EXCEPTION_HANDLER')

# Configure database for development or production.

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',

        # Path to database file if using sqlite3.
        # Database name for others
        'NAME': os.path.join(DATAHOME, 'data', 'project.db'),

        # USER, PASSWORD, HOST and PORT are not used by sqlite3.
        'USER': '',
        'PASSWORD': '',
        'HOST': '',  # Set to empty string for localhost.
        'PORT': '',  # Set to empty string for default.
    }
}

# Setup loggers to local directory
LOGGING['handlers']['logfile']['filename'] = os.path.join(LOG_DIR, 'log.txt')
LOGGING['handlers']['backend-log']['filename'] = os.path.join(LOG_DIR,
                                                              'log-db.txt')

# Optionally add additional global error handlers

LOCAL_ERROR_HANDLERS = (
    # additional global error handlers can be listed here
)
GLOBAL_ERROR_HANDLERS += LOCAL_ERROR_HANDLERS

# Overwrite overall size limit of all Netshark Pcap downloaded files in Bytes
# PCAP_SIZE_LIMIT = 10000000000

# To enable syslog handling instead of local logging, see the next blocks of
# LOGGING statements.  Note the different section for Linux/Mac vs Windows.

# remove these loggers since the configuration will attempt to write the
# files even if they don't have a logger declared for them
#LOGGING['disable_existing_loggers'] = True
#LOGGING['handlers'].pop('logfile')
#LOGGING['handlers'].pop('backend-log')
#
# Use the following handler for Linux/BSD/Mac machines
#LOGGING['handlers']['syslog'] = {
#    'level': 'DEBUG',
#    'class': 'logging.handlers.SysLogHandler',
#    'formatter': 'standard_syslog',
#    'facility': SysLogHandler.LOG_USER,
#    'address': '/var/run/syslog' if sys.platform == 'darwin' else '/dev/log'
#}
#
# Use the following handler for sending to Windows Event logs,
# you will need an additional package for Windows: Python for Windows
# Extensions, which can be found here:
#    http://sourceforge.net/projects/pywin32/files/pywin32/
#LOGGING['handlers']['syslog'] = {
#    'level': 'DEBUG',
#    'class': 'logging.handlers.NTEventLogHandler',
#    'formatter': 'standard_syslog',
#    'appname': 'steelscript',
#}
#
#LOGGING['loggers'] = {
#    'django.db.backends': {
#        'handlers': ['null'],
#        'level': 'DEBUG',
#        'propagate': False,
#    },
#    '': {
#        'handlers': ['syslog'],
#        'level': 'INFO',
#        'propagate': True,
#    },
#}

#OFFLINE_JS = True
#STATICFILES_DIRS += (os.path.join(PROJECT_ROOT, 'offline'), )
SECRET_KEY = '@+^^movly@4_rl-d*&0996q749x9d^ahabhjg(4cw3m7fghjuq'

# Add other settings customizations below, which will be local to this
# machine only, and not recorded by git. This could include database or
# other authentications, LDAP settings, or any other overrides.

# For example LDAP configurations, see the file
# `project/ldap_example.py`.

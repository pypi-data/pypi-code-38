# Django settings for votebase core.
import os
from django.core.urlresolvers import reverse_lazy

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
PREPEND_WWW = True

AUTH_PROFILE_MODULE = 'accounts.Profile'
MAX_USERNAME_LENGTH = 70

LOGIN_URL = reverse_lazy('accounts_login')
REQUIRED_ACTIVATION = False

ADMINS = (
)
MANAGERS = ADMINS

# Facebook
FACEBOOK_APP_ID = '172886466168460'
FACEBOOK_APP_SECRET = '27cdfba10ad0cf80bfceb65fd57f2881'
FACEBOOK_LOGIN_DEFAULT_REDIRECT = reverse_lazy('surveys_index')
FACEBOOK_HIDE_CONNECT_TEST = True

# Google API
GOOGLE_API_KEY = 'TODO'

# GeoIP
import votebase
VOTEBASE_PATH = os.path.dirname(votebase.__file__)
GEOIP_PATH = VOTEBASE_PATH + '/core/voting/geoip/'

# Rosetta
ROSETTA_MESSAGES_PER_PAGE = 10

# DEBUG TOOLBAR CONFIG
INTERNAL_IPS = ('127.0.0.1', )

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


########## EMAIL CONFIGURATION
DEFAULT_EMAIL_FROM = 'TODO'
DEFAULT_EMAIL_FROM_NAME = 'TODO'
EMAIL_HOST = 'TODO'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'TODO'
EMAIL_HOST_PASSWORD = 'TODO'
EMAIL_USE_TLS = True
########## END EMAIL CONFIGURATION


# Packages settings
#from votebase.core.accounts.models import Profile
VOTEBASE_SUBSCRIPTION_PERIOD_IN_DAYS = 31
VOTEBASE_PACKAGES_SETTINGS = {
    'BASIC': {
        'monthly_fee': 0, #EUR per month
        'voters_limit': 100000, #per survey
    },
    'STANDARD': {
        'monthly_fee': 9.90, #EUR per month
        'voters_limit': 1000, #per survey
    },
    'PREMIUM': {
        'monthly_fee': 49.90, #EUR per month
        'voters_limit': 100000, #per survey
    }
}


# Make this unique, and don't share it with anybody.
SECRET_KEY = '4*=tr6jh!fup&amp;jk%g_c#18c*@@2!ag4=cpg=4e2xpw6n=ha(sb'


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'breadcrumbs.middleware.BreadcrumbsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'votebase.core.voting.middleware.VotingFallbackMiddleware',
)

ROOT_URLCONF = 'TODO'

VOTEBASE_APPS = [
    'votebase',
    'votebase.core.utils',
    'votebase.core.accounts',
    'votebase.core.surveys',
    'votebase.core.statistics',
    'votebase.core.questions',
    'votebase.core.voting',
]


VOTEBASE_TEMPLATE_CONTEXT_PROCESSORS = [
    'votebase.context_processors.host',
    'votebase.context_processors.protocol',
    'votebase.context_processors.urls',
    'votebase.context_processors.settings_constants',
]

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'votebase.wsgi.application'



########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
#        'django': {
#            'handlers': ['console'],
#            'level': 'DEBUG',
#            },
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s',
            },
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
}
########## END LOGGING CONFIGURATION




########## DATE CONFIGURATION
from django.conf.global_settings import DATE_INPUT_FORMATS
DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_JS = 'yyyy-mm-dd'
DATE_FORMAT_TAG = 'Y-m-d'
DATE_INPUT_FORMATS = DATE_INPUT_FORMATS + [DATE_FORMAT,]
########## END DATE CONFIGURATION

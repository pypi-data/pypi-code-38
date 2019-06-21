import os

APP_CONFIG_ROOT = os.environ.get('CF_APP_CONFIG_ROOT', os.path.expanduser(f'~/.compose'))
APP_ENVIRONMENTS_ROOT = os.path.join(APP_CONFIG_ROOT, 'environments')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'}},
    'loggers': {
        'compose_flow': {'handlers': ['console'], 'level': 'INFO', 'propagate': False}
    },
    'root': {'handlers': ['console'], 'level': 'WARNING', 'propagate': True},
}

USER = os.environ.get('USER', 'nobody')
DEFAULT_CF_REMOTE_USER = os.environ.get('CF_REMOTE_USER', USER)

DOCKER_IMAGE_PREFIX = os.environ.get('CF_DOCKER_IMAGE_PREFIX', 'localhost.localdomain')

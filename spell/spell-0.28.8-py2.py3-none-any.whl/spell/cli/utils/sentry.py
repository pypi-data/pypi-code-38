import os
import traceback

import sentry_sdk
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from spell import version


SENTRY_URL = "https://9a9530b86ed74e11a28e7f410f31bab7@sentry.io/1285204"
ENVIRONMENT_SUPPRESS_VALUE = "SPELL_QUIET"


_inited = False
_tags = {}
_user = None


def _init_sentry():
    global _inited
    if _inited:
        return

    def noop(*args, **kwargs):
        pass
    atexit_override = AtexitIntegration(noop)

    class NoopExcepthookIntegration(ExcepthookIntegration):
        def install(self, *args, **kwargs):
            pass
    excepthook_override = NoopExcepthookIntegration()

    class NoopLoggingIntegration(LoggingIntegration):
        def install(self, *args, **kwargs):
            pass
    logging_override = NoopLoggingIntegration()

    sentry_sdk.init(
        SENTRY_URL,
        release=version.__version__,
        integrations=[
            logging_override,
            excepthook_override,
            atexit_override
        ],
    )

    _inited = True


def _configure_scope():
    if not _inited:
        return

    with sentry_sdk.configure_scope() as scope:
        scope.clear()
        scope.user = _user
        for k, v in _tags.items():
            scope.set_tag(k, v)


def set_user(user):
    global _user
    _user = user


def set_tag(key, value):
    global _tags
    _tags[key] = value


def capture_exception(error):
    if ENVIRONMENT_SUPPRESS_VALUE not in os.environ:
        _init_sentry()
        _configure_scope()
        sentry_sdk.capture_exception(error)
    else:
        traceback.print_exc()


def capture_message(message, level=None):
    if ENVIRONMENT_SUPPRESS_VALUE not in os.environ:
        _init_sentry()
        _configure_scope()
        sentry_sdk.capture_message(message, level)
    else:
        traceback.print_exc()

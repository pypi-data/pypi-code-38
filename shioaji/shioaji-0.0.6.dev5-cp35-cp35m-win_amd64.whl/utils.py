import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import SentryHandler

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
SENTRY_URI = os.environ.get(
    'SENTRY_URI', "https://6aec6ef8db7148aa979a17453c0e44dd@sentry.io/1371618")
LOG_SENTRY = os.environ.get('LOG_SENTRY', '')

allow_log_level = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
assert LOG_LEVEL in allow_log_level, "LOG_LEVEL not allow, choice {}".format(
    (', ').join(allow_log_level))
LOGGING_LEVEL = getattr(logging, LOG_LEVEL)

log = logging.getLogger('shioaji')
log.setLevel(LOGGING_LEVEL)

console_handler = logging.FileHandler("shioaji.log")
console_handler.setLevel(LOGGING_LEVEL)
log_formatter = logging.Formatter(
    '[%(levelname)1.1s %(asctime)s %(pathname)s:%(lineno)d:%(funcName)s] %(message)s'
)
console_handler.setFormatter(log_formatter)

if LOG_SENTRY:
    sentry_sdk.init(SENTRY_URI)
    sentry_handeler = SentryHandler()
    sentry_handeler.setLevel(LOGGING_LEVEL)
    sentry_handeler.setFormatter(log_formatter)
    log.addHandler(sentry_handeler)

log.addHandler(console_handler)

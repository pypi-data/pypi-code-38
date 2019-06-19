import logging
import os

from .app import cli
import sentry_sdk

sentry_sdk.init("https://f695d7ce05f143b393d6dfc84d1b723f@sentry.io/1335287")
log_level = logging.INFO
log_format = '%(asctime)s %(levelname)-8s: %(message)s'
if os.environ.get('DEBUG', False):
    log_level = logging.DEBUG
    log_format = '%(asctime)s %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d]: %(message)s'
logging.basicConfig(level=log_level, format=log_format, datefmt='%m-%d %H:%M:%S', )
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s [%(name)s]: %(message)s', datefmt='%m-%d %H:%M:%S', )

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger = logging.getLogger('docker')
logger.setLevel(logging.INFO)
logger = logging.getLogger('urllib3')
logger.setLevel(logging.INFO)
logger = logging.getLogger('controllers.transport.backbone')
logger.setLevel(logging.INFO)
logger = logging.getLogger('api.api_commands')
logger.setLevel(logging.INFO)
logger = logging.getLogger('app.config_builder')
logger.setLevel(logging.INFO)


def main():
    cli()


if __name__ == "__main__":
    main()

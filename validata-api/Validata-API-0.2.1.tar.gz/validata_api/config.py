import logging
import os
from distutils.util import strtobool

import requests
import toml
from dotenv import load_dotenv

log = logging.getLogger(__name__)


def guess_bool(v):
    return strtobool(v) if isinstance(v, str) else bool(v)


load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY") or None


SCRIPT_NAME = os.environ.get("SCRIPT_NAME") or ""


DEBUG_PYTHON_HTTP_CLIENT = guess_bool(os.environ.get("DEBUG_PYTHON_HTTP_CLIENT"))

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)

BADGE_CONFIG_URL = os.environ.get("BADGE_CONFIG_URL") or None
BADGE_CONFIG = None
if BADGE_CONFIG_URL is None:
    log.warning("BADGE_CONFIG_URL environment variable is not set, disable badge feature")
else:
    response = requests.get(BADGE_CONFIG_URL)
    if not response.ok:
        log.warning("Can't retrieve badge config from [%s], disable badge feature", BADGE_CONFIG_URL)
    else:
        BADGE_CONFIG = toml.loads(response.text)

MATOMO_AUTH_TOKEN = os.getenv("MATOMO_AUTH_TOKEN") or None
MATOMO_BASE_URL = os.getenv("MATOMO_BASE_URL") or None
MATOMO_SITE_ID = os.getenv("MATOMO_SITE_ID") or None
if MATOMO_SITE_ID:
    MATOMO_SITE_ID = int(MATOMO_SITE_ID)

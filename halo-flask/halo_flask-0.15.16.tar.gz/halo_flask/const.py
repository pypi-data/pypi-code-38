from __future__ import print_function

import logging
from enum import Enum

logger = logging.getLogger(__name__)


LOC = 'loc'
DEV = 'dev'
TST = 'tst'
PRD = 'prd'

class HTTPChoice(Enum):  # A subclass of Enum
    get = "GET"
    post = "POST"
    put = "PUT"
    delete = "DELETE"
    patch = "PATCH"



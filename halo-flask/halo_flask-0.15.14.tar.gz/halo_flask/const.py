from __future__ import print_function

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class HTTPChoice(Enum):  # A subclass of Enum
    get = "GET"
    post = "POST"
    put = "PUT"
    delete = "DELETE"
    patch = "PATCH"



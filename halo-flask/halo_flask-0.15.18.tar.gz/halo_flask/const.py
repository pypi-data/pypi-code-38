from __future__ import print_function

from enum import Enum


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



from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import os
import random
import string
import uuid

from .klass_str import Str


class Random(object):

    @classmethod
    def uuid(cls):
        return Str(uuid.uuid1()).to_str()

    @classmethod
    def base64(cls, length=24):
        return base64.b64encode(os.urandom(length))

    @classmethod
    def alphanum(cls, length=24):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    @classmethod
    def digits(cls, length=24):
        return ''.join(random.choice(string.digits) for _ in range(length))

    @classmethod
    def alpha(cls, length=24):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

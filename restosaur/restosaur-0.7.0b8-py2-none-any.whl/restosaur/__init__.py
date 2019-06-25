"""
Restosaur - a tiny but real REST library

Author: Marcin Nowak <marcin.j.nowak@gmail.com>
"""

from __future__ import absolute_import

from . import resource  # NOQA
from . import responses  # NOQA

from .api import API  # NOQA


default_app_config = 'restosaur.apps.RestosaurAppConfig'

# -*- coding: utf-8 -*-

#  Copyright 2017-2018 Luiz Augusto Alves Ferraz
#  .
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  .
#      http://www.apache.org/licenses/LICENSE-2.0
#  .
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import os

from ._patch_resources import apply_patch
from .controllers.oauth2 import oauth2
from .controllers.service_account import service_acc

__ALL__ = [
    oauth2,
    service_acc,
]

logger = logging.getLogger(__name__)

if not os.environ.get("EASYGOOGLE_NO_AUTO_PATCH_RESOURCES"):
    apply_patch()


def set_default_cache(cache):
    from .controllers import base
    setattr(base, 'DEFAULT_CACHE', cache)

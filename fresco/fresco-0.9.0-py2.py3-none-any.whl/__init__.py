# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
from __future__ import absolute_import


__version__ = '0.9.0'

DEFAULT_CHARSET = 'UTF-8'

from .request import *  # noqa
from .requestcontext import context  # noqa
from .response import *  # noqa
from .core import *  # noqa
from .routing import *  # noqa
from .routeargs import *  # noqa
from .subrequests import *  # noqa

from .util.common import *  # noqa

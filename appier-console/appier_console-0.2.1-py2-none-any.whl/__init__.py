#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import base
from . import http
from . import util

from .base import COLOR_RESET, COLOR_WHITE, COLOR_BLACK, COLOR_BLUE, COLOR_LIGHT_BLUE, COLOR_GREEN,\
    COLOR_LIGHT_GREEN, COLOR_CYAN, COLOR_LIGHT_CYAN, COLOR_RED, COLOR_LIGHT_RED, COLOR_PURPLE,\
    COLOR_LIGHT_PURPLE, COLOR_BROWN, COLOR_YELLOW, COLOR_GRAY, COLOR_LIGHT_GRAY, CLEAR_LINE, COLORS,\
    LoaderThread, ctx_loader, colored
from .http import ctx_http_callbacks
from .util import is_tty, is_ansi, is_color

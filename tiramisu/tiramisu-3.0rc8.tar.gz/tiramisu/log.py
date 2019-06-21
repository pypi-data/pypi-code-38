# -*- coding: utf-8 -*-
"logger for tiramisu"
# Copyright (C) 2019 Team tiramisu (see AUTHORS for all contributors)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ____________________________________________________________
from logging import getLogger, DEBUG, basicConfig, StreamHandler, Formatter
import os


log = getLogger('tiramisu')
if os.environ.get('TIRAMISU_DEBUG') == 'True':
    log.setLevel(DEBUG)
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    log.addHandler(handler)

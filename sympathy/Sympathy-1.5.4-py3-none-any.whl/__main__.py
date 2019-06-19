# -*- coding:utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
try:
    sys.path.append(app_path)
    from Sympathy import launch
finally:
    sys.path.remove(app_path)


def sy():
    launch.run('sy')


def syg():
    launch.run('syg')


if __name__ == '__main__':
    launch.main()

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""tools to help manipulating files"""
import os.path


def get_unique_name(path):
    """generate a path with a name not conflicting with existing file

    @param path(unicode): path to the file to create
    @return (unicode): unique path (can be the same as path if there is not conflict)
    """
    ori_path = path
    idx = 1
    while os.path.exists(path):
        path = ori_path + u"_" + unicode(idx)
        idx += 1
    return path

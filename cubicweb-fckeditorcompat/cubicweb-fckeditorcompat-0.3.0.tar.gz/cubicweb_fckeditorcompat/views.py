# -*- coding: utf-8 -*-
# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-fckeditorcompat views/forms/actions/components for web ui"""

import os.path as osp

from cubicweb.web.views.staticcontrollers import FCKEditorController


class FCKEditorCompatController(FCKEditorController):
    """Controller in charge of serving FCKEditor related file

    The motivational for a dedicated controller have been lost.
    """

    __regid__ = 'fckeditor'

    def publish(self, rset=None):
        relpath = self.relpath
        dirpath = osp.dirname(__file__)
        relpath = relpath.split('?', 1)[0]
        filepath = osp.join(dirpath, 'data', relpath)
        return self.static_file(filepath)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.unregister(FCKEditorController)

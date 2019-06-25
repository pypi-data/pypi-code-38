# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-treeview smoke tests"""
from cubicweb.devtools.testlib import CubicWebTC
from mock import patch


class Treeview(CubicWebTC):
    def test_works(self):
        with self.admin_access.web_request() as req:
            note = req.create_entity('Note', content=u'Title')
            note.view("treeview")

    @patch("cubicweb_treeview.views.treeview.TVDefaultTreeViewItemView.cell_call")
    def test_overrides_DefaultTreeViewItemView(self, cell_call):
        with self.admin_access.web_request() as req:
            note = req.create_entity('Note', content=u'Title')
            note.view("treeview")
            self.assertTrue(cell_call.called)


if __name__ == '__main__':
    import unittest
    unittest.main()

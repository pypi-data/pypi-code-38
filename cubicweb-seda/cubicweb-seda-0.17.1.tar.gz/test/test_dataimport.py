# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-seda unit tests for dataimport"""

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_seda import dataimport


class ConcepSchemeImportTC(CubicWebTC):

    def test_import_seda_schemes(self):
        with self.admin_access.cnx() as cnx:
            dataimport.import_seda_schemes(cnx, lcsv_import=dataimport.lcsv_check)
            self.assertEqual(len(cnx.find('ConceptScheme')), 20)


if __name__ == '__main__':
    import unittest
    unittest.main()

# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017 Combine Control Systems AB
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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os
import unittest

from Gui.flowview import port_icon
from Gui.datatypes import DataType

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class TestPortIcons(unittest.TestCase):

    # TODO(erik): this test expects checks against hard-coded output
    # from svgutils 0.2 and svgutils 0.3; it may fail with other versions of
    # svgutils.

    def test_porticons(self):
        expected_results = []
        for svgutils_version in ['0.2', '0.3']:
            path = os.path.join(
                TEST_DIR, 'expected_porticon_svgutils_{}.svg'.format(
                    svgutils_version))
            with open(path) as f:
                expected_results.append(f.read().encode('ascii'))

        type_ = (                                                       # noqa
            '('                                                         # noqa
                'datasource,'                                           # noqa
                '['                                                     # noqa
                    '('                                                 # noqa
                        '['                                             # noqa
                            '(datasource, figure)], '                   # noqa
                            '('                                         # noqa
                                '(table, adaf -> text), '               # noqa
                                '('                                     # noqa
                                    '(table, adaf -> text), '           # noqa
                                    '('                                 # noqa
                                        '(report, unknown), '           # noqa
                                        '('                             # noqa
                                            '(report, unknown), '       # noqa
                                            '('                         # noqa
                                                '(), '                  # noqa
                                                'lambda'                # noqa
                                            ')'                         # noqa
                                        ')'                             # noqa
                                    ')'                                 # noqa
                                ')'                                     # noqa
                            ')'                                         # noqa
                        ')'                                             # noqa
                    ']'                                                 # noqa
            ')')                                                        # noqa
        icons = {
            'figure': 'ports/figure.svg',
            'text': 'ports/text.svg',
            'table': 'ports/table.svg',
            'datasource': 'ports/datasource.svg',
            'adaf': 'ports/adaf.svg',
            'report': 'ports/report.svg',
            'unknown': 'ports/unknown.svg',
            'lambda': 'ports/lambda.svg'}
        datatype = DataType.from_str(type_)
        svg = port_icon.icon(datatype._datatype, icons)
        assert svg in expected_results


if __name__ == '__main__':
    unittest.main()

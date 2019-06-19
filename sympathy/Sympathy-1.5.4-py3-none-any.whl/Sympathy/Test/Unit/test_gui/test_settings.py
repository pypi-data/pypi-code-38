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
import unittest
from Gui import settings
import tempfile
import os


class TestSettings(unittest.TestCase):

    def setUp(self):
        self._settings = settings.instance()
        fileno, self._filename = tempfile.mkstemp()
        os.close(fileno)
        self._settings.set_ini_file(self._filename)

    def tearDown(self):
        os.remove(self._filename)

    def _perform_test(self, test_vector):
        for key, value in test_vector.items():
            self._settings[key] = value
            retrieved = self._settings[key]
            self.assertEqual(value, retrieved)

    def test_temporary_storage(self):
        test_vector = {
            'my_string': 'string',
            'my_int': 42,
            'my_list': ['hej', 'hej2'],
            'my_short_list': ['hej'],
            'my_empty_list': []}

        self._perform_test(test_vector)

    def test_permanent_storage(self):
        test_vector = {
            'max_temp_folder_age': 5,
            'Gui/recent_flows': ['flow1.syx', 'flow2.syx'],
            'Python/library_path': [],
            'max_temp_folder_size': '2 G'}

        self._perform_test(test_vector)


if __name__ == '__main__':
    unittest.main()

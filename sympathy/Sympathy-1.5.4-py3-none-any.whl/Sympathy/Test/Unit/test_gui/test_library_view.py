# -*- coding:utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2013-2016 Combine Control Systems AB
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
import logging
import os
import sys
import PySide.QtGui as QtGui

import Gui
import launch


# Disabled due to cleanup issues.
@unittest.skip
class TestLibraryView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        environ = os.environ
        environ['PYTHONPATH'] = '{}{}{}'.format(
            environ.get('PYTHONPATH', ''),
            os.path.pathsep,
            environ[launch.SY_PYTHON_SUPPORT])

        cls.app = QtGui.QApplication.instance()
        if cls.app is None:
            cls.app = QtGui.QApplication(sys.argv)
        cls.app.setApplicationName(Gui.version.application_name())
        cls.app.setApplicationVersion(Gui.version.version)
        cls.main_window = QtGui.QMainWindow()

        cls.server = Gui.sy.run_server(1)
        environ['SY_TASK_MANAGER_PORT'] = str(cls.server.remote_server.port)
        cls.server.start()
        cls.app_core, cls.exe_core = Gui.application.common_setup(cls.app)

    @classmethod
    def tearDownClass(cls):
        Gui.application.common_teardown(cls.app_core)
        cls.server.stop()
        cls.server.join()

    def setUp(self):
        self.org_excepthook = sys.excepthook
        self.exceptions = []
        sys.excepthook = self._log_exception
        self.flow = self.app_core.create_flow()

    def tearDown(self):
        self.exceptions = []
        sys.excepthook = self.org_excepthook

    def _log_exception(self, exctype, value, traceback):
        self.exceptions.append((exctype, value, traceback))

    def _pump(self):
        logging.info('Processing events')
        self.app.processEvents()

    def test_library_view(self):
        """
        Test some combinations of:
            reloading library, changing filter and changing view type.

        No exception may occur.
        """
        library_model = Gui.library_view.TagLibraryModel(
            self.app_core.library_root(), self.main_window.style())

        library_view = Gui.library_view.LibraryView(parent=self.main_window)
        library_view.set_model(library_model)

        self.app_core.node_library_added.connect(
            library_model.update_model)

        self.app_core.reload_node_library()
        self._pump()

        for type_ in ['Tag', 'Disk', 'Tag', 'Disk']:

            library_model.set_type(type_)

            for reload_library in [False, False, True, False]:

                if reload_library:
                    self.app_core.reload_node_library()
                    self._pump()

                for c in ['table', 'Nothingatallmatches', 'a']:
                    library_view.update_filter(c)
                    self._pump()

        assert not self.exceptions, 'Exceptions occured'

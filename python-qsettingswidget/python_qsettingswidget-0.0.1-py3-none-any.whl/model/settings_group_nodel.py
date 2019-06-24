# python-qsettingswidget
# Copyright (C) 2019  LoveIsGrief
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout

from model.settings_node import SettingsNode


class SettingsGroupNode(SettingsNode):

    def __init__(self, name, widget=None, ui_string=None, parent=None):
        super().__init__(name, widget, parent)
        if self.widget is None:
            self.widget = QGroupBox(ui_string)
        if self.widget.layout() is None:
            self.widget.setLayout(QVBoxLayout())
        self.ui_string = ui_string

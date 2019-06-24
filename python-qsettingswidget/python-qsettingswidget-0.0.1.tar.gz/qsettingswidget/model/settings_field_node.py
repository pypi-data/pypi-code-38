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

from model.settings_node import SettingsNode


class SettingsFieldNode(SettingsNode):
    """
    :type widget: QWidget
    :type parent: model.settings_group_node.SettingsGroupNode
    """

    def __init__(self, name, widget, parent, default=None, ui_string=None):
        super().__init__(name, widget, parent)
        self.widget = widget
        self.parent = parent
        self.ui_string = ui_string
        self.default = default

    def __str__(self):
        return "SettingsFieldNode(%s) aka '%s'" % (
            self.widget, self.ui_string
        )

    @property
    def path_str(self):
        return "/".join([str(node.name) for node in self.path])

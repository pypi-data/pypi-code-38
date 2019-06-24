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

import logging
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget, QApplication, QTabWidget, QGridLayout, QDateEdit, QTimeEdit, QLineEdit, \
    QTextEdit, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from anytree import PreOrderIter, find, Resolver

from converters import get_converter
from converters.simple_converter import SimpleConverter
from model.settings_field_node import SettingsFieldNode
from model.settings_group_nodel import SettingsGroupNode


class QSettingsWidget(QWidget):
    """
    :type _current_group: QWidget
    """
    GROUP_DELIMITER = '/'

    def __init__(self, *args, **kwargs):
        settings_args = kwargs.pop(
            "settings_args",
            [kwargs.get("organization"), kwargs.get("application")]
        )

        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(self.__class__.__name__)

        self.settings = QSettings(*settings_args)

        self.converters = kwargs.get("converters", [SimpleConverter])

        self._layout = QGridLayout()
        self.setLayout(self._layout)

        self.tabs = QTabWidget(self)

        self._layout.addWidget(self.tabs)

        self._groups = SettingsGroupNode("", self.tabs)

        self._current_node = None

        self.begin_group("main", kwargs.get("main_ui_string", "Main"))
        self.end_group()

    # TODO: pass a settingsfield instead of the params to create one
    def add_field(self, name, widget, default=None, ui_string=None):
        current_node = self._current_node
        if current_node is None:
            current_node = find(self._groups, lambda n: n.name == "main")
        self._logger.debug("add_field %s to %s", name, current_node)
        SettingsFieldNode(
            name,
            widget,
            current_node,
            default,
            ui_string
        )

    def begin_group(self, name, ui_string=None):
        # No current group
        if self._current_node is None:
            self._begin_root_group(name, ui_string)

        # Subgroup
        else:
            self._begin_subgroup(name, ui_string)
        self._logger.info("Current node is now %s", self._current_node)

    def continue_group(self, name_or_path):
        """
        Allow to continue a group somewhere in the tree

        TODO: consider if this is necessary
        :param name_or_path: '/' delimited path to a group
        :type name_or_path: basestring
        """
        self._current_node = Resolver("name").get(self._groups, name_or_path)

    def _begin_root_group(self, name, ui_string):
        self._logger.info("_begin_root_group(%s,%s)", name, ui_string)
        group_widget = QWidget()
        setting_node = SettingsGroupNode(name, group_widget, ui_string, self._groups)
        self.tabs.addTab(setting_node.widget, ui_string)
        self._current_node = setting_node

    def _begin_subgroup(self, name, ui_string):
        self._logger.debug("Beginning subgroup: %s", name)
        settings_node = SettingsGroupNode(name, ui_string=ui_string, parent=self._current_node)
        self._current_node = settings_node

    def end_group(self):
        if not self._current_node:
            return

        self._current_node = self._current_node.parent

    def end_group_hierarchy(self):
        """
        Goes up the hierarchy ending groups
        """
        while self._current_node is not None:
            self.end_group()

    def read_settings(self):
        raise NotImplementedError()

    def save_settings(self):
        for node in PreOrderIter(self._groups, lambda n: isinstance(n, SettingsFieldNode)):
            converter = get_converter(self.converters, node.widget)
            self.settings.setValue(
                node.path_str,
                converter.get(node.widget)
            )
        self._logger.info("Saved settings to '%s'", self.settings.fileName())

    def load_settings(self):
        self._logger.info("Loading settings from '%s'", self.settings.fileName())
        for node in PreOrderIter(self._groups, lambda n: isinstance(n, SettingsFieldNode)):
            converter = get_converter(self.converters, node.widget)
            value = self.settings.value(node.path_str, node.default)
            try:
                converter.set(node.widget, value)
            except Exception as e:
                self._logger.debug(
                    "Couldn't set %s(%s): %s",
                    node.name, node.widget, e
                )

    def build_ui(self):
        """
        Creates the widgets and layouts to add them to the UI
        """
        self._logger.info("Building UI")
        for setting_node in self._groups.children:
            self._logger.debug("Adding tab for %s: %s", setting_node.name, setting_node.widget)
            self.tabs.addTab(
                setting_node.widget,
                setting_node.ui_string
            )
            self._show_children(setting_node)

    def _show_children(self, node):
        """

        :param node:
        :type node: SettingsGroupNode
        :return:
        :rtype:
        """
        self._logger.debug("_show_children(%s)", node)
        for child in node.children:
            if isinstance(child, SettingsGroupNode):
                node.widget.layout().addWidget(child.widget)
                self._show_children(child)
            elif isinstance(child, SettingsFieldNode):
                self._show_field(child)

    def _show_field(self, field):
        """

        :param field:
        :type field: SettingsFieldNode
        :return:
        :rtype:
        """
        self._logger.debug("_show_field %s of parent %s", field, field.parent)
        if field.ui_string:
            layout = QGridLayout()
            label = QLabel(field.ui_string)
            layout.addWidget(label)
            layout.addWidget(
                field.widget,
                0, 1, 0, -1
            )
        else:
            layout = QHBoxLayout()
            layout.addWidget(field.widget)
        # TODO: hook up events
        field.parent.widget.layout().addLayout(layout)


if __name__ == '__main__':
    from pathlib import Path
    from tempfile import gettempdir

    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)

    settings_widget = QSettingsWidget(settings_args=[
        str(Path(gettempdir(), "settings.ini")), QSettings.IniFormat
    ])

    settings_widget.continue_group("main")
    settings_widget.begin_group("appointment", "Appointment Details")

    settings_widget.add_field("date", QDateEdit(), ui_string="Date")
    settings_widget.add_field("time", QTimeEdit(), ui_string="Time")
    settings_widget.add_field("location", QLineEdit(), ui_string="Location")
    settings_widget.add_field("description", QTextEdit())

    settings_widget.end_group()

    settings_widget.load_settings()

    settings_widget.build_ui()

    main_widget = QWidget()
    main_widget.setLayout(QVBoxLayout())
    main_widget.layout().addWidget(settings_widget)
    button = QPushButton("Save")
    main_widget.layout().addWidget(button)

    button.clicked.connect(lambda: settings_widget.save_settings())

    main_widget.show()
    app.exec_()

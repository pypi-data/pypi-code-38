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
from collections import namedtuple
from operator import methodcaller

from PyQt5.QtWidgets import QDateTimeEdit, QTimeEdit, QTextEdit, QLineEdit, QDateEdit

from converters.converter import Converter

GetterSetter = namedtuple("GetterSetter", ["getter", "setter"])

logger = logging.getLogger("converters.SimpleConverter")


class SimpleConverter(Converter):
    CLASS_TO_GETTERSETTER = {
        QDateEdit: GetterSetter("date", "setDate"),
        QDateTimeEdit: GetterSetter("dateTime", "setDateTime"),
        QTimeEdit: GetterSetter("time", "setTime"),
        QTextEdit: GetterSetter("toPlainText", "setText"),
        QLineEdit: GetterSetter("text", "setText")
    }

    @classmethod
    def can_convert(cls, widget):
        for _class in cls.CLASS_TO_GETTERSETTER.keys():
            if isinstance(widget, _class):
                return True
        return False

    @classmethod
    def get(cls, widget):
        """

        :type widget: QDateEdit
        :return:
        :rtype:
        """
        return methodcaller(cls.CLASS_TO_GETTERSETTER[widget.__class__].getter)(widget)

    @classmethod
    def set(cls, widget, value):
        """
        :type value: QVariant
        :type widget: QDateEdit
        :return:
        :rtype:
        """
        methodcaller(cls.CLASS_TO_GETTERSETTER[widget.__class__].setter, value)(widget)

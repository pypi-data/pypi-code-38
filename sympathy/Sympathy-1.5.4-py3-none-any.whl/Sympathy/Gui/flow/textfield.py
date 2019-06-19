# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import PySide.QtCore as QtCore
import six
from .types import ElementInterface, Type
from .. import util
from sympathy.utils.prim import localuri


@six.python_2_unicode_compatible
class TextField(ElementInterface):
    text_changed = QtCore.Signal(six.text_type)
    color_changed = QtCore.Signal(six.text_type)
    order_changed = QtCore.Signal()

    def __init__(self, flow, uuid=None, parent=None):
        super(TextField, self).__init__(parent)
        self._flow = flow
        self._type = Type.TextField
        self._text = ''
        self.uuid = uuid
        self._color = 'Beige'
        self._order = 0.999  # New fields on top
        self._init()

    def _init(self):
        pass

    def add(self, flow=None):
        if flow is not None:
            self._flow = flow
        self._flow.add_text_field(self)

    def remove(self):
        self._flow.remove_text_field(self)

    def to_dict(self):
        return {
            'uuid': self._uuid,
            'full_uuid': self.full_uuid,
            'x': self.position.x(),
            'y': self.position.y(),
            'width': self.size.width(),
            'height': self.size.height(),
            'text': self.text(),
            'color': self._color}

    def text(self):
        """Returns the text in the text field."""
        return self._text

    def color(self):
        return self._color

    def order(self):
        return self._order

    @QtCore.Slot(six.text_type)
    def set_text(self, text):
        """Replace the text in the text field."""
        self._text = text
        self.text_changed.emit(self._text)
        self.name_changed.emit(self._text)
        self.order_changed.emit()

    @QtCore.Slot(six.text_type)
    def set_color(self, color):
        self._color = color
        self.color_changed.emit(self._color)

    @QtCore.Slot(float)
    def set_order(self, order):
        self._order = order
        self.order_changed.emit()

    @property
    def has_svg_icon(self):
        return True

    @property
    def icon(self):
        return localuri(util.icon_path('textfield.svg'))

    def __str__(self):
        return '{}:{}:0x{:x}'.format(
            self.type.name, self.text(), id(self))

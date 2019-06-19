# Copyright (c) 2016, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import numpy as np
import six
from matplotlib import colors as mpl_colors

from sylib.figure import colors
from sylib.icons import utils as icon_utils
from sylib.tree_model import widgets as tree_widgets
from sympathy.api import qt
from sympathy.platform import widget_library as sywidgets

QtCore = qt.QtCore
QtGui = qt.QtGui


class _SyColorEdit(tree_widgets.SyBaseTextEdit):
    def __init__(self, *args, **kwargs):
        super(_SyColorEdit, self).__init__(*args, **kwargs)

        icon = icon_utils.create_icon(icon_utils.SvgIcon.color)
        self.toolbutton = sywidgets.LineEditDropDownMenuButton(
            icon, parent=self)
        self.toolbutton.setPopupMode(QtGui.QToolButton.DelayedPopup)
        self.toolbutton.setToolTip('<p>Select a color.</p>')
        self.add_widget(self.toolbutton)
        self.drop_down_menu = QtGui.QMenu(parent=self)
        self.toolbutton.setMenu(self.drop_down_menu)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.toolbutton.clicked.connect(self._on_color_pick)
        self.textChanged.connect(self._eval_color)

        self.populate_drop_down_menu()
        self.drop_down_menu.triggered.connect(self.insert_action_text)

    def populate_drop_down_menu(self):
        color_names = sorted(colors.COLORS.keys())
        for name in color_names:
            color = colors.COLORS[name]
            icon = icon_utils.color_icon(color)
            self.drop_down_menu.addAction(icon, name)

    def focusOutEvent(self, event):
        # workaround to prevent the widget to lose focus if the color pick
        # dialog or drop down menu is used
        if self.drop_down_menu.isVisible():
            return
        if not self.keep_focus and event.lostFocus() and not self.underMouse():
            self.parent_view_widget.end_edit()
        super(_SyColorEdit, self).focusOutEvent(event)

    def insert_action_text(self, action):
        self.set_value(action.text())

    def _eval_color(self):
        text = self.toPlainText()
        color = colors.parse_to_mpl_color(text)
        self._update_button_color(color)

    def _on_color_pick(self):
        self.keep_focus = True
        # store old value and type
        try:
            old_value = self.get_value()
            old_color_dev = colors.get_color_dev(old_value)
            color = colors.get_color_as_rgba_f(old_value)
        except ValueError:
            old_color_dev = 'rgbF'
            color = None
        if color is None:
            color = [1., 0., 0.]
        color = np.array(color) * 255
        qcolor = QtGui.QColor(*color.astype(int))
        # create dialog
        dialog = QtGui.QColorDialog(qcolor, parent=self)
        color = dialog.getColor()

        if not color.isValid():
            return
        if old_color_dev == 'name':
            color_name = mpl_colors.rgb2hex(color.getRgbF())
            new_value = colors.COLORS_INV.get(color_name, color_name)
        elif old_color_dev in ['rgbf', 'rgbaf']:
            new_value = color.getRgbF()
            new_value = [round(i, 2) for i in new_value]
        elif old_color_dev in ['rgb', 'rgba']:
            new_value = color.getRgb()
        elif old_color_dev == 'hex':
            new_value = mpl_colors.rgb2hex(color.getRgbF())
        else:
            new_value = color.name()
        self.set_value(new_value)
        self.keep_focus = False

    def _update_button_color(self, value):
        if value is not None:
            icon = icon_utils.color_icon(six.text_type(value))
        else:
            icon = icon_utils.create_icon(icon_utils.SvgIcon.color)
        self.toolbutton.setIcon(icon)


# The _SyMPLColorEdit has to wrapped in a QWidget so the widget doesn't lose
# focus when the QColorDialog is shown.
class SyColorEdit(QtGui.QWidget, tree_widgets.SyBaseEditMixin):
    def __init__(self, *args, **kwargs):
        super(SyColorEdit, self).__init__(*args, **kwargs)
        kwargs['parent'] = self
        self._textedit = _SyColorEdit(*args, **kwargs)

        self.setFixedHeight(self.sizeHint().height())

        self.setContentsMargins(0, 0, 0, 0)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._textedit)
        self.setLayout(layout)

        self._completer = None
        self.parent_view_widget = None
        self.setFocusProxy(self._textedit)

    def sizeHint(self):
        return self._textedit.sizeHint()

    def set_completer(self, c):
        self._textedit.set_completer(c)

    def set_value(self, value):
        self._textedit.set_value(six.text_type(value))

    def get_value(self):
        return six.text_type(self._textedit.get_value())

    def set_parent_view_widget(self, widget):
        self.parent_view_widget = widget
        self._textedit.set_parent_view_widget(self.parent_view_widget)

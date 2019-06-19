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
import os.path
import itertools
import six
import sys
import functools

from sympathy.platform import qt_compat
from sympathy.utils import prim
from sympathy.platform import settings
from sympathy.utils.mock import mock_wrap
from sympathy.platform import colors

QtCore = qt_compat.import_module('QtCore')
QtGui = qt_compat.import_module('QtGui')
qt_compat.backend.use_matplotlib_qt()

from matplotlib.backends.backend_qt4agg import (
    NavigationToolbar2QT as NavigationToolbar)


def _pygments():
    # Importing pygments can in rare cases with unicode paths
    # result in UnicodeEncodeErrors.
    import pygments.lexers
    import pygments.styles
    return pygments


toolbar_stylesheet = """
QToolBar {
    background: %s;
    border: 1px solid %s;
    spacing: 3px;
}

QToolButton {
    border-radius: 1px;
    background-color: %s;
}

QToolButton:checked {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 rgba(0,0,0,60),
                                      stop: 1 rgba(0,0,0,30));
}

QToolButton:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 rgba(140,190,255,100),
                                      stop: 1 rgba(140,190,255,50));
}

QToolButton::menu-button {
    border: none;
}

QToolButton::menu-arrow:open {
    top: 1px;
}
"""


@mock_wrap
class SyNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent, coordinates=True):
        super(SyNavigationToolbar, self).__init__(canvas, parent, coordinates)

        self.setStyleSheet(self.construct_style_sheet())

    def construct_style_sheet(self):
        return toolbar_stylesheet % (self.get_parent_color(),
                                     self.get_border_color(),
                                     self.get_parent_color())

    def get_parent_color(self):
        color = self.palette().color(self.backgroundRole())
        return color.name()

    def get_border_color(self):
        color = self.palette().color(QtGui.QPalette.Mid)
        return color.name()


@mock_wrap
class ModeComboBox(QtGui.QComboBox):
    itemChanged = qt_compat.Signal(six.text_type)

    def __init__(self, items, parent=None):
        super(ModeComboBox, self).__init__(parent)
        self._lookup = dict(items)
        self._rlookup = dict(zip(self._lookup.values(), self._lookup.keys()))
        self.addItems([item[1] for item in items])
        self.currentIndexChanged[int].connect(self._index_changed)

    def set_selected(self, key):
        text = self._lookup[key]
        index = self.findText(text)
        if index >= 0:
            self.setCurrentIndex(index)

    def _index_changed(self, index):
        if index >= 0:
            text = self.currentText()
            self.itemChanged.emit(self._rlookup[text])


@mock_wrap
class SpaceHandlingListWidget(QtGui.QListView):
    itemChanged = qt_compat.Signal(QtGui.QStandardItem)

    def __init__(self, parent=None):
        super(SpaceHandlingListWidget, self).__init__(parent)
        self._model = QtGui.QStandardItemModel()
        self.setModel(self._model)
        self._model.itemChanged.connect(self.itemChanged)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            selection = self.selectedItems()
            if len(selection) > 0:
                if selection[0].checkState() == QtCore.Qt.Checked:
                    new_state = QtCore.Qt.Unchecked
                else:
                    new_state = QtCore.Qt.Checked
                for item in selection:
                    item.setCheckState(new_state)
        else:
            super(SpaceHandlingListWidget, self).keyPressEvent(event)

    def clear(self):
        self._model.clear()

    def count(self):
        return self._model.rowCount()

    def addItem(self, item):
        row = self._model.rowCount()
        self._model.insertRow(row, item)

    def addItems(self, items):
        for item in items:
            self.addItem(item)

    def item(self, row):
        return self._model.item(row, 0)

    def items(self):
        return [self.item(row) for row in range(self.count())]

    def row(self, item):
        return self._model.indexFromItem(item).row()

    def removeItem(self, item):
        return self._model.removeRow(item.row())

    def selectedItems(self):
        return [self._model.itemFromIndex(i) for i in self.selectedIndexes()]

    def findItems(self, text, flags=QtCore.Qt.MatchExactly):
        return self._model.findItems(text, flags=flags)


@mock_wrap
class SpaceHandlingContextMenuListWidget(SpaceHandlingListWidget):
    actionTriggered = QtCore.Signal(QtGui.QAction, QtGui.QStandardItem)

    def __init__(self, items, parent=None):
        super(SpaceHandlingContextMenuListWidget, self).__init__(parent)
        self._actions = [[QtGui.QAction(item, self)
                          for item in item_group]
                         for item_group in items]

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        item = None
        if self._actions:
            first = True
            for action_group in self._actions:
                if not first:
                    menu.addSeparator()
                first = False

                for action in action_group:
                    menu.addAction(action)

            global_pos = event.globalPos()
            action = menu.exec_(global_pos)
            event.accept()
            if action:
                self.actionTriggered.emit(action, item)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            event.ignore()
        else:
            super(SpaceHandlingContextMenuListWidget, self).mousePressEvent(
                event)


@mock_wrap
class CheckableComboBox(QtGui.QComboBox):
    selectedItemsChanged = QtCore.Signal(bool)
    checked_items_changed = QtCore.Signal(list)

    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.setItemDelegate(QtGui.QStyledItemDelegate(self))

        self._listview = self.view()

        self._listview.pressed.connect(self.handleItemPressed)
        self._listview.clicked.connect(self.handleItemClicked)

    def handleItemClicked(self, index):
        self.handleItemPressed(index, alter_state=False)

    def handleItemPressed(self, index, alter_state=True):
        item = self.model().itemFromIndex(index)
        self.blockSignals(True)
        if alter_state:
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
                idx = self.select_current_index()
            else:
                item.setCheckState(QtCore.Qt.Checked)
                idx = index.row()
        else:
            if item.checkState():
                idx = index.row()
            else:
                idx = self.select_current_index()
        self.setCurrentIndex(idx)
        self.blockSignals(False)
        self.selectedItemsChanged.emit(True)
        self.currentIndexChanged.emit(idx)
        self.checked_items_changed.emit(self.checkedItemNames())

    def select_current_index(self):
        selected_items = self.checkedItems()
        if len(selected_items):
            idx = selected_items[-1].row()
        else:
            idx = 0
        return idx

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        select_all = menu.addAction('Select all')
        unselect_all = menu.addAction('Unselect all')
        invert_selection = menu.addAction('Invert selection')
        action = menu.exec_(event.globalPos())
        if action == select_all:
            for row_idx in range(self.model().rowCount()):
                self.set_checked_state(row_idx, True)
        elif action == unselect_all:
            for row_idx in range(self.model().rowCount()):
                self.set_checked_state(row_idx, False)
        elif action == invert_selection:
            for row_idx in range(self.model().rowCount()):
                state = self.get_checked_state(row_idx)
                self.set_checked_state(row_idx, not state)
        self.selectedItemsChanged.emit(True)

    def set_checked_state(self, idx, state):
        checked = QtCore.Qt.Checked if state else QtCore.Qt.Unchecked
        self.model().item(idx).setCheckState(checked)

    def get_checked_state(self, idx):
        return bool(self.model().item(idx).checkState())

    def checkedItems(self):
        selected_items = []
        for row_idx in range(self.model().rowCount()):
            item = self.model().item(row_idx)
            if item is not None and bool(item.checkState()):
                selected_items.append(item)
        return selected_items

    def checkedItemNames(self):
        return [item.text() for item in self.checkedItems()]

    def add_item(self, text, checked=False):
        item = QtGui.QStandardItem(text)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                      QtCore.Qt.ItemIsEnabled)
        is_checked = QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
        item.setData(is_checked, QtCore.Qt.CheckStateRole)
        last_idx = self.model().rowCount()
        self.model().setItem(last_idx, 0, item)


@mock_wrap
class MacStyledItemDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        widget = QtGui.QCheckBox(index.data(), parent=parent)
        widget.stateChanged[bool].connect(self.stateChanged)
        return widget

    def paint(self, painter, option, index):
        option.showDecorationSelected = False
        super(MacStyledItemDelegate, self).paint(painter, option, index)

    def setEditorData(self, editor, index):
        editor.setCheckState(index.data(QtCore.Qt.EditRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.checkState(), QtCore.Qt.EditRole)

    @QtCore.Slot(bool)
    def stateChanged(self):
        self.commitData.emit(self.sender())


@mock_wrap
class LineEditClearButton(QtGui.QToolButton):
    def __init__(self, iconname, parent=None):
        super(LineEditClearButton, self).__init__(parent)
        pixmap = QtGui.QPixmap(iconname)
        self.setIcon(QtGui.QIcon(pixmap))
        self.setIconSize(QtCore.QSize(14, 14))
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.setStyleSheet(
            """
            QToolButton {
                border: none;
                padding: 0px;
                background-color: white;
            }
            QToolButton:hover { background-color: rgba(0,0,0,30); }
            QToolButton:pressed { background-color: rgba(0,0,0,60); }
            """)


@mock_wrap
class LineEditDropDownMenuButton(QtGui.QToolButton):
    def __init__(self, icon=None, parent=None):
        super(LineEditDropDownMenuButton, self).__init__(parent)
        if isinstance(icon, QtGui.QIcon):
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(14, 14))
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.setStyleSheet(
            """
            QToolButton {
                border: none;
                padding: 0px;
                background-color: white;
            }
            QToolButton:hover { background-color: rgba(0,0,0,30); }
            QToolButton:pressed { background-color: rgba(0,0,0,60); }
            """)


@mock_wrap
class LineEditComboButton(QtGui.QToolButton):
    value_changed = QtCore.Signal(tuple)
    value_edited = QtCore.Signal(tuple)

    _fixed = 15

    def __init__(self, options=None, value=None, parent=None):
        super(LineEditComboButton, self).__init__(parent=parent)

        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        self._options = []
        self._current_value = None
        self.separator = '\t'
        self.drop_down_menu = QtGui.QMenu(parent=self)
        self.setMenu(self.drop_down_menu)

        if options is None:
            options = []
        elif value is None and options:
            value = options[0]
        self.options = options
        self.current_value = value

        self.set_style_sheet()
        self.drop_down_menu.triggered.connect(self._state_changed)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options
        self.drop_down_menu.clear()
        self.set_drop_down_items(options)
        self.set_style_sheet()

    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._text_changed(value)

    def sizeHint(self):
        hint = super(LineEditComboButton, self).sizeHint()
        fm = QtGui.QFontMetrics(self.font())
        width = max([fm.width(p[0]) for p in self.options]) + self._fixed + 5
        hint.setWidth(width)
        return hint

    def set_style_sheet(self):
        # monospaced font
        f = QtGui.QFont('')
        f.setFixedPitch(True)
        self.setFont(f)

        fm = QtGui.QFontMetrics(f)
        max_len_prefix = max([fm.width(p[0]) for p in self.options])

        self.setStyleSheet("""
        QToolButton {
            border: none;
            padding: 0px;
            background-color: rgba(0,0,0,30);
            max-width: %spx;
        }

        QToolButton:hover {
            background-color: rgba(0,0,0,60);
        }

        QToolButton:pressed {
            font-weight: bold;
        }

        QToolButton::menu-indicator {
            left: 0px;
        }

        QToolButton::menu-indicator::open {
            top: 1px;
        }
        """ % (six.text_type(max_len_prefix + self._fixed)))

    def set_drop_down_items(self, items):
        self.setEnabled(len(items) > 0)
        for short, description in items:
            action = QtGui.QAction(
                '{}{}{}'.format(description, self.separator, short),
                self.drop_down_menu)
            self.drop_down_menu.addAction(action)

    def _state_changed(self, action):
        text = action.text()
        description, short = text.split(self.separator)
        self._text_changed((short, description), edit=True)

    def _text_changed(self, text, edit=False):
        prev = self.current_value
        if isinstance(text, tuple) and text != prev:
            self._current_value = text
            self.setText(text[0])
            if edit:
                self.value_edited.emit(self.current_value)
            self.value_changed.emit(self.current_value)


@mock_wrap
class LineEditToggleableLabelButton(QtGui.QToolButton):
    state_changed = QtCore.Signal(bool)

    def __init__(self, prefix_states=('Off', 'On'), parent=None):
        super(LineEditToggleableLabelButton, self).__init__(parent)

        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.prefix_states = prefix_states

        self.setCheckable(True)
        self.setText(self._prefix_states[self.isChecked()])
        self.set_style_sheet()

        self.toggled.connect(self._state_changed)

    def setChecked(self, state):
        super(LineEditToggleableLabelButton, self).setChecked(state)
        self._state_changed(state)

    @property
    def prefix_states(self):
        return self._prefix_states

    @prefix_states.setter
    def prefix_states(self, prefix_states):
        self._prefix_states = prefix_states
        self.set_style_sheet()

    def set_style_sheet(self):
        # monospaced font
        f = QtGui.QFont('')
        f.setFixedPitch(True)
        self.setFont(f)

        fm = QtGui.QFontMetrics(f)
        max_len_prefix = max([fm.width(p[:3]) for p in
                              self._prefix_states]) + 5

        self.setStyleSheet("""
        QToolButton {
            border: none;
            padding: 0px;
            background-color: rgba(0,0,0,30);
            max-width: %spx;
        }

        QToolButton:hover {
            background-color: rgba(0,0,0,60);
        }

        QToolButton:pressed {
            font-weight: bold;
        }
        """ % (six.text_type(max_len_prefix + 2)))

    def _state_changed(self, state):
        self.setText(self._prefix_states[state][:3])
        self.state_changed.emit(state)

    def _handle_menu(self):
        state = self.menu_action2.isChecked() is True
        self._state_changed(state)


@mock_wrap
class BaseLineTextEdit(QtGui.QTextEdit):
    def __init__(self, parent=None):
        super(BaseLineTextEdit, self).__init__(parent)

        self.left = QtGui.QWidget(self)
        self.left_layout = QtGui.QHBoxLayout(self.left)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.right = QtGui.QWidget(self)
        self.right_layout = QtGui.QHBoxLayout(self.right)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(100)

    def add_widget(self, widget, to_right=True):
        if to_right:
            layout = self.right_layout
            layout.insertWidget(1, widget)
        else:
            layout = self.left_layout
            layout.addWidget(widget)
        self.update_geometry()

    def remove_widget(self, widget):
        self.left_layout.removeWidget(widget)
        self.right_layout.removeWidget(widget)

    def update_geometry(self):
        frame_width = self.style().pixelMetric(
            QtGui.QStyle.PM_DefaultFrameWidth)
        left_padding = self.left.sizeHint().width() + frame_width + 1
        left_padding += 0 if self.left_layout.isEmpty() else 5
        right_padding = self.right.sizeHint().width() + frame_width + 1
        self.setStyleSheet("""
        QTextEdit {
            padding-left: %spx;
            padding-right: %spx;
        }
        """ % (left_padding, right_padding))
        msz = self.minimumSizeHint()
        self.setMinimumSize(
            max(msz.width(),
                self.left.sizeHint().width() + self.right.sizeHint().width() +
                frame_width * 2 + 52),
            max([self.sizeHint().height(),
                 self.right.sizeHint().height() + frame_width * 2 + 2,
                 self.left.sizeHint().height() + frame_width * 2 + 2]))

    def sizeHint(self):
        fm = QtGui.QFontMetrics(self.font())
        opt = QtGui.QStyleOptionFrameV3()
        text = self.document().toPlainText()

        h = max(fm.height(), 14) + 4
        w = fm.width(text) + 4

        opt.initFrom(self)

        o = (self.style().sizeFromContents(QtGui.QStyle.CT_LineEdit,
                                           opt,
                                           QtCore.QSize(w, h),
                                           self))
        return o

    def resizeEvent(self, event):
        super(BaseLineTextEdit, self).resizeEvent(event)
        frame_width = self.style().pixelMetric(
            QtGui.QStyle.PM_DefaultFrameWidth)
        rect = self.rect()
        left_hint = self.left.sizeHint()
        right_hint = self.right.sizeHint()
        self.left.move(frame_width + 1,
                       (rect.bottom() + 1 - left_hint.height()) / 2)
        self.right.move(rect.right() - frame_width - right_hint.width(),
                        (rect.bottom() + 1 - right_hint.height()) / 2)


@mock_wrap
class BaseLineEdit(QtGui.QLineEdit):
    def __init__(self, inactive="", parent=None):
        super(BaseLineEdit, self).__init__(parent)

        self.left = QtGui.QWidget(self)
        self.left_layout = QtGui.QHBoxLayout(self.left)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.right = QtGui.QWidget(self)
        self.right_layout = QtGui.QHBoxLayout(self.right)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.setPlaceholderText(inactive)

        self.setMinimumWidth(100)
        policy = QtGui.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

    def add_widget(self, widget, to_right=True):
        if to_right:
            layout = self.right_layout
            layout.insertWidget(1, widget)
        else:
            layout = self.left_layout
            layout.addWidget(widget)
        self.update_geometry()

    def remove_widget(self, widget):
        self.left_layout.removeWidget(widget)
        self.right_layout.removeWidget(widget)

    def update_geometry(self):
        frame_width = self.style().pixelMetric(
            QtGui.QStyle.PM_DefaultFrameWidth)
        self.setStyleSheet("""
        QLineEdit {
            padding-left: %spx;
            padding-right: %spx;
        }
        """ % (self.left.sizeHint().width() + frame_width + 1,
               self.right.sizeHint().width() + frame_width + 1))
        msz = self.minimumSizeHint()
        self.setMinimumSize(
            max(msz.width(),
                self.left.sizeHint().width() + self.right.sizeHint().width() +
                frame_width * 2 + 52),
            max([msz.height(),
                 self.right.sizeHint().height() + frame_width * 2 + 2,
                 self.left.sizeHint().height() + frame_width * 2 + 2]))

    def resizeEvent(self, event):
        frame_width = self.style().pixelMetric(
            QtGui.QStyle.PM_DefaultFrameWidth)
        rect = self.rect()
        left_hint = self.left.sizeHint()
        right_hint = self.right.sizeHint()
        self.left.move(frame_width + 1,
                       (rect.bottom() + 1 - left_hint.height()) / 2)
        self.right.move(rect.right() - frame_width - right_hint.width(),
                        (rect.bottom() + 1 - right_hint.height()) / 2)


@mock_wrap
class ClearButtonLineEdit(BaseLineEdit):
    def __init__(self, placeholder="", clear_button=True, parent=None):
        super(ClearButtonLineEdit, self).__init__(placeholder, parent)
        if clear_button:
            self.clear_button = LineEditClearButton(
                prim.get_icon_path('actions/edit-delete-symbolic.svg'),
                parent=self)
            self.add_widget(self.clear_button)
            self.clear_button.clicked.connect(self.clear)
            self.textChanged.connect(self.update_clear_button)
            self.clear_button.setEnabled(False)

    def update_clear_button(self, text):
        self.clear_button.setEnabled(not text == '')


@mock_wrap
class PrefixLineEdit(BaseLineEdit):
    def __init__(self, placeholder="", prefix="", parent=None):
        super(PrefixLineEdit, self).__init__(placeholder, parent)

        self.prefix_label = QtGui.QLabel(prefix, parent=self)
        self.add_widget(self.prefix_label, to_right=False)

    def set_prefix(self, prefix):
        self.prefix_label.setText(prefix)


@mock_wrap
class ToggleablePrefixLineEdit(BaseLineEdit):
    state_toggled = QtCore.Signal(bool)

    def __init__(self, placeholder="", state=True, prefix_states=('Off', 'On'),
                 parent=None):
        super(ToggleablePrefixLineEdit, self).__init__(placeholder, parent)

        assert (len(prefix_states) == 2)
        self.prefix_button = LineEditToggleableLabelButton(
            prefix_states=prefix_states, parent=self)
        self.prefix_button.setChecked(state)
        self.add_widget(self.prefix_button, to_right=False)

        self.prefix_button.state_changed.connect(self.state_toggled)

    def get_state(self):
        return self.prefix_button.isChecked()

    def set_state(self, state):
        self.prefix_button.setChecked(state)

    def set_prefix_states(self, prefix_states):
        if len(prefix_states) == 2:
            self.prefix_button.set_prefix_states(prefix_states)


@mock_wrap
class MenuLineEdit(BaseLineEdit):
    state_changed = QtCore.Signal(tuple)
    state_edited = QtCore.Signal(tuple)

    def __init__(self, placeholder="", options=None, value=None, parent=None):
        super(MenuLineEdit, self).__init__(placeholder, parent)

        self.prefix_button = LineEditComboButton(
            options=options, value=value, parent=self)
        self.add_widget(self.prefix_button, to_right=False)
        self.prefix_button.value_edited.connect(self.state_edited)
        self.prefix_button.value_changed.connect(self.state_changed)

    @property
    def current_value(self):
        return self.prefix_button.current_value

    @current_value.setter
    def current_value(self, value):
        self.prefix_button.current_value = value


@mock_wrap
class SyBaseToolBar(QtGui.QToolBar):
    def __init__(self, *args, **kwargs):
        super(SyBaseToolBar, self).__init__(*args, **kwargs)
        self.setStyleSheet(self.construct_style_sheet())

    def construct_style_sheet(self):
        return toolbar_stylesheet % (self.get_parent_color(),
                                     self.get_border_color(),
                                     self.get_parent_color())

    def get_parent_color(self):
        color = self.palette().color(self.backgroundRole())
        return color.name()

    def get_border_color(self):
        color = self.palette().color(QtGui.QPalette.Mid)
        return color.name()



class ToggleFilterButton(QtGui.QPushButton):
    def __init__(self, filter_widget=None, next_to_widget=None):
        """
        Button with a magnifying glass intended for toggling
        the display of filter options.

        If a filter_widget is provided it will automatically
        be connected and hidden by default.

        When placing it next to another widget it will look best if the height
        is the same: use set_size or next_to_widget.
        """
        pixmap = QtGui.QPixmap(prim.get_icon_path(
            'actions/view-filter-symbolic.svg'))
        icon = QtGui.QIcon(pixmap)
        super(ToggleFilterButton, self).__init__(icon, '')
        self.setToolTip('Show/Hide filter.')
        self.setCheckable(True)
        self.setFlat(True)

        self._filter_widget = filter_widget
        if self._filter_widget:
            # Default hidden.
            self._filter_widget.hide()
            self.toggled.connect(self._toggled)

        if next_to_widget:
            # TODO(erik): Assuming a 1px border (which is not always true).
            # Next to a combobox seems good on Windows 10 and worse on Mac OS.
            size = next_to_widget.sizeHint().height() + 2
            self.set_size(size)

    def set_size(self, size):
        self.setIconSize(QtCore.QSize(size, size))
        self.setFixedSize(size, size)

    def _toggled(self, checked=False):
        if checked:
            self._filter_widget.show()
        else:
            self._filter_widget.hide()


@mock_wrap
class SyToolBar(SyBaseToolBar):
    def __init__(self, *args, **kwargs):
        super(SyToolBar, self).__init__(*args, **kwargs)
        self.setMinimumHeight(22)
        self.setMaximumHeight(38)
        self.setIconSize(QtCore.QSize(26, 26))

        self._exclusive_checked_buttons = {}

    def add_action(self, text, icon_name=None, tooltip_text=None,
                   is_checkable=False, is_checked=False, is_exclusive=False,
                   receiver=None, signal_type=None):
        """
        Creates a new action with the given `text` and `tooltip_text`.
        The action is added to the end of the toolbar. The `signal_type`
        sets how the action's signal calls the receiver.
        """
        if icon_name is not None:
            icon = QtGui.QIcon(prim.get_icon_path(icon_name))
        else:
            icon = None
        a = self.addAction(icon, text)
        if tooltip_text is not None:
            a.setToolTip(tooltip_text)
        if is_checkable:
            a.setCheckable(is_checkable)
            a.setChecked(is_checked)
            if is_exclusive:
                self._exclusive_checked_buttons[a] = receiver
                a.toggled.connect(self._update_buttons_checked)
        if receiver is not None and not is_exclusive:
            if signal_type is not None and hasattr(a, signal_type):
                signal = getattr(a, signal_type)
                signal.connect(receiver)
            else:
                a.triggered.connect(receiver)
        return a

    @QtCore.Slot(bool)
    def _update_buttons_checked(self, state):
        sender = self.sender()
        if state:
            for action, callback in \
                    six.iteritems(self._exclusive_checked_buttons):
                action.setChecked(sender == action)
            callback = self._exclusive_checked_buttons[sender]
            if callback is not None:
                callback()
        elif not state and len(self._exclusive_checked_buttons):
            actions = itertools.cycle(self._exclusive_checked_buttons.keys())
            current_action = six.next(actions)
            while current_action != sender:
                current_action = six.next(actions)
            next_action = six.next(actions)
            self.blockSignals(True)
            next_action.setChecked(True)
            self.blockSignals(False)
            callback = self._exclusive_checked_buttons[next_action]
            if callback is not None:
                callback()

    def addStretch(self):
        spacer = QtGui.QWidget(parent=self)
        spacer.setMinimumWidth(0)
        policy = QtGui.QSizePolicy()
        policy.setHorizontalStretch(0)
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        spacer.setSizePolicy(policy)
        self.addWidget(spacer)


@mock_wrap
class BasePreviewTable(QtGui.QTableView):
    contextMenuClicked = QtCore.Signal(six.text_type, int, int)

    def __init__(self, parent=None):
        super(BasePreviewTable, self).__init__(parent)

        self._context_menu_actions = []

        self.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectItems)
        self.setSelectionMode(
            QtGui.QAbstractItemView.ContiguousSelection)
        self.ScrollHint(
            QtGui.QAbstractItemView.EnsureVisible)
        self.setCornerButtonEnabled(True)
        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        self.setMinimumHeight(100)

        vertical_header = self.verticalHeader()
        vertical_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        vertical_header.customContextMenuRequested.connect(
            self.vertical_header_context_menu)
        horizontal_header = self.horizontalHeader()
        horizontal_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        horizontal_header.customContextMenuRequested.connect(
            self.horizontal_header_context_menu)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    def vertical_header_context_menu(self, pos):
        if not self._context_menu_actions:
            return
        header = self.verticalHeader()
        row_idx = header.logicalIndexAt(pos)
        self._show_context_menu(row_idx, -1, header.mapToGlobal(pos))

    def horizontal_header_context_menu(self, pos):
        if not self._context_menu_actions:
            return
        header = self.horizontalHeader()
        column_idx = header.logicalIndexAt(pos)
        self._show_context_menu(-1, column_idx, header.mapToGlobal(pos))

    def contextMenuEvent(self, event):
        if not self._context_menu_actions:
            return

        global_pos = event.globalPos()
        pos = self.viewport().mapFromGlobal(global_pos)
        qindex = self.indexAt(pos)
        row_idx = qindex.row()
        column_idx = qindex.column()

        self._show_context_menu(row_idx, column_idx, global_pos)
        event.accept()

    def _show_context_menu(self, row, column, pos):
        current_menu_items = self.create_menu(row, column)
        action = self.menu.exec_(pos)
        if action:
            callback = current_menu_items[action]
            self.contextMenuClicked.emit(callback, row, column)

    def create_menu(self, row_idx, column_idx):
        self.menu = QtGui.QMenu(self)
        current_menu_items = {}
        for action_param in self._context_menu_actions:
            title, func, icon_name, validate_func = action_param

            is_valid = validate_func(row_idx, column_idx)
            if is_valid:
                if icon_name is not None:
                    icon = QtGui.QIcon(prim.get_icon_path(icon_name))
                    action = self.menu.addAction(icon, title)
                else:
                    action = self.menu.addAction(title)
                current_menu_items[action] = func
        return current_menu_items

    def add_context_menu_action(self, title, function, icon_name=None,
                                validate_callback=None, key_sequence=None):
        # Create a separate action for the shortcut:
        if validate_callback is None:
            def validate_callback(row, col): True
        if key_sequence is not None:
            if icon_name is not None:
                icon = QtGui.QIcon(prim.get_icon_path(icon_name))
                action = QtGui.QAction(icon, title, self)
            else:
                action = QtGui.QAction(title, self)
            action.setShortcuts(key_sequence)
            action.triggered.connect(
                lambda: self._emit_context_menu_clicked(function))
            self.addAction(action)

        self._context_menu_actions.append((title, function, icon_name,
                                           validate_callback))

    def _emit_context_menu_clicked(self, callback, row=0, column=0):
        self.contextMenuClicked.emit(callback, row, column)

    def selection(self):
        """
        Return a tuple with two ranges (startrow, endrow, startcol, endcol) for
        the currently selected area. Both ranges are half closed meaning that
        e.g. rows where startrow <= row < endrow are selected.
        """
        selection_model = self.selectionModel()
        if not selection_model.selection().count():
            return None
        selection_range = selection_model.selection()[0]
        minrow, maxrow = selection_range.top(), selection_range.bottom() + 1
        mincol, maxcol = selection_range.left(), selection_range.right() + 1
        return (minrow, maxrow, mincol, maxcol)

    def center_on_cell(self, row=None, col=None):
        if row is None:
            row = max(self.rowAt(0), 0)
        if col is None:
            col = max(self.columnAt(0), 0)

        index = self.model().createIndex(row, col, 0)
        if index.isValid():
            self.scrollTo(index)


@mock_wrap
class EnhancedPreviewTable(QtGui.QWidget):
    def __init__(self, model=None, filter_function=None, parent=None):
        super(EnhancedPreviewTable, self).__init__(parent)

        if model is None:
            model = QtCore.QAbstractItemModel()
        self._model = model
        self._transposed = False
        self._filter_function = filter_function

        self._preview_table = BasePreviewTable()

        # Toolbar
        self._toolbar = SyToolBar()
        # Search field
        self._filter_lineedit = ClearButtonLineEdit(placeholder='Search',
                                                    parent=self)
        self._filter_lineedit.setMaximumWidth(250)

        self._toolbar.addWidget(self._filter_lineedit)
        self._toolbar.addStretch()

        # Legend
        self._legend_layout = QtGui.QHBoxLayout()
        self._legend_layout.addStretch()

        # Setup layout
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._toolbar)
        layout.addWidget(self._preview_table)
        layout.addLayout(self._legend_layout)

        self.setLayout(layout)

        # Connect signals
        self._filter_lineedit.textChanged[six.text_type].connect(
            self._filter_columns)

        self.set_model(self._model, self._transposed)

    def preview_table(self):
        return self._preview_table

    def toolbar(self):
        return self._toolbar

    def _show_all(self):
        """
        Show all items in the table.
        This method is expensive so don't call it if the table is too big.
        """
        headers = [self._preview_table.horizontalHeader(),
                   self._preview_table.verticalHeader()]
        for header in headers:
            for i in range(header.count()):
                header.showSection(i)

    def _filter_columns(self, pattern):
        try:
            table = self._model.table()
        except AttributeError:
            self._show_all()
            return
        if table is None:
            # No table available for filtering. This probably means that we are
            # currently showing attributes, so simply show all rows and
            # columns.
            self._show_all()
            return

        columns = [table.col(name) for name in table.column_names()]
        item_count = len(columns)

        filter_func = self._filter_function
        if filter_func is None:
            # Fall back to showing all columns
            self._show_all()
            return

        filtered_item_indexes = set(filter_func(pattern, columns))

        if self._transposed:
            set_hidden = self._preview_table.setRowHidden
        else:
            set_hidden = self._preview_table.setColumnHidden
        for i in range(item_count):
            set_hidden(i, i not in filtered_item_indexes)

    def reapply_filter(self):
        filter_pattern = self._filter_lineedit.text()
        self._filter_lineedit.textChanged.emit(filter_pattern)

    def clear_filter(self):
        self._filter_lineedit.textChanged.emit('')

    def set_model(self, model, transposed):
        # Temporary reset the filter to make sure that all columns and rows are
        # shown before changing the model.
        self.clear_filter()
        self._model = model
        self._transposed = transposed
        self._preview_table.setModel(model)
        self.reapply_filter()

    def set_filter_function(self, func):
        self._filter_function = func

    def add_widget_to_legend(self, widget, on_left=False):
        legend_layout = self._legend_layout
        if on_left:
            legend_layout.insertWidget(0, widget)
        else:
            legend_layout.addWidget(widget)

    def add_widget_to_layout(self, widget, on_top=False):
        layout = self.layout()
        if on_top:
            layout.insertWidget(0, widget)
        else:
            layout.addWidget(widget)

    def add_layout_to_layout(self, layout, on_top=False):
        main_layout = self.layout()
        if on_top:
            main_layout.insertLayout(0, layout)
        else:
            main_layout.addLayout(layout)


@mock_wrap
class RowColumnLegend(QtGui.QGroupBox):
    def __init__(self, row=0, column=0, parent=None):
        super(RowColumnLegend, self).__init__(parent)
        self._row = row
        self._column = column
        self._init_gui()

    def _init_gui(self):
        self._row_column_label = QtGui.QLabel()
        self._row_column_label.setMaximumHeight(16)

        row_count_layout = QtGui.QHBoxLayout()
        row_count_layout.setContentsMargins(0, 0, 0, 0)
        row_count_layout.setAlignment(QtCore.Qt.AlignCenter)
        icon_label = QtGui.QLabel()
        icon = QtGui.QPixmap(prim.get_icon_path(
            'actions/view-grid-symbolic.svg'))
        icon_label.setPixmap(icon)
        row_count_layout.addWidget(icon_label)
        row_count_layout.addWidget(self._row_column_label)

        self.setLayout(row_count_layout)
        self._update_row_column_label()

    def _update_row_column_label(self):
        text = '{} \u00D7 {}'.format(self._row, self._column)
        self._row_column_label.setText(text)
        tooltip = '{} row{}<br>{} column{}'.format(
            self._row, '' if self._row == 1 else 's',
            self._column, '' if self._column == 1 else 's')
        self.setToolTip(tooltip)

    def set_row(self, row):
        self._row = row
        self._update_row_column_label()

    def set_column(self, column):
        self._column = column
        self._update_row_column_label()

    def set_row_column(self, row, column):
        self._row = row
        self._column = column
        self._update_row_column_label()


class PathMixinWidget(QtGui.QWidget):
    """
    Mixin which adds context menu actions *Make absolute* and *Make relative*
    to self._editor. It also provides a few helpers.
    """

    def __init__(self, parent=None):
        super(PathMixinWidget, self).__init__(parent)

        make_relative = QtGui.QAction(
            'Make relative', self._editor)
        make_absolute = QtGui.QAction('Make absolute', self._editor)
        self._editor.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self._editor.addAction(make_relative)
        self._editor.addAction(make_absolute)
        make_relative.triggered.connect(self._make_relative)
        make_absolute.triggered.connect(self._make_absolute)

    def _make_default_path(self, path):
        """Helper for making the default kind of path."""
        res = path
        if self._default_relative and self._root_path is not None:
            res = self._make_relative_path(path)
        return res

    def _make_relative_path(self, path):
        """Helper for making relative path out of path."""
        res = path
        if os.path.isabs(path):
            try:
                res = os.path.relpath(path, self._root_path)
            except Exception:
                pass
        return res

    def _make_absolute_path(self, path):
        """Helper for making absolute path out of path."""
        res = path
        try:
            res = os.path.normpath(
                os.path.join(self._root_path, path))
        except Exception:
            pass
        return res


@mock_wrap
class PathListWidget(PathMixinWidget):
    """
    Widget with a list of paths, buttons to add remove paths and some utilities
    for handling relative/absolute paths.
    """
    def __init__(self, paths, root_path=None, default_relative=False,
                 recent=None, parent=None):
        self._root_path = root_path
        self._default_relative = default_relative
        self._editor = QtGui.QListWidget()
        self._editor.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self._editor.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        self._recent = recent
        self._initial_paths = list(paths)

        super(PathListWidget, self).__init__(parent)
        for path in paths:
            self._add_item(path)

        remove_action = QtGui.QAction('Remove items', self._editor)
        remove_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete))
        remove_action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self._editor.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self._editor.addAction(remove_action)
        remove_action.triggered.connect(self._remove_path)
        add_button = QtGui.QPushButton('Add')
        remove_button = QtGui.QPushButton('Remove')

        buttons_container = QtGui.QVBoxLayout()
        buttons_container.addWidget(add_button)
        buttons_container.addWidget(remove_button)
        if recent is not None:
            recent_button = QtGui.QPushButton('Recent')
            buttons_container.addWidget(recent_button)
            menu = QtGui.QMenu(recent_button)
            for i, item in enumerate(recent, 1):
                action = menu.addAction(item)
                action.triggered.connect(functools.partial(
                    lambda item: self._add_item(item), item))
            recent_button.setMenu(menu)
        buttons_container.addStretch()

        container = QtGui.QHBoxLayout()
        container.setContentsMargins(1, 1, 1, 1)
        container.addWidget(self._editor)
        container.addLayout(buttons_container)
        self.setLayout(container)

        add_button.clicked.connect(self._add_path_dialog)
        remove_button.clicked.connect(self._remove_path)

    def _add_item(self, path):
        """Append a path to the list."""
        item = QtGui.QListWidgetItem(path)
        item.setFlags(QtCore.Qt.ItemIsEnabled |
                      QtCore.Qt.ItemIsSelectable |
                      QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsDragEnabled)
        self._editor.addItem(item)

    def _add_path_dialog(self):
        """Open a dialog to let the user select a directory, which is added."""
        default_directory = self._root_path or settings.get_default_dir()
        dir_ = QtGui.QFileDialog.getExistingDirectory(
            self, 'Choose a directory', default_directory)
        if len(dir_) > 0:
            dir_ = self._make_default_path(dir_)
            self._add_item(dir_)

    def _make_relative(self):
        """Make all selected paths relative."""
        if len(self._editor.selectedItems()) > 0:
            for selected_item in self._editor.selectedItems():
                old_path = selected_item.text()
                new_path = self._make_relative_path(old_path)
                if old_path != new_path:
                    self._editor.model().setData(
                        self._editor.indexFromItem(selected_item), new_path,
                        QtCore.Qt.DisplayRole)

    def _make_absolute(self):
        """Make all selected paths absolute."""
        if len(self._editor.selectedItems()) > 0:
            for selected_item in self._editor.selectedItems():
                old_path = selected_item.text()
                new_path = self._make_absolute_path(old_path)
                if old_path != new_path:
                    self._editor.model().setData(
                        self._editor.indexFromItem(selected_item), new_path,
                        QtCore.Qt.DisplayRole)

    def _remove_path(self):
        """Remove all selected paths."""
        if len(self._editor.selectedItems()) > 0:
            for selected_item in self._editor.selectedItems():
                row = self._editor.row(selected_item)
                self._editor.takeItem(row)
                del selected_item

    def paths(self):
        """Return a list of all paths in the list."""
        row_count = self._editor.model().rowCount(QtCore.QModelIndex())
        return [self._editor.item(i).text()
                for i in range(row_count)]

    def recent(self):
        new_recent_libs = []
        new_libs = [path for path in self.paths()
                    if path not in self._initial_paths]
        recent_libs = self._recent or []

        for lib in new_libs + recent_libs:
            if lib not in new_recent_libs:
                new_recent_libs.append(lib)
        return new_recent_libs


@mock_wrap
class PathLineEdit(PathMixinWidget):
    """
    Widget with a single path editor and some utilities
    for handling relative/absolute paths.
    """

    def __init__(self, path, root_path=None, default_relative=False,
                 placeholder_text=None, filter=None, parent=None):
        self._root_path = root_path
        self._default_relative = default_relative
        self._filter = filter
        self._editor = QtGui.QLineEdit()
        self._editor.setText(path or '')
        if placeholder_text:
            self._editor.setPlaceholderText(placeholder_text)

        super(PathLineEdit, self).__init__(parent)
        self._editor.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        dialog_button = QtGui.QPushButton('...')
        container = QtGui.QHBoxLayout()
        container.setContentsMargins(1, 1, 1, 1)
        container.addWidget(self._editor)
        container.addWidget(dialog_button)
        self.setLayout(container)
        dialog_button.clicked.connect(self._add_path_dialog)

    def _add_path_dialog(self):
        """Open a dialog to let the user select a directory, which is added."""
        default_directory = self._root_path or settings.get_default_dir()
        fq_filename = QtGui.QFileDialog.getOpenFileName(
            self, "Select file", default_directory, self._filter)[0]
        if len(fq_filename) > 0:
            fq_filename = self._make_default_path(fq_filename)
            self._change_item(fq_filename)

    def _change_item(self, path):
        """Change current itemt."""
        self._editor.setText(path)

    def _make_relative(self):
        """Make all selected paths relative."""
        old_path = self._editor.text()
        new_path = self._make_relative_path(old_path)
        if old_path != new_path:
            self._editor.setText(new_path)

    def _make_absolute(self):
        """Make all selected paths absolute."""
        old_path = self._editor.text()
        new_path = self._make_absolute_path(old_path)
        if old_path != new_path:
            self._editor.setText(new_path)

    def path(self):
        return self._editor.text()


@mock_wrap
class ExpandingTextEdit(QtGui.QTextEdit):
    def __init__(self, text='', parent=None):
        super(ExpandingTextEdit, self).__init__(parent)
        self.setReadOnly(True)
        policy = self.sizePolicy()
        policy.setVerticalStretch(1)
        self.setSizePolicy(policy)

        if text:
            self.setHtml(text)


@mock_wrap
class CodeEdit(QtGui.QTextEdit):
    def __init__(self, language='python', *args, **kwargs):
        super(CodeEdit, self).__init__(*args, **kwargs)

        # This should select the systems default monospace font
        f = QtGui.QFont('')
        f.setFixedPitch(True)
        self.setFont(f)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)

        self._highlighter = PygmentsHighlighter(self, language)
        self.textChanged.connect(self._highlighter.rehighlight)


@mock_wrap
class PygmentsHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, text_edit_widget, language):
        super(PygmentsHighlighter, self).__init__(text_edit_widget.document())
        style = settings.get_code_editor_theme()
        try:
            self._style = _pygments().styles.get_style_by_name(style)
        except _pygments().util.ClassNotFound:
            self._style = _pygments().styles.get_style_by_name('default')
        self._lexer = _pygments().lexers.get_lexer_by_name(
            language, stripall=True)

        self._tokens = []
        self._highlighting = False

        # Set background color from style
        palette = text_edit_widget.palette()
        palette.setColor(
            QtGui.QPalette.Base, QtGui.QColor(self._style.background_color))
        text_edit_widget.setPalette(palette)

    def _qt_format_for_token(self, token):
        styles = self._style.style_for_token(token)
        f = QtGui.QTextCharFormat()
        if styles['color'] is not None:
            f.setForeground(QtGui.QBrush(QtGui.QColor(
                '#' + styles['color'])))
        if styles['bgcolor'] is not None:
            f.setBackground(QtGui.QBrush(QtGui.QColor(
                '#' + styles['bgcolor'])))
        if styles['bold']:
            f.setFontWeight(QtGui.QFont.Bold)
        if styles['italic']:
            f.setFontItalic(True)
        return f

    def _parse_document(self):
        text = self.document().toPlainText()
        self._tokens = list(self._lexer.get_tokens_unprocessed(text))

    def rehighlight(self):
        # Prevent highlighting calling itself
        if self._highlighting:
            return
        self._highlighting = True

        self._parse_document()
        super(PygmentsHighlighter, self).rehighlight()
        self._highlighting = False

    def highlightBlock(self, text):
        block_start = self.previousBlockState() + 1
        block_end = block_start + len(text)

        for token_start, token_type, value in self._tokens:
            # Constrain token to block limits
            token_start = max(token_start, block_start)
            token_end = min(token_start + len(value), block_end)
            token_length = token_end - token_start

            # Skip tokens that are completely outside of this block
            if token_length <= 0:
                continue

            self.setFormat(token_start - block_start, token_length,
                           self._qt_format_for_token(token_type))

        # Adding one for the inevitable trailing newline character
        self.setCurrentBlockState(self.previousBlockState() + len(text) + 1)


class ValidationError(Exception):
    pass


class ValidatedLineEditBase(QtGui.QLineEdit):
    """Abstract base class for validated Line edit widgets."""

    def __init__(self, *args, **kwargs):
        super(ValidatedLineEditBase, self).__init__(*args, **kwargs)
        self._builder = None
        self._base_builder = None
        self.textChanged.connect(self._handleTextChanged)
        self._value = None

    def setBuilder(self, builder):
        self._builder = builder

    def _build(self, text):
        value = self._base_builder(text)
        if self._builder is not None:
            value = self._builder(value)
        return value

    def _handleTextChanged(self, text):
        tooltip = ''
        valid = False
        try:
            value = self._build(text)
            if value != self._value:
                self._value = value
                self.valueChanged.emit(value)
            valid = True
        except ValidationError as v:
            tooltip = six.text_type(v) + '\nValue: {}'.format(
                self._value)
        except Exception:
            pass
        self.setToolTip(tooltip)
        palette = self.palette()
        if valid:
            palette = QtGui.QPalette()
        else:
            if sys.platform == 'win32':
                # Special-case handling for Windows.
                # For some reason, changing the background color does not work
                # with the spinbox editors. For consistency, only text color
                # is changed -- this works for all line edits.
                palette.setColor(
                    QtGui.QPalette.Text, colors.DANGER_TEXT_NORMAL_BG_COLOR)
            else:
                palette.setColor(QtGui.QPalette.Text, colors.DANGER_TEXT_COLOR)
                palette.setColor(QtGui.QPalette.Base, colors.DANGER_BG_COLOR)

        self.setPalette(palette)

    def value(self):
        """
        Return the stored value.

        Not necessarily the same as what is currently shown in the text box.
        """
        return self._value


class ValidatedIntLineEdit(ValidatedLineEditBase):
    """Signal valueChanged is emitted when the stored value is changed."""
    valueChanged = qt_compat.Signal(int)

    def __init__(self, *args, **kwargs):
        super(ValidatedIntLineEdit, self).__init__(*args, **kwargs)
        self._base_builder = self._valid_int_builder

    def _valid_int_builder(self, text):
        try:
            return int(text)
        except Exception:
            raise ValidationError(
                '"{}" is not a valid int value.'.format(text))


class ValidatedFloatLineEdit(ValidatedLineEditBase):
    """Signal valueChanged is emitted when the stored value is changed."""
    valueChanged = qt_compat.Signal(float)

    def __init__(self, *args, **kwargs):
        super(ValidatedFloatLineEdit, self).__init__(*args, **kwargs)
        self._base_builder = self._valid_float_builder

    def _valid_float_builder(self, text):
        try:
            return float(text)
        except Exception:
            raise ValidationError(
                '"{}" is not a valid floating point value.'.format(text))


class ValidatedTextLineEdit(ValidatedLineEditBase):
    """Signal valueChanged is emitted when the stored value is changed."""
    valueChanged = qt_compat.Signal(six.text_type)

    def __init__(self, *args, **kwargs):
        super(ValidatedTextLineEdit, self).__init__(*args, **kwargs)
        self._base_builder = self._valid_text_builder

    def _valid_text_builder(self, text):
        try:
            return six.text_type(text)
        except Exception:
            raise ValidationError(
                '"{}" is not a valid text value.'.format(text))


class ValidatedSpinBoxBase(QtGui.QAbstractSpinBox):
    """Signal valueChanged is emitted when the stored value is changed."""

    def __init__(self, *args, **kwargs):
        super(ValidatedSpinBoxBase, self).__init__(*args, **kwargs)
        self._max = None
        self._min = None
        self._step = 1
        self._value = None

    def _init_line_validator(self):
        def bounded_validator(value):
            if self._max is not None and value > self._max:
                raise ValidationError(
                    '"{}" is greater than upper bound: "{}".'.format(
                        value, self._max))

            if self._min is not None and value < self._min:
                raise ValidationError(
                    '"{}" is smaller than lower bound: "{}".'.format(
                        value, self._min))
            return value

        self.lineEdit().setBuilder(bounded_validator)

    def setLineEdit(self, line_edit):
        super(ValidatedSpinBoxBase, self).setLineEdit(line_edit)
        line_edit.valueChanged.connect(self._handleValueChanged)
        self._init_line_validator()

    def setMaximum(self, value):
        self._max = value

    def setMinimum(self, value):
        self._min = value

    def setSingleStep(self, value):
        self._step = value

    def setValue(self, value):
        if self._max is not None and value > self._max:
            value = self._max
        if self._min is not None and value < self._min:
            value = self._min

        line_edit = self.lineEdit()
        line_edit.setText(six.text_type(value))

    def value(self):
        return self._value

    def stepEnabled(self):
        state = QtGui.QAbstractSpinBox.StepNone
        if self._value is not None:
            if self._max is not None and self._value < self._max:
                state |= QtGui.QAbstractSpinBox.StepUpEnabled
            if self._min is not None and self._value > self._min:
                state |= QtGui.QAbstractSpinBox.StepDownEnabled
        return state

    def stepBy(self, steps):
        self.setValue(self._value + steps * self._step)

    def _handleValueChanged(self, value):
        self._value = value
        self.valueChanged.emit(value)


class ValidatedFloatSpinBox(ValidatedSpinBoxBase):
    valueChanged = qt_compat.Signal(float)

    def __init__(self, *args, **kwargs):
        super(ValidatedFloatSpinBox, self).__init__(*args, **kwargs)
        self._decimals = None
        line_edit = ValidatedFloatLineEdit(parent=self)
        super(ValidatedFloatSpinBox, self).setLineEdit(line_edit)

    def setValue(self, value):
        if self._decimals is not None:
            value = float(round(value, self._decimals))
        super(ValidatedFloatSpinBox, self).setValue(value)

    def setMaximum(self, value):
        if value is None:
            self._max = None
        else:
            self._max = float(value)

    def setMinimum(self, value):
        if value is None:
            self._min = None
        else:
            self._min = float(value)

    def setDecimals(self, value):
        self._decimals = value


class ValidatedIntSpinBox(ValidatedSpinBoxBase):
    valueChanged = qt_compat.Signal(int)

    def __init__(self, *args, **kwargs):
        super(ValidatedIntSpinBox, self).__init__(*args, **kwargs)
        line_edit = ValidatedIntLineEdit(parent=self)
        super(ValidatedIntSpinBox, self).setLineEdit(line_edit)

    def setValue(self, value):
        super(ValidatedIntSpinBox, self).setValue(value)


class ValidatedComboBoxBase(QtGui.QComboBox):
    def __init__(self, *args, **kwargs):
        super(ValidatedComboBoxBase, self).__init__(*args, **kwargs)
        self._max = None
        self._min = None
        self._value = None
        self.currentIndexChanged[int].connect(self._handleIndexChanged)
        self.setEditable(True)

    def _init_line_validator(self):
        def bounded_validator(value):
            if self._max is not None and value > self._max:
                raise ValidationError(
                    '"{}" is greater than upper bound: "{}".'.format(
                        value, self._max))

            if self._min is not None and value < self._min:
                raise ValidationError(
                    '"{}" is smaller than lower bound: "{}".'.format(
                        value, self._min))
            return value

        self.lineEdit().setBuilder(bounded_validator)

    def setLineEdit(self, line_edit):
        super(ValidatedComboBoxBase, self).setLineEdit(line_edit)
        line_edit.valueChanged.connect(self._handleValueChanged)
        self._init_line_validator()

    def setMaximum(self, value):
        self._max = value

    def setMinimum(self, value):
        self._min = value

    def setValue(self, value):
        if self._max is not None and value > self._max:
            value = self._max
        if self._min is not None and value < self._min:
            value = self._min

        line_edit = self.lineEdit()
        line_edit.setText(six.text_type(value))

    def value(self):
        return self._value

    def _handleValueChanged(self, value):
        self._value = value
        self.valueChanged.emit(value)

    def _handleIndexChanged(self, index):
        line_edit = self.lineEdit()
        text = line_edit.text()
        line_edit.setText(text)


class ValidatedTextComboBox(ValidatedComboBoxBase):
    valueChanged = qt_compat.Signal(six.text_type)

    def __init__(self, *args, **kwargs):
        super(ValidatedTextComboBox, self).__init__(*args, **kwargs)
        line_edit = ValidatedTextLineEdit(parent=self)
        super(ValidatedTextComboBox, self).setLineEdit(line_edit)


class ValidatedFloatComboBox(ValidatedComboBoxBase):
    valueChanged = qt_compat.Signal(float)

    def __init__(self, *args, **kwargs):
        super(ValidatedFloatComboBox, self).__init__(*args, **kwargs)
        self._decimals = None
        line_edit = ValidatedFloatLineEdit(parent=self)
        super(ValidatedFloatComboBox, self).setLineEdit(line_edit)

    def setValue(self, value):
        if self._decimals is not None:
            value = round(value, self._decimals)
        super(ValidatedFloatComboBox, self).setValue(value)

    def setDecimals(self, value):
        self._decimals = value


class ValidatedIntComboBox(ValidatedComboBoxBase):
    valueChanged = qt_compat.Signal(int)

    def __init__(self, *args, **kwargs):
        super(ValidatedIntComboBox, self).__init__(*args, **kwargs)
        line_edit = ValidatedIntLineEdit(parent=self)
        super(ValidatedIntComboBox, self).setLineEdit(line_edit)

    def setValue(self, value):
        super(ValidatedIntComboBox, self).setValue(value)


class NonEditableComboBox(QtGui.QComboBox):
    valueChanged = qt_compat.Signal(six.text_type)

    def __init__(self, *args, **kwargs):
        super(NonEditableComboBox, self).__init__(*args, **kwargs)
        self.setEditable(False)
        self.currentIndexChanged[int].connect(self._handleIndexChanged)

    def value(self):
        return self.currentText()

    def _handleIndexChanged(self, index):
        self.valueChanged.emit(self.currentText())


# leave for debugging widgets
if __name__ == '__main__':
    application = QtGui.QApplication(sys.argv)

    widget = QtGui.QWidget()
    layout = QtGui.QVBoxLayout()

    test_widget = ToggleablePrefixLineEdit(placeholder='enter filename',
                                           prefix_states=('rel', 'abs'),
                                           parent=widget)
    # test_widget.textChanged.connect(lambda a: test_widget.set_state(a == ''))

    other_widget = ClearButtonLineEdit(parent=widget)

    normal_widget = QtGui.QLineEdit(widget)

    layout.addWidget(test_widget)
    layout.addWidget(other_widget)
    layout.addWidget(normal_widget)

    widget.setLayout(layout)
    widget.show()
    widget.raise_()

    # print(test_widget.rect().height())
    # print(other_widget.rect().height())
    # print(normal_widget.rect().height())

    sys.exit(application.exec_())

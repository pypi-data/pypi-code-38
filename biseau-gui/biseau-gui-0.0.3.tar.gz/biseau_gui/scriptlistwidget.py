"""View of loaded scripts, allowing to rearrange, add and delete them.

"""
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import biseau as bs


ScriptRole = Qt.UserRole + 1
DurationRole = Qt.UserRole + 2


class ScriptDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):

        super().paint(painter, option, index)

        duration = index.data(DurationRole)
        if duration:
            painter.drawText(
                option.rect, Qt.AlignRight | Qt.AlignVCenter, f"{duration} ms"
            )


class ScriptListWidget(QWidget):
    def __init__(self, parent=None):

        super().__init__(parent)
        self.view = QListWidget(self)
        self.view.setItemDelegate(ScriptDelegate())

        # TODO: fix that bug (reproduced by lucas & sacha)
        # self.view.setDragEnabled(True)
        # self.view.setDragDropMode(QAbstractItemView.InternalMove)
        # self.view.viewport().setAcceptDrops(True)
        # self.view.setDropIndicatorShown(True)

        self.toolbar = QToolBar()
        self.view.setIconSize(QSize(32, 32))

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.view)

        self.setLayout(main_layout)

        # create actions
        self.toolbar.addAction(QIcon.fromTheme("go-up"), "Move up", self._script_move_up)
        self.toolbar.addAction(QIcon.fromTheme("go-down"), "Move down", self._script_move_down)
        self.toolbar.addAction(QIcon.fromTheme("remove"), "Delete", self._script_delete)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)


        self.toolbar.addAction(QIcon.fromTheme("view-sort-ascending"), "Sort", self.sort_script)

        # self.view.itemChanged.connect(self.changed)
        # self.view.itemDoubleClicked.connect(lambda i: self.scriptClicked.emit(i.data(Qt.UserRole)))

    def add_script(self, script: bs.Script):
        """ Add script to the list """
        if script:
            item = QListWidgetItem(script.name)
            item.setToolTip(script.description)
            item.setCheckState(Qt.Checked)
            item.setSizeHint(QSize(32, 32))
            # keep script as item data
            item.setData(ScriptRole, script)
            self.view.addItem(item)

    def _script_move_up(self):
        """ move up selected row """
        index = self.view.currentRow()
        if index > 0:
            item = self.view.takeItem(index)
            self.view.insertItem(index - 1, item)
            self.view.setCurrentItem(item)

    def _script_move_down(self):
        """ move down selected row """
        index = self.view.currentRow()
        if index < self.view.count() - 1:
            item = self.view.takeItem(index)
            self.view.insertItem(index + 1, item)
            self.view.setCurrentItem(item)

    def _script_delete(self):
        """ move up selected row """
        index = self.view.currentRow()
        if index >= 0:
            item = self.view.takeItem(index)
            self.parent().parent().delete_docks_of_script(item.data(ScriptRole))

    def get_scripts(self):
        """ return scripts as a list in the same order than the view  """
        scripts = []
        for index in range(self.view.count()):
            if self.view.item(index).checkState() == Qt.Checked:
                scripts.append(self.view.item(index).data(ScriptRole))
        return scripts

    def set_item_duration(self, row, duration):
        """ set item duration """
        self.view.item(row).setData(DurationRole, duration)

    def index_of_script(self, script: bs.Script):
        for index in range(self.view.count()):
            if self.view.item(index).data(ScriptRole) == script:
                return index
        return None

    def set_current_script(self, script: bs.Script):
        """ active selection for the current script """
        index = self.index_of_script(script)
        if index is not None:
            self.view.setCurrentRow(index)

    def sort_script(self):
        """ sort script in the list """
        scripts = self.get_scripts()
        self.view.clear()
        for script in bs.sort_scripts_per_dependancies(scripts):
            self.add_script(script)


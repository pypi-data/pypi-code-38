"""Interface to load scripts."""

import pkg_resources
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import biseau as bs

import glob
import os


class ScriptBrowserModel(QAbstractTableModel):
    """
    Load all Scripts file into a model from a directory location

    @see set_path
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scripts = []
        self.headers = ["name", "tags", "language", "description"]

    def rowCount(self, index: QModelIndex):
        """Overrided"""
        return len(self.scripts)

    def columnCount(self, index: QModelIndex):
        """Overrided"""
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Overrided """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]

        return None

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """ Overrided """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return self.scripts[index.row()].name

            if index.column() == 1:
                return ",".join(self.scripts[index.row()].tags)

            if index.column() == 2:
                return self.scripts[index.row()].language

            if index.column() == 3:
                return self.scripts[index.row()].description

    def set_path(self, path):
        """
        Search all scripts in the path
        """
        self.beginResetModel()
        self.scripts.clear()
        extensions = ("*.py", "*.lp", "*.json")
        for ext in extensions:
            for file in glob.glob(os.path.join(path, ext), recursive=False):
                script = next(bs.module_loader.build_scripts_from_file(file), None)
                if isinstance(script, bs.Script):
                    self.scripts.append(script)
                    # print('LBQLIR:', script)
        self.endResetModel()

    def get_script(self, index: QModelIndex):
        """
        Return a script according index
        """
        if index.isValid():
            return self.scripts[index.row()]


class ScriptBrowserDialog(QDialog):
    """
    A Script Browser to select Script file
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Script browser")

        self.search_edit = QLineEdit()
        self.search_box = QComboBox()
        self.view = QTableView()
        self.model = ScriptBrowserModel()
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.addButton(
            "Select all", QDialogButtonBox.ActionRole
        ).clicked.connect(self.view.selectAll)
        self.file_browser = QListView()
        self.file_model = QFileSystemModel()
        self.file_path_edit = QLineEdit()

        # search bar
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.search_edit)
        h_layout.addWidget(self.search_box)

        # script view
        v_layout = QVBoxLayout()
        v_widget = QWidget()
        v_layout.addLayout(h_layout)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addWidget(self.view)
        v_widget.setLayout(v_layout)

        main_splitter = QSplitter(Qt.Horizontal)
        # set file browser  model
        file_layout = QVBoxLayout()
        self.file_browser.setModel(self.file_model)
        self.file_model.setFilter(QDir.AllDirs)

        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.file_browser)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_widget = QWidget()
        file_widget.setLayout(file_layout)

        self.file_model.setFilter(QDir.Dirs | QDir.NoDot)

        main_splitter.addWidget(file_widget)
        main_splitter.addWidget(v_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        self.view.setModel(self.proxy)
        self.view.setSortingEnabled(True)
        self.view.setWordWrap(False)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.search_box.addItems(self.model.headers)

        self.file_model.directoryLoaded.connect(self.file_path_edit.setText)
        self.file_path_edit.textChanged.connect(self.set_current_path)
        self.file_browser.doubleClicked.connect(
            lambda x: self.set_current_path(self.file_model.filePath(x))
        )

        self.search_edit.textChanged.connect(self.set_filter)
        self.search_box.currentTextChanged.connect(self.set_filter)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.resize(800, 400)
        self.set_current_path(pkg_resources.resource_filename(__name__, 'embedded_scripts'))
        self.file_path_edit.setFocus()

    def set_filter(self, text):
        """ set filter : called by search_edit """
        self.proxy.setFilterKeyColumn(self.search_box.currentIndex())
        self.proxy.setFilterRegExp(text)

    def set_current_path(self, path):
        """ set current path """
        index = self.file_model.setRootPath(path)
        self.file_browser.setRootIndex(index)
        self.model.set_path(path)

    def get_scripts(self):
        """ get selected Script """
        scripts = []
        for index in self.view.selectionModel().selectedRows():
            index = self.proxy.mapToSource(index)
            scripts.append(self.model.get_script(index))

        return scripts

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import biseau as bs
import random
from pathlib import Path


# ========= Some editor =============


class IntEditor(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        maxi = 2**31 -1
        self.setRange(-maxi, maxi)

    def get_value(self):
        return self.value()

    def set_value(self, value):
        self.setValue(int(value))


class FloatEditor(QDoubleSpinBox):
    def get_value(self):
        return self.value()

    def set_value(self, value):
        self.setValue(int(value))


class BoolEditor(QCheckBox):
    def get_value(self):
        return self.checkState() == Qt.Checked

    def set_value(self, value):
        self.setCheckState(Qt.Checked if value else Qt.Unchecked)


class StrEditor(QLineEdit):
    def get_value(self):
        return self.text()

    def set_value(self, value):
        self.setText(str(value))


class MultiLineEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50)

    def get_value(self):
        return self.toPlainText()

    def set_value(self, value: str):
        self.setPlainText(value)


class ChoiceEditor(QComboBox):
    def __init__(self, parent, choices:list, default:object):
        super().__init__(parent)
        self.clear()
        self.addItems(choices)
        self.setCurrentText(default)

    def get_value(self):
        return self.currentText()

    def set_value(self, value):
        self.setCurrentIndex(self.findText(value))


class MultiChoiceEditor(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setEditable(True)

    def populate(self, values: list):
        self.model.clear()
        for value in values:
            item = QStandardItem(value)
            item.setCheckable(True)
            item.setCheckState(Qt.Unchecked)
            self.model.appendRow(item)

    def get_value(self):
        for value in self:
            if value.checkState:
                yield value

    def set_value(self, value):
        self.setCurrentIndex(self.findText(value))


class RangeEditor(QSpinBox):
    def __init__(self, parent, value, start, end=None, step=1):
        super().__init__(parent)
        self.setRange(start, end)
        self.setSingleStep(step)
        self.set_value(value)

    def get_value(self):
        return self.value()

    def set_value(self, value):
        self.setValue(value)


class FileEditor(QLineEdit):
    def __init__(self, parent=None, mode='r'):
        super().__init__(parent)
        self.__mode = mode
        browse_action = self.addAction(
            QIcon.fromTheme("system-file-manager"),
            QLineEdit.LeadingPosition
        )
        browse_action.triggered.connect(self._browse)

    def _browse(self):
        # print(dir(QFileDialog))
        filename = QFileDialog.getOpenFileName(self, "open file")
        if filename:
            self.set_value(filename[0])

    def get_value(self) -> Path:
        return self.text()
        return Path(self.text())

    def set_value(self, value: Path):
        self.setText(str(value))


# ========= Some editor =============


class OptionDelegate(QStyledItemDelegate):
    """ Delegate custom the view by adding editor with specific type """

    def __init__(self):
        super().__init__()

    def createEditor(self, parent: QWidget, option, index):
        """ overrided : Return a widget for the index """

        name, val_type, val_default, descr = index.data(Qt.UserRole)
        BUILDER = {
            int: IntEditor,
            float: FloatEditor,
            bool: BoolEditor,
        }
        if val_type in BUILDER:
            value_editor = BUILDER[val_type](parent)
            value_editor.set_value(val_default)
            return value_editor
        elif val_type is str:  # a string
            value_editor = (MultiLineEditor if '\n' in val_default else StrEditor)(parent)
            value_editor.set_value(val_default)
            return value_editor
        elif isinstance(val_type, range):  # range of int
            return RangeEditor(parent, val_default, val_type.start, val_type.stop, val_type.step)
        elif isinstance(val_type, (list, tuple)):  # list of things
            return ChoiceEditor(parent, choices=val_type, default=val_default)
        elif isinstance(val_type, (set, frozenset)):  # subset of list of things
            return MultiChoiceEditor(parent, val_type, val_default)

        elif val_type is open:  # an openable file
            editor = FileEditor(parent)
            editor.set_value(val_default)
            return editor
        elif isinstance(val_type, (list, tuple)) and len(val_type) == 2 and val_type[0] is open:  # a file
            editor = FileEditor(parent, mode=val_type[1])
            editor.set_value(val_default)
            return editor

        raise ValueError(f"unhandled option '{name}' of type {val_type}.")


    def setModelData(self, editor, model, index):
        """ overridded: get data from widget and write it in the model  """
        name, val_type, val_default, descr = index.data(Qt.UserRole)

        if "get_value" in dir(editor):
            return model.setData(index, editor.get_value())
        else:
            return super().setModelData(editor, model, index)


class OptionsModel(QAbstractTableModel):
    """
    This is an editable Model for option scripts
    """

    options_changed = Signal()

    def __init__(self):
        super().__init__()
        self.script = None
        self.option_values = {}

    def rowCount(self, index=QModelIndex()):
        """ overrided """
        if self.script:
            return len(self.script.options)
        else:
            return 0

    def columnCount(self, index=QModelIndex()):
        """ overrided """
        return 2

    def set_script(self, script: bs.Script):
        """ load option script into the model """
        self.beginResetModel()
        self.script = script
        self.endResetModel()

    def data(self, index: QModelIndex(), role=Qt.DisplayRole):
        """ overrided : return data according index and role """

        if not index.isValid():
            return None

        name, val_type, val_default, description = self.script.options[index.row()]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            # Display the key
            if index.column() == 0:
                return name

            # Display the Value
            if index.column() == 1:
                return self.option_values.get(name, val_default)

            # Qt.UserRole return the full script's option tuple
        if role == Qt.UserRole:
            return self.script.options[index.row()]

    def setData(self, index: QModelIndex(), value, role=Qt.EditRole):
        """ overrided : write value into the model """
        if role == Qt.EditRole:
            name, val_type, _, _ = self.script.options[index.row()]
            self.option_values[name] = value
            self.options_changed.emit()

    def flags(self, index=QModelIndex()) -> Qt.ItemFlags:
        """ overrided : set item flag attributes """
        if index.column() == 0:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

        if index.column() == 1:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return self.tr("key")
            if section == 1:
                return self.tr("value")

        return None

    #     self.script = script
    #     self.clear()
    #     self.setColumnCount(2)
    #     self.setHorizontalHeaderLabels(["key", "value"])

    #     print(self.script.options)

    #     # for testing
    #     tmp  = list(self.script.options)
    #     print("OPTIONS", tmp)
    #     # #tmp.append(("colordemo",QColor, 2,''))
    #     # tmp.append(("pathdemo",Path, "/home/",''))
    #     # tmp.append(("color demo",QColor, "red",''))

    #     # self.script.options = tmp
    #     # #self.script.options = tuple(tmp)
    #     # # end testing

    #     for option in self.script.options:
    #         name, _type, default_value, description = option

    #         print(name, default_value, _type)
    #         key_item = QStandardItem(name)  # option name
    #         #val_item = QStandardItem(str(default_value))  # default value ?
    #         #Type = option[1]  # Get option type
    #         #print(Type, type(default_value))
    #         # val_item.setData(
    #         #     Type(default_value), Qt.EditRole
    #         # )  # cast according option type

    #         # key_item.setEditable(False)
    #         #self.appendRow([key_item, val_item])

    def get_option_values(self):
        """
        return options value according model
        """
        return self.option_values


class OptionsWidget(QTableView):
    """ Widget to display options """

    def __init__(self):
        super().__init__()
        self.model = OptionsModel()
        self.delegate = OptionDelegate()

        self.setModel(self.model)
        self.setItemDelegate(self.delegate)
        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.CurrentChanged)
    def set_script(self, script: bs.Script):
        """
        @see OptionModel.setScript())
        """
        self.model.set_script(script)

    def get_option_values(self):
        """
        @see OptionModel.get_option_values())
        """
        return self.model.get_option_values()

    def is_empty(self):
        return self.model.rowCount() == 0


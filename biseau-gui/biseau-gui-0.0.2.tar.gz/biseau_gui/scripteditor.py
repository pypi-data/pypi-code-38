from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import biseau as bs

from .optionswidget import OptionsWidget


class ScriptEditor(QWidget):

    # emit when script changed ( source code or options )
    changed = Signal()

    def __init__(self, script, parent=None):
        super().__init__(parent)

        v_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        # First tab = editor
        self.edit_widget = QPlainTextEdit()
        self.tab_widget.addTab(self.edit_widget, "editor")

        # Second Tab = options
        self.option_widget = OptionsWidget()
        self.tab_widget.addTab(self.option_widget, "options")

        v_layout.addWidget(self.tab_widget)
        v_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(v_layout)

        self.set_script(script)

        self.setStyleSheet("QFrame:focus {  border: 2px solid red; }")

        self.option_widget.model.options_changed.connect(self.on_option_changed)
        self.edit_widget.textChanged.connect(self.on_code_changed)
        self.symbol_count = {}  # {char: count in code}, allowing to trigger autocompile


    def set_script(self, script: bs.Script):
        """ set script reference for this editor """
        self.script = script
        self.edit_widget.setPlainText(self.script.source_code)
        self.option_widget.set_script(script)

        if not self.option_widget.is_empty():
            self.tab_widget.setCurrentIndex(1)
        else:
            self.tab_widget.setCurrentIndex(0)

    def update_script(self):
        self.script.source_code = self.edit_widget.toPlainText()
        self.script.options_values.update(self.option_widget.get_option_values())

    def on_option_changed(self):
        self.changed.emit()  # triggering autocompile
    def on_code_changed(self):
        """Called when source code is changed ; propagate to autocompile
        when some characters add added/removed
        """
        source = self.edit_widget.toPlainText()
        counts = {c: source.count(c) for c in '.%'}
        if counts != self.symbol_count:  # something changed
            self.symbol_count = counts
            self.changed.emit()  # triggering autocompile

from PySide2 import QtWidgets
from PySide2.QtWidgets import QLabel

import vstreamer_utils


class PropertiesWidget(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        vstreamer_utils.load_ui("PropertiesWidget.ui", self)

    def set_properties(self, file_entry):
        self.clear()
        if file_entry is None:
            return

        self.title_label.setText(file_entry.properties["Filename"])
        if file_entry.description is not None:
            self.description_label.setText(file_entry.description)
        PropertiesWidget._add_lines_to_layout(self.properties_layout, file_entry.properties)
        PropertiesWidget._add_lines_to_layout(self.other_properties_layout,
                                              file_entry.other_properties)
        if len(file_entry.properties) > 0:
            self.properties_info_label.setText("Properties")
        if len(file_entry.other_properties) > 0:
            self.other_properties_info_label.setText("Other properties")

    def clear(self):
        PropertiesWidget._clear_layout(self.properties_layout)
        PropertiesWidget._clear_layout(self.other_properties_layout)
        self.title_label.setText("")
        self.description_label.setText("")
        self.properties_info_label.setText("")
        self.other_properties_info_label.setText("")

    @staticmethod
    def _add_lines_to_layout(layout, properties):
        for key, value in properties.items():
            left_label = QLabel(key + ":")
            right_label = QLabel(value)
            right_label.setWordWrap(True)
            layout.addRow(left_label, right_label)

    @staticmethod
    def _clear_layout(layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            item.widget().deleteLater()

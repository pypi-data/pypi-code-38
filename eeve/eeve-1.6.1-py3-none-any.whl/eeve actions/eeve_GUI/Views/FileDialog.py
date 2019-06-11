import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon


def openFileNamesDialog():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    files, _ = QFileDialog.getOpenFileNames(
        None,
        "QFileDialog.getOpenFileNames()",
        "",
        "All Files (*);;Python Files (*.py)",
        options=options)
    if files:
        return files

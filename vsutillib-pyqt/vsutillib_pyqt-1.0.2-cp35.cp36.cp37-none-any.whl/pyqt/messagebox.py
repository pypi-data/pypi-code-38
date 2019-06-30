"""
function for QMessageBox Yes|No needed for change
font on the fly and localization

Args:
    self (QWidget): parent QWidget
    tittle (str): tittle for QMessageBox
    text (str): text for QMessageBox
    icon (QIcon): standard icons for QMessageBox
        question mark, warning ...
Returns:
    QMessageBox.button: standar QMessageBox button

"""

from PySide2.QtWidgets import QMessageBox

def messageBoxYesNo(self, title, text, icon):

    """
    Save window state before exit
    """

    m = QMessageBox(self)
    m.setWindowTitle(title)
    m.setText(text)
    m.setIcon(icon)
    yesButton = m.addButton('Yes', QMessageBox.ButtonRole.YesRole)
    noButton = m.addButton('No', QMessageBox.ButtonRole.NoRole)
    m.setDefaultButton(noButton)
    m.setFont(self.font())
    m.exec_()

    if m.clickedButton() == yesButton:
        return QMessageBox.Yes

    return QMessageBox.No

from .GUI_Main import *
from PyQt5.QtWidgets import QApplication
import sys

# if __name__ == '__main__':
def run():
    app = None
    app = QApplication(sys.argv)
    Window_Main()
    app.exec_()

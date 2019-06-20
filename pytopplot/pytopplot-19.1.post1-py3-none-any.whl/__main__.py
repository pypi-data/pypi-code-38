from sys import argv, exit
from os.path import dirname
from PyQt5 import QtWidgets
from pytopplot.ui.window import MainWindow


def main():
    app = QtWidgets.QApplication(argv)
    window = MainWindow(dirname(__file__))
    exit(app.exec_())

#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "K.I.A.Derouiche"
__author_email__ = "kamel.derouiche@gmail.com"

import sys

from PyQt5.QtWidgets import QApplication
from sumtool.mainwindow import ChecksumMainWindowApp

def main():
    app = QApplication(sys.argv)
    myapp = ChecksumMainWindowApp()
    myapp.show()
    sys.exit(app.exec_())

if  __name__ == '__main__':
    main()

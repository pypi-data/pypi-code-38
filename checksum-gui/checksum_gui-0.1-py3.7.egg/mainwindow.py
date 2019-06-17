#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "K.I.A.Derouiche"
__author_email__ = "kamel.derouiche@gmail.com"


import hashlib

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog

from sumtool.forms.uimain import Ui_Dialog
from sumtool.apropos import AboutApp

class ChecksumMainWindowApp(QDialog, Ui_Dialog):
    def __init__(self, *args, **kwargs):
        super(ChecksumMainWindowApp, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.show()
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(self.openFilechecksum)
        self.aboutButton.clicked.connect(self.aboutApp)
        self.pushButton_2.clicked.connect(self.quitApp)

    @pyqtSlot()
    def openFilechecksum(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file", "", "", options=options)
        if fileName:
            self.getCheckFileSum(fileName)

    @pyqtSlot()
    def getCheckFileSum(self, filname):
        self.lineEdit.setText(str(filname))
        self.lineEdit.setReadOnly(True)

        sumvalue = self.checkFileSum(filname, blocksize=65536)
        self.lineEdit_2.setText(sumvalue)
        self.lineEdit_2.setReadOnly(True)

        self.lineEdit_4.textChanged.connect(self.onChanged)

    @pyqtSlot()
    def checkFileSum(self, filname, blocksize) -> str:
        hash = hashlib.md5()
        with open(filname, 'rb') as f:
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest()

    def onChanged(self, svalue):
        textValue = self.lineEdit_2.text()
        if svalue == textValue:
            self.label_4.setStyleSheet('color: green')
            self.label_4.setText("IDENTICAL")
        else:
            self.label_4.setStyleSheet('color: red')
            self.label_4.setText("Not IDENTICAL")

    @pyqtSlot()
    def aboutApp(self):
        '''
        About for Author, version and short descr
        '''
        self.__about = AboutApp()
        self.__about.show()

    def quitApp(self):
        QApplication.quit()

# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets,QtCore,QtGui
import webbrowser 
import pyperclip

f = open("csgoparse.js", "r")
code = f.read()

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(640,480)
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(10, 70, 400, 400))
        self.textBrowser.setText(code)
        self.textBrowser.setObjectName("textBrowser")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 20, 500, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAccessibleName("")
        self.label.setAccessibleDescription("")
        self.label.setScaledContents(True)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.linkButton = QtWidgets.QPushButton(Form)
        self.linkButton.setGeometry(QtCore.QRect(420, 300, 200, 35))
        self.linkButton.setObjectName("linkButton")
        self.linkButton.clicked.connect(self.link_method)
        self.copyButton = QtWidgets.QPushButton(Form)
        self.copyButton.setGeometry(QtCore.QRect(420, 120, 200, 35))
        self.copyButton.setObjectName("copyButton")
        self.copyButton.clicked.connect(self.copy_method)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Collect Match Data for Computation"))
        self.label.setText(_translate("Form", "Copy the script and run it on the Console(F12 in Chrome) of the following link"))
        self.linkButton.setText(_translate("Form", "Open CSGO Personal Game Data"))
        self.copyButton.setText(_translate("Form","Copy to Clipboard"))
    
    def link_method(self, Form):
        webbrowser.open_new_tab('https://steamcommunity.com/login/home/?goto=%2Fmy%2Fgcpd%2F730%2F%3Ftab%3Dmatchhistorycompetitive')
    
    def copy_method(self, Form):
        pyperclip.copy(code)
        
class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
    
app = QtWidgets.QApplication([])
 
application = mywindow()
 
application.show()
 
sys.exit(app.exec())

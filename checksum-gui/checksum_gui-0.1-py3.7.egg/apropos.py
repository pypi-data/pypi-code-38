#!/usr/bin/env python
#-*- coding: utf-8 -*-


from PyQt5.QtWidgets import QDialog

from sumtool.forms.about import  Ui_Dialog

class AboutApp(QDialog, Ui_Dialog):
    """ """
    def __init__(self):
        super(AboutApp, self).__init__()
        self.setupUi(self)

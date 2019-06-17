#!/usr/bin/env python3
"""
Copyright 2015 Hippos Technical Systems BV.
(but borrows somme code from the painting/svgviewer example of PyQt v4.x)

@author: larry
n.b. text_view.py is defunct... for now! just use normal stdout window! why not?  
"""

from .. import (dbg_print, QtWidgets, WithMenu)

class TextView(QtWidgets.QPlainTextEdit, WithMenu):

    menuTag = '&Text'

    def menuItems(self):
        return [
#                    ('Set &Font', 'F', self.changeMyFont,),
        ]

    def __init__(self):
        dbg_print ("TextView.__init__")
        QtWidgets.QPlainTextEdit.__init__(self)
        WithMenu.__init__(self)

    def showOutput(self, text_bytes):
        self.setPlainText(text_bytes)

    def showAtRowAndCol(self, row, col):
        pass  # for now!

    def locateXY(self, x, y):
        pass  # for now!

# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

import os
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QApplication, QStyle, \
    QTextBrowser, QWidget, QGridLayout, QTextEdit, QCheckBox, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.Qt import QFont, QIcon
from pyIMD.ui.resource_path import resource_path
from pyIMD.__init__ import __version__, __operating_system__

__author__ = 'Andreas P. Cuny'


class QuickInstructions(QWidget):
    """
    Implementation of the quick instructions.
    """

    def __init__(self, parent=None):
        super(QuickInstructions, self).__init__(parent)
        # self.setAttribute(Qt.WA_DeleteOnClose) # Deletes instance on window close
        self.setWindowTitle('pyIMD :: Quick instructions')
        self.display_on_startup = 2
        self.resize(400, 370)
        self.setWindowIcon(QtGui.QIcon(resource_path(os.path.join(os.path.join("ui", "icons",
                                                                               "pyIMD_logo_icon.ico")))))
        grid = QGridLayout()
        grid.setContentsMargins(5, 5, 5, 5)
        ok = QPushButton('Ok')
        ok.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogApplyButton))
        ok.setMaximumWidth(100)
        ok.clicked.connect(self.close)
        self.chk = QCheckBox('Display quick instructions at startup')
        self.chk.setFont(QFont('Arial', 9, QFont.Bold))
        self.chk.setChecked(1)
        self.chk.clicked.connect(self.on_display_qi)

        self.quick_instructions = QTextEdit(self)
        self.quick_instructions.setText('<h3>Quick Instructions</h3> '
                                        'Edit the settings first according to your experimental setup. Second select '
                                        'the directory containing your experimental data and determine the file name '
                                        'to measurement relationship as well as the measurement mode the data was '
                                        'recorded with.'
                                        '<br><br>Controls:'
                                        '<ul>'
                                        '<li><b>Ctrl+N (Cmd+N):</b> Create a new pyIMD project.'
                                        '</li>'
                                        '<li><b>Ctrl+O (Cmd+O):</b> Open an existing pyIMD project'
                                        '</li>'
                                        '<li><b>Ctrl+S (Cmd+S):</b> Save the current pyIMD project'
                                        '</li>'
                                        '<li><b>Ctrl+P (Cmd+P):</b> Open the settings dialog to change the project '
                                        'parameters</li></ul>'
                                        'Hints:'
                                        '<ul><li>Create a pyIMD project for all your experiments first and save '
                                        'the pyIMD projects before running them individually. The projects can then '
                                        'be run sequentially using the batch mode (Batch processing tab).'
                                        '</li>'
                                        '<li>Select multiple data files holding the Ctrl button during selection after'
                                        'clicking on <i>Select directory</i> or Ctrl+N.</li><'
                                        '</ul>'
                                        'You can open this window any time from the Help menu.</ul>')
        self.quick_instructions.setReadOnly(1)
        self.quick_instructions.setFont(QFont('Arial', 9))
        grid.addWidget(self.quick_instructions, 0, 0, 1, 0)
        grid.addWidget(ok, 1, 1)
        grid.addWidget(self.chk, 1, 0)
        self.setLayout(grid)

    def on_display_qi(self):
        self.display_on_startup = self.chk.checkState()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class ChangeLog(QWidget):
    """
    Implementation of the program change log.
    """
    def __init__(self,):
        super(ChangeLog, self).__init__()
        self.setWindowTitle('pyIMD :: What\'s new in pyIMD')
        self.setFixedSize(1100, 500)
        self.setWindowIcon(QtGui.QIcon(resource_path(os.path.join(os.path.join("ui", "icons",
                                                                               "pyIMD_logo_icon.ico")))))
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        h_box = QVBoxLayout()
        v_box = QHBoxLayout()
        grid_h = QGridLayout()
        grid_v = QGridLayout()
        self.change_log_text = QTextBrowser()
        self.cancel_btn = QPushButton('Close', self)
        self.cancel_btn.clicked.connect(self.close_window)

        grid_v.addWidget(self.cancel_btn, 1, 1)
        v_box.addStretch()
        v_box.addLayout(grid_v)
        grid_h.addWidget(self.change_log_text)
        h_box.addLayout(grid_h)
        h_box.addLayout(v_box)
        self.setLayout(h_box)

        change_log = open(resource_path('change_log.txt')).read()
        self.change_log_text.setText(change_log)

    def close_window(self):
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class About(QWidget):
    """
    Implementation of the about dialog.
    """
    def __init__(self,):
        super(About, self).__init__()
        self.setWindowTitle('pyIMD :: About')
        self.setFixedSize(320, 450)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        about_icon = QIcon()
        about_icon.addPixmap(self.style().standardPixmap(QStyle.SP_FileDialogInfoView))
        self.setWindowIcon(about_icon)

        self.le = QLabel()
        self.build = QLabel("[build: v%s %s bit]" % (__version__, __operating_system__))
        self.author = QLabel("pyIMD: Inertial mass determination. \nWritten by Andreas P. Cuny and Gotthold\nFläschner")
        self.license = QLabel("Licensed under the GPL v3 license.")
        self.copyright = QLabel("\u00a9 Copyright  Andreas P. Cuny \n2018-2019. All rights reserved. \
                                \nCSB Laboratory @ ETH Zurich\nMattenstrasse 26 \n4058 Basel Switzerland")
        self.dependencies = QTextBrowser()
        self.dependencies.setHtml("The authors appreciate and use the following 3rd parties libraries: <br> \
                                <br>Python v3.5, under the <a href=https://docs.python.org/3/license.html>PSF License</a> \
                                <br>lxml, under the <a href=https://github.com/lxml/lxml/blob/master/LICENSES.txt>BSD 3-Clause License</a> \
                                <br>numpy v1.14.5, under the <a href=https://docs.scipy.org/doc/numpy-1.10.0/license.html>BSD 3-Clause License</a> \
                                <br>scipy v1.1.0, under the <a href=https://docs.scipy.org/doc/numpy-1.10.0/license.html>BSD 3-Clause License</a> \
                                <br>pandas v0.23.3, under the <a href=https://pandas.pydata.org/pandas-docs/stable/getting_started/overview.html>BSD 3-Clause License</a> \
                                <br>nptdms v0.12.0, under the <a href=https://github.com/adamreeve/npTDMS>GPL v3 License</a> \
                                <br>tqdm v4.23.4, under the <a href=https://github.com/tqdm/tqdm/blob/master/LICENCE>MIT License</a> \
                                <br>plotnine v0.3.0, under the <a href=https://github.com/has2k1/plotnine/blob/master/LICENSE>GPL v2 License</a> \
                                <br>PyQT5, under the <a href=https://www.riverbankcomputing.com/static/Docs/PyQt5/introduction.html#license>GPL v3 License</a> \
                                <br>xmltodict, under the <a href=https://github.com/martinblech/xmltodict/blob/master/LICENSE>MIT License</a> \
                                <br>matplotlib, under the <a href=https://matplotlib.org/devel/license.html>PSF License</a>\
                                <br>pyqtgraph, under the <a href=https://github.com/pyqtgraph/pyqtgraph/blob/develop/LICENSE.txt>MIT License</a>\
                                <br>xmlunittest, under the <a href=https://github.com/Exirel/python-xmlunittest/blob/master/LICENSE>MIT License</a>")
        self.dependencies.setReadOnly(True)
        self.dependencies.setOpenExternalLinks(True)
        self.le.setAlignment(Qt.AlignCenter)
        self.build.setAlignment(Qt.AlignCenter)

        font_b = QtGui.QFont()
        font_b.setPointSize(9)
        self.build.setFont(font_b)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.author.setFont(font)
        self.copyright.setFont(font)
        self.dependencies.setFont(font_b)

        logo = QtGui.QPixmap(resource_path(os.path.join(os.path.join("ui", "icons", "pyIMD_logo.png"))))
        logo = logo.scaled(250, 250, Qt.KeepAspectRatio)
        self.le.setPixmap(logo)

        v_box = QVBoxLayout()
        v_box.addWidget(self.le)
        v_box.addWidget(self.build)
        v_box.addWidget(self.license)
        v_box.addStretch()
        v_box.addWidget(self.author)
        v_box.addStretch()
        v_box.addWidget(self.copyright)
        v_box.addWidget(self.dependencies)
        v_box.addStretch()
        self.setLayout(v_box)

        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

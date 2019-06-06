import os, sys
from PIL import Image
# os.chdir(os.path.expanduser("~")+"/Dropbox/James_Git/PyPi/AgricolAi/AgricolAi/Field_Segmentation")
from .GUI_Input import *
from .GUI_Cropper import *
from .GUI_Kmeaner import *
from .GUI_Anchor import *
from .GUI_Output import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Window_Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
        QWidget {\
            font: 20pt Trebuchet MS
        }
        QGroupBox::title{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        QGroupBox {
            border: 1px solid gray;
            border-radius: 9px;
            margin-top: 0.5em;
        }
        """)
        '''attr'''
        # GUI components
        self.pn_content = QWidget()
        self.pn_main = QWidget()
        self.pn_navi = QWidget()
        self.bt_next = QPushButton()
        self.bt_back = QPushButton()
        self.layout = None
        # image-related
        self.img_raw = None
        self.img_crop = None
        self.img_bin = None
        self.k_center = None
        # info
        self.title = "GRID"
        self.width = 1440
        self.height = 720
        '''initialize UI'''
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setMinimumSize(self.width, self.height)
        '''first input'''
        self.show_input()
        '''set up windows'''
        center = QApplication.desktop().availableGeometry().center()
        rect = self.geometry()
        rect.moveCenter(center)
        self.setGeometry(rect)
    def show_input(self):
        '''input panel'''
        self.pn_main = Panel_Input()
        '''navigation bar'''
        self.assemble_navigation(name_next="Load Files ->", oneSide=True)
        self.bt_next.clicked.connect(lambda: self.show_cropper(isNewImg=True))
        '''finalize'''
        self.assemble_and_show()
    def show_cropper(self, isNewImg=True):
        '''input panel'''
        self.img_raw, self.map = self.pn_main.get_img() if isNewImg else (self.img_raw, self.map)
        self.pn_main = Panel_Cropper(np_img=self.img_raw)
        '''navigation bar'''
        self.assemble_navigation()
        self.bt_back.clicked.connect(self.show_input)
        self.bt_next.clicked.connect(lambda: self.show_kmeaner(isNewImg=True))
        '''finalize'''
        self.assemble_and_show()
    def show_kmeaner(self, isNewImg=True):
        '''input panel'''
        self.img_crop = self.pn_main.get_transformed_img() if isNewImg else self.img_crop
        self.pn_main = Panel_Kmeaner(np_img=self.img_crop)
        '''navigation bar'''
        self.assemble_navigation()
        self.bt_back.clicked.connect(lambda: self.show_cropper(isNewImg=False))
        self.bt_next.clicked.connect(lambda: self.show_anchor(isNewImg=True))
        '''finalize'''
        self.assemble_and_show()
    def show_anchor(self, isNewImg=True):
        '''input panel'''
        self.img_crop, self.img_bin = self.pn_main.get_img() if isNewImg else (self.img_crop, self.img_bin)
        self.pn_main = Panel_Anchor(img=self.img_bin, map=self.map)
        '''navigation bar'''
        self.assemble_navigation()
        self.bt_back.clicked.connect(lambda: self.show_kmeaner(isNewImg=False))
        self.bt_next.clicked.connect(lambda: self.show_output(isNewImg=True))
        '''finalize'''
        self.assemble_and_show()
    def show_output(self, isNewImg=True):
        '''input panel'''
        self.anchors, self.nc, self.nr = self.pn_main.get_anchors() if isNewImg else (self.anchors, self.nc, self.nr)
        # test
        import json
        with open('anchors', 'w') as fout:
            json.dump(self.anchors, fout)
        np.save("img_crop", self.img_crop)
        np.save("img_bin", self.img_bin)
        np.save("map", self.map)
        print("nc:%d"%(self.nc))
        print("nr:%d"%(self.nr))
        # test
        self.pn_main = Panel_Output(img_raw=self.img_crop, img_bin=self.img_bin, map=self.map, nc=self.nc, nr=self.nr, anchors=self.anchors)
        '''navigation bar'''
        self.assemble_navigation(name_next="Finish")
        self.bt_back.clicked.connect(lambda: self.show_anchor(isNewImg=False))
        self.bt_next.clicked.connect(self.finish)
        '''finalize'''
        self.assemble_and_show()
    def finish(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Start another job?")
        msgBox.setWindowTitle("Finish")
        msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes | QMessageBox.Save)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            self.pn_main.output()
            self.show_input()
        elif returnValue == QMessageBox.Save:
            self.pn_main.output()
            self.show_output(isNewImg=False)
    def assemble_navigation(self, name_next="Next ->", name_back="<- Back", oneSide=False):
        self.pn_navi = QWidget()
        self.bt_next = QPushButton(name_next)
        self.bt_back = QPushButton(name_back)
        layout_navi = QHBoxLayout()
        if oneSide:
            layout_navi.addStretch(1)
        else:
            layout_navi.addWidget(self.bt_back)
        layout_navi.addWidget(self.bt_next)
        self.pn_navi.setLayout(layout_navi)
    def assemble_and_show(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pn_main, Qt.AlignCenter)
        self.layout.addWidget(self.pn_navi)
        self.pn_content = QWidget()
        self.pn_content.setLayout(self.layout)
        self.setCentralWidget(self.pn_content)
        self.show()

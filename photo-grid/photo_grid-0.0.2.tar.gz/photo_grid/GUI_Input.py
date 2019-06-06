import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1e+9
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Panel_Input(QWidget):
    def __init__(self):
        super().__init__()
        # QGroupBox{border-radius:px}
        '''attr'''
        # user define
        self.gr_user = QGroupBox("User's Input")
        self.lo_user = QGridLayout()
        self.lb_img = QLabel()
        self.lb_map = QLabel()
        self.fd_img = QLineEdit()
        self.fd_map = QLineEdit()
        self.bt_img = QPushButton()
        self.bt_map = QPushButton()
        # demo
        self.gr_demo = QGroupBox("Demo")
        self.lo_demo = QVBoxLayout()
        self.lb_demo = QLabel("Will use sample files to demo the program")
        # self
        self.layout = QVBoxLayout()
        '''initialize UI'''
        self.initUI()
    def initUI(self):
        '''user'''
        # GUI components
        self.gr_user.setCheckable(True)
        self.gr_user.setChecked(False)
        self.gr_user.clicked.connect(lambda: self.toggle(self.gr_user))
        self.lb_img.setText("Image (.tif, .jpg, .png):")
        self.lb_map.setText("Map (.csv, .txt)(OPTIONAL):")
        font = self.fd_img.font()
        font.setPointSize(25)
        fm = QFontMetrics(font)
        self.fd_img.setFixedHeight(fm.height())
        self.fd_map.setFixedHeight(fm.height())
        self.bt_img.setText("Browse")
        self.bt_img.clicked.connect(self.assign_PathImg)
        self.bt_map.setText("Browse")
        self.bt_map.clicked.connect(self.assign_PathMap)
        # layout
        self.lo_user.addWidget(self.lb_img, 0, 0)
        self.lo_user.addWidget(self.fd_img, 0, 1)
        self.lo_user.addWidget(self.bt_img, 0, 2)
        self.lo_user.addWidget(self.lb_map, 1, 0)
        self.lo_user.addWidget(self.fd_map, 1, 1)
        self.lo_user.addWidget(self.bt_map, 1, 2)
        self.gr_user.setLayout(self.lo_user)
        '''demo'''
        # GUI components
        self.gr_demo.setCheckable(True)
        self.gr_demo.setChecked(True)
        self.gr_demo.clicked.connect(lambda: self.toggle(self.gr_demo))
        # layout
        self.lo_demo.addWidget(self.lb_demo)
        self.gr_demo.setLayout(self.lo_demo)
        '''layout'''
        self.layout.setContentsMargins(400, 50, 400, 50)
        self.layout.addWidget(self.gr_user)
        self.layout.addWidget(self.gr_demo)
        '''finalize'''
        self.setLayout(self.layout)
        self.show()
    def toggle(self, groupbox):
        if (groupbox.title()=="Demo"):
            self.gr_user.setChecked(not self.gr_user.isChecked())
        elif (groupbox.title()!="Demo"):
            self.gr_demo.setChecked(not self.gr_demo.isChecked())
    def assign_PathImg(self):
        fileter = "Images (*.tif *.jpg *.jpeg *.png)"
        path = QFileDialog().getOpenFileName(self, "", "", fileter)[0]
        self.fd_img.setText(path)
    def assign_PathMap(self):
        fileter = "Map (*.csv *.txt)"
        path = QFileDialog().getOpenFileName(self, "", "", fileter)[0]
        self.fd_map.setText(path)
    def get_img(self):
        import pandas as pd
        import cv2
        import io
        import urllib.request
        if self.gr_user.isChecked():
            # user input
            try:
                img = np.array(Image.open(self.fd_img.text())).astype(np.uint8)
            except:
                img = read_tiff(self.fd_img.text())
            try:
                map = pd.read_csv(self.fd_map.text(), header=None)
            except:
                map = None
        else:
            # demo
            # path_map = "http://www.zzlab.net/James_Demo/seg_map.csv"
            # path_img = "http://www.zzlab.net/James_Demo/seg_img.jpg"
            # map = pd.read_csv(path_map, header=None)
            # with urllib.request.urlopen(path_img) as url:
            #     file = io.BytesIO(url.read())
            #     img = np.array(Image.open(file))
            # demo 2
            img = read_jpg("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
            map = pd.read_csv("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus_Solution.csv", header=None)
        return img, map

def read_jpg(filename):
    img = np.array(Image.open(filename)).astype(np.uint8)
    return img
#
def read_tiff(filename, bands=None, xBSize=5000, yBSize=5000):
    '''import'''
    import gdal
    import numpy as np
    from tqdm import tqdm_gui
    '''program'''
    ds = gdal.Open(filename)
    gdal.UseExceptions()
    nrow = ds.RasterYSize
    ncol = ds.RasterXSize
    if bands==None:
        bands = range(ds.RasterCount)
    data = np.zeros((nrow, ncol, len(bands)))
    for b in bands:
        band = ds.GetRasterBand(b+1)
        for i in tqdm_gui(range(0, nrow, yBSize), desc="Channel %d/%d"%(b, len(bands)-1), leave=False):
            if i + yBSize < nrow:
                numRows = yBSize
            else:
                numRows = nrow - i
            for j in range(0, ncol, xBSize):
                if j + xBSize < ncol:
                    numCols = xBSize
                else:
                    numCols = ncol - j
                data[i:(i+numRows), j:(j+numCols), b] = band.ReadAsArray(j, i, numCols, numRows)
    # data = (data - data.min(axis=(0,1)))/(data.max(axis=(0,1))-data.min(axis=(0,1)))
    return data.astype(np.uint8)

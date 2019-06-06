import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .GUI_ClassFun import *

class Panel_Cropper(QGroupBox):
    def __init__(self, np_img):
        super().__init__("Image Correction: Please click on the image to assign four anchors")
        self.setStyleSheet("""
        QGroupBox::title{
            subcontrol-origin: margin;
            subcontrol-position: top center;
        }
        """)
        '''attr'''
        self.layout = QVBoxLayout()
        self.wg_img = Widget_ViewCrop(np_img)
        self.initUI()
    def initUI(self):
        self.layout.addWidget(self.wg_img)
        # self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.show()
    def get_transformed_img(self):
        return self.wg_img.get_transformed_img()

class Widget_ViewCrop(Widget_Img):
    def __init__(self, img):
        super().__init__(img)
        self.setMouseTracking(True)
        self.pos = None
        self.zoom = 1
        self.ratio = 1
        self.marks = []
        self.n_marks = 0
        self.is_fit_width = True
        self.pt_st_img = 0
        self.size_img = 0
        self.imgH, self.imgW = img.shape[0], img.shape[1]
        self.initUI()
    def initUI(self):
        super().make_rgb_img(self.img_vis)
        self.show()
    def paintEvent(self, paint_event):
        painter = QPainter(self)
        super().paintImage(painter)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.white)
        for pos in self.marks:
            draw_cross(pos.x(), pos.y(), painter, 5)
        # coordinate
        if self.pos is not None:
            painter.setFont(QFont("Trebuchet MS",14))
            painter.drawText(self.pos.x()-20, self.pos.y()+20, "(%d, %d)" %(self.pos.x(), self.pos.y()))
        painter.end()
    def mouseMoveEvent(self, event):
        pos = event.pos()
        self.pos = pos
        if self.zoom!=0:
            magnifying_glass(self, pos, area=200, zoom=self.zoom*2)
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.zoom = (self.zoom+1)%3
            self.mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        pt_mouse = event.pos()
        # determine the image boundary
        bd_neg = self.pt_st_img
        if event.button() == Qt.LeftButton:
            if self.is_fit_width:
                pt_1d = pt_mouse.y()
                bd_pos = self.pt_st_img + self.size_img.height()
            else:
                pt_1d = pt_mouse.x()
                bd_pos = self.pt_st_img + self.size_img.width()
            # if the click is in the image
            if (pt_1d >= bd_neg) & (pt_1d <= bd_pos):
                if self.n_marks<4:
                    self.marks.append(pt_mouse)
                    self.n_marks += 1
                else:
                    self.marks = []
                    self.n_marks = 0
            # print('(x:%d, y:%d)' % (pt_mouse.x()*(self.ratio), pt_mouse.y()*(self.ratio)))
            # print("ratio: %.2f" % (self.ratio))
            self.update()
        self.mouseMoveEvent(event)
        self.pos = None
    def get_transformed_img(self):
        if self.is_fit_width:
            self.ratio = (self.imgW)/(self.width())
            pts = [[pt.x()*(self.ratio), (pt.y()-self.pt_st_img)*(self.ratio)] for pt in self.marks]
        else:
            self.ratio = (self.imgH)/(self.height())
            pts = [[(pt.x()-self.pt_st_img)*(self.ratio), pt.y()*(self.ratio)] for pt in self.marks]
        if len(pts)<4:
            pts = [[0, 0], [0, self.imgH], [self.imgW, 0], [self.imgW, self.imgH]]
        return transform_by_cv2(self.img_raw, pts).copy()


def rotate(pts, angle):
    import math
    ptx = np.array([pts[i, 0] for i in range(len(pts))])
    pty = np.array([pts[i, 1] for i in range(len(pts))])
    qx = math.cos(math.radians(angle))*(ptx)-math.sin(math.radians(angle))*(pty)
    qy = math.sin(math.radians(angle))*(ptx)+math.cos(math.radians(angle))*(pty)
    qpts = [[qx[i], qy[i]] for i in range(len(pts))]
    return np.array(qpts)

def transform_by_cv2(img, pts):
    import cv2
    # convert to opencv cpmatitable
    pts = np.array(pts).astype(np.float32)
    # find four corners
    token = True
    while token:
        try:
            order_x = np.argsort([pts[i, 0] for i in range(4)])
            order_y = np.argsort([pts[i, 1] for i in range(4)])
            pt_NW = pts[order_x[:2][np.isin(order_x[:2], order_y[:2])][0]]
            pt_SW = pts[order_x[:2][np.isin(order_x[:2], order_y[2:])][0]]
            pt_NE = pts[order_x[2:][np.isin(order_x[2:], order_y[:2])][0]]
            pt_SE = pts[order_x[2:][np.isin(order_x[2:], order_y[2:])][0]]
            token = False
        except:
            pts = rotate(pts, 15)
    # generate sorted source point
    pts = np.array([pt_NW, pt_NE, pt_SW, pt_SE])
    # estimate output dimension
    img_W = (sum((pt_NE-pt_NW)**2)**(1/2)+sum((pt_SE-pt_SW)**2)**(1/2))/2
    img_H = (sum((pt_SE-pt_NE)**2)**(1/2)+sum((pt_SW-pt_NW)**2)**(1/2))/2
    while (img_W > 1500):
        img_W /= 2
        img_H /= 2
    shape = (int(img_W), int(img_H))
    # generate target point
    pts2 = np.float32([[0,0],[shape[0], 0],[0, shape[1]],[shape[0],shape[1]]])
    # transformation
    M = cv2.getPerspectiveTransform(pts, pts2)
    dst = cv2.warpPerspective(img, M, (shape[0], shape[1]))
    dst = np.array(dst).astype(np.uint8)
    return dst

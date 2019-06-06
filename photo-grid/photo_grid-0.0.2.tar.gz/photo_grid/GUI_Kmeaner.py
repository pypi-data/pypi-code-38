import numpy as np
from .GUI_ClassFun import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Panel_Kmeaner(QWidget):
    def __init__(self, np_img):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.update()
        '''attr'''
        # main/img
        self.layout = QGridLayout()
        # img preview (left)
        self.gr_left = QGroupBox("Corrected Image")
        self.lo_left = QGridLayout()
        self.wg_img = Widget_Kmeans(np_img)
        self.bt_ccw = QPushButton("rotate ccw (Q)")
        self.bt_cw = QPushButton("rorate cw (E)")
        # K mean (right)
        self.gr_pre = QGroupBox("K-means Algo.")
        self.lo_pre = QVBoxLayout()
        self.gr_ch = QGroupBox("Channel")
        self.lo_ch = QGridLayout()
        self.lb_nir = QLabel("NIR")
        self.cb_nir = QComboBox()
        self.lb_red = QLabel("Red")
        self.cb_red = QComboBox()
        self.gr_k = QGroupBox("K = 3")
        self.lo_k = QVBoxLayout()
        self.sl_k = QSlider(Qt.Horizontal)
        # Binarization
        self.gr_bin = QGroupBox("Binarization")
        self.lo_bin = QVBoxLayout()
        self.gr_cut = QGroupBox("Auto cutoff = 1")
        self.lo_cut = QVBoxLayout()
        self.sl_cut = QSlider(Qt.Horizontal)
        self.gr_cusb = QGroupBox("Custom")
        self.lo_cusb = QHBoxLayout()
        self.ck_cusb = []
        for i in range(1, 7):
            checkbox = QCheckBox(str(i))
            checkbox.stateChanged.connect(self.append_cut)
            if i>3:
                checkbox.setEnabled(False)
            self.ck_cusb.extend([checkbox])
        self.ls_bin = [0]
        # Display
        self.gr_dis = QGroupBox("Display")
        self.lo_dis = QHBoxLayout()
        self.rb_bin = QRadioButton("Binary (A)")
        self.rb_rgb = QRadioButton("RGB (S)")
        self.rb_k = QRadioButton("K-Means (D)")
        # refine (right)
        self.gr_pro = QGroupBox("Clusters Refine")
        self.lo_pro = QVBoxLayout()
        self.gr_shad = QGroupBox("De-Shadow = 0")
        self.lo_shad = QVBoxLayout()
        self.sl_shad = QSlider(Qt.Horizontal)
        self.gr_gb = QGroupBox("De-Noise = 0")
        self.lo_gb = QVBoxLayout()
        self.sl_gb = QSlider(Qt.Horizontal)
        '''initialize UI'''
        self.initUI()
    def initUI(self):
        '''img preview (left)'''
        # components
        self.bt_ccw.clicked.connect(self.wg_img.rotate_CCW)
        self.bt_cw.clicked.connect(self.wg_img.rotate_CW)
        # layout
        self.lo_left.addWidget(self.wg_img, 0, 0, 1, 2)
        self.lo_left.addWidget(self.bt_ccw, 1, 0)
        self.lo_left.addWidget(self.bt_cw, 1, 1)
        self.gr_left.setLayout(self.lo_left)
        '''pre keans (right)'''
        # components
        self.sl_k.setMinimum(2)
        self.sl_k.setMaximum(6)
        self.sl_k.setValue(3)
        self.sl_k.setTickInterval(1)
        self.sl_k.setTickPosition(QSlider.TicksBelow)
        self.sl_k.valueChanged.connect(self.change_k)
        for i in range(self.wg_img.imgC):
            self.cb_nir.addItem(str(i))
            self.cb_red.addItem(str(i))
        if self.wg_img.imgC>3:
            self.cb_nir.setCurrentIndex(3)
        else:
            self.cb_nir.setCurrentIndex(1)
        # layout
        self.lo_ch.addWidget(self.lb_nir, 0, 0)
        self.lo_ch.addWidget(self.lb_red, 0, 1)
        self.lo_ch.addWidget(self.cb_nir, 1, 0)
        self.lo_ch.addWidget(self.cb_red, 1, 1)
        self.gr_ch.setLayout(self.lo_ch)
        self.gr_ch.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.lo_k.addWidget(self.sl_k)
        self.gr_k.setLayout(self.lo_k)
        self.lo_pre.addWidget(self.gr_ch)
        self.lo_pre.addWidget(self.gr_k)
        self.gr_pre.setLayout(self.lo_pre)
        '''binarization'''
        # component
        self.gr_cut.setCheckable(True)
        self.gr_cut.setChecked(True)
        self.gr_cut.clicked.connect(lambda: self.toggle(self.gr_cut))
        self.sl_cut.setMinimum(1)
        self.sl_cut.setMaximum(3)
        self.sl_cut.setValue(1)
        self.sl_cut.setTickInterval(1)
        self.sl_cut.setTickPosition(QSlider.TicksBelow)
        self.sl_cut.valueChanged.connect(self.change_cut)
        self.gr_cusb.setCheckable(True)
        self.gr_cusb.setChecked(False)
        self.gr_cusb.clicked.connect(lambda: self.toggle(self.gr_cusb))
        # layout
        self.lo_cut.addWidget(self.sl_cut)
        self.gr_cut.setLayout(self.lo_cut)
        for i in range(6):
            self.lo_cusb.addWidget(self.ck_cusb[i])
        self.gr_cusb.setLayout(self.lo_cusb)
        self.lo_bin.addWidget(self.gr_cut)
        self.lo_bin.addWidget(self.gr_cusb)
        self.gr_bin.setLayout(self.lo_bin)
        '''pro keans (right)'''
        # components
        self.sl_shad.setMinimum(0)
        self.sl_shad.setMaximum(255)
        self.sl_shad.setValue(0)
        self.sl_shad.setTickInterval(20)
        self.sl_shad.setTickPosition(QSlider.TicksBelow)
        self.sl_shad.valueChanged.connect(self.change_shad)
        self.sl_gb.setMinimum(0)
        self.sl_gb.setMaximum(50)
        self.sl_gb.setValue(0)
        self.sl_gb.setTickInterval(5)
        self.sl_gb.setTickPosition(QSlider.TicksBelow)
        self.sl_gb.valueChanged.connect(self.change_gb)
        # layout
        self.lo_shad.addWidget(self.sl_shad)
        self.gr_shad.setLayout(self.lo_shad)
        self.lo_gb.addWidget(self.sl_gb)
        self.gr_gb.setLayout(self.lo_gb)
        self.lo_pro.addWidget(self.gr_shad)
        self.lo_pro.addWidget(self.gr_gb)
        self.gr_pro.setLayout(self.lo_pro)
        '''display'''
        # components
        self.rb_bin.setChecked(True)
        self.rb_bin.toggled.connect(self.wg_img.switch_imgB)
        self.rb_rgb.toggled.connect(self.wg_img.switch_imgVis)
        self.rb_k.toggled.connect(self.wg_img.switch_imgK)
        # layout
        self.lo_dis.addWidget(self.rb_bin)
        self.lo_dis.addWidget(self.rb_rgb)
        self.lo_dis.addWidget(self.rb_k)
        self.gr_dis.setLayout(self.lo_dis)
        '''assemble'''
        policy_right = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy_right.setHorizontalStretch(1)
        self.gr_pre.setSizePolicy(policy_right)
        self.gr_bin.setSizePolicy(policy_right)
        self.gr_dis.setSizePolicy(policy_right)
        self.gr_pro.setSizePolicy(policy_right)
        policy_left = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        policy_left.setHorizontalStretch(3)
        self.gr_left.setSizePolicy(policy_left)
        self.layout.addWidget(self.gr_left, 0, 0, 4, 1)
        self.layout.addWidget(self.gr_pre, 0, 1)
        self.layout.addWidget(self.gr_bin, 1, 1)
        self.layout.addWidget(self.gr_pro, 2, 1)
        self.layout.addWidget(self.gr_dis, 3, 1)
        self.setLayout(self.layout)
        self.do_kmeans()
        self.wg_img.set_binarize([0])
        self.show()
    def toggle(self, groupbox):
        if (groupbox.title()=="Custom"):
            self.gr_cut.setChecked(not self.gr_cut.isChecked())
        else:
            self.gr_cusb.setChecked(not self.gr_cusb.isChecked())
        if self.gr_cusb.isChecked():
            self.append_cut()
        else:
            self.change_cut()
    def change_k(self):
        value = self.sl_k.value()
        self.sl_cut.setMaximum(value)
        self.gr_k.setTitle("K = %d" % value)
        self.do_kmeans()
        if self.gr_cusb.isChecked():
            self.append_cut()
        else:
            self.change_cut()
    def change_cut(self):
        value = self.sl_cut.value()
        self.gr_cut.setTitle("Auto cutoff = %d" % value)
        self.ls_bin = []
        for i in range(6):
            self.ck_cusb[i].setEnabled(False)
            if i<value:
                self.ls_bin.extend([i])
        self.wg_img.set_binarize(list=self.ls_bin)
    def append_cut(self):
        value = self.sl_k.value()
        self.ls_bin = []
        for i in range(6):
            if i<value:
                self.ck_cusb[i].setEnabled(True)
                if self.ck_cusb[i].isChecked():
                    self.ls_bin.extend([i])
            else:
                self.ck_cusb[i].setEnabled(False)
        self.wg_img.set_binarize(list=self.ls_bin)
    def change_shad(self):
        value = self.sl_shad.value()
        self.gr_shad.setTitle("De-Shadow = %d" % value)
        # self.sl_shad.setValue(0)
        self.wg_img.set_deshadow(value=value)
    def change_gb(self):
        value = self.sl_gb.value()
        self.gr_gb.setTitle("De-Noise = %d" % value)
        self.wg_img.set_smooth(value=value)
    def do_kmeans(self):
        # panel launch kmeans
        self.wg_img.do_kmeans(k=self.sl_k.value(), ch_NIR=int(self.cb_nir.currentText()), ch_Red=int(self.cb_red.currentText()))
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.rb_bin.setChecked(True)
        elif event.key() == Qt.Key_S:
            self.rb_rgb.setChecked(True)
        elif event.key() == Qt.Key_D:
            self.rb_k.setChecked(True)
        elif event.key() == Qt.Key_Q:
            self.wg_img.rotate_CCW()
        elif event.key() == Qt.Key_E:
            self.wg_img.rotate_CW()
    def keyReleaseEvent(self, event):
        self.rb_bin.setChecked(True)
    def get_img(self):
        return self.wg_img.getImages()

class Widget_Kmeans(Widget_Img):
    def __init__(self, img):
        super().__init__(img)
        self.setMouseTracking(True)
        self.pos = None
        self.zoom = 1
        self.imgC = img.shape[2]
        self.img_k = None
        self.img_bin, self.img_temp, self.img_bin_sm = None, None, None
        self.nK, self.center = 0, None
        # img process
        self.img_deshad = np.ones((img.shape[0], img.shape[1]))
        self.val_shad, self.val_shad_tp = 0, 0
        self.val_sm, self.val_sm_tp = 0, 0
        self.ls_bin = [0]
        #
        self.initUI()
    def initUI(self):
        self.show()
    def paintEvent(self, paint_event):
        painter = QPainter(self)
        super().paintImage(painter)
        painter.end()
    def do_kmeans(self, k=3, ch_NIR=1, ch_Red=0):
        self.nK = k
        self.img_k, self.center = get_kmeans(self.img_raw, k, ch_NIR, ch_Red)
    def set_binarize(self, list):
        self.ls_bin = np.array(list)
        self.do_process()
    def set_deshadow(self, value=0):
        self.val_shad_tp = value
        self.do_process()
    def set_smooth(self, value=0):
        self.val_sm_tp = value
        self.do_process()
    def do_process(self):
        # binary
        self.do_binarize()
        # smooth
        self.do_smooth()
        # deshadow
        if self.val_shad!=self.val_shad_tp:
            self.val_shad = self.val_shad_tp
            self.do_deshadow()
        self.switch_imgB()
    def do_binarize(self):
        # prop_g = [self.center[i, 0] for i in range(self.center.shape[0])]
        prop_g = [(self.center[i, 1]-self.center[i, 0]) for i in range(self.center.shape[0])]
        # prop_g = [(self.center[i, 0]-self.center[i, 1])/self.center[i, :].sum() for i in range(self.center.shape[0])]
        rank_g = np.flip(np.argsort(prop_g), 0)
        try:
            idx_select = rank_g[self.ls_bin]
        except:
            idx_select = []
        self.img_bin = ((np.isin(self.img_k, idx_select))*1).astype(np.int)
        self.img_bin_sm = self.img_bin.copy()
        self.img_temp = self.img_bin.copy()
        self.val_sm = 0
    def do_deshadow(self):
        img_mean = self.img_raw[:,:,:3].mean(axis=2)
        self.img_deshad = (img_mean >= self.val_shad)*1
    def do_smooth(self):
        '''
        '''
        from scipy.signal import convolve2d
        k_blur = np.array((
            [1, 4, 1],\
            [4, 9, 4],\
            [1, 4, 1]), dtype='int')/29

        nSm_diff = self.val_sm_tp - self.val_sm
        self.val_sm = self.val_sm_tp
        if nSm_diff>0:
            n_really_do = nSm_diff
        elif nSm_diff<0:
            n_really_do = self.val_sm_tp
            self.img_temp = self.img_bin.copy()
        else:
            n_really_do = 0
        # print("really do : %d, cur sm : %d" % (n_really_do, self.nSm))
        for i in range(n_really_do):
            self.img_temp = convolve2d(self.img_temp, k_blur, mode='same')
        self.img_bin_sm[self.img_temp>0.5] = 1
        self.img_bin_sm[self.img_temp<=0.5] = 0
        self.img_bin_sm = self.img_bin_sm.astype(np.int)
    def switch_imgVis(self):
        super().make_rgb_img(self.img_vis)
        self.repaint()
        self.updateMag()
    def switch_imgK(self):
        super().make_idx8_img(self.img_k, self.nK)
        self.repaint()
        self.updateMag()
    def switch_imgB(self):
        img_b = np.multiply(self.img_bin_sm, self.img_deshad)
        super().make_bin_img(img_b)
        self.repaint()
        self.updateMag()
    def rotate_CW(self):
        self.img_raw = np.rot90(self.img_raw, 3).copy()
        self.img_vis = np.rot90(self.img_vis, 3).copy()
        self.img_k = np.rot90(self.img_k, 3).copy()
        self.img_bin = np.rot90(self.img_bin, 3).copy()
        self.img_temp = np.rot90(self.img_temp, 3).copy()
        self.img_bin_sm = np.rot90(self.img_bin_sm, 3).copy()
        self.img_deshad = np.rot90(self.img_deshad, 3).copy()
        self.switch_imgB()
    def rotate_CCW(self):
        self.img_raw = np.rot90(self.img_raw, 1).copy()
        self.img_vis = np.rot90(self.img_vis, 1).copy()
        self.img_k = np.rot90(self.img_k, 1).copy()
        self.img_bin = np.rot90(self.img_bin, 1).copy()
        self.img_temp = np.rot90(self.img_temp, 1).copy()
        self.img_bin_sm = np.rot90(self.img_bin_sm, 1).copy()
        self.img_deshad = np.rot90(self.img_deshad, 1).copy()
        self.switch_imgB()
    def getImages(self):
        self.img_bin_sm = np.multiply(self.img_bin_sm, self.img_deshad).astype(np.uint8)
        return self.img_raw, self.img_bin_sm
    def mouseMoveEvent(self, event):
        self.updateMag()
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.zoom = (self.zoom+1)%3
            self.mouseMoveEvent(event)
    def updateMag(self):
        pos = self.mapFromGlobal(QCursor().pos())
        if self.zoom!=0:
            magnifying_glass(self, pos, area=200, zoom=self.zoom*2)
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

def get_kmeans(img, k=3, ch_NIR=1, ch_Red=0):
    '''
    '''
    import cv2
    # data type conversion for opencv
    # img = img[:,:,[ch_NIR, ch_Red]].copy()
    img_max, img_min = img.max(axis=(0, 1)), img.min(axis=(0, 1))-(1e-8)
    img = (img-img_min)/(img_max-img_min)
    img_z = img.reshape((-1, img.shape[2])).astype(np.float32)
    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 1.0)
    param_k = dict(data=img_z,\
                   K=k,\
                   bestLabels=None,\
                   criteria=criteria,\
                   attempts=30,\
                   flags=cv2.KMEANS_PP_CENTERS)
                   # KMEANS_RANDOM_CENTERS
    _, img_k_temp, center = cv2.kmeans(**param_k)
    # Convert back
    img_k = img_k_temp.astype(np.uint8).reshape((img.shape[0], -1))
    # return
    return img_k, center

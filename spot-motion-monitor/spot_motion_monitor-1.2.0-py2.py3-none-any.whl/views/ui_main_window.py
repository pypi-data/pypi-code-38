# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(962, 685)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_4.setSpacing(2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cameraPlot = CameraPlotWidget(self.centralwidget)
        self.cameraPlot.setMinimumSize(QtCore.QSize(400, 300))
        self.cameraPlot.setObjectName("cameraPlot")
        self.verticalLayout.addWidget(self.cameraPlot)
        self.scatterPlot = CentroidScatterPlotWidget(self.centralwidget)
        self.scatterPlot.setMinimumSize(QtCore.QSize(400, 300))
        self.scatterPlot.setObjectName("scatterPlot")
        self.verticalLayout.addWidget(self.scatterPlot)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.centroidXPlot = Centroid1dPlotWidget(self.centralwidget)
        self.centroidXPlot.setMinimumSize(QtCore.QSize(250, 200))
        self.centroidXPlot.setObjectName("centroidXPlot")
        self.horizontalLayout_2.addWidget(self.centroidXPlot)
        self.centroidYPlot = Centroid1dPlotWidget(self.centralwidget)
        self.centroidYPlot.setMinimumSize(QtCore.QSize(250, 200))
        self.centroidYPlot.setObjectName("centroidYPlot")
        self.horizontalLayout_2.addWidget(self.centroidYPlot)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.psdXPlot = PsdWaterfallPlotWidget(self.centralwidget)
        self.psdXPlot.setMinimumSize(QtCore.QSize(250, 200))
        self.psdXPlot.setObjectName("psdXPlot")
        self.horizontalLayout.addWidget(self.psdXPlot)
        self.psdYPlot = PsdWaterfallPlotWidget(self.centralwidget)
        self.psdYPlot.setMinimumSize(QtCore.QSize(250, 200))
        self.psdYPlot.setObjectName("psdYPlot")
        self.horizontalLayout.addWidget(self.psdYPlot)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cameraControl = CameraControlWidget(self.centralwidget)
        self.cameraControl.setMinimumSize(QtCore.QSize(0, 0))
        self.cameraControl.setStyleSheet("")
        self.cameraControl.setObjectName("cameraControl")
        self.horizontalLayout_3.addWidget(self.cameraControl)
        self.cameraData = CameraDataWidget(self.centralwidget)
        self.cameraData.setMinimumSize(QtCore.QSize(100, 100))
        self.cameraData.setStyleSheet("")
        self.cameraData.setObjectName("cameraData")
        self.horizontalLayout_3.addWidget(self.cameraData)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 962, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuCamera = QtWidgets.QMenu(self.menubar)
        self.menuCamera.setObjectName("menuCamera")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionDummy = QtWidgets.QAction(MainWindow)
        self.actionDummy.setObjectName("actionDummy")
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuCamera.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuCamera.setTitle(_translate("MainWindow", "Camera"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionExit.setToolTip(_translate("MainWindow", "Exit the Program"))
        self.actionExit.setShortcut(_translate("MainWindow", "Meta+Q"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionDummy.setText(_translate("MainWindow", "Dummy"))

from spot_motion_monitor.views.camera_control_widget import CameraControlWidget
from spot_motion_monitor.views.camera_data_widget import CameraDataWidget
from spot_motion_monitor.views.camera_plot_widget import CameraPlotWidget
from spot_motion_monitor.views.centroid_1d_plot_widget import Centroid1dPlotWidget
from spot_motion_monitor.views.centroid_scatter_plot_widget import CentroidScatterPlotWidget
from spot_motion_monitor.views.psd_waterfall_plot_widget import PsdWaterfallPlotWidget

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


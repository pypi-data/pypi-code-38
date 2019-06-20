'''
Created on Apr 17, 2019

@author: reynolds
'''
from wrtdk.io.streamer.serial_streamer import serial_streamer
import sys
from PyQt5.QtWidgets import QApplication,QMainWindow, QPushButton, QGridLayout,QWidget
from PyQt5.QtCore import pyqtSlot
from wrtdk.comms.comms import SerialPort

class test(QMainWindow):
    '''
    classdocs
    '''

    def __init__(self):
        ''' Constructor '''
        QMainWindow.__init__(self)
        
        main = QWidget(self)
        btn = QPushButton('Connect')
        btn.clicked.connect(self._connect)
        log = QPushButton('Log')
        log.clicked.connect(self._log)
        
        l = QGridLayout()
        l.addWidget(btn)
        l.addWidget(log)
        
        main.setLayout(l)
        self.setFocus()
        self.setCentralWidget(main)
        
        self._port = None
        self._thread = None
        
    def _connect(self):
        if self._port is None:
            self._port = SerialPort('COM8',9600)
            self._thread = serial_streamer(self._port)
            self._thread.new_msg.connect(self._new_msg)
            self._thread.start()
        else:
            self._thread.stop()
            self._thread.wait()
            self._thread = None
            self._port = None
    
    def _log(self):
        if self._thread.isRunning():
            if self._thread.isLogging():
                self._thread.stopLog()
            else:
                self._thread.startLog('test.gps','wb')
        
    @pyqtSlot(list,str,int,int)
    def _new_msg(self,data,status,system,sensor):
        print(data,status,system,sensor)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    aw = test()
    aw.show()
    app.exec_()
'''
Created on Feb 14, 2019

@author: reynolds
'''
import sys, os

from PyQt5.QtWidgets import QApplication,QMainWindow, QPushButton, QGridLayout,QWidget
from PyQt5.QtCore import pyqtSlot
from wrtdk.io.streamer.simstreamer import simstreamer
from wrtdk.comms.comms import UDPServerPort

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
            f = r'C:\Users\reynolds\Documents\1704_madunit\data\20190507_gprip\GPRIP_SWXXX.dat'
            print(os.path.exists(f))
            self._port = UDPServerPort('',7654,1)
            self._thread = simstreamer(self._port,
                                       debug=True,
                                       filename=f,
                                       dt=.001)
            self._thread.new_mcu.connect(self._new_mcu)
            self._thread.new_gga.connect(self._new_gga)
            self._thread.new_rmc.connect(self._new_rmc)
            self._thread.new_hdt.connect(self._new_hdt)
            self._thread.new_rmc.connect(self._new_rmc)
            self._thread.new_vhw.connect(self._new_vhw)
            self._thread.new_vtg.connect(self._new_vtg)
            self._thread.new_gprip.connect(self._new_gprip)
            self._thread.new_qmag.connect(self._new_qmag)
            self._thread.new_mfam1.connect(self._new_mfam1)
            self._thread.new_mfam2.connect(self._new_mfam2)
            self._thread.new_vmag.connect(self._new_vmag)
            self._thread.new_imu.connect(self._new_imu)
            self._thread.new_sonar.connect(self._new_sonar)
            self._thread.new_lidar.connect(self._new_lidar)
            self._thread.new_sys.connect(self._new_sys)
            self._thread.new_timeout.connect(self._new_timeout)
            self._thread.new_rtcom_mag.connect(self._new_com_mag)
            self._thread.new_rtdet_mag.connect(self._new_det_mag)
            self._thread.new_rtinv_mag.connect(self._new_inv_mag)
            self._thread.new_rttrk_mag.connect(self._new_trk_mag)
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
                self._thread.startLog('test.dat','wb')
            
        
    @pyqtSlot(list,str,int,int)
    def _new_qmag(self,data,status,system,sensor):
        '''  updates the total field  '''
        print('TF:',data[0],'strength:',data[1],'state:',status,system,sensor)
    
    @pyqtSlot(list,str,int,int)
    def _new_sys(self,data,status,system,sensor):
        ''' updates the system state '''
        print(data,status,system,sensor)
            
    @pyqtSlot(list,str,int,int)
    def _new_gga(self,data,status,system,sensor):
        '''  updates the gga display  '''
        print(data,status,system,sensor)
    
    @pyqtSlot(list,str,int,int)
    def _new_rmc(self,data,status,system,sensor):
        ''' updates the gprmc state '''
        print(data,status,system,sensor)
            
    @pyqtSlot(list,str,int,int)
    def _new_vtg(self,data,status,system,sensor):
        ''' updates the gpvtg state '''
        print(data,status,system,sensor)
            
    @pyqtSlot(list,str,int,int)
    def _new_vhw(self,data,status,system,sensor):
        ''' updates the gpvhw state '''
        print(data,status,system,sensor)
            
    @pyqtSlot(list,str,int,int)
    def _new_hdt(self,data,status,system,sensor):
        ''' updates the gphdt state '''
        print(data,status,system,sensor)
        
    @pyqtSlot(list,str,int,int)
    def _new_gprip(self,data,status,system,sensor):
        print('GPRIP',data,status,system,sensor)
    
    @pyqtSlot(list,str,int,int)
    def _new_mfam1(self,data,status,system,sensor):
        ''' updates the MFAM tf plot and statuses '''
        print('MFAM1',data,status,system,sensor)
    
    @pyqtSlot(list,str,int,int)
    def _new_mfam2(self,data,status,system,sensor):
        ''' updates MFAM2 data '''
        print('MFAM2',data,status,system,sensor)
            
    @pyqtSlot(list,str,int,int)
    def _new_imu(self,data,status,system,sensor):
        ''' updates the IMU readout '''
        print(data,status,system,sensor)
            
    @pyqtSlot(list,str,int,int)
    def _new_vmag(self,data,status,system,sensor):
        ''' updates the vector mag plots '''
        print(data,status,system,sensor)
    
    @pyqtSlot(list,str,int,int)
    def _new_sonar(self,data,status,system,sensor):
        ''' updates the sonar display '''
        print(data,status,system,sensor)
        
    @pyqtSlot(list,str,int,int)
    def _new_lidar(self,data,status,system,sensor):
        ''' updates the lidar display '''
        print('$LIDAR',data,status,system,sensor)
        
    @pyqtSlot(list,str,int,int)
    def _new_com_mag(self,data,status,system,sensor):#tf,status):
        ''' updates the real time compensated value display '''
        print(data,status,system,sensor)
        
    @pyqtSlot(list,str,int,int)
    def _new_det_mag(self,data,status,system,sensor):#flag,strength,status):
        ''' updates the real time detection display '''
        print(data,status,system,sensor)
        
    @pyqtSlot(list,str,int,int)
    def _new_inv_mag(self,data,status,system,sensor):
        ''' updates the real time inversion display '''
        print(data,status,system,sensor)
        
    @pyqtSlot(list,str,int,int)
    def _new_trk_mag(self,data,status,system,sensor):
        ''' updates the track message '''
        print('RTTRK',data,status,system,sensor)
    
    @pyqtSlot(list,str,int,int)
    def _new_mcu(self,data,status,system,sensor):
        ''' updates the mcu time '''
        print(data,status,system,sensor)
    
    @pyqtSlot()
    def _new_timeout(self):
        ''' lets the user know if there is a socket timeout '''
        print('Timeout')
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    aw = test()
    aw.show()
    app.exec_()
    
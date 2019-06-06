'''
Created on Feb 14, 2019

@author: reynolds
'''

import sys, os, time

from PyQt5.QtCore import pyqtSignal

from wrtdk.io.streamer.streamer import LoggingStreamer
from wrtdk.parser.msg.wrtmsg import wrtsys, udp_wrapper, rtinv_mag, rtcom_mag, rtdet_mag,\
    rttrk_mag
from wrtdk.parser.imu.bno055 import bno055
from wrtdk.parser.imu.microstrain import lord3dm_cv5
from wrtdk.parser.tfmag.mfam import mx3g
from wrtdk.parser.tfmag.qmag import qmag
from wrtdk.parser.nmea.nmea import gpgga, gprmc
from wrtdk.parser.alt.hcsr04 import hcsr04
from wrtdk.parser.vmag.pni import pni
from wrtdk.io.sim.sim_simulator import sim_simulator
from wrtdk.parser.alt.lidar_lite_v3 import lidar_lite_v3
from wrtdk.parser.vehicle.gprip import gprip

class simstreamer(LoggingStreamer):
    ''' a class to read read data for the WRT sim board and send data to the ui '''
    
    # pyqtSignal to send data to the gui
    new_gga = pyqtSignal(list,'QString',int,int)
    new_rmc = pyqtSignal(list,'QString',int,int)
    new_vhw = pyqtSignal(list,'QString',int,int)
    new_vtg = pyqtSignal(list,'QString',int,int)
    new_hdt = pyqtSignal(list,'QString',int,int)
    new_gprip = pyqtSignal(list,'QString',int,int)
    new_qmag = pyqtSignal(list,'QString',int,int)
    new_mfam1 = pyqtSignal(list,'QString',int,int)
    new_mfam2 = pyqtSignal(list,'QString',int,int)
    new_vmag = pyqtSignal(list,'QString',int,int)
    new_imu = pyqtSignal(list,'QString',int,int)
    new_sonar = pyqtSignal(list,'QString',int,int)
    new_lidar = pyqtSignal(list,'QString',int,int)
    new_sys = pyqtSignal(list,'QString',int,int)
    new_mcu = pyqtSignal(list,'QString',int,int)
    new_rtcom_mag = pyqtSignal(list,'QString',int,int)
    new_rtdet_mag = pyqtSignal(list,'QString',int,int)
    new_rtinv_mag = pyqtSignal(list,'QString',int,int)
    new_rttrk_mag = pyqtSignal(list,'QString',int,int)
    new_timeout = pyqtSignal()

    def __init__(self,port=None,debug=False,filename=None,dt=0.1):
        ''' Constructor '''
        super().__init__(debug=debug)# inherit super class
        
        # set the port
        self.port = port
        
        # set the parsers
        self.h = udp_wrapper()
        self.systm = wrtsys()
        self.imu = bno055()
        self.imux1 = lord3dm_cv5()
        self.mfamo = mx3g()
        self.qmago = qmag()
        self.gga = gpgga()
        self.rmc = gprmc()
        self.gprip = gprip()
        self.hcsr = hcsr04()
        self.lite_v3 = lidar_lite_v3()
        self.vmag = pni()
        self.rtcommag = rtcom_mag()
        self.rtdetmag = rtdet_mag()
        self.rtinvmag = rtinv_mag()
        self.rttrkmag = rttrk_mag()
        
        # set the simulator
        self.sim = None# initialize
        self.dt = dt# timing
        if self._debug and os.path.join(filename):
            self.sim = sim_simulator()
            # read file
            if not self.sim.read(filename):# handle an improper file read
                self.sim = None# clear simulator
                self._debug = False# exit debug mode if not read properly
        
    def run(self):
        ''' main loop for thread '''
        if not self._debug: self._running = True # set to run if not simulating
        
        # read the port and send signals
        while self._running:
            # read in the message
            try:
                msg,addr = self.port.read(1024)
            except Exception as e:
                exc_type, _, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('%s:%s in %s at %d'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))
                self.new_timeout.emit()
                continue
            
            self._getmsg(msg,addr)
                
        # close the port if not is sim mode
        if not self._debug: self.port.close()
        
        # enter debug mode if the user specifies
        while self._debug:
            # add a simulator that reads a file and send messages based on the file
            msg = self.sim.getNext()
            
            self._getmsg(msg,None)
            time.sleep(self.dt)
            
    def _getmsg(self,msg,addr):
        # check for invalid messages
            if len(msg) < self.h.LENGTH: print('Invalid message received received from',addr,msg)
            
            # write the new unaltered message to the log
            if self.writer.isLogging(): self.writer.write(msg)
            
            # define the position in the buffer
            pos = 0
            
            while pos < len(msg):   
                # parse the first header
                self.h.parse(msg[pos:pos+self.h.LENGTH])
                
                # check to see if the parser has errored and continue if it has
                if self.h.hasErrored():
                    print('Error reading header:',self.h.hasErrored())
                    break# this message is corrupt, wait for the next
                
                # parse the message
                self.parse(self.h,msg[self.h.getMsgStart(pos):self.h.getMsgEnd(pos)])
                
                # increment pos
                pos += self.h.getMsgEnd()
        
    def parse(self,h,msg):
        ''' parses the incoming message '''
        
        msg_type = h.getType()
        if not msg_type.startswith('$RT'):# send if it's not realtime message
            self.new_mcu.emit([h.getTimestamp(),h.getMCU()],
                              h.getStatus(),
                              h.getSystemID(),
                              h.getSensorID())
        
        if msg_type.startswith('$GPGGA'):# deprecated
            # parse the gpgga message and send it to te UI thread
            self.gga.parse(msg.decode().strip())
            if not self.gga.hasErrored():
                self.new_gga.emit(self.gga.getData(),
                                    h.getStatus(),
                                    h.getSystemID(),
                                    h.getSensorID())
        elif msg_type.startswith('$GPRMC'):# deprecated
            # send the status to the UI
            self.rmc.parse(msg.decode().strip())
            if not self.rmc.hasErrored():
                self.new_rmc.emit(self.rmc.getData(),
                                  h.getStatus(),
                                  h.getSystemID(),
                                  h.getSensorID())
        elif msg_type.startswith('$GPVHW'):# deprecated
            # send the status to the UI
            self.new_vhw.emit([msg.decode().strip()],
                              h.getStatus(),
                              h.getSystemID(),
                              h.getSensorID())
        elif msg_type.startswith('$GPHDT'):# deprecated
            # send the status to the UI
            self.new_hdt.emit([msg.decode().strip()],
                              h.getStatus(),
                              h.getSystemID(),
                              h.getSensorID())
        elif msg_type.startswith('$GPVTG'):# deprecated
            # send the status to the UI
            self.new_vtg.emit([msg.decode().strip()],
                              h.getStatus(),
                              h.getSystemID(),
                              h.getSensorID())
        elif msg_type.startswith('$GPS'):
            if msg.decode().startswith('$GPGGA'):
                # parse the gpgga message and send it to te UI thread
                self.gga.parse(msg.decode().strip())
                if not self.gga.hasErrored():
                    self.new_gga.emit(self.gga.getData(),
                                      h.getStatus(),
                                      h.getSystemID(),
                                      h.getSensorID())
            elif msg.decode().startswith('$GPRMC'):
                self.rmc.parse(msg.decode().strip())
                if not self.rmc.hasErrored():
                    self.new_rmc.emit(self.rmc.getData(),
                                      h.getStatus(),
                                      h.getSystemID(),
                                      h.getSensorID())
            elif msg.decode().startswith('$GPVHW'):
                self.new_vhw.emit([msg.decode().strip()],
                                  h.getStatus(),
                                  h.getSystemID(),
                                  h.getSensorID())
            elif msg.decode().startswith('$GPHDT'):
                self.new_hdt.emit([msg.decode().strip()],
                                  h.getStatus(),
                                  h.getSystemID(),
                                  h.getSensorID())
            elif msg.decode().startswith('$GPVTG'):
                self.new_vtg.emit([msg.decode().strip()],
                                  h.getStatus(),
                                  h.getSystemID(),
                                  h.getSensorID())
        elif msg_type.startswith('$GPRIP'):
            # parse and send the gprip message along
            self.gprip.parse(msg)
            if not self.gprip.hasErrored():
                self.new_gprip.emit(self.gprip.getData(),
                                    h.getStatus(),
                                    h.getSystemID(),
                                    h.getSensorID())
        elif msg_type.startswith('$TFMAG'):
            # parse the qmag message and send it to the UI thread
            self.qmago.parse(msg)
            if not self.qmago.hasErrored():
                _tf,_strength = self.qmago.getData()
                        
                # send every message to the UI
                for i in range(len(_tf)):
                    self.new_qmag.emit([_tf[i],_strength[i]],
                                       h.getStatus(),
                                       h.getSystemID(),
                                       h.getSensorID())
        elif msg_type.startswith("$MFAM1"):
            # parse the mfam message and send it to the UI thread
            self.mfamo.parse(msg)                
            if not self.mfamo.hasErrored():
                self.new_mfam1.emit(self.mfamo.getData(),
                                    h.getStatus(),
                                    h.getSystemID(),
                                    h.getSensorID())
        elif msg_type.startswith("$MFAM2"):
            # parse the mfam message and send it to the UI thread
            self.mfamo.parse(msg)
            if not self.mfamo.hasErrored():
                self.new_mfam2.emit(self.mfamo.getData(),
                                    h.getStatus(),
                                    h.getSystemID(),
                                    h.getSensorID())
        elif msg_type.startswith('$VCMAG'):
            # parse the vector mag message and send it to the UI thread
            self.vmag.parse(msg)
            if not self.vmag.hasErrored():
                self.new_vmag.emit(self.vmag.getData(),
                                   h.getStatus(),
                                   h.getSystemID(),
                                   h.getSensorID())
        elif msg_type.startswith('$IMUXX'):
            # parse the imu message and send it to the UI thread
            self.imu.parse(msg)
            if not self.imu.hasErrored():
                self.new_imu.emit(self.imu.getData(),
                                  h.getStatus(),
                                  h.getSystemID(),
                                  h.getSensorID())
        elif msg_type.startswith('$IMUX1'):
            # parse the imu message and send it to the UI thread
            self.imux1.parse(msg)
            if not self.imux1.hasErrored():
                self.new_imu.emit(self.imux1.getData(),
                                  h.getStatus(),
                                  h.getSystemID(),
                                  h.getSensorID())
        elif msg_type.startswith('$SONAR'):
            # parse the sonar message and send to the UI thread
            self.hcsr.parse(msg)
            if not self.hcsr.hasErrored():
                self.new_sonar.emit(self.hcsr.getData(),
                                    h.getStatus(),
                                    h.getSystemID(),
                                    h.getSensorID())
        elif msg_type.startswith('$LIDAR'):
            self.lite_v3.parse(msg)
            if not self.lite_v3.hasErrored():
                self.new_lidar.emit(self.lite_v3.getData(),
                                      h.getStatus(),
                                      h.getSystemID(),
                                      h.getSensorID())
        elif msg_type.startswith('$RTCOM'):
            # parse the real time compensation method
            self.rtcommag.parse(msg)
            if not self.rtcommag.hasErrored():
                self.new_rtcom_mag.emit(self.rtcommag.getData(),
                                        h.getStatus(),
                                        h.getSystemID(),
                                        h.getSensorID())
        elif msg_type.startswith('$RTDET'):
            # parse the real time detection method
            self.rtdetmag.parse(msg)
            if not self.rtdetmag.hasErrored():
                self.new_rtdet_mag.emit(self.rtdetmag.getData(),
                                        h.getStatus(),
                                        h.getSystemID(),
                                        h.getSensorID())
        elif msg_type.startswith('$RTINV'):
            # parse the real time inversion method
            self.rtinvmag.parse(msg)
            if not self.rtinvmag.hasErrored():
                self.new_rtinv_mag.emit(self.rtinvmag.getData(),
                                        h.getStatus(),
                                        h.getSystemID(),
                                        h.getSensorID())
        elif (msg_type.startswith('$RTTRK') or 
              msg_type.startswith('$SWIDL') or 
              msg_type.startswith('$SWHUN') or
              msg_type.startswith('$SWSTP') or
              msg_type.startswith('$SWCOR') or 
              msg_type.startswith('$SWDUN') or 
              msg_type.startswith('$SWABT')):
            
            # send the ui the type of message received
            if msg_type.startswith('$RTTRK'): sen = 0
            elif msg_type.startswith('$SWABT'): sen = 1
            elif msg_type.startswith('$SWIDL'): sen = 2
            elif msg_type.startswith('$SWHUN'): sen = 3
            elif msg_type.startswith('$SWSTP'): sen = 4 
            elif msg_type.startswith('$SWCOR'): sen = 5
            elif msg_type.startswith('$SWDUN'): sen = 6
            else: sen = -1
            # parse the real time track message
            self.rttrkmag.parse(msg)
            if not self.rttrkmag.hasErrored():
                self.new_rttrk_mag.emit(self.rttrkmag.getData(),
                                        h.getStatus(),
                                        h.getSystemID(),
                                        sen)
        elif msg_type.startswith('$SYSTM'):
            # parse the system message and send it to the UI thread
            self.systm.parse(msg)    
            if not self.systm.hasErrored():
                self.new_sys.emit(self.systm.getData(),
                                  h.getStatus(),
                                  h.getSystemID(),
                                  h.getSensorID())
        else: print('UnknownMessageType:%s %s'% (msg_type,msg))
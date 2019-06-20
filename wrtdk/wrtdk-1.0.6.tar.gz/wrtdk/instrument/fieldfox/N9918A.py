'''
Created on Oct 16, 2018

@author: reynolds
'''
import time, os
import numpy as np

from wrtdk.instrument.instrument import instrument

class N9918A(instrument):
    '''
    classdocs
    '''
    _ifft = 4096

    def __init__(self, params):
        ''' Constructor '''
        super().__init__(params)
        
        self._open = False
        self.verb = self._params['verb']
        self.dstr = ''
        self.trace = 0
        self.data = np.array([])
        
        print('Attempting to connect to the Field Fox at',self._params['addr'],'...',end=' ')
        self._device = self._rm.open_resource('TCPIP0::%s::inst0::INSTR' % self._params['addr'])
        self._wait()
        
        self._device.chunk_size = self._params['chunk_size']
        self._device.timeout = self._params['timeout']
        self._device.write_termination = '\r\n'
        self._device.read_termination = '\n'
        self._device.write('*CLS')
        if self.verb: print('')# add a space
        if self.verb: print('*IDN:',self._device.query("*IDN?").strip())
        if self.verb: print('chunk_size: %d' % self._device.chunk_size)
        if self.verb: print('timeout: %d ms' % self._device.timeout)
        if self.verb: print('read_termination: %s' % repr(self._device.read_termination))
        if self.verb: print('write_termination: %s' % repr(self._device.write_termination))
        if self.verb: print('send_end: %r' % self._device.send_end)
        if self.verb: print('query_delay: %d s' % self._device.query_delay)
        print('Done\n')
        
        self._hdrlist = []
        self._hdr = ''
        
        print('Configuring the Field Fox ... ')
        while True:
            try:
                # begin configuration
                self._device.write('INST:SEL "NA"')# set the network analyzer mode
                self._wait()#time.sleep(5)# sleep to allow the program to load
                self._hdrlist.append('SEL: %s' %self._device.query('INST:SEL?').strip())
                self._wait()
                
                # set the sweep settings
                self._device.write('FREQ:STAR %f' % self._params['fstart'])
                self._device.write('FREQ:STOP %f' % self._params['fstop'])
                self._device.write('BWID %f' % self._params['bwid'])
                self._device.write('FREQ:CENT %f' % self._params['fcen'])
                self._device.write('FREQ:SPAN %f' % self._params['fspn'])
                self._device.write('SWE:POIN %d' % self._params['np'])
                self._device.write('SOUR:POW:ALC MAN')
                self._device.write('SOUR:POW %.1f' % self._params['spwr'])
                self._device.write('CALC:TRAN:TIME:STAT %s' % self._params['trans'])
                
                # get the transform information
                if self._params['trans'] is 'OFF':# frequency domain
                    self.x_units = 'Hz'
                    self.start = float(self._device.query('FREQ:STAR?'))
                    self.stop = float(self._device.query('FREQ:STOP?'))
                else:# time domain
                    self.start = float(self._device.query('CALCulate:TRANsform:TIME:STARt?')) # get f start and stop
                    self.stop = float(self._device.query('CALC:TRANsform:TIME:STOP?'))
                    self.x_units = 's'
                
                # print the x axis settings to the user
                self._hdrlist.append('BWID: %s Hz' % self._device.query('BWID?').strip())
                self._hdrlist.append('FREQ:STAR: %s Hz' % self._device.query('FREQ:STAR?').strip())
                self._hdrlist.append('FREQ:STAR: %s Hz' % self._device.query('FREQ:STAR?').strip())
                self._hdrlist.append('FREQ:STOP %s Hz' % self._device.query('FREQ:STOP?').strip())
                self._hdrlist.append('FREQ:SPAN %s Hz' % self._device.query('FREQ:SPAN?').strip())
                self._hdrlist.append('FREQ:CENT %s Hz' % self._device.query('FREQ:CENT?').strip())
                self._hdrlist.append('SWE:TIME %s s' % self._device.query('SWE:TIME?').strip())
                self._hdrlist.append('FREQ:MTIM %s s' % self._device.query('SWE:MTIM?').strip())
                self._hdrlist.append('SOUR:POW %s dBm' % self._device.query('SOUR:POW?').strip())
                self._hdrlist.append('SOUR:POW:ALC %s' % self._device.query('SOUR:POW:ALC?').strip())
                self._hdrlist.append('TRANSFORM: % s' % self._device.query('CALC:TRAN:TIME:STAT?').strip())
                self._hdrlist.append('AVER:MODE %s' % self._device.query('AVER:MODE?').strip())
                self._hdrlist.append('AVER:COUN %s' % self._device.query('AVER:COUN?').strip())
                self._hdrlist.append('CALC:SMO %s' % self._device.query('CALC:SMO?').strip())
                self._hdrlist.append('CALC:SMO:APER %s' % self._device.query('CALC:SMO:APER?').strip())
                self._hdrlist.append('SWE:POIN %s' % self._device.query('SWE:POIN?').strip())
                self._hdrlist.append('CALC:TRAN:TIME:STAR %s s' % self._device.query('CALCulate:TRANsform:TIME:STARt?'))
                self._hdrlist.append('CALC:TRAN:TIME:STOP %s s' % self._device.query('CALC:TRANsform:TIME:STOP?'))
                self.n = float(self._device.query('SENS:SWE:POIN?'))# tell the user the number of points
                self.axis = np.linspace(self.start,self.stop,self.n)# set the x vector
                self.dx = np.mean(np.diff(self.axis))
                self.time = np.linspace(0,1.0/self.dx,self._ifft)
                self.xdata = np.concatenate((np.array([np.NaN,np.NaN]),self.axis)).reshape((int(self.n)+2,1))
                self.window = np.hanning(200)
                
                # setup the display
                self._device.write('CALC:FORM %s' % self._params['form'])
                self._hdrlist.append('CALC:FORM: %s' % self._device.query('CALC:FORM?').strip())
                self._device.write('DISP:WIND:TRACe1:Y:AUTO')# set the plot to autoscale
                
                # setup the transmission type
                self._device.write('CALC:PAR1:DEF S12')# set the measurement parameter
                self._hdrlist.append('TX: %s' % self._device.query('CALC:PAR:DEF?').strip())
                self._device.write('CALC:PAR1:SEL')# set the active trace
                self._device.write('FORM %s' % self._params['dform'])# REAL,64 for binary
                self._hdrlist.append('FORM: %s' % self._device.query('FORM?').strip())
                
                # set trigger
                self._hdrlist.append('CONT: %s' % self._device.query('INIT:CONT?').strip())
                self._device.write('INIT:CONT 0')# set non-continuous
                self._hdrlist.append('AVER: %s' % self._device.query('AVER:COUNt?').strip())
                
                # create the header and print if verbose
                for i in self._hdrlist: self._hdr += i + '\n'
                if self.verb: print(self._hdr,end='')
                
                # wait for everything and clear the buffer
                self._wait()
                self._clear()
                self._open = True
            except Exception as e:
                print('Error.',str(e))
                # reopen the device
                self.reopen_inst()
                #time.sleep(0.5)
            else:
                break
            
        self._open = True
        print('Setup complete.\n')
        
    def isOpen(self):
        ''' returns whether the port is open '''
        return self._open
        
    def measure(self):
        ''' measures the current data '''
        instrument.measure(self)
        
        try:
            self._clear()# clear the buffer
                            # get the data from the instrument
            if self.verb: print('Starting measurement ... ',end='')
            self._device.write('INIT:IMMediate')# trigger a measurement
            self._wait()
                
            if self.verb: print('ascan%d ... ' % self.trace,end=' ')
            
            #self._device.write('MMEMory:STORe:FDATa "ascan.csv"')
            if self._params['dform'] == "REAL,64":
                self._device.write('CALC:DATA:SDATa?')
                self.dstr = self._device.read_bytes(int(self.n)*2*8+7)
                data = np.frombuffer(self.dstr[6:-1]).reshape((int(self.n),2))
            elif self._params['dform'] == 'REAL,32':
                self._device.write('CALC:DATA:SDATa?')
                self.dstr = self._device.read_bytes(int(self.n)*2*4+7)
                data = np.frombuffer(self.dstr[6:-1],dtype=np.float32).reshape((int(self.n),2))
            else:
                self.dstr = self._device.query('CALC:DATA:SDATa?')
                data = np.fromstring(self.dstr,sep=',').reshape((int(self.n),2))
                
            self.data = np.vstack((np.array([np.NaN,np.NaN,np.NaN,np.NaN]).reshape(2,2),data))
            #self.data = np.column_stack((self.data,dout))
            if self.verb: print('Done')
                
            self.trace = self.trace + 1
                
            return True
        except Exception as e:
            print('Error.',str(e))
            #self.reopen_inst()
            #time.sleep(0.5)
            return False
        
    def getData(self):
        ''' returns the data 
        0) x data
        1) trace data 
        2) number of samples
        3) time in seconds
        4) ascan
        '''
        # process the ascan
        a = self.data[2:,0] + 1j*self.data[2:,1]
        ww = np.ones((int(self.n)))
        ww[0:100] = self.window[0:100]
        ascan = np.fft.ifft(ww*a,self._ifft)# taken from MATLAB
        return [self.axis,self.data[2:,:],int(self.n),self.time,ascan]
        
    def write(self, fn='',odir='',d=np.nan,t=np.nan):
        ''' writes a measurement to a file '''
        instrument.write(self, fn=fn)
        
        # insert filename if it does not exist
        if fn == '': fn = r'bscan.csv'
        
        # set the directory path
        odir = os.path.join(os.getcwd(),odir)
        if not os.path.exists(odir): os.mkdir(odir)
        fn = os.path.join(odir,fn)
        
        # write the data
        print('Writing %s ... ' % fn,end='')
        try:
            self.data[0][0] = t
            self.data[0][1] = t
            self.data[1][0] = d
            self.data[1][1] = d
            
            # append to the file
            f = open(fn,'a')
            np.savetxt(f,self.data.T,delimiter=',')
            os.chmod(fn,0o666)# don't know what this does
            f.close()
            print('Done')
        except Exception as e:
            print('Error',str(e))
            
    def header(self, fn='',odir=''):
        ''' writes the header '''
        
        # set the directory path
        odir = os.path.join(os.getcwd(),odir)
        if not os.path.exists(odir): os.mkdir(odir)
        fn = os.path.join(odir,fn)
        
        # write header to file
        try:
            print('Writing %s header ... ' % fn,end='')
            f = open(fn,'a')
            f.write(self._hdr)
            np.savetxt(f,self.xdata.T,delimiter=',')
            os.chmod(fn,0o666)# don't know what this does
            f.close()
            self.resetTrace()
            print('Done')
        except Exception as e:
            print('Error',str(e))
            
    def resetTrace(self):
        self.trace = 0
            
    def _clear(self):
        ''' clears the buffer '''
        try:
            self._device.write('*CLS')
        except:
            return
            
    def _wait(self):
        ''' waits for the fieldfox to finish '''
        try:
            return self._device.query('*OPC?').strip()
        except:
            return 'Error'
            
    def reopen_inst(self):
        ''' reopens the instance of the instrument '''
        while True:
            try:
                self._device = self._rm.open_resource('TCPIP0::%s::inst0::INSTR' % self._params['addr'])
            except:
                print('resource busy?')
                print('DEBUG:','')
                self._device.close()
                time.sleep(1)
            else:
                self._open = False
                break
        
    def oppar(self,par):
        ''' checks the parameters in '''
        instrument.oppar(self,par)
        if ('timeout' not in par): par['timeout'] = None
        if ('verb' not in par): par['verb'] = False
        if ('py' not in par): par['py'] = True
        if ('np' not in par): par['np'] = 801
        if ('addr' not in par): par['addr'] = '169.254.10.100'
        if ('trans' not in par): par['trans'] = 'ON'
        if ('form' not in par): par['form'] = 'REAL'
        if ('chunk_size' not in par): par['chunk_size'] = 102400
        if ('fstart' not in par): par['fstart'] = 30e3
        if ('fstop' not in par): par['fstop'] = 12e9
        if ('bwid' not in par): par['bwid'] = 10e3
        if ('fcen' not in par): par['fcen'] = 6000015000
        if ('fspn' not in par): par['fspn'] = 11999970000
        if ('spwr' not in par): par['spwr'] = -2
        
    def close(self):
        ''' closes the device '''
        print('Closing connection to %s ... ' % self._params['addr'],end='')
        self._device.close()
        self._rm.close()
        self._open = False
        print('Done')
        
if __name__ == '__main__':
    print('Starting fieldfox comms')
    par = dict(py=True,
               verb=True,
               addr='128.128.204.202',
               trans='OFF',
               form='POL',
               timeout=2000,
               chunk_size=102400,
               dform='REAL,64',
               np=401,
               spwr=-2)
    fn = 'test6.csv'
    odir='20180102_gpr'
    ff = N9918A(par)
    ff.header(fn=fn,odir=odir)
    for _ in range(1):#190 will do down and back on the gantry
        if ff.measure():
            ff.write(fn=fn,odir=odir,d=np.NaN,t=time.time())
    
    ff.close()
    print('Shutting down')
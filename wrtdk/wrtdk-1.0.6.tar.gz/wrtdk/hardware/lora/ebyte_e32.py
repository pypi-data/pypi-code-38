'''
Created on Mar 22, 2019

@author: reynolds
'''

import struct
from wrtdk.comms.comms import SerialPort

class e32_ebyte_lora(object):
    '''
    A class for interacting with the ebyte E32 long range radios
    '''

    def __init__(self,port=None):
        '''
        Constructor.
        
        port: Serial port information
        '''
        self.port = port
        
    def get_parameters(self):
        '''
        returns the current operation parameters as a byte array
        '''
        msg = struct.pack('BBB',193,193,193)
        port.write(msg)
        param,_ = port.readLine()
        for p in param: print(p,end=' ')
        print()
        return param
    
    def get_version(self):
        '''
        returns the present version number as a byte array
        '''
        msg = struct.pack('BBB',195,195,195)
        port.write(msg)
        param,_ = port.readLine()
        return param
    
    def reconfigure(self,head=192,addh=0,addl=0,sped=26,chan=15,option=68):
        '''
        head=194 -- > don't save settings on power down
        sped=34: --> ttl uart: 19200
        '''
        msg = struct.pack('BBBBBB',head,addh,addl,sped,chan,option)
        for m in msg: print(m,end=' ')
        print()
        print('reconfig:',msg)
        self.port.write(msg)
    
    def reset(self):
        '''
        resets the radio to its initial settings
        '''
        msg = struct.pack('BBB',196,196,196)
        port.write(msg)
        param,_ = port.readLine()
        return param
        
if __name__ == '__main__':
    port = SerialPort('COM12',9600)
    lora = e32_ebyte_lora(port)
    print('parameters:',lora.get_parameters())
    print('version:',lora.get_version())
    lora.reconfigure(head=192,sped=34)
    port.close()
        
'''
Created on Feb 20, 2019

@author: reynolds
'''
from wrtdk.io.sim.simulator import simulator
from wrtdk.parser.msg.wrtmsg import udp_wrapper

class sim_simulator(simulator):
    ''' classdocs '''

    def __init__(self):
        ''' Constructor '''
        super().__init__()    
        
    def read(self,filename,filt=None):
        simulator.read(self, filename)
        
        if not self.didError():
            # initialize the message parser and variable to store the bytes
            h = udp_wrapper()
            b = None
            pos = 0
            
            # open the file
            with open(filename,'rb') as f:
                b = f.read()# read in the bytes
                blen = len(b)# get the length of the buffer
                
                while pos < blen:
                    h.parse(b[pos:pos+h.LENGTH])
                    if h.hasErrored():
                        pos += 1
                        print('Error reading header:',h.hasErrored())
                        continue
                    
                    if filt is not None:
                        if h.getType().startswith(filt):
                            self._msgs.append(b[pos:h.getMsgEnd(pos)])
                        pos += h.getMsgEnd()
                    else:
                        self._msgs.append(b[pos:h.getMsgEnd(pos)])
                        pos += h.getMsgEnd()
                
            if b is not None:
                print('Done')
                self._len = len(self._msgs)
                return True
            else:
                print('Error')
                return False
        return False
            
    def writeNext(self,addr='128.128.204.201',port=7654):
        ''' writes the message to the udp port '''
        self._port.write(self.getNext(),addr,port)
        
def test():
    ''' tests the simulator '''
    s = sim_simulator()
    s.read(r'C:\Users\reynolds\Documents\1704_madunit\data\20190227_imu-vmag_compare\imu_vcmag_test_1.dat')
    
    while s.hasNext():
        print(s.current(),'/',s.length(),s.getNext())
    
if __name__ == '__main__':
    test()
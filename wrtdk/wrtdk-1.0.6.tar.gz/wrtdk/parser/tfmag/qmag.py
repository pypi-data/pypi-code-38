'''
Created on Aug 17, 2018

@author: reynolds
'''
from wrtdk.parser.parser import parser
from wrtdk.data.buffer.buffer import searcher
import os, sys
from wrtdk.parser.msg.wrtmsg import udp_wrapper

class qmag(parser):
    ''' parser for the qmag madunit messages '''
    
    def __init__(self):
        ''' constructor '''
        super().__init__()# inherit superclass
        self.reset()# initlaize properties
        # define constants
        self.COUNT_2_NT = 1/6009.342147
        
    def reset(self):
        ''' resets the data fields '''
        self._tf = []#self._nan()
        self._strength = []#-1
        
    def parse(self,msg):
        ''' parses a bytes array '''
        self.reset()
        
        try:
            string = msg.decode()
            string = string.split('@')
            
            # insert -1 if no strength found
            if len(string) < 2: string.insert(1,'-1')
                           
            self._tf.append(int(string[0][1:].rstrip('\x00'))*self.COUNT_2_NT)
            self._strength.append(int(string[1].rstrip('\x00')))
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data 
        0) list of total field in nT
        1) list of signal strength '''
        return self._tf,self._strength

class qmagasciibinary(qmag):
    ''' a parser for the nuwc qmag messages '''

    def __init__(self):
        ''' Constructor '''
        super().__init__()# inherit superclass
        self.reset()# initialize properties
        
        # define searcher for !
        self.search = searcher(b'!',w=0)
        
    def reset(self):
        ''' resets the properties '''
        self._tf = []
        self._strength = []
        
    def parse(self,msg):
        ''' parses John-Mikes stupid mixed ascii binary 
        with no delimiters message type '''
        self.reset()
        
        try:
            l = self.search.search(msg)
            l.append(len(msg))#mlen)
            
            # process indices
            d = [j-i for i, j in zip(l[:-1], l[1:])]# find the difference
            dd = [ j for (i,j) in zip(d,range(len(d))) if i <= 8 ]# find all differences too small
            d = [e for i,e in enumerate(l) if i not in dd]# remove any small differences
            
            for i in range(len(d)-1):
                string = msg[d[i]:d[i+1]-9].decode()
                string = string.split('@')
                
                # insert -1 if no strength found
                if len(string) < 2: string.insert(1,'-1')
                                
                self._tf.append(int(string[0][1:])*self.COUNT_2_NT)
                self._strength.append(int(string[1].strip()))
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
def test_qmagfile():
    q = qmag()
    filename = r'C:\Users\reynolds\Documents\1704_madunit\data\20180523_tethers\pre-deckcheckstatic_2018_05_23_1041.dat'
    msg = get_msg(filename)
    print('msg:%s' % msg)
    q.parse(msg)
    print(q.getData())
    
def test_qmagasciibinary():
    q = qmagasciibinary()
    filename = r'C:\Users\reynolds\Documents\1711_nuwc\data\20180732_deckcheck\20180731_deckcheckS01.dat'
    msg = get_msg(filename)
    print('msg:%s' % msg)
    q.parse(msg)
    print(q.getData())
    
def get_msg(filename):
    with open(filename,'rb') as f:
        idlen = 6
        msg = f.read(idlen)
        pos = 6
        
        while msg != b'$TFMAG' and pos < 1000:
            msg = msg[1::] + f.read(1)
            pos = pos + 1
            
        wrapper = udp_wrapper()
            
        msg = msg + f.read(36-6)
        pos = pos + 36 - 6
        wrapper.parse(msg)
        
        payload = f.read(wrapper.getLength())
        pos = pos + 1
        return payload
            
if __name__ == '__main__':
    test_qmagfile()
    print()
    test_qmagasciibinary()
    
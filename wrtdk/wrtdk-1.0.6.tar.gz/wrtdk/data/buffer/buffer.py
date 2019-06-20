'''
Created on Aug 17, 2018

@author: reynolds
'''

import numpy as np

class searcher(object):
    '''
    A class for searching a bytes buffer for a specific bytes
    '''
    
    def __init__(self,mid='!',w=1):
        ''' Constructor '''
        self.setID(mid)
        self.setMessageWidth(w)
        
    def search(self,buffer=b''):
        ''' searches the buffer for the byte id with the given width '''
        locs = []
        pos = 0
        
        # search the entire buffer
        while True:
            val = buffer.find(self._id,pos)
            
            # check to make sure the byte is there
            if val > -1:
                pos = val + 1
                if not locs:
                    # the list is empty
                    locs.append(val)
                else:
                    # list is not empty so check the message width
                    if val - locs[-1] > self._width:
                        locs.append(val)
            else:
                # if the value is negative then break. there are no more messages
                break
            
        return locs
        
    def setID(self,mid = '!'):
        ''' sets the id to look for '''
        self._id = mid
        
    def setMessageWidth(self,w=1):
        ''' sets the message width '''
        self._width = w

class data_buffer(object):
    ''' a class for buffering data for plotting or anaysis '''
    
    def __init__(self,ch=1,length=100,window=15,time=10):
        ''' constructor '''
        self._n = ch
        self._len = length
        self._time = time
        self.clear()
        self._window = window
        
    def clear(self):
        '''  clears the buffer  '''
        self.data = self._init_data(self._len,self._n)# clear the data variable
        self.x = self._init_x(self._len,self._time)#clear the x variable
        self._counter = [0] * self._n# intialize the counter
        
    def _init_data(self,m,n):
        ''' initializes the data array '''
        data = []
        for _ in range(n):
            d = np.empty([m])
            d[:] = np.NaN
            data.append(d)
        return data
    
    def _init_x(self,m,t):
        ''' initializes the x data '''
        return np.linspace(0,t,m)
    
    def append(self,col=0,d=0):
        ''' appends data to the buffer'''
        self.data[col][0:-1] = self.data[col][1:]
        self.data[col][-1] = d
        self._counter[col] += 1
        
    def doUdpate(self,col=0):
        ''' tells the user when to update the plot '''
        if self._counter[col] > self._window:
            self._counter[col] = 0
            return True
        else: return False
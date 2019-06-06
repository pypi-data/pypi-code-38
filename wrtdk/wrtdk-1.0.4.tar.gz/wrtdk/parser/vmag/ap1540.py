'''
Created on Aug 17, 2018

@author: reynolds
'''

class ap1540(object):
    ''' a parser for the ap150 fluxgate '''

    def __init__(self):
        ''' Constructor '''
        super().__init__()
        
        # initialzie properties
        self.reset()
        
        # define constants
        self.COUNT_2_NT = 1000/75
        
    def reset(self):
        ''' resets the properties '''
        self._bx = self._nan()
        self._by = self._nan()
        self._bx = self._nan()
        
    def parse(self,msg):
        ''' parses the ap1540 message '''
        print(msg)
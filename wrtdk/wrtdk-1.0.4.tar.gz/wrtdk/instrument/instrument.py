'''
Created on Oct 16, 2018

@author: reynolds
'''

import visa

class instrument(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self._params = params.copy()
        self.oppar(self._params)
        
        self._rm = visa.ResourceManager('@py')
        
    def oppar(self,par):
        pass
    
    def measure(self):
        pass
    
    def write(self,fn=''):
        pass
    
    def isOpen(self):
        return False
    
    
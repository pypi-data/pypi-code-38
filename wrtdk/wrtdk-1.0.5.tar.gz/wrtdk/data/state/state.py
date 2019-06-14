'''
Created on Aug 17, 2018

@author: reynolds
'''

class state(object):
    '''
    a class for representing the state. It alerts the user if the
    state changes
    '''
    
    def __init__(self):
        ''' constructor '''
        self.reset()
             
    def isDifferent(self,val=-1):
        ''' checks to see if the current value is different 
        and updates if the value is different
        '''
        if self._curr != val:
            self._curr = val
            return True
        return False
    
    def reset(self):
        self._curr = []
    
class updater(object):
    '''
    controls when to udpate sensor data based on a number of update samples
    '''
    
    def __init__(self,update=10):
        ''' constructor '''
        self.reset()
        self._update = update
        
    def update(self):
        ''' calculates whether to update or not '''
        self._n += 1
        if self._n > self._update:
            self.reset()
            return True
        return False
        
    def reset(self):
        self._n = 1
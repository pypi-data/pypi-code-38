'''
Created on Nov 30, 2018

@author: reynolds
'''

import numpy as np

class BuoyantObject(object):
    '''
    classdocs
    '''


    def __init__(self,density=1,volume=0,infill=1):
        '''
        Constructor
        '''
        
        if infill > 1: infill = 1
        if infill < 0: infill = 0
        
        self._d = density
        self._v = volume * infill
        self._w = self._d * self._v
        
    def add(self,weight=0):
        if type(weight) == type(self): self._w + weight.getWeight()
        else: self._w += weight
        
    def getWeight(self):
        return self._w
        
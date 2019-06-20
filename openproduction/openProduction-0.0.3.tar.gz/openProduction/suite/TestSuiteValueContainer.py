# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:41:59 2019

@author: Markus
"""
from openProduction.common.Types import String, Float, Bool, BaseType, Date

class TestSuiteValues:
    
    def __init__(self):
        self._entries = []
        self.addValue(String("OPEN_PRODUCTION_VERSION", "Version string of open prodcution"))
        self.addValue(String("DEVICE_UUID", "Global Unique ID of DUT"))
        self.addValue(Date("DATE", "Run date of device"))
        self.addValue(String("VERSION", "Version string of testsuite"))
        self.addValue(Float("DURATION", "Duration of test run in seconds"))
        self.addValue(Bool("SUCCESS", "True if product run was successful in this station"))
    
    def addValue(self, value, errorOnExist=True):
        if isinstance(value, BaseType) == False:
            raise RuntimeError("value has to be a subclass of openProduction.common.Types.BaseType")
        
        exists = False
        
        for e in self._entries:
            if e.name == value.name:
                exists = True
            
        if exists and errorOnExist:
            raise RuntimeError("value %s already exists"%value.name)
            
        if exists == False:
            setattr(self, value.name, value)
            self._entries.append(value)
        
    def addValueContainer(self, container):
        if isinstance(container, TestSuiteValues) == False:
            raise RuntimeError("container has to be a subclass of openProduction.suite.TestSuiteValueContainer.TestSuiteValues")
            
        for val in container:
            self.addValue(val, errorOnExist=False)
    
    def getNames(self):
        names = []
        for e in self._entries:
            names.append(e.name)
        return names
    
    def getValue(self, name):
        for e in self._entries:
            if e.name == name:
                return e.getValue()
            
        raise RuntimeError("value %s not found"%name)
    
    def setValue(self, name, value):
        for e in self._entries:
            if e.name == name:
                e.setValue(value)
                return
            
        raise RuntimeError("value %s not found"%name)
    
    def clear(self):
        for val in self._entries:
            val.clear()
    
    def __setattr__(self, name, value):
        try:
            for e in self._entries:
                if e.name == name:
                    e.setValue(value)
                    return
        except:
            pass
        
        self.__dict__[name] = value
    
    def __len__(self):
        return len(self._entries)
        
    def __iter__(self):
        self.idx = 0
        return self
        
    def __next__(self):
        if self.idx >= len(self._entries):
            raise StopIteration
        else:
            self.idx += 1
            return self._entries[self.idx-1]
        
    def __str__(self):
        maxName = len("Name")
        maxValue = len("Value")
        
        for e in self._entries:
            maxName = max(maxName, len(e.name))
            maxValue = max(maxValue, len(str(e.value)))
            
        colName = maxName+2
        colVal = maxValue+2
        
        myStr = ""
        myStr += ("+"+"-"*colName + "+" + "-"*colVal + "+") + "\n"
        myStr += ("| Name " + " "*(colName-6) + "| Value " + " "*(colVal-7) + "|") + "\n"
        myStr += ("+"+"="*colName + "+" + "="*colVal + "+") + "\n"
        
        for e in self._entries:
            myStr += ("| " + e.name + " "*(colName-len(e.name)-1) + "| " +
                      str(e.value) +" "*(colVal-len(str(e.value))-1) + "|" ) + "\n"
            myStr += ("+"+"-"*colName + "+" + "-"*colVal + "+") + "\n"
        return myStr
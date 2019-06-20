""" Simple example of digital output

    This example outputs the values of data on line 0 to 7
"""

import numpy
import PyDAQmx
from enum import Enum
import nidaqmx.system

class IOType(Enum):
    DIGITAL_OUT = 0
    DIGITAL_IN = 1
    ANALOG_OUT = 2
    ANALOG_IN = 3
    ANALOG_IN_DIFFERENTIAL = 4
        
class NI6001:
    _MAX_SAMP_READ_SIZE = 2047
    
    def __init__(self):
        system = nidaqmx.system.System.local()
        self.device = system.devices[0].name
        print ("using device %s"%self.device)
        self.task = {}
        
    def setDevice(self, device):
        self.device = device
        
    def getDevice(self):
        return self.device
        
    def reset(self):
        PyDAQmx.DAQmxResetDevice(self.device)
        
    def configPin(self, port, cfg, minVal = 0, maxVal = 3):
        self.task[port] = PyDAQmx.Task()
        if cfg == IOType.DIGITAL_OUT:
            self.task[port].CreateDOChan("/%s/%s"%(self.device, port),"",PyDAQmx.DAQmx_Val_ChanForAllLines)
        elif cfg == IOType.ANALOG_IN:
            self.task[port].CreateAIVoltageChan("/%s/%s"%(self.device, port),"", PyDAQmx.DAQmx_Val_RSE, minVal, maxVal, PyDAQmx.DAQmx_Val_Volts, None)
        elif cfg == IOType.ANALOG_IN_DIFFERENTIAL:
            self.task[port].CreateAIVoltageChan("/%s/%s"%(self.device, port),"", PyDAQmx.DAQmx_Val_Diff, minVal, maxVal, PyDAQmx.DAQmx_Val_Volts, None)
        elif cfg == IOType.DIGITAL_IN:
            self.task[port].CreateDIChan("/%s/%s"%(self.device, port),"",PyDAQmx.DAQmx_Val_ChanForAllLines)
        elif cfg == IOType.ANALOG_OUT:    
            self.task[port].CreateAOVoltageChan("/%s/%s"%(self.device, port), "", minVal, maxVal, PyDAQmx.DAQmx_Val_Volts, None)

    def setOutput(self, port, val):
        data = numpy.array([val], dtype=numpy.uint8)
        self.task[port].StartTask()
        try:
            self.task[port].WriteDigitalLines(1,1,10.0,PyDAQmx.DAQmx_Val_GroupByChannel,data,None,None)
        finally:
            self.task[port].StopTask()
            
    def setAnalogOutput(self, port, val):
        self.task[port].StartTask()
        try:
            self.task[port].WriteAnalogScalarF64(1, 10.0, val, None)
        finally:
            self.task[port].StopTask()
        
    def getAnalogIn(self, port, numSamples = 1):
        read = PyDAQmx.int32()
        data = numpy.zeros((numSamples,), dtype=numpy.float64)
        self.task[port].StartTask()
        samples_left = numSamples
        while samples_left != 0:
            
            samples_to_read = min(samples_left, self._MAX_SAMP_READ_SIZE)
            off = numSamples - samples_left
            self.task[port].ReadAnalogF64(samples_to_read,10.0,PyDAQmx.DAQmx_Val_GroupByChannel,data[off:],samples_to_read, PyDAQmx.byref(read),None)
            samples_left -= samples_to_read
        self.task[port].StopTask()
        return data
    
    def getDigitalIn(self, port, numSamples = 1):
        self.task[port].StartTask()
        read = PyDAQmx.int32()
        numS = PyDAQmx.int32()
        data = numpy.zeros((numSamples,), dtype=numpy.uint8)
        try:
            self.task[port].ReadDigitalLines(numSamples,10.0,PyDAQmx.DAQmx_Val_GroupByChannel,data,numSamples, PyDAQmx.byref(read), PyDAQmx.byref(numS),None)
        finally:
            self.task[port].StopTask()
        return data
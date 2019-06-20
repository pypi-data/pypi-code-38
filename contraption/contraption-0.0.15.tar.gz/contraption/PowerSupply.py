#Legacy import (dont touch)
from .Keithley import PowerSupplyFactory,Keithley2657a,Keithley2400
#End of legacy imports

"""
This is an abstract class to explain what all oscilloscopes should do.
Use this to program your code, then it will support all oscilloscopes.
"""
from abc import ABCMeta, abstractmethod
from .Instrument import Instrument

class PowerSupply(Instrument):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getCurrent(self):
        """Returns current in amps"""
        
    @abstractmethod
    def getVoltage(self):
        """Returns voltage in volts"""
        
    @abstractmethod
    def setCurrent(self):
        """
         - Channel
         - Amplitude in amps
         - Compliance in volts
        """

    @abstractmethod
    def setVoltage(self):
        """
         - Channel
         - Amplitude in volts
         - Compliance in amps
        """


            
    

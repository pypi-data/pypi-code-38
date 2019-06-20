"""
This is an abstract class to explain what all oscilloscopes should do.
Use this to program your code, then it will support all oscilloscopes.
"""
from abc import ABCMeta, abstractmethod
from .Instrument import Instrument
class Oscilloscope(Instrument):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getWaveform():
        """Should return the waveform in either binary or ascii"""

    @abstractmethod
    def setTrigger():
        """
        The trigger requires a few parameters.
         - Channel
         - Threshold (level to trigger in A or V)
         - Side (rising side, or falling side)
         - Mode (single, many, contiuous, stop)
        """
            
    

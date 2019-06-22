from enum import Enum
from openProduction.common import Signals

class ProgressResult(Enum):
    INIT = 0
    SUCCESS = 1
    ERROR = 2
    UPDATE = 3

class ProgressHandler:
           
    def __init__(self):
        self.newProgress  = Signals.Signal()
        
    def reportProgress(self, idx, numSteps, description, result):
        self.newProgress.emit(idx, numSteps, description, result)
    
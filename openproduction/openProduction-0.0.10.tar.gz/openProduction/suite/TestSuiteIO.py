from enum import Enum
from openProduction.common import Signals
import os
import winsound



class IOAnswer(Enum):
    YES = 0
    NO = 1
    CANCEL = 2
    TIMEOUT = 3

class BaseIOHandler:
    def __init__(self):
        self.signalMessage = Signals.Signal()

    def queryYesNo(self, title, msg, timeout=10):
        return IOAnswer.CANCEL

    def message(self, msg, timeout=10):
        self.signalMessage.emit(msg)
        
    @staticmethod
    def playNotify():
        myPath = os.path.split(os.path.abspath(__file__))[0]
        soundPath = os.path.abspath(os.path.join(myPath, "../UI/qml/sound/notify.wav"))
        try:
            winsound.PlaySound(soundPath, winsound.SND_FILENAME)
        except:
            pass
        
    @staticmethod
    def playError():
        myPath = os.path.split(os.path.abspath(__file__))[0]
        soundPath = os.path.abspath(os.path.join(myPath, "../UI/qml/sound/error.wav"))
        try:
            winsound.PlaySound(soundPath, winsound.SND_FILENAME)
        except:
            pass
        
    @staticmethod
    def playSuccess():
        myPath = os.path.split(os.path.abspath(__file__))[0]
        soundPath = os.path.abspath(os.path.join(myPath, "../UI/qml/sound/success.wav"))
        try:
            winsound.PlaySound(soundPath, winsound.SND_FILENAME)
        except:
            pass               

class IOMessage:
    def __init__(self, msg):
        self.msg = msg

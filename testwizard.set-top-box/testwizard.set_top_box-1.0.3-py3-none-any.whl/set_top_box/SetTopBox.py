import json
import time
import urllib
import sys

from testwizard.testobjects_core import TestObjectBase

#Remote control commands
from testwizard.commands_remotecontrol import SendRCKeyCommand

#Power control commands
from testwizard.commands_powerswitch import GetPowerSwitchStatusCommand
from testwizard.commands_powerswitch import SwitchPowerCommand
from testwizard.commands_powerswitch import SwitchPowerOffCommand
from testwizard.commands_powerswitch import SwitchPowerOnCommand

#Audio commands
from testwizard.commands_audio import WaitForAudioCommand
from testwizard.commands_audio import WaitForAudioPeakCommand

#Video commands
from testwizard.commands_video import CaptureReferenceBitmapCommand
from testwizard.commands_video import CompareCommand
from testwizard.commands_video import CountLastPatternMatchesCommand
from testwizard.commands_video import DeleteAllRecordingsCommand
from testwizard.commands_video import DeleteAllSnapshotsCommand
from testwizard.commands_video import DetectMotionCommand
from testwizard.commands_video import DetectNoMotionCommand
from testwizard.commands_video import FilterBlackWhiteCommand
from testwizard.commands_video import FilterCBICommand
from testwizard.commands_video import FilterColorBlackWhiteCommand
from testwizard.commands_video import FilterGrayscaleCommand
from testwizard.commands_video import FilterInvertCommand
from testwizard.commands_video import FindAllPatternLocationsCommand
from testwizard.commands_video import FindAllPatternLocationsExCommand
from testwizard.commands_video import FindPatternCommand
from testwizard.commands_video import FindPatternExCommand
from testwizard.commands_video import GetVideoFormatCommand
from testwizard.commands_video import GetVideoResolutionCommand
from testwizard.commands_video import LoadReferenceBitmapCommand
from testwizard.commands_video import SaveReferenceBitmapCommand
from testwizard.commands_video import SaveRegionCommand
from testwizard.commands_video import SetRegionCommand
from testwizard.commands_video import SnapShotBMPCommand
from testwizard.commands_video import SnapShotJPGCommand
from testwizard.commands_video import StartBackgroundCaptureCommand
from testwizard.commands_video import StartRecordingCommand
from testwizard.commands_video import StopBackgroundCaptureCommand
from testwizard.commands_video import StopRecordingCommand
from testwizard.commands_video import TextOCRCommand
from testwizard.commands_video import WaitForColorCommand
from testwizard.commands_video import WaitForColorNoMatchCommand
from testwizard.commands_video import WaitForPatternCommand
from testwizard.commands_video import WaitForPatternNoMatchCommand
from testwizard.commands_video import WaitForSampleCommand
from testwizard.commands_video import WaitForSampleNoMatchCommand

class SetTopBox(TestObjectBase):
    def __init__(self, session, name):
        TestObjectBase.__init__(self, session, name, "WEB")

    #Remote Control Commands
    def sendRCKey(self, keyName):
        self.checkIsDisposed()
        return SendRCKeyCommand(self.session, self.name).execute(keyName)

    #Power control commands
    def switchPower(self, on):
        self.checkIsDisposed()
        return SwitchPowerCommand(self.session, self.name).execute(on)
    def switchPowerOff(self):
        self.checkIsDisposed()
        return SwitchPowerOffCommand(self.session, self.name).execute()
    def switchPowerOn(self):
        self.checkIsDisposed()
        return SwitchPowerOnCommand(self.session, self.name).execute()
    def getPowerSwitchStatus(self):
        self.checkIsDisposed()
        return GetPowerSwitchStatusCommand(self.session, self.name).execute()

    #Audio Commands
    def waitForAudio(self, level, timeout):
        self.checkIsDisposed()
        return WaitForAudioCommand(self.session, self.name).execute(level, timeout)
    
    def waitForAudioPeak(self, level, timeout):
        self.checkIsDisposed()
        return WaitForAudioPeakCommand(self.session, self.name).execute(level, timeout)

    #Video Commands
    def captureReferenceBitmap(self):
        self.checkIsDisposed()
        return CaptureReferenceBitmapCommand(self.session, self.name).execute()
    def getVideoFormat(self):
        self.checkIsDisposed()
        return GetVideoFormatCommand(self.session, self.name).execute()
    def getVideoResolution(self):
        self.checkIsDisposed()
        return GetVideoResolutionCommand(self.session, self.name).execute()
    def compare(self, x, y, width, height, filename, tolerance):
        self.checkIsDisposed()
        return CompareCommand(self.session, self.name).execute(x, y, width, height, filename, tolerance)
    def countLastPatternMatches(self, similarity):
        self.checkIsDisposed()
        return CountLastPatternMatchesCommand(self.session, self.name).execute(similarity)
    def filterBlackWhite(self, separation):
        self.checkIsDisposed()
        return FilterBlackWhiteCommand(self.session, self.name).execute(separation)
    def filterCBI(self, contrast, brightness, intensity):
        self.checkIsDisposed()
        return FilterCBICommand(self.session, self.name).execute(contrast, brightness, intensity)
    def filterColorBlackWhite(self, color, tolerance):
        self.checkIsDisposed()
        return FilterColorBlackWhiteCommand(self.session, self.name).execute(color, tolerance)
    def filterGrayscale(self, levels):
        self.checkIsDisposed()
        return FilterGrayscaleCommand(self.session, self.name).execute(levels)
    def filterInvert(self):
        self.checkIsDisposed()
        return FilterInvertCommand(self.session, self.name).execute()
    def findAllPatternLocations(self, filename, mode, similarity):
        self.checkIsDisposed()
        return FindAllPatternLocationsCommand(self.session, self.name).execute(filename, mode, similarity)
    def findAllPatternLocationsEx(self, filename, mode, similarity, x, y, width, height):
        self.checkIsDisposed()
        return FindAllPatternLocationsExCommand(self.session, self.name).execute(filename, mode, similarity, x, y, width, height)
    def findPattern(self, filename, mode):
        self.checkIsDisposed()
        return FindPatternCommand(self.session, self.name).execute(filename, mode)
    def findPatternEx(self, filename, mode, x, y, width, height):
        self.checkIsDisposed()
        return FindPatternExCommand(self.session, self.name).execute(filename, mode, x, y, width, height)
    def setRegion(self, x, y, width, height):
        self.checkIsDisposed()
        return SetRegionCommand(self.session, self.name).execute(x, y, width, height)
    def textOCR(self, characterSet, dictionary):
        self.checkIsDisposed()
        return TextOCRCommand(self.session, self.name).execute(characterSet, dictionary)
    def deleteAllRecordings(self):
        self.checkIsDisposed()
        return DeleteAllRecordingsCommand(self.session, self.name).execute()
    def deleteAllSnapshots(self):
        self.checkIsDisposed()
        return DeleteAllSnapshotsCommand(self.session, self.name).execute()
    def detectMotion(self, x, y, width, height, minDifference, timeout, motionDuration = None, tolerance = None, distanceMethod = None, minDistance = None):
        self.checkIsDisposed()
        return DetectMotionCommand(self.session, self.name).execute(x, y, width, height, minDifference, timeout, motionDuration, distanceMethod, minDistance)
    def detectNoMotion(self, x, y, width, height, minDifference, timeout, motionDuration = None, tolerance = None, distanceMethod = None, minDistance = None):
        self.checkIsDisposed()
        return DetectNoMotionCommand(self.session, self.name).execute(x, y, width, height, minDifference, timeout, motionDuration, distanceMethod, minDistance)
    def loadReferenceBitmap(self, filename):
        self.checkIsDisposed()
        return LoadReferenceBitmapCommand(self.session, self.name).execute(filename)
    def saveReferenceBitmap(self, filename):
        self.checkIsDisposed()
        return SaveReferenceBitmapCommand(self.session, self.name).execute(filename) 
    def saveRegion(self, filename):
        self.checkIsDisposed()
        return SaveRegionCommand(self.session, self.name).execute(filename)
    def snapShotBMP(self, filename):
        self.checkIsDisposed()
        return SnapShotBMPCommand(self.session, self.name).execute(filename)
    def snapShotJPG(self, filename, quality):
        self.checkIsDisposed()
        return SnapShotJPGCommand(self.session, self.name).execute(filename, quality)
    def startBackGroundCapture(self, stepSize, captures):
        self.checkIsDisposed()
        return StartBackgroundCaptureCommand(self.session, self.name).execute(stepSize, captures)
    def startRecording(self, filename):
        self.checkIsDisposed()
        return StartRecordingCommand(self.session, self.name).execute(filename)
    def stopBackGroundCapture(self):
        self.checkIsDisposed()
        return StopBackgroundCaptureCommand(self.session, self.name).execute()
    def stopRecording(self):
        self.checkIsDisposed()
        return StopRecordingCommand(self.session, self.name).execute()
    def waitForColor(self, x, y, width, height, refColor, tolerance, minSimilarity, timeout):
        self.checkIsDisposed()
        return WaitForColorCommand(self.session, self.name).execute(x, y, width, height, refColor, tolerance, minSimilarity, timeout)
    def waitForColorNoMatch(self, x, y, width, height, refColor, tolerance, minSimilarity, timeout):
        self.checkIsDisposed()
        return WaitForColorNoMatchCommand(self.session, self.name).execute(x, y, width, height, refColor, tolerance, minSimilarity, timeout)
    def waitForPattern(self, filename, minSimilarity, timeout, mode, x, y, width, height):
        self.checkIsDisposed()
        return WaitForPatternCommand(self.session, self.name).execute(filename, minSimilarity, timeout, mode, x, y, width, height)
    def waitForPatternNoMatch(self, filename, minSimilarity, timeout, mode, x, y, width, height):
        self.checkIsDisposed()
        return WaitForPatternNoMatchCommand(self.session, self.name).execute(filename, minSimilarity, timeout, mode, x, y, width, height)
    def waitForSample(self, x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod = None, maxDistance = None):
        self.checkIsDisposed()
        return WaitForSampleCommand(self.session, self.name).execute(x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod, maxDistance)
    def waitForSampleNoMatch(self, x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod = None, maxDistance = None):
        self.checkIsDisposed()
        return WaitForSampleNoMatchCommand(self.session, self.name).execute(x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod, maxDistance)

    def checkIsDisposed(self):
        if(self.disposed):
            raise Exception("Cannot access a disposed object.")

    def dispose(self):
        self.disposed = True
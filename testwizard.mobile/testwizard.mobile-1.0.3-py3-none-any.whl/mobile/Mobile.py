import json
import time
import urllib
import sys

from testwizard.testobjects_core import TestObjectBase

#Mobile commands
from testwizard.commands_mobile import InitDriverCommand
from testwizard.commands_mobile import QuitDriverCommand
from testwizard.commands_mobile import AddCapabilityCommand
from testwizard.commands_mobile import Android_SendKeyCodeCommand
from testwizard.commands_mobile import ClickElementCommand
from testwizard.commands_mobile import ClickPositionCommand
from testwizard.commands_mobile import FindElementCommand
from testwizard.commands_mobile import GetElementAttributeCommand
from testwizard.commands_mobile import GetElementLocationCommand
from testwizard.commands_mobile import GetElementSizeCommand
from testwizard.commands_mobile import GetOrientationCommand
from testwizard.commands_mobile import GetScreenSizeCommand
from testwizard.commands_mobile import GetSourceCommand
from testwizard.commands_mobile import HideKeyboardCommand
from testwizard.commands_mobile import InputTextCommand
from testwizard.commands_mobile import LaunchAppCommand
from testwizard.commands_mobile import MultiTouch_AddCommand
from testwizard.commands_mobile import MultiTouch_NewCommand
from testwizard.commands_mobile import MultiTouch_PerformCommand
from testwizard.commands_mobile import PinchCoordinatesCommand
from testwizard.commands_mobile import PinchElementCommand
from testwizard.commands_mobile import ResetAppCommand
from testwizard.commands_mobile import RunAppInBackgroundCommand
from testwizard.commands_mobile import ScreenshotBMPCommand
from testwizard.commands_mobile import ScreenShotJPGCommand
from testwizard.commands_mobile import SetOrientationCommand
from testwizard.commands_mobile import StartDeviceLoggingCommand
from testwizard.commands_mobile import StopDeviceLoggingCommand
from testwizard.commands_mobile import SwipeCommand
from testwizard.commands_mobile import SwipeArcCommand
from testwizard.commands_mobile import TouchAction_MoveToCommand
from testwizard.commands_mobile import TouchAction_MoveToElementCommand
from testwizard.commands_mobile import TouchAction_NewCommand
from testwizard.commands_mobile import TouchAction_PerformCommand
from testwizard.commands_mobile import TouchAction_PressCommand
from testwizard.commands_mobile import TouchAction_PressElementCommand
from testwizard.commands_mobile import TouchAction_ReleaseCommand
from testwizard.commands_mobile import TouchAction_TapCommand
from testwizard.commands_mobile import TouchAction_WaitCommand
from testwizard.commands_mobile import WaitForElementCommand
from testwizard.commands_mobile import ZoomCoordinatesCommand
from testwizard.commands_mobile import ZoomElementCommand

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

class Mobile(TestObjectBase):
    def __init__(self, session, name):
        TestObjectBase.__init__(self, session, name, "MOBILE")

    #Mobile commands
    def initDriver(self, appPath = None):
        self.checkIsDisposed()
        return InitDriverCommand(self.session,self.name).execute(appPath)
    def quitDriver(self):
        self.checkIsDisposed()
        return QuitDriverCommand(self.session,self.name).execute()
    def addCapability(self, name, value):
        self.checkIsDisposed()
        return AddCapabilityCommand(self.session, self.name).execute(name, value)
    def android_SendKeyCode(self, keyCode):
        self.checkIsDisposed()
        return Android_SendKeyCodeCommand(self.session, self.name).execute(keyCode)
    def clickElement(self, selector):
        self.checkIsDisposed()
        return ClickElementCommand(self.session, self.name).execute(selector) 
    def clickPosition(self, x, y):
        self.checkIsDisposed()
        return ClickPositionCommand(self.session, self.name).execute(x, y) 
    def findElement(self, selector):
        self.checkIsDisposed()
        return FindElementCommand(self.session,self.name).execute(selector)
    def getElementAttribute(self, selector, attribute):
        self.checkIsDisposed()
        return GetElementAttributeCommand(self.session, self.name).execute(selector, attribute)    
    def getElementLocation(self, selector):
        self.checkIsDisposed()
        return GetElementLocationCommand(self.session, self.name).execute(selector)
    def getElementSize(self, selector):
        self.checkIsDisposed()
        return GetElementSizeCommand(self.session, self.name).execute(selector)   
    def getOrientation(self):
        self.checkIsDisposed()
        return GetOrientationCommand(self.session, self.name).execute()
    def getScreenSize(self):
        self.checkIsDisposed()
        return GetScreenSizeCommand(self.session, self.name).execute()   
    def getSource(self):
        self.checkIsDisposed()
        return GetSourceCommand(self.session, self.name).execute()
    def hideKeyboard(self, iOS_Key = None):
        self.checkIsDisposed()
        return HideKeyboardCommand(self.session, self.name).execute(iOS_Key)
    def inputText(self, selector, text):
        self.checkIsDisposed()
        return InputTextCommand(self.session, self.name).execute(selector, text)
    def launchApp(self):
        self.checkIsDisposed()
        return LaunchAppCommand(self.session, self.name).execute()
    def multiTouch_Add(self):
        self.checkIsDisposed()
        return MultiTouch_AddCommand(self.session, self.name).execute()   
    def multiTouch_New(self):
        self.checkIsDisposed()
        return MultiTouch_NewCommand(self.session, self.name).execute()     
    def multiTouch_Perform(self):
        self.checkIsDisposed()
        return MultiTouch_PerformCommand(self.session, self.name).execute()    
    def pinchCoordinates(self, x, y, length):
        self.checkIsDisposed()
        return PinchCoordinatesCommand(self.session, self.name).execute(x, y, length)    
    def pinchElement(self, selector):
        self.checkIsDisposed()
        return PinchElementCommand(self.session, self.name).execute(selector)
    def resetApp(self):
        self.checkIsDisposed()
        return ResetAppCommand(self.session, self.name).execute()    
    def runAppInBackground(self, seconds = None):
        self.checkIsDisposed()
        return RunAppInBackgroundCommand(self.session, self.name).execute(seconds)
    def screenshotBMP(self, filename):
        self.checkIsDisposed()
        return ScreenshotBMPCommand(self.session, self.name).execute(filename)    
    def screenshotJPG(self, filename, quality):
        self.checkIsDisposed()
        return ScreenShotJPGCommand(self.session, self.name).execute(filename, quality)    
    def setOrientation(self, orientation):
        self.checkIsDisposed()
        return SetOrientationCommand(self.session, self.name).execute(orientation)
    def startDeviceLogging(self, filename, username = None, password = None):
        self.checkIsDisposed()
        return StartDeviceLoggingCommand(self.session, self.name).execute(filename, username, password)    
    def stopDeviceLogging(self):
        self.checkIsDisposed()
        return StopDeviceLoggingCommand(self.session, self.name).execute()    
    def swipe(self, startX, startY, endX, endY, duration):
        self.checkIsDisposed()
        return SwipeCommand(self.session, self.name).execute(startX, startY, endX, endY, duration)
    def swipeArc(self, centerX, centerY, radius, startDegree, degrees, steps):
        self.checkIsDisposed()
        return SwipeArcCommand(self.session, self.name).execute(centerX, centerY, radius, startDegree, degrees, steps)    
    def touchAction_MoveTo(self, x, y):
        self.checkIsDisposed()
        return TouchAction_MoveToCommand(self.session, self.name).execute(x, y)
    def touchAction_MoveToElement(self, selector):
        self.checkIsDisposed()
        return TouchAction_MoveToElementCommand(self.session, self.name).execute(selector)    
    def touchAction_New(self):
        self.checkIsDisposed()
        return TouchAction_NewCommand(self.session, self.name).execute()
    def touchAction_Perform(self):
        self.checkIsDisposed()
        return TouchAction_PerformCommand(self.session, self.name).execute()    
    def touchAction_Press(self, x, y):
        self.checkIsDisposed()
        return TouchAction_PressCommand(self.session, self.name).execute(x, y)    
    def touchAction_PressElement(self, selector):
        self.checkIsDisposed()
        return TouchAction_PressElementCommand(self.session, self.name).execute(selector)    
    def touchAction_Release(self):
        self.checkIsDisposed()
        return TouchAction_ReleaseCommand(self.session, self.name).execute()
    def touchAction_Tap(self, x, y):
        self.checkIsDisposed()
        return TouchAction_TapCommand(self.session, self.name).execute(x, y)
    def touchAction_Wait(self, duration):
        self.checkIsDisposed()
        return TouchAction_WaitCommand(self.session, self.name).execute(duration)    
    def waitForElement(self, selector, maxSeconds):
        self.checkIsDisposed()
        return WaitForElementCommand(self.session, self.name).execute(selector, maxSeconds)    
    def zoomCoordinates(self, x, y, length):
        self.checkIsDisposed()
        return ZoomCoordinatesCommand(self.session, self.name).execute(x, y, length)    
    def zoomElement(self, selector):
        self.checkIsDisposed()
        return ZoomElementCommand(self.session, self.name).execute(selector)

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
    def filterGrayscaleCommand(self, levels):
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
    def startBackgroundCapture(self, stepSize, captures):
        self.checkIsDisposed()
        return StartBackgroundCaptureCommand(self.session, self.name).execute(stepSize, captures)
    def startRecording(self, filename):
        self.checkIsDisposed()
        return StartRecordingCommand(self.session, self.name).execute(filename)
    def stopBackgroundCapture(self):
        self.checkIsDisposed()
        return StopBackgroundCaptureCommand(self.session, self.name).execute()
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
    def WaitForSample(self, x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod = None, maxDistance = None):
        self.checkIsDisposed()
        return WaitForSampleCommand(self.session, self.name).execute(x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod, maxDistance)
    def WaitForSampleNoMatch(self, x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod = None, maxDistance = None):
        self.checkIsDisposed()
        return WaitForSampleNoMatchCommand(self.session, self.name).execute(x, y, width, height, minSimilarity, timeout, tolerance, distanceMethod, maxDistance)



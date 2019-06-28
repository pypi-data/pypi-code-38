import json
import time
import urllib
import sys

from testwizard.testobjects_core import TestObjectBase

#Audio commands
from testwizard.commands_audio import WaitForAudioCommand
from testwizard.commands_audio import WaitForAudioPeakCommand

#Web Commands
from testwizard.commands_web.AcceptAlertCommand import AcceptAlert
from testwizard.commands_web.AddArgumentCommand import AddArgument
from testwizard.commands_web.AddChromeExtensionCommand import AddChromeExtension
from testwizard.commands_web.AuthenticateUrlCommand import AuthenticateUrl
from testwizard.commands_web.ClearCommand import Clear
from testwizard.commands_web.ClickCommand import Click
from testwizard.commands_web.DeleteAllCookiesCommand import DeleteAllCookies
from testwizard.commands_web.DismissAlertCommand import DismissAlert
from testwizard.commands_web.DragNDropCommand import DragNDrop
from testwizard.commands_web.GetChildrenCommand import GetChildren
from testwizard.commands_web.GetCurrentWindowHandleCommand import GetCurrentWindowHandle
from testwizard.commands_web.GetElementCommand import GetElement
from testwizard.commands_web.GetElementAttributeCommand import GetElementAttribute
from testwizard.commands_web.GetUrlCommand import GetUrl
from testwizard.commands_web.GetWindowHandlesCommand import GetWindowHandles
from testwizard.commands_web.GoToUrlCommand import GoToUrl
from testwizard.commands_web.IsDriverLoadedCommand import IsDriverLoaded
from testwizard.commands_web.MaximizeWindowCommand import MaximizeWindow
from testwizard.commands_web.MultiAction_ClickCommand import MultiAction_Click
from testwizard.commands_web.MultiAction_ClickAndHoldCommand import MultiAction_ClickAndHold
from testwizard.commands_web.MultiAction_ContextClickCommand import MultiAction_ContextClick
from testwizard.commands_web.MultiAction_DoubleClickCommand import MultiAction_DoubleClick
from testwizard.commands_web.MultiAction_DragAndDropCommand import MultiAction_DragAndDrop
from testwizard.commands_web.MultiAction_DragAndDropToOffsetCommand import MultiAction_DragAndDropToOffset
from testwizard.commands_web.MultiAction_keyDownCommand import MultiAction_keyDown
from testwizard.commands_web.MultiAction_keyUpCommand import MultiAction_keyUp
from testwizard.commands_web.MultiAction_MoveToElementCommand import MultiAction_MoveToElement
from testwizard.commands_web.MultiAction_MoveToElementOffsetCommand import MultiAction_MoveToElementOffset
from testwizard.commands_web.MultiAction_NewCommand import MultiAction_New
from testwizard.commands_web.MultiAction_PerformCommand import MultiAction_Perform
from testwizard.commands_web.MultiAction_ReleaseCommand import MultiAction_Release
from testwizard.commands_web.MultiAction_SendKeysCommand import MultiAction_SendKeys
from testwizard.commands_web.OpenInNewTabCommand import OpenInNewTab
from testwizard.commands_web.OpenInNewWindowCommand import OpenInNewWindow
from testwizard.commands_web.QuitDriverCommand import QuitDriver
from testwizard.commands_web.ScreenshotBMPCommand import ScreenshotBMP
from testwizard.commands_web.ScreenshotJPGCommand import ScreenshotJPGCommand
from testwizard.commands_web.ScrollByCommand import ScrollBy
from testwizard.commands_web.SendKeyboardShortcutCommand import SendKeyboardShortcut
from testwizard.commands_web.SendKeysCommand import SendKeys
from testwizard.commands_web.SendKeysAlertCommand import SendKeysAlert
from testwizard.commands_web.StartWebDriverCommand import StartWebDriver
from testwizard.commands_web.SubmitCommand import Submit
from testwizard.commands_web.SwitchToFrameCommand import SwitchToFrame
from testwizard.commands_web.SwitchToWindowCommand import SwitchToWindow
from testwizard.commands_web.WaitForControlCommand import WaitForControl

#Video commands
from testwizard.commands_video import GetVideoFormatCommand
from testwizard.commands_video import GetVideoResolutionCommand
from testwizard.commands_video import CompareCommand
from testwizard.commands_video import CountLastPatternMatchesCommand
from testwizard.commands_video import FilterBlackWhiteCommand
from testwizard.commands_video import FilterCBICommand
from testwizard.commands_video import FilterColorBlackWhiteCommand
from testwizard.commands_video import FilterGrayscaleCommand
from testwizard.commands_video import FilterInvertCommand
from testwizard.commands_video import FindAllPatternLocationsCommand
from testwizard.commands_video import FindAllPatternLocationsExCommand
from testwizard.commands_video import FindPatternCommand
from testwizard.commands_video import FindPatternExCommand
from testwizard.commands_video import SetRegionCommand
from testwizard.commands_video import TextOCRCommand
from testwizard.commands_video import CaptureReferenceBitmapCommand
from testwizard.commands_video import DeleteAllRecordingsCommand
from testwizard.commands_video import DeleteAllSnapshotsCommand
from testwizard.commands_video import DetectMotionCommand
from testwizard.commands_video import DetectNoMotionCommand
from testwizard.commands_video import LoadReferenceBitmapCommand
from testwizard.commands_video import SaveReferenceBitmapCommand
from testwizard.commands_video import SaveRegionCommand
from testwizard.commands_video import SnapShotBMPCommand
from testwizard.commands_video import SnapShotJPGCommand
from testwizard.commands_video import StartBackgroundCaptureCommand
from testwizard.commands_video import StartRecordingCommand
from testwizard.commands_video import StopBackgroundCaptureCommand
from testwizard.commands_video import StopRecordingCommand
from testwizard.commands_video import WaitForColorCommand
from testwizard.commands_video import WaitForColorNoMatchCommand
from testwizard.commands_video import WaitForPatternCommand
from testwizard.commands_video import WaitForPatternNoMatchCommand
from testwizard.commands_video import WaitForSampleCommand
from testwizard.commands_video import WaitForSampleNoMatchCommand


class Web(TestObjectBase):
    def __init__(self, session, name):
        TestObjectBase.__init__(self, session, name, "WEB")

    #Web Commands
    def acceptAlert(self):
        self.checkIsDisposed()
        return AcceptAlert(self.session, self.name).execute()
    def addArgument(self, argument):
        self.checkIsDisposed()
        return AddArgument(self.session, self.name).execute(argument)
    def addChromeExtension(self, filePath):
        self.checkIsDisposed()
        return AddChromeExtension(self.session, self.name).execute(filePath)
    def authenticateUrl(self, username, password, link):
        self.checkIsDisposed()
        return AuthenticateUrl(self.session, self.name).execute(username, password, link)
    def clear(self, selector):
        self.checkIsDisposed()
        return Clear(self.session, self.name).execute(selector)
    def click(self, selector):
        self.checkIsDisposed()
        return Click(self.session, self.name).execute(selector)
    def deleteAllCookies(self):
        self.checkIsDisposed()
        return DeleteAllCookies(self.session, self.name).execute()
    def dismissAlert(self):
        self.checkIsDisposed()
        return DismissAlert(self.session, self.name).execute()
    def dragNDrop(self, object, target):
        self.checkIsDisposed()
        return DragNDrop(self.session, self.name).execute(object, target) 
    def getChildren(self, selector):
        self.checkIsDisposed()
        return GetChildren(self.session, self.name).execute(selector)
    def getCurrentWindowHandle(self):
        self.checkIsDisposed()
        return GetCurrentWindowHandle(self.session, self.name).execute()      
    def getElement(self, selector):
        self.checkIsDisposed()
        return GetElement(self.session, self.name).execute(selector)   
    def getElementAttribute(self, selector, name):
        self.checkIsDisposed()
        return GetElementAttribute(self.session, self.name).execute(selector, name)
    def getUrl(self):
        self.checkIsDisposed()
        return GetUrl(self.session, self.name).execute()
    def getWindowHandles(self):
        self.checkIsDisposed()
        return GetWindowHandles(self.session, self.name).execute()
    def goToUrl(self, url):
        self.checkIsDisposed()
        return GoToUrl(self.session, self.name).execute(url)
    def isDriverLoaded(self):
        self.checkIsDisposed()
        return IsDriverLoaded(self.session, self.name).execute()
    def maximizeWindow(self):
        self.checkIsDisposed()
        return MaximizeWindow(self.session, self.name).execute()
    def multiAction_Click(self, selector):
        self.checkIsDisposed()
        return MultiAction_Click(self.session, self.name).execute(selector)
    def multiAction_ClickAndHold(self, selector):
        self.checkIsDisposed()
        return MultiAction_ClickAndHold(self.session, self.name).execute(selector)
    def multiAction_ContextClick(self, selector):
        self.checkIsDisposed()
        return MultiAction_ContextClick(self.session, self.name).execute(selector)
    def multiAction_DoubleClick(self, selector):
        self.checkIsDisposed()
        return MultiAction_DoubleClick(self.session, self.name).execute(selector)
    def multiAction_DragAndDrop(self, sourceSelector, targetSelector):
        self.checkIsDisposed()
        return MultiAction_DragAndDrop(self.session, self.name).execute(sourceSelector, targetSelector)
    def multiAction_DragAndDropToOffset(self, selector, targetXOffset, targetYOffset):
        self.checkIsDisposed()
        return MultiAction_DragAndDropToOffset(self.session, self.name).execute(selector, targetXOffset, targetYOffset)
    def multiAction_KeyDown(self, key, selector = None):
        self.checkIsDisposed()
        return MultiAction_keyDown(self.session, self.name).execute(key, selector)
    def multiAction_KeyUp(self, key, selector = None):
        self.checkIsDisposed()
        return MultiAction_keyUp(self.session, self.name).execute(key, selector)
    def multiAction_MoveToElement(self, selector):
        self.checkIsDisposed()
        return MultiAction_MoveToElement(self.session, self.name).execute(selector)
    def multiAction_MoveToElementOffset(self, selector, xOffset, yOffset):
        self.checkIsDisposed()
        return MultiAction_MoveToElementOffset(self.session, self.name).execute(selector, xOffset, yOffset)
    def multiAction_New(self):
        self.checkIsDisposed()
        return MultiAction_New(self.session, self.name).execute()
    def multiAction_Perform(self):
        self.checkIsDisposed()
        return MultiAction_Perform(self.session, self.name).execute()
    def multiAction_Release(self):
        self.checkIsDisposed()
        return MultiAction_Release(self.session, self.name).execute()
    def multiAction_SendKeys(self, inputString, Selector = None):
        self.checkIsDisposed()
        return MultiAction_SendKeys(self.session, self.name).execute(inputString, Selector)
    def openInNewTab(self, selector):
        self.checkIsDisposed()
        return OpenInNewTab(self.session, self.name).execute(selector)
    def openInNewWindow(self, selector):
        self.checkIsDisposed()
        return OpenInNewWindow(self.session, self.name).execute(selector)
    def quitDriver(self):
        self.checkIsDisposed()
        return QuitDriver(self.session, self.name).execute()
    def screenshotBMP(self, filename):
        self.checkIsDisposed()
        return ScreenshotBMP(self.session, self.name).execute(filename)
    def screenshotJPG(self, filename, quality):
        self.checkIsDisposed()
        return ScreenshotJPGCommand(self.session, self.name).execute(filename, quality)
    def scrollBy(self, x, y):
        self.checkIsDisposed()
        return ScrollBy(self.session, self.name).execute(x, y)
    def sendKeyboardShortcut(self, selector, keys):
        self.checkIsDisposed()
        return SendKeyboardShortcut(self.session, self.name).execute(selector, keys)
    def sendKeys(self, selector, text):
        self.checkIsDisposed()
        return SendKeys(self.session, self.name).execute(selector, text)
    def sendKeysAlert(self, text):
        self.checkIsDisposed()
        return SendKeysAlert(self.session, self.name).execute(text)
    def startWebDriver(self, browser = None, serverUrl = None):
        self.checkIsDisposed()
        return StartWebDriver(self.session, self.name).execute(browser, serverUrl)
    def submit(self, selector):
        self.checkIsDisposed()
        return Submit(self.session, self.name).execute(selector)
    def switchToFrame(self, selector):
        self.checkIsDisposed()
        return SwitchToFrame(self.session, self.name).execute(selector)
    def switchToWindow(self, selector):
        self.checkIsDisposed()
        return SwitchToWindow(self.session, self.name).execute(selector)
    def waitForControl(self, selector, seconds):
        self.checkIsDisposed()
        return WaitForControl(self.session, self.name).execute(selector, seconds)

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

    def checkIsDisposed(self):
        if(self.disposed):
            raise Exception("Cannot access a disposed object.")

    def dispose(self):
        self.disposed = True
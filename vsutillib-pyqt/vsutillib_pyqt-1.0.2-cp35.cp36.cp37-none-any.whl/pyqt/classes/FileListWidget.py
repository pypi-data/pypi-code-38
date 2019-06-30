"""
Sub-class of QTextEdit accepts drag and drop
"""
import logging
from pathlib import Path

from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QTextEdit, QStyleFactory, QMenu

import vsutillib.macos as macos

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class FileListWidget(QTextEdit):
    """
    QTextEdit subclass that accepts dropped files
    displays only the name of the files.
    The full path is save and use internally.
    """

    filesDroppedUpdateSignal = Signal(list)
    # log state
    __log = False

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:

            returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    def __init__(self, parent):
        super(FileListWidget, self).__init__(parent)

        #self.setDragEnabled(True)
        self.fileList = []
        self.bBlockDrops = False
        self.bFilesDropped = False

    def clear(self):
        self.fileList = []
        self.bBlockDrops = False
        self.bFilesDropped = False
        super().setAcceptDrops(True)
        super().clear()

    def dragEnterEvent(self, event):

        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()

        bUpdate = False
        for f in urls:
            filePath = str(f.path())[1:]

            fPath = Path(filePath)

            if fPath.is_dir():
                files = [x for x in fPath.glob('*.*') if x.is_file()]
                for x in files:
                    if x not in self.fileList:
                        self.fileList.append(x)
                        bUpdate = True
            elif fPath.is_file():
                if fPath not in self.fileList:
                    self.fileList.append(fPath)
                    bUpdate = True

        if bUpdate:
            if not self.bFilesDropped:
                self.bFilesDropped = True

            self._displayFiles()
            self.filesDroppedUpdateSignal.emit(self.fileList)

    def contextMenuEvent(self, event):

        if self.bFilesDropped and self.fileList:
            menu = QMenu(self)
            clearAction = menu.addAction(Actions.Clear)
            sortAction = menu.addAction(Actions.Sort)
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == clearAction:
                self.clear()
                self.filesDroppedUpdateSignal.emit(self.fileList)
            elif action == sortAction:
                if self.fileList:
                    self.fileList.sort(key=str)
                    self._displayFiles()
                    self.filesDroppedUpdateSignal.emit(self.fileList)

    def connectToInsertText(self, objSignal):
        """Connect to signal"""

        objSignal.connect(self.insertText)

    def setAcceptDrops(self, value):

        if not self.bBlockDrops:
            # don't check for type to raise error
            super().setAcceptDrops(value)

    @Slot(str, dict)
    def insertText(self, strText, kwargs):
        """
        Insert text in output window
        Cannot use standard keyword argument kwargs
        on emit calls, use dictionary instead

        Args:
            strText (str): text to insert on windows
            kwargs (dict): dictionary for additional
                commands for the insert operation
        """

        strTmp = ""

        color = None
        replaceLine = False
        appendLine = False

        if 'color' in kwargs:
            color = kwargs['color']

        if 'replaceLine' in kwargs:
            replaceLine = kwargs['replaceLine']

        if 'appendLine' in kwargs:
            appendLine = kwargs['appendLine']

        # still no restore to default the ideal configuration
        # search will continue considering abandoning color
        # in macOS saveStype works on Windows

        saveStyle = self.styleSheet()

        color = _setColor(color)

        self.setTextColor(color)

        if replaceLine:
            self.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

        if appendLine:
            self.append(strText)
        else:
            self.insertPlainText(strText)

        self.ensureCursorVisible()

        self.setStyleSheet(QStyleFactory.create(saveStyle))

        if self.log:
            strTmp = strTmp + strText
            strTmp = strTmp.replace("\n", " ")
            if strTmp != "" and strTmp.find(u"Progress:") != 0:
                if strTmp.find(u"Warning") == 0:
                    MODULELOG.warning("OTW0001: %s", strTmp)
                elif strTmp.find(u"Error") == 0 or color == Qt.red:
                    MODULELOG.error("OTW0002: %s", strTmp)
                else:
                    MODULELOG.info("OTW0003: %s", strTmp)

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

        Returns:
            bool:

            True if logging is enable False otherwise
        """
        if self.__log is not None:
            return self.__log

        return FileListWidget.classLog()

    @log.setter
    def log(self, value):
        """
        set instance log variable

        Args:
            value (bool): logging on if True.  Off if it False.
        """
        if isinstance(value, bool) or value is None:
            self.__log = value

    @Slot(list)
    def setFileList(self, filesList=None):
        """
        Set the files manually

        Args:
            filesList (list, optional): file list to display. Defaults to None.
        """

        if filesList:
            self.bBlockDrops = True
            self.bFilesDropped = False
            super().setAcceptDrops(False)
            self.fileList = []

            for f in filesList:
                self.fileList.append(f)

            self._displayFiles()

    def _displayFiles(self):
        """display the files on QTextEdit box"""

        super().clear()

        for f in self.fileList:
            self.insertPlainText(f.name + '\n')


def _setColor(color):

    if macos.isMacDarkMode():
        if color is None:
            return Qt.white
        else:
            if color == Qt.red:
                return Qt.magenta
            elif color == Qt.darkGreen:
                return Qt.green
            elif color == Qt.blue:
                return Qt.cyan
    elif color is None:
        return Qt.black

    return color


class Actions():
    """
    Actions labels for context menu
    """

    Clear = "Clear"
    Sort = "Sort"

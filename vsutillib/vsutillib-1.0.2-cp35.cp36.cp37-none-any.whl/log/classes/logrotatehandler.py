"""
rotating logging handler
it rotates at initialization
this means by number of executions
"""


import codecs
import logging.handlers
import re
import sys
from pathlib import Path


class LogRotateFileHandler(logging.handlers.RotatingFileHandler):

    """
    logging handler that rotate files at initialization time
    this will create a new file each time is run against
    the same log file.

    Args:
        fileName (Path|str): file where to save the log

        **kwargs: variable number of key value parameters
            that are passed to the super class on
            initialization
    """

    def __init__(self, fileName, **kwargs):

        # Python 3.5 open not compatible with pathlib
        if sys.version_info[:2] == (3, 5):
            f = str(fileName)
        else:
            f = fileName

        super(LogRotateFileHandler, self).__init__(
            f,
            **kwargs
        )

        self.doRollover()

class LogRotateFileHandlerOriginal(logging.Handler):
    """
    Custom logging handler that rotate files at the start

    :param logFile: file where to save logs
    :type logFile: str
    :param backupCount: number of files to save
    :type backupCount: int
    """

    def __init__(self, logFile, backupCount=0):
        super(LogRotateFileHandlerOriginal, self).__init__()

        self.logFile = logFile
        self.backupCount = backupCount
        self._rollover()
        self.logFilePointer = None

    def _rollover(self):
        """Rollover log files"""
        regEx = re.compile(r".*\.log\.(\d+)")

        bRotate = False
        logFile = Path(self.logFile)

        if logFile.is_file():
            bRotate = True
        #else:
        #    logFile.touch(exist_ok=True)

        if bRotate:
            filesDir = Path(logFile.parent)
            logFilesInDir = filesDir.glob("*.log.*")

            dFiles = {}
            maxIndexFile = 0

            for lFile in logFilesInDir:
                m = regEx.search(str(lFile))
                if m:
                    n = int(m.group(1))
                    dFiles[n] = lFile

            maxIndexFile = self.backupCount

            for i in range(1, self.backupCount, 1):
                if i not in dFiles:
                    maxIndexFile = i
                    break

            for n in range(maxIndexFile - 1, 0, -1):
                if n in dFiles:
                    rollFile = str(logFile) + "." + str(n+1)
                    dFiles[n].replace(rollFile)

            rollFile = str(logFile) + ".1"
            logFile.replace(rollFile)
            #logFile.touch(exist_ok=True)

    def emit(self, record):
        """
        Write record entry to log file
        """

        # Python 3.5 open not compatible with pathlib
        if sys.version_info[:2] == (3, 5):
            f = str(self.logFile)
        else:
            f = self.logFile

        with codecs.open(f, "a", encoding="utf-8") as file:
            logEntry = self.format(record)
            file.write(logEntry + "\n")

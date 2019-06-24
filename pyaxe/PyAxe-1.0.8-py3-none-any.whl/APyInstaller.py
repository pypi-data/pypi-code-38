import sys
import os
from . import (ACommandLineTool)


_commandlineTool = ACommandLineTool.CommandLineTool('pyinstaller')
def getCommandLineTool():
    _commandlineTool.checkExistence()
    return _commandlineTool


def getResourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)


class ExtraOptions:
    def __init__(self):
        self.debug = False
        self.datas = []  # [(源文件, 目标目录),...]
        self.moduleSearchPaths = []
        self.hasConsole = True  # 对于控制台程序必须为True，对于图形界面程序该值若为True则包含控制台窗口

    def toCommandLineStr(self):
        s = ''
        if self.debug:
            s += ' --debug'
        for data in self.datas:
            s += ' --add-data %s%s%s' % (data[0], ';' if os.name == 'nt' else ':', data[1])
        for moduleSearchPath in self.moduleSearchPaths:
            s += ' --paths ' + moduleSearchPath.replace('\\', '/')
        if not self.hasConsole:
            s += ' --noconsole'
        return s


def execCommand(mainPy, exeName, oneFile=True, extraOptions=None):
    """
    :param extraOptions can be None/str/ExtraOptions
    """
    cmd = mainPy
    cmd += ' --name ' + exeName
    cmd += ' --onefile' if oneFile else ' --onedir'
    if isinstance(extraOptions, str):
        cmd += ' ' + extraOptions
    elif isinstance(extraOptions, ExtraOptions):
        cmd += extraOptions.toCommandLineStr()
    else:
        assert extraOptions is None
    getCommandLineTool().execCommand(cmd)

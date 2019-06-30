"""
mkvUtils:

related to mkv application functionality
"""

import glob
import logging
import os
import platform
import shlex

from pathlib import Path

from vsutillib.files import findFileInPath
from vsutillib.process import RunCommand

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


def getMKVMerge():
    """
    get the name of the mkvmerge executable in the system

    Returns:
        pathlib.Path:

        fully qualified mkvmerge executable
    """

    currentOS = platform.system()

    if currentOS == "Darwin":

        lstTest = glob.glob("/Applications/MKVToolNix*")
        if lstTest:
            f = lstTest[0] + "/Contents/MacOS/mkvmerge"
            mkvmerge = Path(f)
            if mkvmerge.is_file():
                return mkvmerge

    elif currentOS == "Windows":

        defPrograms64 = os.environ.get('ProgramFiles')
        defPrograms32 = os.environ.get('ProgramFiles(x86)')

        dirs = []
        if defPrograms64 is not None:
            dirs.append(defPrograms64)

        if defPrograms32 is not None:
            dirs.append(defPrograms32)

        # search 64 bits
        for d in dirs:
            search = sorted(Path(d).rglob("mkvmerge.exe"))
            if search:
                mkvmerge = Path(search[0])
                if mkvmerge.is_file():
                    return mkvmerge

    elif currentOS == "Linux":

        search = findFileInPath("mkvmerge")

        if search:
            for s in search:
                mkvmerge = Path(s)
                if mkvmerge.is_file():
                    return mkvmerge

    return None


def getMKVMergeVersion(mkvmerge):
    """
    get mkvmerge version

    Args:
        mkvmerge (str): mkvmerge executable with full path

    Returns:
        str:

        version of mkvmerge
    """

    s = mkvmerge

    if s[0:1] != "'" and s[-1:] != "'":
        s = shlex.quote(s)
        print(s)

    runCmd = RunCommand(s + " --version", regexsearch=r" v(.*?) ")

    if runCmd.run():
        return runCmd.regexmatch

    return None


def stripEncaseQuotes(strFile):
    """
    Strip single quote at start and end of file name
    if they are found

    Args:
        strFile (str): file name

    Returns:
        str:

        file name without start and end single quoute
    """

    # Path or str should work
    s = str(strFile)

    if (s[0:1] == "'") and (s[-1:] == "'"):
        s = s[1:-1]

    return s

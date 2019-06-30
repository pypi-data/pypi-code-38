"""
File utilities
"""

import os
import platform
from pathlib import Path, PurePath

def findFileInPath(element, dirPath=None):
    """
    Convenience function that finds a file in the
    PATH environment variable

    Args:
        dirPath (str): search in the specified PATH

    Returns:
        list: list of :py:class:`pathlib.Path`

    I really like the :mod:`threading` module which has the
    :class:`threading.Thread` class.

    Here is a link :func:`time.time`.
    """

    filesFound = []

    if dirPath is None:
        dirPath = os.getenv('PATH')

    if isinstance(dirPath, str):
        dirs = dirPath.split(os.pathsep)
    else:
        dirs = dirPath

    for dirname in dirs:
        candidate = Path(PurePath(dirname).joinpath(element))
        if candidate.is_file():
            filesFound.append(candidate)

    return filesFound


def getFileList(strPath,
                wildcard=None,
                fullpath=False,
                recursive=False,
                strName=False):
    """
    Get files in a directory
    strPath has to be an existing directory or file
    in case of a file the parent directory is used
    strExtFilter in the form -> .ext
    """

    p = Path(strPath)

    if (not p.is_file()) and (not p.is_dir()):
        return []

    lstFilesFilter = []

    if p.is_file():
        p = p.parent

    if wildcard is None:
        wc = "*.*"
    else:
        wc = wildcard

    if recursive:
        wc = "**/" + stripEncaseQuotes(wildcard)

    lstObjFileNames = [x for x in p.glob(wc) if x.is_file()]

    if not fullpath:
        lstFilesFilter = [x.name for x in lstObjFileNames]
        return lstFilesFilter

    if strName:
        lstFilesFilter = [str(x) for x in lstObjFileNames]
        return lstFilesFilter

    return lstObjFileNames


def getExecutable(search):
    """
    search for executable for macOS and
    """

    fileToSearch = search

    currentOS = platform.system()

    if currentOS == "Darwin":

        lstTest = Path("/Applications").glob('**/' + fileToSearch)

        for l in lstTest:
            p = Path(l)
            if p.stem == fileToSearch:
                return p

    elif currentOS == "Windows":

        if fileToSearch.find('.') < 0:
            # assume is binary executable
            fileToSearch += '.exe'

        defPrograms64 = os.environ.get('ProgramFiles')
        defPrograms32 = os.environ.get('ProgramFiles(x86)')

        dirs = []
        if defPrograms64 is not None:
            dirs.append(defPrograms64)

        if defPrograms32 is not None:
            dirs.append(defPrograms32)

        # search 64 bits
        for d in dirs:
            search = sorted(Path(d).rglob(fileToSearch))
            if search:
                executable = Path(search[0])
                if executable.is_file():
                    return executable

    searchFile = findFileInPath(fileToSearch)

    if searchFile:
        for e in searchFile:
            executable = Path(e)
            if executable.is_file():
                return executable

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

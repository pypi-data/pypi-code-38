"""Utility functions"""


import ctypes
import platform


def isMediaInfoLib():
    """
    Check if MediaInfo library is on the system

    Returns:
        bool: True if found False otherwise
    """

    currentOS = platform.system()
    libNames = ()

    if currentOS == "Windows":
        libraryType = ctypes.WinDLL
        libNames = ["MediaInfo.dll"]
    else:
        libraryType = ctypes.CDLL

    if currentOS == "Darwin":
        libNames = ["libmediainfo.0.dylib", "libmediainfo.dylib"]
    elif currentOS == "Linux":
        libNames = ["libmediainfo.so.0", "libzen.so.0"]

    for library in libNames:
        try:
            libFile = libraryType(library) # pylint: disable=W0612
        except OSError:
            return False

    return True

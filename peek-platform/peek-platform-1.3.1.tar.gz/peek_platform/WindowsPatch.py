import logging
import os
import platform

logger = logging.getLogger(__name__)

isWindows = platform.system() == "Windows"
isMacOS = platform.system() == "Darwin"



def createHardLink(src, dst):
    import ctypes
    flags = 1 if src is not None and os.path.isdir(src) else 0
    if not ctypes.windll.kernel32.CreateHardLinkA(dst, src, flags):
        raise OSError(ctypes.get_last_error())


def createSymbolicLink(src, dst, target_is_directory=False):
    """ Create Symbolic Link

    http://timgolden.me.uk/pywin32-docs/win32file__CreateSymbolicLink_meth.html
    """
    import win32file
    flags = 1 if target_is_directory else 0
    win32file.CreateSymbolicLink(dst, src, flags)


if isWindows:
    logger.info("Replacing os.link/os.symlink functions.")
    os.link = createHardLink
    os.symlink = createSymbolicLink

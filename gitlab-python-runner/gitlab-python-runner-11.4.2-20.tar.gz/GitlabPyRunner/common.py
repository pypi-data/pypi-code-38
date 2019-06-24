"""
Various functions shared between the other modules
"""
import socket
import platform


def gethostname():
    try:
        return socket.gethostname()
    except:
        return "unknown-hostname"


def iswindows():
    return platform.system() == "Windows"

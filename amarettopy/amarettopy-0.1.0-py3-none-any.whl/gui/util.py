from tkinter import messagebox
import sys,os
from amarettopy import *
import logging

logger = logging.getLogger("amarettopy")

faultDict = dict([
            (0x000, "Stable"),
            (0x001, "FOC Duration"),
            (0x002, "Over Voltage"),
            (0x004, "Under Voltage"),
            (0x008, "Over Temperature"),
            (0x040, "Break In"),
            (0x100, "Stop Control Error"),
            (0x200, "Stop Timeout"),
            (0x800, "Unknown Error"),
            ])

class AmarettoGuiInfo:
    targetDevId = 1

amarettoGuiInfo = AmarettoGuiInfo()
tickListener = []

def tryAmaretto(f):
    try:
        return f()
    except MCPError as e:
        messagebox.showerror('communication exception', e.__class__.__name__)

        logger.error('communication exception: %s'%e.__class__.__name__)
    except Exception as e:
        messagebox.showerror('exception',str(e))
        
        logger.error('exception: %s'% str(e))
    return None

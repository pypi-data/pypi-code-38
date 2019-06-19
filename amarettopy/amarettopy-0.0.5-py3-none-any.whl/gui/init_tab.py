import sys,os
from tkinter import *
import tkinter as Tk
import tkinter.ttk as ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog
import yaml
from collections import OrderedDict
from amarettopy import *
import logging
from amarettopy.gui.util  import *

logger = logging.getLogger("amarettopy")

class InitTab(Tk.Frame):

    def __init__(self, amaretto, master=None):
        Tk.Frame.__init__(self, master)
        self.amaretto = amaretto

        self.initButton= Tk.Button(self, text='Init', width= "10", command=self.init)
        self.initButton.pack(pady=5)

        self.calibButton = Tk.Button(self, text='Calib', width= "10", command=self.calib)
        self.calibButton .pack(pady=5)

        self.zeroButton= Tk.Button(self, text='SetZero', width= "10", command=self.setZero)
        self.zeroButton.pack(pady=5)

        self.resetButton= Tk.Button(self, text='Reset', width= "10", command=self.reset)
        self.resetButton.pack(pady=5)

        self.setFaultButton= Tk.Button(self, text='Fault', width= "10", command=self.fault_open)
        self.setFaultButton.pack(pady=5)

    def fault_open(self):
        
        logger.error("Fault button clicked")
        inputDialog = SelectFaultDialog(self)
        self.wait_window(inputDialog.top)

        if inputDialog.faults is None:
            return
        
        tryAmaretto(lambda: self.amaretto.fault(amarettoGuiInfo.targetDevId, inputDialog.faults))
        logger.error("Fault Error1 %s" % str(inputDialog.faults))

    def reset(self):
        logger.info("Reset button clicked ")
        tryAmaretto(lambda: self.amaretto.reset(amarettoGuiInfo.targetDevId))

    def calib(self):
        logger.info("Calib button clicked ")
        tryAmaretto(lambda: calibrate(self.amaretto, amarettoGuiInfo.targetDevId))

    def init(self):
        logger.info("Init button clicked ")

        def f():
            _f = os.path.join(os.path.dirname(__file__), "config/default_params.yml")
            self.amaretto.load_servo_params(amarettoGuiInfo.targetDevId, _f)
            self.amaretto.set_device_id(amarettoGuiInfo.targetDevId, 1)

        tryAmaretto(f)

    def setZero(self):
        logger.info("Zero button clicked ")

        def f():
            p = self.amaretto.query_servo_status(amarettoGuiInfo.targetDevId)[POS]
            self.set_sys_offset(amarettoGuiInfo.targetDevId, p % 65536)

        tryAmaretto(f)


class SelectFaultDialog:
    
    def __init__(self, parent):
        top = self.top = Tk.Toplevel(parent)
        top.grab_set()
        top.focus_set()

        self.faults = None

        self.vars = []
        self.checkButtons = []

        for (faultNo, faultName) in faultDict.items():
            var = Tk.BooleanVar()
            checkButton = Tk.Checkbutton(top, text=faultName, variable=var)
            checkButton.pack(anchor = "w")
            self.vars.append(var)
            self.checkButtons.append(checkButton)

        self.submitButton = Tk.Button(top, text='Submit', command=self.send)
        self.submitButton.pack()

    def send(self):
        self.faults = 0

        for i, var in enumerate(self.vars):
            if var.get() == True:
                self.faults += list(faultDict.keys())[i]

        self.top.destroy()


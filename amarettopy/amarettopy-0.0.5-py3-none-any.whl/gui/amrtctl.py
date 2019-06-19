
from tkinter import *
import tkinter as tk

from amarettopy.gui.top_panel import TopPanel
from amarettopy.gui.side_panel import SidePanel
from amarettopy.gui.main_panel import MainPanel

import sys,os
from amarettopy import *

import time
import logging
import logging.handlers as handlers

logger = logging.getLogger("amarettopy")

class AmarettoGUI(tk.Frame):
    def __init__(self, amaretto, master=None):
        tk.Frame.__init__(self, master)
        self.amaretto = amaretto
        self.pack(expand = True, fill = BOTH)
        self.make_root()
        self.text_log_file()


    def make_root(self):

        self.master.title("AmarettoPy")

        if os.name == 'nt':
            root = PanedWindow(self, sashwidth = 2, orient=VERTICAL, width=1000, height=820)
            bottom = PanedWindow(root, sashwidth = 2)
        else:
            root = PanedWindow(self, sashwidth = 2, orient=VERTICAL, width=1000, height=1000)
            bottom = PanedWindow(root, sashwidth = 2, width=1000, height=800)
        
        root.pack(expand = True, fill = BOTH)

        main = Label(bottom, text = 'panedwindow\nmain', bg = 'yellow')        
    
        side = SidePanel(self.amaretto, root)
        main = MainPanel(self.amaretto, root)


        bottom.add(side, width=200)         
        bottom.add(main)
        
        root.add(TopPanel(self.amaretto, root), height=50)
        root.add(bottom)


    def text_log_file(self):
        
        logfile_name = "amaretto-gui.log"

        #Create logger
        logger.setLevel(logging.INFO)

        FORMAT =logging.Formatter("[%(asctime)s] %(levelname)s: %(filename)s:%(lineno)s: %(message)s")
        
        #handler = handlers. TimedRotatingFileHandler(logfile_name, when="M",  interval=5, backupCount=20 )
        handler = handlers.RotatingFileHandler(logfile_name, maxBytes=1000000,  backupCount=0 )
    
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(FORMAT)
  
        errorlog = handlers.RotatingFileHandler('error.log', maxBytes=1000000, backupCount=0)
        errorlog.setLevel(logging.ERROR)
        errorlog.setFormatter(FORMAT)
        
        logger.addHandler(handler)
        logger.addHandler(errorlog)
        
        logger.info("Amaretto-GUI STARTED")
        msg = "LOG DATA is gathering ..."
        logger.info(msg)       
        

def main():
    amaretto = UnsafeAmarettoPy(baud=115200,port=None,timeout_ms=3000)
    global targetDevId
    targetDevId = 1
    app = AmarettoGUI(amaretto)
    app.mainloop()

if __name__ == '__main__':
    main()




from tkinter import *
import tkinter as Tk
import tkinter.ttk as ttk
import sys
from amarettopy import *
from amarettopy.gui.util  import *
import logging
from tkinter import messagebox

logger = logging.getLogger("amarettopy")

class LogTab(Tk.Frame):
     
    def __init__(self, amaretto, master):
        Tk.Frame.__init__(self, master)
        self.amaretto = amaretto

        self.log_menu()
    
    def log_menu(self):
     
        self.logFrame = Frame(self)
        self.logFrame.pack()

        self.refreshButton= Tk.Button(self.logFrame, text='Refresh', command=self.refresh)
        self.refreshButton.grid(row=0, column=0, columnspan=1, padx=5, pady=5)

        self.clearLogButton= Tk.Button(self.logFrame, text='ClearLog', command=self.clear_log)
        self.clearLogButton.grid(row=0, column=1, columnspan=1, padx=5, pady=5)

        self.init_table()

    def init_table(self):
        tree = ttk.Treeview(self)

        tree["columns"] = (0,1,2,3,4,5,6)
        tree["show"] = "headings"

        tree.column(0,width=30,stretch=False)     # i
        tree.column(1,width=90,stretch=False)     # index
        tree.column(2,width=60)                   # logLevel
        tree.column(3,width=100)                  # group
        tree.column(4,width=100)                  # subGroup
        tree.column(5,width=40,stretch=False)     # code
        tree.column(6,width=300)                  # payload

        tree.heading(1,text="Index")
        tree.heading(2,text="LogLevel")
        tree.heading(3,text="Group")
        tree.heading(4,text="SubGroup")
        tree.heading(5,text="Code")
        tree.heading(6,text="Payload")

        tree.pack(fill="both", expand=True)
        self.tableView = tree

    def refresh(self):

        logger.info("refresh log")
        text_log_data= "power_on_time : %d [sec]\n" % (self.get_life_log() / 100)

        n = self.get_log_info()
        i = 0

        self.tableView.delete(*self.tableView.get_children())

        index = 0
        while i < n :
            recs =self.get_log(start_index=i, read_size=min(10, n -i))
            for rec in recs:
                text_log_data = text_log_data + str(rec) + "\n"
                logIndex = rec["index"]
                level    = rec["level"]
                group    = rec["group"]
                subGroup = rec["subGroup"]
                code     = rec["code"]
                payload  = rec["payload"]
 
                self.tableView.insert("","end",values=(index, logIndex, level, group, subGroup, code, payload))
                index += 1
            i +=10

    def get_log_info(self):
        
        logger.info("get_log_info")
        readableSize = tryAmaretto(lambda: self.amaretto.get_log_info(amarettoGuiInfo.targetDevId))
        return readableSize

    def get_log(self, start_index, read_size):
        
        data = tryAmaretto(lambda: self.amaretto.get_log(amarettoGuiInfo.targetDevId, start_index, read_size))
        return data["logRecords"]

    def get_life_log(self):
        return tryAmaretto(lambda: self.amaretto.get_power_on_time(amarettoGuiInfo.targetDevId))

    def clear_log(self):

        res = messagebox.askokcancel('askokcancel','Clear Log?')
        if not res:
            return

        logger.info("Clear log button clicked")
        tryAmaretto(lambda: self.amaretto.clear_log(amarettoGuiInfo.targetDevId))

        self.refresh()
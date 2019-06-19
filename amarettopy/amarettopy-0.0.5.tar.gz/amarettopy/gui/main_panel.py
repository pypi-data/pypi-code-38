import os
from tkinter import *
import tkinter as Tk
import tkinter.ttk as ttk
from amarettopy.gui.graph_tab import GraphTab
from amarettopy.gui.config_tab import ConfigTab
from amarettopy.gui.log_tab import LogTab
from amarettopy.gui.init_tab import InitTab

class MainPanel(Tk.Frame):

    def __init__(self, amaretto, master):
        Tk.Frame.__init__(self, master)
        self.amaretto = amaretto

        self.add_tab()

    def add_tab(self, event=None):
        
        note = ttk.Notebook(self, width=600, height=800)
        if int(os.getenv('UNSAFE_AMARETTO', 0)) == 1:
            note.add(InitTab(self.amaretto, note), text = "Init")
        note.add(ConfigTab(self.amaretto, 'servo.yml', True, note), text = "ServoParam")
        note.add(ConfigTab(self.amaretto, 'system.yml', int(os.getenv('UNSAFE_AMARETTO', 0)) == 1, note), text = "SystemParam")
        note.add(LogTab(self.amaretto, note), text = "Log")

        note.add(GraphTab(self.amaretto, note), text = "Graph")

        note.pack(fill="both", expand=True)


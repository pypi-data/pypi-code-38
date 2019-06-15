import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
    import ttk
else:
    import tkinter as tk
    from tkinter import ttk

"""
TODO:
    create everything
"""


class Tab4():
    """
    Display results for manual classification
    """
    def __init__(self,master,notebook,interface):
        self.master = master
        self.n = notebook
        self.interface = interface
        self.initialized = False

        # TAB 4: AUTONOMOUS TARGET SUBMISSION ------------------------------------------------
        self.tab4 = ttk.Frame(self.n)
        self.n.add(self.tab4, text='Autonomous Target Submission')

        self.initialized = True

    def run(self,interface):
        self.interface = interface
        # setup all keybindings
        self.master.unbind("<Right>")
        self.master.unbind("<Left>")
        self.master.unbind("<d>")
        self.master.unbind("<a>")
        self.master.unbind("<Configure>")
        self.master.unbind("<Control-z>")
        self.master.unbind("<Return>")

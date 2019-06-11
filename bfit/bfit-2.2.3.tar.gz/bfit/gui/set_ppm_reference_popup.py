# Drawing style window
# Derek Fujimoto
# July 2018

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import webbrowser
import logging

# ========================================================================== #
class set_ppm_reference_popup(object):
    """
        Popup window for setting ppm reference frequency. 
    """

    # ====================================================================== #
    def __init__(self,parent):
        self.parent = parent
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(parent.mainframe)
        self.win.title('Set PPM Reference')
        frame = ttk.Frame(self.win,relief='sunken',pad=5)
        topframe = ttk.Frame(frame,pad=5)

        # Key bindings
        self.win.bind('<Return>',self.set)             
        self.win.bind('<KP_Enter>',self.set)

        # make objects: text entry
        l1 = ttk.Label(topframe,text='PPM Reference Frequency:',pad=5,justify=LEFT)
        self.text = IntVar()
        self.text.set(parent.ppm_reference)
        entry = ttk.Entry(topframe,textvariable=self.text,width=10,justify=RIGHT)
        l2 = ttk.Label(topframe,text='Hz',pad=5,justify=LEFT)
        
        # make objects: buttons
        set_button = ttk.Button(frame,text='Set',command=self.set)
        close_button = ttk.Button(frame,text='Cancel',command=self.cancel)
        
        # grid
        l1.grid(column=0,row=0)
        entry.grid(column=1,row=0)
        l2.grid(column=2,row=0)
        topframe.grid(column=0,row=0,columnspan=2,pady=10)
        set_button.grid(column=0,row=1)
        close_button.grid(column=1,row=1)
            
        # grid frame
        frame.grid(column=0,row=0)
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def set(self,*args):
        """Set entered values"""        
        self.parent.ppm_reference = self.text.get()
        self.logger.info('Set ppm reference to %s Hz',self.parent.ppm_reference)
        self.logger
        self.win.destroy()
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()

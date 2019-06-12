# Setting asym calculation histograms window
# Derek Fujimoto
# August 2018

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import webbrowser
import textwrap
import os
import logging

# ========================================================================== #
class set_histograms_popup(object):
    """
        Popup window for setting asymmetry calculation histograms. 
    """

    # ====================================================================== #
    def __init__(self,parent):
        self.parent = parent
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(parent.mainframe)
        self.win.title('Set Histograms')
        frame = ttk.Frame(self.win,relief='sunken',pad=5)
        
        # Key bindings
        self.win.bind('<Return>',self.set)             
        self.win.bind('<KP_Enter>',self.set)
        
        # labels 
        title_label = ttk.Label(frame,text=\
                'Set histogram names for asymmetry calcultions.')
                
        explanation_frame = ttk.Frame(frame,relief='sunken',pad=5)
        explanation_label = ttk.Label(explanation_frame,
            text=textwrap.dedent("""\
            If we wished to do a simple asymmetry calculation in the form of 
                                    
                                    (F-B)/(F+B)
            
            for each helicity, then 
                                       
                                    'F+,F-,B+,B-'
                                       
            for alpha diffusion calculations append the two alpha counters
            
                                 'R+,R-,L+,L-,A+,A-
            
            for alpha tagged calculations do the following
            
                     'R+,R-,L+,L-,TR+,TR-,TL+,TL-,nTR+,nTR-,nTL+,nTL-'
                    
                where TR is the right counter tagged (coincident) with alphas, 
                      TL is the left  counter tagged with alphas, 
                     nTR is the right counter tagged with !alphas (absence of), 
                     nLR is the right counter tagged with !alphas
                     
            (note the lack of spaces in each list)
            """),\
            pad=5,justify=LEFT,font=('Courier'))
        
        self.text = StringVar()
        self.text.set(self.parent.hist_select)
        self.entry = ttk.Entry(frame,textvariable=self.text,width=75,justify=CENTER)
        
        try:
            if hasattr(parent.fileviewer,'data'): 
                s = list(parent.fileviewer.data.hist.keys())
            else:
                run = list(parent.fetch_files.data.keys())[0]
                s = list(parent.fetch_files.data[run].hist.keys())
        except (IndexError,AttributeError):
            self.logger.exception('No files fetched or viewed')
            s = 'No files fetched or viewed'
        else:
            s.sort()
            s = ''.join(["'%s', "%i for i in s])
            s = s[:-2]
            s = textwrap.wrap(s,75)
            s = '\n'.join(s)
            
        detected_label = ttk.Label(frame,text='The detected histogram titles are:')
        detected_label2 = ttk.Label(frame,text=s,font=('Courier'),justify=CENTER)
        
        # grid 
        r = 0
        title_label.grid(column=0,row=r,columnspan=3,sticky=(W,E)); r+=1
        explanation_frame.grid(column=0,row=r,columnspan=3,sticky=(W,E),pady=10); r+=1
        explanation_label.grid(column=0,row=0,sticky=(W,E))
        detected_label.grid(column=0,row=r,sticky=(W,E),columnspan=3,pady=20); r+= 1
        detected_label2.grid(column=0,row=r,sticky=(W,E),columnspan=3); r+= 1
        self.entry.grid(column=0,row=r,columnspan=3,pady=20); r+=1
          
        # add buttons
        set_button = ttk.Button(frame,text='Set',command=self.set)
        close_button = ttk.Button(frame,text='Cancel',command=self.cancel)
        help_button = ttk.Button(frame,text='Help',command=self.help)
        set_button.grid(column=0,  row=r)
        help_button.grid(column=1, row=r)
        close_button.grid(column=2,row=r)
            
        # grid frame
        frame.grid(column=0,row=0)
        
        self.logger.debug('Initialization success. Starting mainloop.')

    # ====================================================================== #
    def help(self):
        self.logger.info('Opening help')
        p = os.path
        webbrowser.open(p.split(p.abspath(p.realpath(__file__)))[0]+'/help.html')

    # ====================================================================== #
    def set(self,*args):
        """Set entered values"""
        self.parent.hist_select = self.entry.get()
        self.logger.info('Set histogram selection to "%s"',self.parent.hist_select)
        self.win.destroy()
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()

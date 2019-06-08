# Calculate needed current from desired magnetic field. 
# Derek Fujimoto
# Feb 2019

from tkinter import *
from tkinter import ttk
import pandas as pd
import numpy as np
import logging
from bfit import logger_name


class show_param_popup(object):
    """
        Display pandas dataframe object as pretty table in popup window.
    """
    
    rounding = 8
    
    # ======================================================================= #
    def __init__(self,df):
        """
            Draw window for show parameter popup
            
            df: pandas dataframe with run information
        """
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # root 
        root = Toplevel()
        root.title("Fitted Parameters")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # main frame
        mainframe = ttk.Frame(root,pad=5)
        mainframe.grid(column=0,row=0,sticky=(N,W))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # round values
        df.reset_index(inplace=True)
        df = df.round(decimals=self.rounding)
        
        # make strings with errors
        for c in df.columns:
            if 'Error' in c:    continue
            
            if 'Error '+c in df.columns:
                df[c] = df[c].map(str) + ' +/- ' + df['Error '+c].map(str)
        df.drop(labels=df.columns[['Error' in c for c in df.columns]],
                axis='columns',inplace=True)
        
        # make list of outputs
        header = df.columns.values
        output_list = df.values
        output_list = np.vstack((header,output_list))
        
        # get len of each column
        maxlen = [max(map(len,map(str,line))) for line in output_list.T]
        splitter = ['-'*n for n in maxlen]
        output_list = np.vstack((output_list[0],splitter,output_list[1:]))
        
        # get nicely formatted string to output
        str_fmt = ' '.join(['%-'+'%ds' % n for n in maxlen])
                    
        nice_output = '\n'.join([str_fmt % tuple(line) for line in output_list])
                
        # Text box and other objects
        self.text = Text(mainframe,width=150,height=30,state='normal',wrap="none")
        self.text.delete('1.0',END)
        self.text.insert('1.0',nice_output)
        
        vsb = Scrollbar(mainframe, orient="vertical")
        hsb = Scrollbar(mainframe, orient="horizontal")
        
        self.text.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.text.yview)
        self.text.configure(xscrollcommand=hsb.set)
        hsb.configure(command=self.text.xview)
        
        # Gridding
        self.text.grid(column=0,row=0,sticky=(N,S,E,W))
        vsb.grid(row=0, column=1, sticky="nse")
        hsb.grid(row=1, column=0, sticky="wse")
        
        mainframe.grid_columnconfigure(0,weight=1)
        mainframe.grid_rowconfigure(0,weight=1)
        
        # runloop
        self.root = root
        self.logger.debug('Initialization success. Starting mainloop.')
        root.mainloop()
    

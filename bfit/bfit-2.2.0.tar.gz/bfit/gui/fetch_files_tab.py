# fetch_files tab for bfit
# Derek Fujimoto
# Nov 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
from bfit import logger_name
from bdata import bdata
from functools import partial
from bfit.gui.fitdata import fitdata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging
import time,datetime


__doc__="""
    """

# =========================================================================== #
# =========================================================================== #
class fetch_files(object):
    """
        Data fields:
            
            canvas_frame_id: id number of frame in canvas
            check_rebin: IntVar for handling rebin aspect of checkall
            check_bin_remove: StringVar for handing omission of 1F data
            check_state: BooleanVar for handling check all
            check_state_data: BooleanVar for handling check_all_data
            check_state_fit: BooleanVar for handling check_all_fit
            check_state_res: BooleanVar for handling check_all_res
            
            data_canvas: canvas object allowing for scrolling 
            dataline_frame: frame holding all the data lines. Exists as a window
                in the data_canvas
            
            entry_asym_type: combobox for asym calc and draw type
            year: IntVar of year to fetch runs from 
            run: StringVar input to fetch runs.
            bfit: pointer to parent class
            data_lines: dictionary of dataline obj, keyed by run number
            data_lines_old: dictionary of removed dataline obj, keyed by run number
            fet_entry_frame: frame of fetch tab
            runmode_label: display run mode
            runmode: display run mode string
            max_number_fetched: max number of files you can fetch
    """
    
    runmode_relabel = {'20':'Spin-Lattice Relaxation (20)',
                       '1f':'Frequency Scan (1f)',
                       '2e':'Randomized Frequency (2e)',
                       '1n':'Rb Cell Scan (1n)',
                       '2h':'Alpha Tagging/Diffusion (2h)'}
    run_number_starter_line = '40001 40005-40010 (run numbers)'
    bin_remove_starter_line = '1 5 100-200 (omit bins)'
    max_number_fetched = 500
    
    # ======================================================================= #
    def __init__(self,fetch_data_tab,bfit):
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing')
    
        # initialize
        self.bfit = bfit
        self.data_lines = {}
        self.data_lines_old = {}
        self.fit_input_tabs = {}
        self.check_rebin = IntVar()
        self.check_bin_remove = StringVar()
        self.check_state = BooleanVar()
        self.fetch_data_tab = fetch_data_tab
        
        # Frame for specifying files -----------------------------------------
        fet_entry_frame = ttk.Labelframe(fetch_data_tab,text='Specify Files')
        self.year = IntVar()
        self.run = StringVar()
        
        self.year.set(self.bfit.get_latest_year())
        
        entry_year = Spinbox(fet_entry_frame,textvariable=self.year,width=5,
                             from_=2000,to=datetime.datetime.today().year)
        entry_run = ttk.Entry(fet_entry_frame,textvariable=self.run,width=80)
        entry_run.insert(0,self.run_number_starter_line)
        entry_fn = partial(on_entry_click,text=self.run_number_starter_line,\
                            entry=entry_run)
        on_focusout_fn = partial(on_focusout,text=self.run_number_starter_line,\
                            entry=entry_run)
        entry_run.bind('<FocusIn>', entry_fn)
        entry_run.bind('<FocusOut>', on_focusout_fn)
        entry_run.config(foreground='grey')
        
        # fetch button
        fetch = ttk.Button(fet_entry_frame,text='Fetch',command=self.get_data)
        
        # grid and labels
        fet_entry_frame.grid(column=0,row=0,sticky=(N,W))
        ttk.Label(fet_entry_frame,text="Year:").grid(column=0,row=0,sticky=W)
        entry_year.grid(column=1,row=0,sticky=(W))
        ttk.Label(fet_entry_frame,text="Run Number:").grid(column=2,row=0,sticky=W)
        entry_run.grid(column=3,row=0,sticky=W)
        fetch.grid(column=4,row=0,sticky=E)
        
        # padding 
        for child in fet_entry_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        
        # Frame for run mode -------------------------------------------------
        runmode_label_frame = ttk.Labelframe(fetch_data_tab,pad=(10,5,10,5),\
                text='Run Mode',)
        
        self.runmode_label = ttk.Label(runmode_label_frame,text="",font='bold',justify=CENTER)
        
        # Scrolling frame to hold datalines
        yscrollbar = Scrollbar(fetch_data_tab, orient=VERTICAL)         
        self.data_canvas = Canvas(fetch_data_tab,bd=0,              # make a canvas for scrolling
                yscrollcommand=yscrollbar.set,                      # scroll command receive
                scrollregion=(0, 0, 5000, 5000),confine=True)       # default size
        yscrollbar.config(command=self.data_canvas.yview)           # scroll command send
        dataline_frame = ttk.Frame(self.data_canvas,pad=5)          # holds 
        
        self.canvas_frame_id = self.data_canvas.create_window((0,0),    # make window which can scroll
                window=dataline_frame,
                anchor='nw')
        dataline_frame.bind("<Configure>",self.config_canvas) # bind resize to alter scrollable region
        self.data_canvas.bind("<Configure>",self.config_dataline_frame) # bind resize to change size of contained frame
        
        # Frame to hold everything on the right ------------------------------
        bigright_frame = ttk.Frame(fetch_data_tab,pad=5)
        
        # Frame for group set options ----------------------------------------
        right_frame = ttk.Labelframe(bigright_frame,\
                text='Operations on Checked Items',pad=30)
        
        check_remove = ttk.Button(right_frame,text='Remove',\
                command=self.remove_all,pad=5)
        check_draw = ttk.Button(right_frame,text='Draw',\
                command=self.draw_all,pad=5)
        
        check_set = ttk.Button(right_frame,text='Set',\
                command=self.set_all)
        check_rebin_label = ttk.Label(right_frame,text="SLR Rebin:",pad=5)
        check_rebin_box = Spinbox(right_frame,from_=1,to=100,width=3,\
                textvariable=self.check_rebin)
        check_bin_remove_entry = ttk.Entry(right_frame,\
                textvariable=self.check_bin_remove,width=20)
        
        check_all_box = ttk.Checkbutton(right_frame,
                text='Force Check State',variable=self.check_state,
                onvalue=True,offvalue=False,pad=5,command=self.check_all)
        self.check_state.set(True)
        
        right_checkbox_frame = ttk.Frame(right_frame)
        
        self.check_state_data = BooleanVar()        
        check_data_box = ttk.Checkbutton(right_checkbox_frame,
                text='Data',variable=self.check_state_data,
                onvalue=True,offvalue=False,pad=5,command=self.check_all_data)
        self.check_state_data.set(True)
        
        self.check_state_fit = BooleanVar()        
        check_fit_box = ttk.Checkbutton(right_checkbox_frame,
                text='Fit',variable=self.check_state_fit,
                onvalue=True,offvalue=False,pad=5,command=self.check_all_fit)
        
        self.check_state_res = BooleanVar()        
        check_res_box = ttk.Checkbutton(right_checkbox_frame,
                text='Res',variable=self.check_state_res,
                onvalue=True,offvalue=False,pad=5,command=self.check_all_res)
                
        check_toggle_button = ttk.Button(right_frame,\
                text='Toggle All Check States',command=self.toggle_all,pad=5)
        
        # add grey to check_bin_remove_entry
        check_bin_remove_entry.insert(0,self.bin_remove_starter_line)
        
        check_entry_fn = partial(on_entry_click,\
                text=self.bin_remove_starter_line,\
                entry=check_bin_remove_entry)
        
        check_on_focusout_fn = partial(on_focusout,\
                text=self.bin_remove_starter_line,\
                entry=check_bin_remove_entry)
        
        check_bin_remove_entry.bind('<FocusIn>', check_entry_fn)
        check_bin_remove_entry.bind('<FocusOut>', check_on_focusout_fn)
        check_bin_remove_entry.config(foreground='grey')
                
        # grid
        runmode_label_frame.grid(column=2,row=0,sticky=(N,W,E))
        self.runmode_label.grid(column=0,row=0,sticky=(N,W,E))
        
        bigright_frame.grid(column=2,row=1,sticky=(N,E))
        
        self.data_canvas.grid(column=0,row=1,sticky=(E,W,S,N))
        yscrollbar.grid(column=1,row=1,sticky=(W,S,N))
        
        check_data_box.grid(        column=0,row=0,sticky=(N))
        check_fit_box.grid(         column=1,row=0,sticky=(N))
        check_res_box.grid(         column=2,row=0,sticky=(N)) 
        
        right_frame.grid(           column=0,row=0,sticky=(N,E,W))
        r = 0
        check_all_box.grid(         column=0,row=r,sticky=(N)); r+= 1
        right_checkbox_frame.grid(  column=0,row=r,sticky=(N)); r+= 1
        check_toggle_button.grid(   column=0,row=r,sticky=(N,E,W),pady=1); r+= 1
        check_draw.grid(            column=0,row=r,sticky=(N,W));
        check_remove.grid(          column=1,row=r,sticky=(N,E)); r+= 1
        check_rebin_label.grid(     column=0,row=r)
        check_rebin_box.grid(       column=1,row=r); r+= 1
        check_bin_remove_entry.grid(column=0,row=r,sticky=(N)); r+= 1
        check_set.grid(             column=0,row=r,sticky=(N,E,W))
        
        bigright_frame.grid(        rowspan=2,sticky=(N,E,W))
        check_all_box.grid(         columnspan=2)
        right_checkbox_frame.grid(  columnspan=2)
        check_toggle_button.grid(   columnspan=2)
        check_bin_remove_entry.grid(columnspan=2)
        check_set.grid(             columnspan=2)
        
        check_rebin_box.grid_configure(padx=5,pady=5,sticky=(E,W))
        check_rebin_label.grid_configure(padx=5,pady=5,sticky=(E,W))
        check_set.grid_configure(padx=5,pady=5,sticky=(E,W))
        
        # resizing
        fetch_data_tab.grid_columnconfigure(0, weight=1)        # main area
        fetch_data_tab.grid_rowconfigure(1,weight=1)            # main area
        
        for i in range(3):
            if i%2 == 0:    fet_entry_frame.grid_columnconfigure(i, weight=2)
        fet_entry_frame.grid_columnconfigure(3, weight=1)
            
        self.data_canvas.grid_columnconfigure(0,weight=1)    # fetch frame 
        self.data_canvas.grid_rowconfigure(0,weight=1)
            
        # drawing style
        style_frame = ttk.Labelframe(bigright_frame,text='Drawing Quantity',\
                pad=5)
        self.entry_asym_type = ttk.Combobox(style_frame,\
                textvariable=self.bfit.fileviewer.asym_type,state='readonly',\
                width=20)
        self.entry_asym_type['values'] = ()
        
        style_frame.grid(column=0,row=1,sticky=(W,N))
        self.entry_asym_type.grid(column=0,row=0,sticky=(N))
        self.entry_asym_type.grid_configure(padx=24)
        
        # passing
        self.entry_run = entry_run
        self.entry_year = entry_year
        self.check_rebin_box = check_rebin_box
        self.check_bin_remove_entry = check_bin_remove_entry
        self.check_all_box = check_all_box
        self.dataline_frame = dataline_frame

        self.logger.debug('Initialization success.')
    
    # ======================================================================= #
    def __del__(self):
        
        # delete lists and dictionaries
        if hasattr(self,'data_lines'):      del self.data_lines
        if hasattr(self,'data_lines_old'):  del self.data_lines_old
        
        # kill buttons and frame
        try:
            for child in self.fetch_data_tab.winfo_children():
                child.destroy()
            self.fetch_data_tab.destroy()
        except Exception:
            pass
        
    # ======================================================================= #
    def _do_check_all(self,state,var,box):
        """
            Force all tickboxes of a given type to be in a given state, assuming 
            the tickbox is active
        """
        
        self.logger.info('Changing state of all %s tickboxes to %s',var,state)
        for k in self.data_lines.keys():
            
            # check if tickbox is object variable
            if hasattr(self.data_lines[k],box):
                
                # check if tickbox is disabled
                if str(getattr(self.data_lines[k],box)['state']) == 'disabled':
                    continue
                    
            # set value
            getattr(self.data_lines[k],var).set(state)

    # ======================================================================= #
    def canvas_scroll(self,event):
        """Scroll canvas with files selected."""
        if event.num == 4:
            self.data_canvas.yview_scroll(-1,"units")
        elif event.num == 5:
            self.data_canvas.yview_scroll(1,"units")
    
    # ======================================================================= #
    def check_all(self):  
        self._do_check_all(self.check_state.get(),'check_state','None')
        
    def check_all_data(self):  
        self._do_check_all(self.check_state_data.get(),'check_data','None')
        
    def check_all_fit(self):  
        self._do_check_all(self.check_state_fit.get(),'check_fit','draw_fit_checkbox')
    
    def check_all_res(self):  
        self._do_check_all(self.check_state_res.get(),'check_res','draw_res_checkbox')    
        
    # ======================================================================= #
    def config_canvas(self,event):
        """Alter scrollable region based on canvas bounding box size. 
        (changes scrollbar properties)"""
        self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all"))
    
    # ======================================================================= #
    def config_dataline_frame(self,event):
        """Alter size of contained frame in canvas. Allows for inside window to 
        be resized with mouse drag""" 
        self.data_canvas.itemconfig(self.canvas_frame_id,width=event.width)
        
    # ======================================================================= #
    def draw_all(self,ignore_check=False):
        """Draw all data in data lines"""
        
        self.logger.debug('Drawing all data (ignore check: %s)', ignore_check)
        
        # condense drawing into a funtion
        def draw_lines():
            for r in self.data_lines.keys():
                if self.data_lines[r].check_state.get() or ignore_check:
                    self.data_lines[r].draw()
                
        # get draw style
        style = self.bfit.draw_style.get()
        self.logger.debug('Draw style: "%s"',style)
        
        # make new figure, draw stacked
        if style == 'stack':
            draw_lines()
            
        # overdraw in current figure, stacked
        elif style == 'redraw':
            plt.clf()
            self.bfit.draw_style.set('stack')
            draw_lines()
            self.bfit.draw_style.set('redraw')
            
        # make new figure, draw single
        elif style == 'new':
            plt.figure()
            self.bfit.draw_style.set('stack')
            draw_lines()
            self.bfit.draw_style.set('new')
        else:
            s = "Draw style not recognized"
            messagebox.showerror(message=s)
            self.logger.error(s)
            raise ValueError(s)
    
    # ======================================================================= #
    def export(self):
        """Export all data files as csv"""
        
        # filename
        filename = self.bfit.fileviewer.default_export_filename
        self.logger.info('Exporting to file %s',filename)
        try:
            filename = filedialog.askdirectory()+'/'+filename
        except TypeError:
            pass
        
        # get data and write
        for k in self.bfit.data.keys():
            d = self.bfit.data[k].bd
            self.bfit.export(d,filename%(d.year,d.run))
        self.logger.debug('Success.')
        
    # ======================================================================= #
    def get_data(self):
        """Split data into parts, and assign to dictionary."""
        
        self.logger.debug('Fetching runs')
    
        # make list of run numbers, replace possible deliminators
        try:
            run_numbers = self.string2run(self.run.get())
        except ValueError:
            self.logger.exception('Bad run number string')
            return
            
        # get the selected year
        year = int(self.year.get())
        
        # get data
        data = {}
        s = ['Failed to open run']
        for r in run_numbers:
            
            # get key for data storage
            runkey = self.bfit.get_run_key(r=r,y=year)
            
            # read from archive
            try:
                new_data = bdata(r,year=year)
            except (RuntimeError,ValueError):
                s.append("%d (%d)" % (r,year))
            else:
                
                # update data
                if runkey in self.bfit.data.keys():
                    self.bfit.data[runkey].bd = new_data
                    
                # new data
                else:
                    data[runkey] = fitdata(self.bfit,new_data)
            
        # print error message
        if len(s)>1:
            s = '\n'.join(s)
            print(s)
            self.logger.warning(s)
            messagebox.showinfo(message=s)
        
        # check that data is all the same runtype
        run_types = [self.bfit.data[k].mode for k in self.bfit.data.keys()]
        run_types = run_types + [data[k].mode for k in data.keys()]
        
        # different run types: select all runs of same type
        if not all([r==run_types[0] for r in run_types]):
            
            # unique run modes
            run_type_unique = np.unique(run_types)
            
            # message
            message = "Multiple run types detected:\n("
            for m in run_type_unique: 
                message += m+', '
            message = message[:-2]
            message += ')\n\nSelecting ' + run_types[0] + ' runs.'
            messagebox.showinfo(message=message)
            
        # get only run_types[0]
        self.logger.debug('Fetching runs of mode %s',run_types[0])
        for k in tuple(data.keys()):
            if data[k].mode == run_types[0]:
                self.bfit.data[k] = data[k]
            else:
                del data[k]
        
        try:
            self.runmode = run_types[0]
        except IndexError:
            s = 'No valid runs detected.'
            messagebox.showerror(message=s)
            self.logger.warning(s)
            raise RuntimeError(s)
        self.runmode_label['text'] = self.runmode_relabel[self.runmode]
        self.bfit.set_asym_calc_mode_box(self.runmode)
        
        keys_list = list(self.bfit.data.keys())
        keys_list.sort()
        
        # make lines
        n = 1
        for r in keys_list:
            
            # new line
            if r not in self.data_lines.keys():
                
                if r in self.data_lines_old.keys():
                    self.data_lines[r] = self.data_lines_old[r]
                    del self.data_lines_old[r]
                else:
                    self.data_lines[r] = dataline(\
                                            bfit = self.bfit,\
                                            lines_list = self.data_lines,\
                                            lines_list_old = self.data_lines_old,
                                            fetch_tab_frame = self.dataline_frame,\
                                            bdfit = self.bfit.data[r],\
                                            row = n)
            self.data_lines[r].grid(n)
            if n==1 or n%20==0:  self.dataline_frame.update_idletasks()
            n+=1
            
        # remove old runs, modes not selected
        for r in tuple(self.data_lines.keys()):
            if self.data_lines[r].bdfit.mode != self.runmode:
                self.data_lines[r].degrid()
            
        self.logger.info('Fetched runs %s',list(data.keys()))
        
    # ======================================================================= #
    def remove_all(self):
        """Remove all data files from self.data_lines"""
        
        self.logger.info('Removing all data files')
        del_list = []
        for r in self.data_lines.keys():
            if self.data_lines[r].check_state.get():
                del_list.append(self.data_lines[r])
        for d in del_list:
            d.degrid()
    
    # ======================================================================= #
    def return_binder(self):
        """Switch between various functions of the enter button. """
        
        # check where the focus is
        focus_id = str(self.bfit.root.focus_get())
        
        # run or year entry
        if focus_id in [str(self.entry_run), str(self.entry_year)]:
            self.logger.debug('Focus is: run or year entry')
            self.get_data()
        
        # checked rebin or checked run omission
        elif focus_id in [str(self.check_rebin_box),\
                          str(self.check_bin_remove_entry)]:
            self.logger.debug('Focus is: checked rebin or checked run omission')
            self.set_all()
        elif focus_id == str(self.check_all_box):
            self.logger.debug('Focus is: check all box')
            self.draw_all()
        else:
            pass

    # ======================================================================= #
    def set_all(self):
        """Set a particular property for all checked items. """
        
        self.logger.info('Set all')
        
        # check all file lines
        for r in self.data_lines.keys():
            
            # if checked
            if self.data_lines[r].check_state.get():
                
                # get values to enter
                self.data_lines[r].rebin.set(self.check_rebin.get())
                new_text = self.check_bin_remove.get()
                
                # check for greyed text
                if new_text != self.bin_remove_starter_line:
                    self.data_lines[r].bin_remove.set(new_text)
                else:
                    self.data_lines[r].bin_remove.set("")
                    
                # generate focus out event: trigger grey text reset
                self.data_lines[r].bin_remove_entry.event_generate('<FocusOut>')

    # ======================================================================= #
    def set_all_labels(self):
        """Set lable text in all items """
        
        self.logger.info('Setting all label text')
        
        # check all file lines
        for r in self.data_lines.keys():
            self.data_lines[r].set_label()
            
        for r in self.data_lines_old.keys():
            self.data_lines_old[r].set_label()

    # ======================================================================= #
    def string2run(self,string):
        """Parse string, return list of run numbers"""
        
        full_string = string.replace(',',' ').replace(';',' ')
        full_string = full_string.replace(':','-')
        part_string = full_string.split()
        
        run_numbers = []
        for s in part_string:
            if '-' in s:
                try:
                    rn_lims = [int(s2) for s2 in s.split('-')]
                except ValueError:
                    run_numbers.append(int(s.replace('-','')))
                else:
                    rns = np.arange(rn_lims[0],rn_lims[1]+1).tolist()
                    run_numbers.extend(rns)
            else:
                run_numbers.append(int(s))
        
        # sort
        run_numbers.sort()
        self.logger.debug('Parsed "%s" to run numbers (len: %d) %s',string,
                          len(run_numbers),run_numbers)
        
        if len(run_numbers) > self.max_number_fetched:
            raise RuntimeWarning("Too many files selected (max 50).")
        return run_numbers
    
    # ======================================================================= #
    def toggle_all(self):
        """Toggle all tickboxes"""
        self.logger.info('Toggling all tickboxes')
        for k in self.data_lines.keys():
            state = not self.data_lines[k].check_state.get()
            self.data_lines[k].check_state.set(state)

# =========================================================================== #
# =========================================================================== #
class dataline(object):
    """
        A line of objects to display run properties and remove bins and whatnot.
        
        bfit:           pointer to root 
        bin_remove:     StringVar for specifying which bins to remove in 1f runs
        bin_remove_entry: Entry object for bin remove 
        check_data:     BooleanVar for specifying to draw data
        check_fit:      BooleanVar for specifying to draw fit
        check_res:      BooleanVar for specifying to draw residual
        check_state:    BooleanVar for specifying check state
        draw_fit_checkbox: Checkbutton linked to check_fit
        draw_res_checkbox: Checkbutton linked to check_res
        id:             Str key for unique idenfication
        label:          StringVar for labelling runs in legends
        label_entry:    Entry object for labelling runs in legends
        line_frame:     Frame that object is placed in
        lines_list:     dictionary of datalines
        lines_list_old: dictionary of datalines
        mode:           bdata run mode
        rebin:          IntVar for SLR rebin
        row:            position in list
        run:            bdata run number
        year:           bdata year
    """
        
    bin_remove_starter_line = '1 5 100-200 (omit bins)'
    
    # ======================================================================= #
    def __init__(self,bfit,lines_list,lines_list_old,fetch_tab_frame,bdfit,row):
        """
            Inputs:
                fetch_tab_frame: parent in which to place line
                bdfit: fitdata object corresponding to the file which is placed here. 
                row: where to grid this object
        """
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing run %d (%d)',bdfit.run,bdfit.year)
        
        # variables
        self.bfit = bfit
        self.bin_remove = bdfit.omit
        self.label = bdfit.label
        self.rebin = bdfit.rebin
        self.check_state = bdfit.check_state
        self.mode = bdfit.mode
        self.run =  bdfit.run
        self.year = bdfit.year
        self.row = row
        self.lines_list = lines_list
        self.lines_list_old = lines_list_old
        bd = bdfit.bd
        self.bdfit = bdfit
        self.id = bdfit.id
        
        # temperature
        try:
            self.temperature = int(np.round(bdfit.temperature.mean))
        except AttributeError:
            self.temperature = np.nan
                
        # field
        self.field = np.around(bdfit.field,2)
        
        try:
            field_text = "%3.2f T"%self.field
        except TypeError:
            field_text = ' '
        
        # bias
        self.bias = self.bdfit.bias
        try:
            bias_text = "%4.2f kV"%self.bias
        except TypeError:
            bias_text = ' '
        
        # build objects
        line_frame = ttk.Frame(fetch_tab_frame,pad=(5,0))
        
        info_str = "%d  %d  %3d K  %s  %s" % (self.year,self.run,
                                              self.temperature,field_text,
                                              bias_text)
        info_label = ttk.Label(line_frame,text=info_str,pad=5)
        bin_remove_entry = ttk.Entry(line_frame,textvariable=self.bin_remove,\
                width=20)
                
        label_label = ttk.Label(line_frame,text="Label:",pad=5)
        self.label_entry = ttk.Entry(line_frame,textvariable=self.label,\
                width=20)
                
        remove_button = ttk.Button(line_frame,text='Remove',\
                command=self.degrid,pad=1)
        draw_button = ttk.Button(line_frame,text='Draw',command=self.draw,pad=1)
        
        self.check_data = BooleanVar()
        self.check_data.set(True)
        draw_data_checkbox = ttk.Checkbutton(line_frame,text='Data',
                variable=self.check_data,onvalue=True,offvalue=False,pad=5)
        
        self.check_fit = BooleanVar()
        self.check_fit.set(False)
        self.draw_fit_checkbox = ttk.Checkbutton(line_frame,text='Fit',
                variable=self.check_fit,onvalue=True,offvalue=False,pad=5,
                state=DISABLED)
        
        self.check_res = BooleanVar()
        self.check_res.set(False)
        self.draw_res_checkbox = ttk.Checkbutton(line_frame,text='Res',
                variable=self.check_res,onvalue=True,offvalue=False,pad=5,
                state=DISABLED)
        
        rebin_label = ttk.Label(line_frame,text="Rebin:",pad=5)
        rebin_box = Spinbox(line_frame,from_=1,to=100,width=3,\
                textvariable=self.rebin)
                
        self.check_state.set(bfit.fetch_files.check_state.get())
        check = ttk.Checkbutton(line_frame,text='',variable=self.check_state,\
                onvalue=True,offvalue=False,pad=5)
         
        # add grey text to bin removal
        bin_remove_entry.insert(0,self.bin_remove_starter_line)
        entry_fn = partial(on_entry_click,\
                text=self.bin_remove_starter_line,entry=bin_remove_entry)
        on_focusout_fn = partial(on_focusout,\
                text=self.bin_remove_starter_line,entry=bin_remove_entry)
        bin_remove_entry.bind('<FocusIn>', entry_fn)
        bin_remove_entry.bind('<FocusOut>', on_focusout_fn)
        bin_remove_entry.config(foreground='grey')
             
        # add grey text to label
        self.set_label()
                
        # grid
        c = 1
        check.grid(column=c,row=0,sticky=E); c+=1
        info_label.grid(column=c,row=0,sticky=E); c+=1
        if self.mode in ['1f','1n']: 
            bin_remove_entry.grid(column=c,row=0,sticky=E); c+=1
        if self.mode in ['20','2h']: 
            rebin_label.grid(column=c,row=0,sticky=E); c+=1
            rebin_box.grid(column=c,row=0,sticky=E); c+=1
        label_label.grid(column=c,row=0,sticky=E); c+=1
        self.label_entry.grid(column=c,row=0,sticky=E); c+=1
        draw_data_checkbox.grid(column=c,row=0,sticky=E); c+=1
        self.draw_fit_checkbox.grid(column=c,row=0,sticky=E); c+=1
        self.draw_res_checkbox.grid(column=c,row=0,sticky=E); c+=1
        draw_button.grid(column=c,row=0,sticky=E); c+=1
        remove_button.grid(column=c,row=0,sticky=E); c+=1
        
        # resizing
        fetch_tab_frame.grid_columnconfigure(0, weight=1)   # big frame
        for i in (3,5,7):
            line_frame.grid_columnconfigure(i, weight=100)    # input labels
        for i in (4,6,8):
            line_frame.grid_columnconfigure(i, weight=1)  # input fields
        
        # passing
        self.line_frame = line_frame
        self.bin_remove_entry = bin_remove_entry
        
    # ======================================================================= #
    def __del__(self):
        
        # kill buttons and frame
        try:
            for child in self.line_frame.winfo_children():
                child.destroy()
        except Exception:
            pass
            
    # ======================================================================= #
    def grid(self,row):
        """Re-grid a dataline object so that it is in order by run number"""
        self.row = row
        self.line_frame.grid(column=0,row=row,columnspan=2, sticky=(W,N))
        self.bfit.data[self.id] = self.bdfit
        
    # ======================================================================= #
    def degrid(self):
        """Hide displayed dataline object from file selection. """
        
        self.logger.info('Degridding run %d (%d)',self.run,self.year)
        
        self.line_frame.grid_forget()
        
        self.lines_list_old[self.id] = self.lines_list[self.id]
        del self.lines_list[self.id]
        del self.bfit.data[self.id]
        
        # repopulate fit files tab
        self.bfit.fit_files.populate()
        
        # remove data from storage
        if len(self.lines_list) == 0:
            ff = self.bfit.fetch_files
            ff.runmode_label['text'] = ''
                
    # ======================================================================= #
    def draw(self):
        """Draw single data file."""
        
        # draw data
        if self.check_data.get():
            self.logger.debug('Draw run %d (%d)',self.run,self.year)
                    
            # get new data file
            data = bdata(self.run,year=self.year)
            
            # get data file run type
            d = self.bfit.fileviewer.asym_type.get()
            d = self.bfit.fileviewer.asym_dict[d]
            
            if self.bin_remove.get() == self.bin_remove_starter_line:
                self.bfit.draw(data,d,self.rebin.get(),
                    label=self.label.get())
            else:
                self.bfit.draw(data,d,self.rebin.get(),\
                    option=self.bin_remove.get(),label=self.label.get())

        # draw fit
        if self.check_fit.get():
            self.bfit.fit_files.draw_fit(id=self.id),
        
        # draw residual
        if self.check_res.get():
            self.bfit.fit_files.draw_residual(id=self.id,
                                              rebin=self.rebin.get())

    # ======================================================================= #
    def set_label(self):
        """Set default label text"""
        
        # clear old text
        self.label_entry.delete(0,'end')
        
        # get default label
        label = self.bfit.get_label(self.bfit.data[self.id])
        self.label_entry.insert(0,label)
        
        # make function to clear and replace with default text
        entry_fn_lab = partial(on_entry_click,text=label,
                               entry=self.label_entry)
        on_focusout_fn_lab = partial(on_focusout,text=label,
                                 entry=self.label_entry)
                                 
        # bindings
        self.label_entry.bind('<FocusIn>', entry_fn_lab)
        self.label_entry.bind('<FocusOut>', on_focusout_fn_lab)
        self.label_entry.config(foreground='grey')
        
# =========================================================================== #
def on_entry_click(event,entry,text):
    """Vanish grey text on click"""
    if entry.get() == text:
        entry.delete(0, "end") # delete all the text in the entry
        entry.insert(0, '') #Insert blank for user input
        entry.config(foreground = 'black')

# =========================================================================== #
def on_focusout(event,entry,text):
    """Set grey text for boxes on exit"""
    if entry.get() == '':
        entry.insert(0,text)
        entry.config(foreground = 'grey')
    else:
        entry.config(foreground = 'black')




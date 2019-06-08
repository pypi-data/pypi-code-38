# fit_files tab for bfit
# Derek Fujimoto
# Dec 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
from functools import partial
from bfit.gui.zahersCalculator import current2field
from bfit.gui.show_param_popup import show_param_popup
from bfit.gui.gui_param_popup import gui_param_popup
from bdata import bdata
from bfit import logger_name

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import datetime, os, traceback
import logging

"""
"""

# =========================================================================== #
# =========================================================================== #
class fit_files(object):
    """
        Data fields:
            annotation:     stringvar: name of quantity for annotating parameters 
            canvas_frame_id:id number of frame in canvas
            chi_threshold:  if chi > thres, set color to red
            draw_components:list of titles for labels, options to export, draw.
            fit_canvas:     canvas object allowing for scrolling 
            fit_data_tab:   containing frame (for destruction)
            fit_function_title: title of fit function to use
            fit_function_title_box: spinbox for fit function names
            fit_input:      fitting input values = (fn_name,ncomp,data_list)
            fit_lines:      Dict storing fitline objects
            fit_lines_old: dictionary of previously used fitline objects, keyed by run
            fitter:         fitting object from self.bfit.routine_mod
            mode:           what type of run is this. 
            n_component:    number of fitting components (IntVar)
            runframe:       frame for displaying fit results and inputs
            runmode_label:  display run mode 
            set_as_group:   BooleanVar() if true, set fit parfor whole group
            share_var:      BooleanVar() holds share checkbox for all fitlines
            xaxis:          StringVar() for parameter to draw on x axis
            yaxis:          StringVar() for parameter to draw on y axis
            xaxis_combobox: box for choosing x axis draw parameter
            yaxis_combobox: box for choosing y axis draw parameter
    """ 
    
    default_fit_functions = {'20':('Exp','Str Exp'),'2h':('Exp','Str Exp'),
            '1f':('Lorentzian','Gaussian'),'1n':('Lorentzian','Gaussian')}
    mode = ""
    chi_threshold = 1.5 # threshold for red highlight on bad fits 
    n_fitx_pts = 500    # number of points to draw in fitted curves
    
    # ======================================================================= #
    def __init__(self,fit_data_tab,bfit):
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing')
        
        # initialize
        self.bfit = bfit
        self.fit_output = {}
        self.share_var = {}
        self.fitter = self.bfit.routine_mod.fitter(bfit.probe_species.get())
        self.draw_components = bfit.draw_components
        self.fit_data_tab = fit_data_tab
            
        # make top level frames
        mid_fit_frame = ttk.Labelframe(fit_data_tab,
                    text='Set Initial Parameters',pad=5)
        right_frame = ttk.Labelframe(fit_data_tab,
            text='Fit Results and Run Conditions',pad=5)     # draw fit results
        
        mid_fit_frame.grid(column=0,row=1,sticky=(N,W,E,S))
        right_frame.grid(column=1,row=1,columnspan=2,sticky=(N,E,W))
        
        fit_data_tab.grid_columnconfigure(0,weight=1)   # fitting space
        mid_fit_frame.grid_columnconfigure(0,weight=1)
        mid_fit_frame.grid_rowconfigure(0,weight=1)
        
        # TOP FRAME -----------------------------------------------------------
        
        # fit function select 
        fn_select_frame = ttk.Labelframe(fit_data_tab,text='Fit Function')
        self.fit_function_title = StringVar()
        self.fit_function_title.set("")
        self.fit_function_title_box = ttk.Combobox(fn_select_frame, 
                textvariable=self.fit_function_title,state='readonly')
        self.fit_function_title_box.bind('<<ComboboxSelected>>',
            lambda x :self.populate_param(force_modify=True))
        
        # number of components in fit spinbox
        self.n_component = IntVar()
        self.n_component.set(1)
        n_component_box = Spinbox(fn_select_frame,from_=1,to=20, 
                textvariable=self.n_component,width=5,
                command=lambda:self.populate_param(force_modify=True))
        
        # fit and other buttons
        fit_button = ttk.Button(fn_select_frame,text='Fit',command=self.do_fit,\
                                pad=1)
        set_param_button = ttk.Button(fn_select_frame,text='Set Result as P0',
                        command=self.do_set_result_as_initial,pad=1)                        
        reset_param_button = ttk.Button(fn_select_frame,text='Reset Inputs',
                        command=self.do_reset_initial,pad=1)
        gui_param_button = ttk.Button(fn_select_frame,text='P0 Finder',
                        command=self.do_gui_param,pad=1)
        
        # set as group checkbox
        self.set_as_group = BooleanVar()
        set_group_check = ttk.Checkbutton(fn_select_frame,
                text='Modify For All',\
                variable=self.set_as_group,onvalue=True,offvalue=False)
        self.set_as_group.set(True)
        
        # run mode 
        fit_runmode_label_frame = ttk.Labelframe(fit_data_tab,pad=(10,5,10,5),
                text='Run Mode',)
        self.fit_runmode_label = ttk.Label(fit_runmode_label_frame,text="",
                font='bold',justify=CENTER)
        
        # fitting routine
        fit_routine_label_frame = ttk.Labelframe(fit_data_tab,pad=(10,5,10,5),
                text='Fitting Routine',)
        self.fit_routine_label = ttk.Label(fit_routine_label_frame,text="",
                font='bold',justify=CENTER)
                
        # GRIDDING
            
        # top frame gridding
        fn_select_frame.grid(column=0,row=0,sticky=(W,E))
        
        c = 0
        self.fit_function_title_box.grid(column=c,row=0); c+=1
        ttk.Label(fn_select_frame,text="Number of Terms:").grid(column=c,
                row=0,sticky=(E),padx=5,pady=5); c+=1
        n_component_box.grid(column=c,row=0,padx=5,pady=5); c+=1
        fit_button.grid(column=c,row=0,padx=5,pady=1); c+=1
        set_param_button.grid(column=c,row=0,padx=5,pady=1); c+=1
        reset_param_button.grid(column=c,row=0,padx=5,pady=1); c+=1
        gui_param_button.grid(column=c,row=0,padx=5,pady=1); c+=1
        set_group_check.grid(column=c,row=0,padx=5,pady=1); c+=1
        
        # run mode gridding
        fit_runmode_label_frame.grid(column=1,row=0,sticky=(E,W))
        self.fit_runmode_label.grid(column=0,row=0,sticky=(E,W))
        
        # routine label gridding
        fit_routine_label_frame.grid(column=2,row=0,sticky=(E,W))
        self.fit_routine_label.grid(column=0,row=0,sticky=(E,W))
        
        # MID FRAME -----------------------------------------------------------
        
        # Scrolling frame to hold fitlines
        yscrollbar = Scrollbar(mid_fit_frame, orient=VERTICAL)         
        self.fit_canvas = Canvas(mid_fit_frame,bd=0,                # make a canvas for scrolling
                yscrollcommand=yscrollbar.set,                      # scroll command receive
                scrollregion=(0, 0, 5000, 5000),confine=True)       # default size
        yscrollbar.config(command=self.fit_canvas.yview)            # scroll command send
        self.runframe = ttk.Frame(self.fit_canvas,pad=5)           # holds 
        
        self.canvas_frame_id = self.fit_canvas.create_window((0,0),    # make window which can scroll
                window=self.runframe,
                anchor='nw')
        self.runframe.bind("<Configure>",self.config_canvas) # bind resize to alter scrollable region
        self.fit_canvas.bind("<Configure>",self.config_runframe) # bind resize to change size of contained frame
        
        # gridding
        self.fit_canvas.grid(column=0,row=0,sticky=(E,W,S,N))
        yscrollbar.grid(column=1,row=0,sticky=(W,S,N))
        
        self.runframe.grid_columnconfigure(0,weight=1) 
        self.fit_canvas.grid_columnconfigure(0,weight=1) 
        self.fit_canvas.grid_rowconfigure(0,weight=1)
        
        self.runframe.bind("<Configure>",self.config_canvas) # bind resize to alter scrollable region
        self.fit_canvas.bind("<Configure>",self.config_runframe) # bind resize to change size of contained frame
        
        # RIGHT FRAME ---------------------------------------------------------
        
        # draw and export buttons
        button_frame = ttk.Frame(right_frame)
        draw_button = ttk.Button(button_frame,text='Draw',command=self.draw_param)
        export_button = ttk.Button(button_frame,text='Export',command=self.export)
        show_button = ttk.Button(button_frame,text='Show All',command=self.show_all_results)
        
        # menus for x and y values
        ttk.Label(right_frame,text="x axis:").grid(column=0,row=1)
        ttk.Label(right_frame,text="y axis:").grid(column=0,row=2)
        ttk.Label(right_frame,text="Annotation:").grid(column=0,row=3)
        
        self.xaxis = StringVar()
        self.yaxis = StringVar()
        self.annotation = StringVar()
        
        self.xaxis.set('')
        self.yaxis.set('')
        self.annotation.set('')
        
        self.xaxis_combobox = ttk.Combobox(right_frame,textvariable=self.xaxis,
                                      state='readonly',width=15)
        self.yaxis_combobox = ttk.Combobox(right_frame,textvariable=self.yaxis,
                                      state='readonly',width=15)
        self.annotation_combobox = ttk.Combobox(right_frame,
                                      textvariable=self.annotation,
                                      state='readonly',width=15)
        
        # gridding
        button_frame.grid(column=0,row=0,columnspan=2)
        draw_button.grid(column=0,row=0,padx=5,pady=5)
        export_button.grid(column=1,row=0,padx=5,pady=5)
        show_button.grid(column=2,row=0,padx=5,pady=5)
        
        self.xaxis_combobox.grid(column=1,row=1,pady=5)
        self.yaxis_combobox.grid(column=1,row=2,pady=5)
        self.annotation_combobox.grid(column=1,row=3,pady=5)
        
        # resizing
        
        # fn select
        fn_select_frame.grid_columnconfigure(1,weight=10)   # Nterms
        fn_select_frame.grid_columnconfigure(4,weight=1)    # Set result to p0
        fn_select_frame.grid_columnconfigure(5,weight=1)    # reset p0
        
        # fitting frame
        self.fit_canvas.grid_columnconfigure(0,weight=1)    # fetch frame 
        self.fit_canvas.grid_rowconfigure(0,weight=1)
        
        fit_data_tab.grid_rowconfigure(1,weight=1)  #fitting area
        
        # right frame
        for i in range(2):
            right_frame.grid_columnconfigure(i,weight=0)
        
        # store lines for fitting
        self.fit_lines = {}
        self.fit_lines_old = {}
        
    # ======================================================================= #
    def __del__(self):
        
        if hasattr(self,'fit_lines'):       del self.fit_lines
        if hasattr(self,'fit_lines_old'):   del self.fit_lines_old
        if hasattr(self,'fitter'):          del self.fitter
        
        # kill buttons and frame
        try:
            for child in self.fetch_data_tab.winfo_children():
                child.destroy()
            self.fetch_data_tab.destroy()
        except Exception:
            pass
            
    # ======================================================================= #
    def _make_shared_var_dict(self):
        """Make the dictionary to make sure all shared checkboxes are synched"""
        
        # get parameter list
        try:
            parlst = [p for p in self.fitter.gen_param_names(
                                                self.fit_function_title.get(),
                                                self.n_component.get())]
        # no paramteters: empty out the variable list
        except KeyError:
            share_var = {}
        
        # make new shared list
        else:
            # re-initialize
            share_var = {p:BooleanVar() for p in parlst}    
            
            # set to old values if they exist
            for p in parlst:
                if p in self.share_var.keys():
                    share_var[p].set(self.share_var[p].get())
                    
        # save to object
        self.share_var = share_var
            
    # ======================================================================= #
    def canvas_scroll(self,event):
        """Scroll canvas with files selected."""
        if event.num == 4:
            self.fit_canvas.yview_scroll(-1,"units")
        elif event.num == 5:
            self.fit_canvas.yview_scroll(1,"units")  
    
    # ======================================================================= #
    def config_canvas(self,event):
        """Alter scrollable region based on canvas bounding box size. 
        (changes scrollbar properties)"""
        self.fit_canvas.configure(scrollregion=self.fit_canvas.bbox("all"))
    
    # ======================================================================= #
    def config_runframe(self,event):
        """Alter size of contained frame in canvas. Allows for inside window to 
        be resized with mouse drag""" 
        self.fit_canvas.itemconfig(self.canvas_frame_id,width=event.width)
    
    # ======================================================================= #
    def populate(self,*args):
        """
            Make tabs for setting fit input parameters. 
        """
        
        # get data
        dl = self.bfit.fetch_files.data_lines
        keylist = [k for k in dl.keys() if dl[k].check_state.get()]
        keylist.sort()
        self.logger.debug('Populating data for %s',keylist)
        
        # get run mode by looking at one of the data dictionary keys
        for key_zero in self.bfit.data.keys(): break
        
        # create fit function combobox options
        try:               
            if self.mode != self.bfit.data[key_zero].mode:
                
                # set run mode 
                self.mode = self.bfit.data[key_zero].mode 
                self.fit_runmode_label['text'] = \
                        self.bfit.fetch_files.runmode_relabel[self.mode]
                self.logger.debug('Set new run mode %s',self.mode)
                
                # set routine
                self.fit_routine_label['text'] = self.fitter.__name__
                
                # set run functions        
                fn_titles = self.fitter.function_names[self.mode]
                self.fit_function_title_box['values'] = fn_titles
                if self.fit_function_title.get() == '':
                    self.fit_function_title.set(fn_titles[0])
                    
        except UnboundLocalError:
            self.fit_function_title_box['values'] = ()
            self.fit_function_title.set("")
            self.fit_runmode_label['text'] = ""
            self.mode = ""
        
        # make shared_var dictionary
        self._make_shared_var_dict()
        
        # delete unused fitline objects
        for k in list(self.fit_lines.keys()):       # iterate fit list
            if k not in keylist:                    # check data list
                self.fit_lines[k].degrid()
                self.fit_lines_old[k] = self.fit_lines[k]
                del self.fit_lines[k]
            
        # make or regrid fitline objects
        n = 0
        for k in keylist:
            if k not in self.fit_lines.keys():
                if k in self.fit_lines_old.keys():
                    self.fit_lines[k] = self.fit_lines_old[k]
                else:
                    self.fit_lines[k] = fitline(self.bfit,self.runframe,dl[k],n)
            self.fit_lines[k].grid(n)
            if n==0 or n%5==0:  self.runframe.update_idletasks()
            n+=1
        
        self.populate_param()
            
    # ======================================================================= #
    def populate_param(self,*args,force_modify=False):
        """
            Populate the list of parameters
            
            force_modify: passed to line.populate
        """
        
        self.logger.debug('Populating fit parameters')
        
        # populate axis comboboxes
        lst = self.draw_components.copy()
        lst.sort()
        
        try:
            parlst = [p for p in self.fitter.gen_param_names(
                                                self.fit_function_title.get(),
                                                self.n_component.get())]
        except KeyError:
            self.xaxis_combobox['values'] = []
            self.yaxis_combobox['values'] = []
            self.annotation_combobox['values'] = []
            return
            
        parlst.sort()
        
        self.xaxis_combobox['values'] = ['']+parlst+lst
        self.yaxis_combobox['values'] = ['']+parlst+lst
        self.annotation_combobox['values'] = ['']+parlst+lst

        self._make_shared_var_dict()
            
        # turn off modify all so we don't cause an infinite loop
        modify_all_value = self.set_as_group.get()
        self.set_as_group.set(False)
            
        # regenerate fitlines
        for k in self.fit_lines.keys():
            self.fit_lines[k].populate(force_modify=force_modify)
            
        # reset modify all value
        self.set_as_group.set(modify_all_value)
            
    # ======================================================================= #
    def do_fit(self,*args):
                
        # fitter
        fitter = self.fitter
        
        # get fitter inputs
        fn_name = self.fit_function_title.get()
        ncomp = self.n_component.get()
        
        self.logger.info('Fitting with "%s" with %d components',fn_name,ncomp)
        
        # build data list
        data_list = []
        for key in self.fit_lines.keys():
            
            # get fit line
            fitline = self.fit_lines[key]
            
            # bdata object
            bdfit = fitline.dataline.bdfit
            bdataobj = bdfit.bd
            
            # pdict
            pdict = {}
            for parname in fitline.parentry.keys():
                
                # get entry values
                pline = fitline.parentry[parname]
                line = []
                for col in fitline.collist:
                    
                    # get number entries
                    if col in ['p0','blo','bhi']:
                        try:
                            line.append(float(pline[col][0].get()))
                        except ValueError as errmsg:
                            self.logger.exception("Bad input.")
                            messagebox.showerror("Error",str(errmsg))
                    
                    # get "Fixed" entry
                    elif col in ['fixed']:
                        line.append(pline[col][0].get())
                
                    # get "Shared" entry
                    elif col in ['shared']:
                        line.append(pline[col][0].get())
                
                # make dict
                pdict[parname] = line
                
            # doptions
            doptions = {}
            doptions['rebin'] = bdfit.rebin.get()
            
            if self.mode == '1f':
                dline = self.bfit.fetch_files.data_lines[key]
                doptions['omit'] = dline.bin_remove.get()
                if doptions['omit'] == dline.bin_remove_starter_line: 
                    doptions['omit'] = ''
                
            elif self.mode == '20':
                pass
                
            elif self.mode == '2h':
                pass
                
            elif self.mode == '2e':
                self.logger.error('2e fitting not implemented')
                raise RuntimeError('2e fitting not implemented')
            
            else:
                self.logger.error('Fitting mode not recognized')
                raise RuntimeError('Fitting mode not recognized')
            
            # make data list
            data_list.append([bdataobj,pdict,doptions])
        
        # call fitter with error message, potentially
        self.fit_input = (fn_name,ncomp,data_list)
        
        # make fitting status window
        fit_status_window = Toplevel(self.bfit.root)
        fit_status_window.lift()
        fit_status_window.resizable(FALSE,FALSE)
        ttk.Label(fit_status_window,text="Please Wait",pad=20).grid(column=0,
                                                    row=0,sticky=(N,S,E,W))
        fit_status_window.update_idletasks()
        self.bfit.root.update_idletasks()
        
        width = fit_status_window.winfo_reqwidth()
        height = fit_status_window.winfo_reqheight()
        
        rt_x = self.bfit.root.winfo_x()
        rt_y = self.bfit.root.winfo_y()
        rt_w = self.bfit.root.winfo_width()
        rt_h = self.bfit.root.winfo_height()
        
        x = rt_x + rt_w/2 - (width/2)
        y = rt_y + rt_h/3 - (width/2)
        
        fit_status_window.geometry('{}x{}+{}+{}'.format(width, height, int(x), int(y)))
        fit_status_window.update_idletasks()
        
        # do fit then kill window
        for d in data_list:
            self.logger.info('Fitting run %d (%d): %s',d[0].run,d[0].year,d[1:])
            
        try:
            # fit_output keyed as {run:[key/par/cov/chi/fnpointer]}
            fit_output = fitter(fn_name=fn_name,ncomp=ncomp,
                                     data_list=data_list,
                                     hist_select=self.bfit.hist_select)
        except Exception as errmsg:
            self.logger.exception('Fitting error')
            fit_status_window.destroy()
            messagebox.showerror("Error",str(errmsg))
            raise errmsg
        else:
            fit_status_window.destroy()
        
        # set output results
        for key in fit_output.keys():
            self.bfit.data[key].set_fitresult(fit_output[key])
            
        # display run results
        for key in self.fit_lines.keys():
            self.fit_lines[key].show_fit_result()
        
        # enable draw buttons on fetch files tab
        for k in self.bfit.fetch_files.data_lines.keys():
            dline = self.bfit.fetch_files.data_lines[k]
            
            dline.draw_fit_checkbox['state'] = 'normal'
            dline.draw_res_checkbox['state'] = 'normal'
            dline.check_fit.set(True)
        
        # draw fit results
        self.bfit.fetch_files.draw_all(ignore_check=False)
        style = self.bfit.draw_style.get()
        
        if style in ['redraw','new']:
            self.bfit.draw_style.set('stack')
        
        self.bfit.draw_style.set(style)
            
    # ======================================================================= #
    def do_gui_param(self,*args):
        """Set initial parmeters with GUI"""
        gui_param_popup(self.bfit)
        
    # ======================================================================= #
    def do_set_result_as_initial(self,*args):
        """Set initial parmeters as the fitting results"""
        
        # turn off modify all 
        modify_all_value = self.set_as_group.get()
        self.set_as_group.set(False)
        
        # set result to initial value
        for k in self.fit_lines.keys():
            
            # get line
            line = self.fit_lines[k]
            
            # get parameters
            parentry = line.parentry
            
            # set 
            for p in parentry.keys():
                parentry[p]['p0'][0].set(parentry[p]['res'][0].get()) 
    
        # reset modify all setting
        self.set_as_group.set(modify_all_value)
        
    # ======================================================================= #
    def do_reset_initial(self,*args):
        """Reset initial parmeters to defaults"""
                
        for k in self.fit_lines.keys():
            self.fit_lines[k].populate(force_modify=True)
    
    # ======================================================================= #
    def draw_residual(self,id,rebin=1,**drawargs):
        """Draw fitting residuals for a single run"""
        
        self.logger.info('Drawing residual for run %s, rebin %d, '+\
                         'standardized: %s, %s',id,rebin,
                         self.bfit.draw_standardized_res.get(),drawargs)
        
        # Settings
        xlabel_dict={'20':"Time (s)",
                     '2h':"Time (s)",
                     '2e':'Frequency (MHz)',
                     '1f':'Frequency (MHz)',
                     '1n':'Voltage (V)'}
        
        # get draw setting 
        draw_style = self.bfit.draw_style
        plt.ion()
        
        # get data and fit results
        data = self.bfit.data[id]
        fit_par = [data.fitpar['res'][p] for p in data.parnames]
        fn = data.fitfn
        data = data.bd
        
        # default label value
        if 'label' not in drawargs.keys():
            label = str(data.run)
        else:
            label = drawargs.pop('label',None)
            
        # set drawing style arguments
        for k in self.bfit.style:
            if k not in drawargs.keys():
                drawargs[k] = self.bfit.style[k]
        
        # make new window
        if draw_style.get() == 'new':
            plt.figure()
            ax = plt.gca()
            
        # get index of label in run and delete that run
        elif draw_style.get() == 'stack':
            ax = plt.gca()
            try:
                idx = [ell.get_label() for ell in ax.containers].index(label)
            except ValueError as err:
                pass
            else:
                del ax.lines[idx]              # clear lines 
                del ax.collections[idx]        # clear errorbar object 
                del ax.containers[idx]         # clear errorbar object
        
        # delete all runs
        elif draw_style.get() == 'redraw':
            ax = plt.gca()
            del ax.lines[:]              # clear lines 
            del ax.collections[:]        # clear errorbar object 
            del ax.containers[:]         # clear errorbar object
            
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        
        # get draw style
        style = self.bfit.draw_style.get()

        # get residuals
        x,a,da = data.asym('c',rebin=rebin)
        res = a - fn(x,*fit_par)
            
        # set x axis
        if   data.mode == '1f': x *= self.bfit.freq_unit_conv
        elif data.mode == '1n': x *= self.bfit.volt_unit_conv    

        # draw 
        if self.bfit.draw_standardized_res.get():
            plt.errorbar(x,res/da,np.zeros(len(x)),label=label,**drawargs)
            
            # draw fill
            ax = plt.gca()
            lim = ax.get_xlim()
            for i in range(1,4):
                ax.fill_between(lim,-1*i,i,color='k',alpha=0.1)
            plt.xlim(lim)
            plt.ylabel(r'Standardized Residual ($\sigma$)')
        else:
            plt.errorbar(x,res,da,label=label,**drawargs)
            plt.ylabel('Residual')
        
        # draw pulse marker
        if '2' in data.mode: plt.axvline(data.get_pulse_s(),ls='--',color='k')
            
        
        # plot elementsplt.ylabel('Residual')
        plt.xlabel(xlabel_dict[self.mode])
        plt.axhline(0,color='k',linestyle='-',zorder=20)
        
        # show
        plt.tight_layout()
        plt.legend()
        
    # ======================================================================= #
    def draw_fit(self,id,**drawargs):
        """Draw fit for a single run"""
        
        self.logger.info('Drawing fit for run %s. %s',id,drawargs)
        
        # Settings
        xlabel_dict={'20':"Time (s)",
                     '2h':"Time (s)",
                     '2e':'Frequency (MHz)',
                     '1f':'Frequency (MHz)',
                     '1n':'Voltage (V)'}
                     
        # get data and fit results
        data = self.bfit.data[id]
        fit_par = [data.fitpar['res'][p] for p in data.parnames]
        fn = data.fitfn
        data = data.bd
        
        # get draw style
        style = self.bfit.draw_style.get()
        
        # label reset
        if 'label' not in drawargs.keys():
            drawargs['label'] = self.bfit.data[id].label.get()
        drawargs['label'] += ' (fit)'
        label = drawargs['label']
        
        # set drawing style
        if style == 'new':
            plt.figure()
        if style == 'stack':
            
            ax = plt.gca()
            try:
                idx = [ell.get_label() for ell in ax.lines].index(label)
            except ValueError as err:
                pass
            else:
                del ax.lines[idx]              # clear lines 
                
        elif style == 'redraw':
            ylim = ax.get_ylim()
            xlim = ax.get_xlim()
            plt.clf()
            plt.ylim(*ylim)
            plt.xlim(*xlim)
            
        # set drawing style arguments
        for k in self.bfit.style:
            if k not in drawargs.keys() \
                    and 'marker' not in k \
                    and k not in ['elinewidth','capsize']:
                drawargs[k] = self.bfit.style[k]
        
        # linestyle reset
        if drawargs['linestyle'] == 'None': 
            drawargs['linestyle'] = '-'
        
        # draw
        t,a,da = data.asym('c')
        fitx = np.arange(self.n_fitx_pts)/float(self.n_fitx_pts)*\
                                                    (max(t)-min(t))+min(t)
        
        if   data.mode == '1f': fitxx = fitx*self.bfit.freq_unit_conv
        elif data.mode == '1n': fitxx = fitx*self.bfit.volt_unit_conv
        else:                   fitxx = fitx
    
        plt.plot(fitxx,fn(fitx,*fit_par),zorder=10,**drawargs)
        
        # plot elements
        plt.ylabel('Asymmetry')
        plt.xlabel(xlabel_dict[self.mode])
        
        # show
        plt.tight_layout()
        plt.legend()
        
    # ======================================================================= #
    def draw_param(self,*args):
        
        # make sure plot shows
        plt.ion()
        
        # get draw components
        xdraw = self.xaxis.get()
        ydraw = self.yaxis.get()
        ann = self.annotation.get()
        
        self.logger.info('Draw fit paramters "%s" vs "%s" with annotation "%s"',
                          ydraw,xdraw,ann)
        
        # get plottable data
        try:
            xvals, xerrs = self.get_values(xdraw)
            yvals, yerrs = self.get_values(ydraw)
        except UnboundLocalError as err:
            self.logger.error('Bad input parameter selection')
            messagebox.showerror("Error",'Select two input parameters')
            raise err
        except (KeyError,AttributeError) as err:
            self.logger.error('Parameter "%s or "%s" not found for drawing',
                              xdraw,ydraw)
            messagebox.showerror("Error",
                    'Drawing parameter "%s" or "%s" not found' % (xdraw,ydraw))
            raise err
            
        # get annotation
        if ann != '':
            try:
                ann, _ = self.get_values(ann)
            except UnboundLocalError:
                ann = None
            except (KeyError,AttributeError) as err:
                self.logger.error('Bad input annotation value "%s"',ann)
                messagebox.showerror("Error",
                        'Annotation "%s" not found' % (ann))
                raise err
        
        # fix annotation values (blank to none)
        else:
            ann = None
        
        # fix annotation values (round floats)
        if ann is not None: 
            number_string = '%.'+'%df' % self.bfit.rounding
            for i,a in enumerate(ann):
                if type(a) in [float,np.float64]:
                    ann[i] = number_string % np.around(a,self.bfit.rounding)
            
        # get draw style
        style = self.bfit.draw_style.get()
        
        if style == 'new':
            plt.figure()
        elif style == 'redraw':
            plt.clf()
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        
        # draw
        if type(xvals[0]) == str:
            plt.xticks(np.arange(len(xvals)))
            plt.gca().set_xticklabels(xvals)
            xvals = np.arange(len(xvals))
        
        if type(yvals[0]) == str:
            plt.yticks(np.arange(len(yvals)))
            plt.gca().set_yticklabels(yvals)
            yvals = np.arange(len(yvals))
        
        f = plt.errorbar(xvals,yvals,xerr=xerrs,yerr=yerrs,fmt='.')
        self._annotate(xvals,yvals,ann,color=f[0].get_color())
        
        # plot elements
        plt.xlabel(xdraw)
        plt.ylabel(ydraw)
        plt.tight_layout()
        
    # ======================================================================= #
    def export(self,savetofile=True):
        
        # get values and errors
        val = {}
        
        for v in self.xaxis_combobox['values']:
            if v == '': continue
            
            try:
                v2 = self.get_values(v) 
            except Exception: 
                traceback.print_exc()
            else:
                val[v] = v2[0]
                val['Error '+v] = v2[1]
        
        # make data frame for output
        df = pd.DataFrame(val)
        df.set_index('Run Number',inplace=True)
        
        # drop completely empty columns
        bad_cols = [c for c in df.columns if all(df[c].isna())]
        for c in bad_cols:
            df.drop(c,axis='columns',inplace=True)
        
        if savetofile:
            
            # get file name
            filename = filedialog.asksaveasfilename()
            self.logger.info('Exporting parameters to "%s"',filename)
            
            # check extension 
            if os.path.splitext(filename)[1] == '':
                filename += '.csv'
            df.to_csv(filename)
            self.logger.debug('Export success')
        else:
            self.logger.info('Returned exported parameters')
            return df
        
    # ======================================================================= #
    def get_values(self,select):
        """ Get plottable values"""
        data = self.bfit.data
        runs = list(data.keys())
        runs.sort()
    
        self.logger.debug('Fetching parameter %s',select)
    
        # Data file options
        if select == 'Temperature (K)':
            val = [data[r].temperature.mean for r in runs]
            err = [data[r].temperature.std for r in runs]
        
        elif select == 'B0 Field (T)':
            val = [data[r].field for r in runs]
            err = [data[r].field_std for r in runs]
        
        elif select == 'RF Level DAC':
            try:
                val = [data[r].camp.rf_dac.mean for r in runs]
                err = [data[r].camp.rf_dac.std for r in runs]
            except AttributeError:
                pass
        
        elif select == 'Platform Bias (kV)':
            try:
                val = [data[r].bias for r in runs]
                err = [data[r].bias_std for r in runs]
            except AttributeError:
                pass
                
        elif select == 'Impl. Energy (keV)':
            val =  [data[r].bd.beam_kev() for r in runs]
            err =  [data[r].bd.beam_kev(get_error=True) for r in runs]
        
        elif select == 'Run Duration (s)':
            val = [data[r].bd.duration for r in runs]
            err = [np.nan for r in runs]
        
        elif select == 'Run Number':
            val = [data[r].run for r in runs]
            err = [np.nan for r in runs]
        
        elif select == 'Sample':
            val = [data[r].bd.sample for r in runs]
            err = [np.nan for r in runs]
            
        elif select == 'Start Time':
            val = [data[r].bd.start_date for r in runs]
            err = [np.nan for r in runs]
        
        elif select == 'Title':
            val = [data[r].bd.title for r in runs]
            err = [np.nan for r in runs]
        
        # fitted parameter options
        elif select in self.fitter.gen_param_names(self.fit_function_title.get(),
                                                   self.n_component.get()):
            val = []
            err = []
            
            for r in runs:
                try:
                    val.append(self.bfit.data[r].fitpar['res'][select])
                    err.append(self.bfit.data[r].fitpar['dres'][select])
                except KeyError:
                    val.append(np.nan)
                    err.append(np.nan)
    
        try:
            return (val,err)
        except UnboundLocalError:
            self.logger.warning('Parameter selection "%s" not found' % select)
            raise AttributeError('Selection "%s" not found' % select)
    
    # ======================================================================= #
    def modify_all(self,*args,source=None,par='',column=''):
        """
            Modify all input fields of each line to match the altered one, 
            conditional on self.set_as_group
            
            source_line: the fitline to copy
            parameter:   name of the parameter to copy
            column:      name of the column to copy            
        """
        
        setall = self.set_as_group.get()
        for k in self.fit_lines.keys():
            self.fit_lines[k].set_input(source,par,column,setall)        
    
    # ======================================================================= #
    def show_all_results(self):
        """Make a window to display table of fit results"""
        
        # get fit results
        df = self.export(savetofile=False)
        show_param_popup(df)
        
    # ======================================================================= #
    def return_binder(self):
        """
            Binding to entery key press, depending on focus. 
            
            FOCUS                   ACTION
            
            comboboxes or buttons   draw_param
                in right frame
            else                    do_fit
        """
    
        # get focus
        focus = self.bfit.root.focus_get()
        
        # right frame items
        draw_par_items = (  self.xaxis_combobox,
                            self.yaxis_combobox,
                            self.annotation_combobox)
                            
        # do action 
        if focus in draw_par_items:
            self.draw_param()
        elif focus == self.bfit.root:
            pass
        else:
            self.do_fit()
            
    # ======================================================================= #
    def _annotate(self,x,y,ptlabels,color='k'):
        """Add annotation"""
        
        # base case
        if ptlabels is None: return
        
        # do annotation
        for label,xcoord,ycoord in zip(ptlabels,x,y):        
            if type(label) != type(None):
                plt.annotate(label,
                             xy=(xcoord,ycoord),
                             xytext=(-3, 20),
                             textcoords='offset points', 
                             ha='right', 
                             va='bottom',
                             bbox=dict(boxstyle='round,pad=0.1',
                                       fc=color, 
                                       alpha=0.1),
                             arrowprops=dict(arrowstyle = '->', 
                                             connectionstyle='arc3,rad=0'),
                            fontsize='xx-small',
                            )    
                            
# =========================================================================== #
# =========================================================================== #
class fitline(object):
    """
        Instance variables 
        
            bfit        pointer to top class
            dataline    pointer to dataline object in fetch_files_tab
            parent      pointer to parent object (frame)
            parlabels   label objects, saved for later destruction
            parentry    [parname][colname] of ttk.Entry objects saved for 
                            retrieval and destruction
            run_label   label for showing which run is selected
            fitframe    mainframe for this tab. 
    """
    
    n_runs_max = 5      # number of runs before scrollbar appears
    collist = ['p0','blo','bhi','res','dres','chi','fixed','shared']
    selected = 0        # index of selected run 
    
    # ======================================================================= #
    def __init__(self,bfit,parent,dataline,row):
        """
            Inputs:
                bfit:       top level pointer
                parent:     pointer to parent frame object
                dataline:   fetch_files.dataline object corresponding to the 
                                data we want to fit
                row:        grid position
        """
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing fit line for run %d in row %d',
                          dataline.run,row)
        
        # initialize
        self.bfit = bfit
        self.parent = parent
        self.dataline = dataline
        self.row = row
        self.parlabels = []
        self.parentry = {}
             
        # get parent frame
        fitframe = ttk.Frame(self.parent,pad=(5,0))
        
        # label for displyaing run number
        self.run_label = ttk.Label(fitframe,text='[ %d ]' % (self.dataline.run),
                                    font='bold')
     
        # Parameter input labels
        c = 0
        ttk.Label(fitframe,text='Parameter').grid(    column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Initial Value').grid(column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Low Bound').grid(    column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='High Bound').grid(   column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Result').grid(       column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Error').grid(        column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='ChiSq').grid(        column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Fixed').grid(        column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Shared').grid(       column=c,row=1,padx=5); c+=1
        
        # grid the run_label
        self.run_label.grid(column=0,row=0,padx=5,pady=5,columnspan=c-1)
        
        # save frame 
        self.fitframe = fitframe
        
        # resizing
        for i in range(c):
            self.fitframe.grid_columnconfigure(i,weight=1)
        
        # fill with initial parameters
        self.parlabels = []     # track all labels and inputs
        self.populate()
                
    # ======================================================================= #
    def __del__(self):
        
        if hasattr(self,'parlabels'):   del self.parlabels
        
        # kill buttons and frame
        try:
            for child in self.parent.winfo_children():
                child.destroy()
        except Exception:
            pass
    
        if hasattr(self,'parentry'):    del self.parentry
    
    # ======================================================================= #
    def populate(self,force_modify=False):
        """
            Fill and grid new parameters. Reuse old fields if possible
            
            force_modify: if true, clear and reset parameter inputs. 
        """
        
        # get list of parameters and initial values
        try:
            plist = self.get_new_parameters()
        except KeyError:
            return          # returns if no parameters found
        finally:
            
            n_old_par = len(self.parlabels)
            n_new_par = len(plist)
            min_n_par = min(n_old_par,n_new_par)
            
            parkeys = list(self.parentry.keys())    # old parameter keys
            parkeys.sort()
            
            # destroy excess labels and entries
            for i in range(n_new_par,n_old_par):
                self.parlabels[-1].destroy()
                for p in self.parentry[parkeys[i]].keys():
                    self.parentry[parkeys[i]][p][1].destroy()
                    
                del self.parlabels[-1]
                del self.parentry[parkeys[i]]
        
        self.logger.debug('Populating parameter list with %s',plist)

        # get data and frame
        fitframe = self.fitframe
        fitdat = self.dataline.bdfit
        
        # labels ------------------------------------------------------------
        c = 0

        # repurpose old labels
        for i in range(min_n_par):
            self.parlabels[i]['text'] = plist[i]
        
        # make new labels
        for i in range(n_old_par,n_new_par):
            self.parlabels.append(ttk.Label(fitframe,text=plist[i],justify=LEFT))
            self.parlabels[-1].grid(column=c,row=2+i,padx=5,sticky=E)
        
        # move all parameters entries and values to new key set
        new_parentry = {}
        for i in range(min_n_par):
            p = plist[i]
            p_old = parkeys[i]
            new_parentry[p] = self.parentry[p_old]
        self.parentry = new_parentry
        
        # initial parameters ------------------------------------------------- 
        
        # repurpose old parameter fields
        r = 1
        for i in range(min_n_par):
            p = plist[i]
            c = 1
            r += 1
            
            # clear entry and insert new text
            for col in ('p0','blo','bhi'):                
                entry = self.parentry[p][col][1]
                
                if force_modify:
                    entry.delete(0,'end')
                    
                if not entry.get():
                    entry.insert(0,str(fitdat.fitpar[col][p]))
                entry.grid(column=c,row=r,padx=5,sticky=E); c += 1
                    
        r = min_n_par+1
                
        # make new parameter fields
        for i in range(n_old_par,n_new_par):
            p = plist[i]
            self.parentry[p] = {}
            
            c = 0               # gridding column         
            r += 1              # gridding row         
            
            for col in ('p0','blo','bhi'):
                c += 1
                
                value = StringVar()
                entry = ttk.Entry(fitframe,textvariable=value,width=10)
                entry.insert(0,str(fitdat.fitpar[col][p]))
                entry.grid(column=c,row=r,padx=5,sticky=E)
                self.parentry[p][col] = (value,entry)
        
        # fit results ------------------------------------------------------- 
        
        # repurpose old result fields
        r = 1
        for i in range(min_n_par):
            r += 1
            c = 4
            p = plist[i]
            
            # clear text in parentry fields
            for col in ('res','dres','chi'):
                if col in self.parentry[p].keys():  # exception needed for chi
                    par = self.parentry[p][col][1]
                    par.delete(0,'end')
                    
                    if col == 'chi':
                        par.grid(column=c,row=r,padx=5,sticky=E,rowspan=len(plist))
                    else:
                        par.grid(column=c,row=r,padx=5,sticky=E)
                c += 1
                    
            # do fixed box
            self.parentry[p]['fixed'][1].grid(column=c,row=r,padx=5,sticky=E); c += 1
            
            # do shared box
            self.parentry[p]['shared'][1].grid(column=c,row=r,padx=5,sticky=E); c += 1
        
        # make new result fields
        r = min_n_par+1
        for i in range(n_old_par,n_new_par):
            r += 1
            c = 4
            p = plist[i]
            
            # do results
            par_val = StringVar()
            par = ttk.Entry(fitframe,textvariable=par_val,width=15)
            par['state'] = 'readonly'
            par['foreground'] = 'black'
            
            dpar_val = StringVar()
            dpar = ttk.Entry(fitframe,textvariable=dpar_val,width=10)
            dpar['state'] = 'readonly'
            dpar['foreground'] = 'black'
                                     
            par. grid(column=c,row=r,padx=5,sticky=E); c += 1
            dpar.grid(column=c,row=r,padx=5,sticky=E); c += 1

            # do chi only once
            if i==0:
                chi_val = StringVar()
                chi = ttk.Entry(fitframe,textvariable=chi_val,width=7)
                chi['state'] = 'readonly'
                chi['foreground'] = 'black'
                
                chi.grid(column=c,row=r,padx=5,sticky=E,rowspan=len(plist)); 
                self.parentry[p]['chi'] = (chi_val,chi)
            c += 1
            
            # save ttk.Entry objects in dictionary [parname][colname]
            self.parentry[p]['res'] = (par_val,par)
            self.parentry[p]['dres'] = (dpar_val,dpar)
            
            # do fixed box
            value = BooleanVar()
            entry = ttk.Checkbutton(fitframe,text='',\
                                     variable=value,onvalue=True,offvalue=False)
            entry.grid(column=c,row=r,padx=5,sticky=E); c += 1
            self.parentry[p]['fixed'] = (value,entry)
            
            # do shared box
            entry = ttk.Checkbutton(fitframe,text='',onvalue=True,offvalue=False)
            entry.grid(column=c,row=r,padx=5,sticky=E); c += 1
            self.parentry[p]['shared'] = [value,entry]
            
        for p in self.parentry.keys():
            parentry = self.parentry[p]
            
            # shared box value synchronization
            var = self.bfit.fit_files.share_var[p]
            parentry['shared'][0] = var
            parentry['shared'][1].config(variable=var)
            
            # set parameter entry synchronization
            for k in ('p0','blo','bhi','fixed'):
                
                # make callback function
                callback = partial(self.bfit.fit_files.modify_all,
                                   source=self,par=p,column=k)
                
                # remove old trace callbacks
                for t in parentry[k][0].trace_vinfo():
                    parentry[k][0].trace_vdelete(*t)
                
                # set new trace callback
                parentry[k][0].trace_id = parentry[k][0].trace("w", callback)
                parentry[k][0].trace_callback = callback
        
    # ======================================================================= #
    def get_new_parameters(self):
        """
            Fetch initial parameters from fitter, set to data.    
            
            plist: Dictionary of initial parameters {par_name:par_value}
        """
        
        run = self.dataline.id
        
        # get pointer to fit files object
        fit_files = self.bfit.fit_files
        fitter = fit_files.fitter
        ncomp = fit_files.n_component.get()
        fn_title = fit_files.fit_function_title.get()
        
        # get list of parameter names
        plist = list(fitter.gen_param_names(fn_title,ncomp))
        plist.sort()
        
        # get init values
        values = fitter.gen_init_par(fn_title,ncomp,self.bfit.data[run].bd)
        
        # set to data
        self.bfit.data[run].set_fitpar(values)
        
        return tuple(plist)
        
    # ======================================================================= #
    def grid(self,row):
        """Re-grid a dataline object so that it is in order by run number"""
        self.row = row
        self.fitframe.grid(column=0,row=row, sticky=(W,N))
           
    # ======================================================================= #
    def degrid(self):
        """Remove displayed dataline object from file selection. """
        
        self.logger.info('Degridding fitline for run %d (%d)',self.dataline.run,
                                                          self.dataline.year)
        self.fitframe.grid_forget()
    
    # ======================================================================= #
    def set_input(self,source_line,parameter,column,set_all):
        """
            Set the input value for a given parameter to match the value in 
            another fitline
            
            source_line: the fitline to copy
            parameter:   name of the parameter to copy
            column:      name of the column to copy
            set_all:     boolean corresponding to fit_files.set_as_group    
        """
        
        # get parameter entry line and sharing
        try:
            parentry = self.parentry[parameter]
            shared = parentry['shared'][0].get()
            source_entry = source_line.parentry[parameter]
        except KeyError:
            return
        
        # set value
        if set_all or shared:
            
            p = parentry[column][0]
            
            # remove the trace
            p.trace_vdelete("w",p.trace_id)
            
            # set the value
            p.set(source_entry[column][0].get())
    
            # add the trace back
            p.trace_id = p.trace("w", p.trace_callback)
    
    # ======================================================================= #
    def show_fit_result(self):
        
        self.logger.debug('Showing fit result for run %d',self.dataline.run)
        
        # Set up variables
        displays = self.parentry
        
        try:
            data = self.dataline.bdfit
        except KeyError:
            return
            
        try:
            chi = data.chi
        except AttributeError:
            return 
        
        # display
        for parname in displays.keys():
            disp = displays[parname]
            showstr = "%"+".%df" % self.bfit.rounding
            disp['res'][0].set(showstr % data.fitpar['res'][parname])
            disp['dres'][0].set(showstr % data.fitpar['dres'][parname])
            
            if 'chi' in disp.keys():
                disp['chi'][0].set(showstr % chi)
         
    

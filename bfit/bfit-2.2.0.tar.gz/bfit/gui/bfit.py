#!/usr/bin/python3
# Fit and draw BNMR data 
# Derek Fujimoto
# November 2017

from tkinter import *
from tkinter import ttk,filedialog,messagebox
from bdata import bdata
from scipy.optimize import curve_fit

try:
    from mpl_toolkits.mplot3d import Axes3D
except ImportError as errmsg:
    print('No 3D axes drawing available')
    print(errmsg)

import sys,os,datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import bdata as bd
import webbrowser
import subprocess
import importlib
import logging

from bfit import __version__,logger_name
from bfit.gui.fileviewer_tab import fileviewer
from bfit.gui.fetch_files_tab import fetch_files
from bfit.gui.fit_files_tab import fit_files
from bfit.gui.zahersCalculator import zahersCalculator
from bfit.gui.monikasCalculator import monikasCalculator
from bfit.gui.drawstyle_popup import drawstyle_popup
from bfit.gui.redraw_period_popup import redraw_period_popup
from bfit.gui.set_ppm_reference_popup import set_ppm_reference_popup
from bfit.gui.set_histograms_popup import set_histograms_popup
from bfit.gui.fitdata import fitdata

__doc__="""
    BNMR/BNQR data visualization and curve fitting.
    
    Hotkeys:
    
        General
            Command-------------Effect
            ctrl+n:             set draw mode "new"
            ctrl+s:             set draw mode "stack"
            ctrl+r:             set draw mode "redraw"
    
        File Details
            Command-------------Effect
            return:             fetch file
            ctrl+return:        draw file
            shift+return:       draw file
            ctrl+a:             toggle check all
        Fit 
            Fetch Data
                Command---------Focus-----------------------Effect    
                return:         run/year entry:             fetch
                                SLR rebin:                  set checked
                                bin omit entry (checked):   set checked
                ctrl+return:                                draw file
                shift+return:                               draw file
                
            Fit Data
            
        View Fit Results
    
    Derek Fujimoto
    November 2017
    """

# =========================================================================== #
class bfit(object):
    """
        Build the mainframe and set up the runloop for the tkinter GUI. 
        
        Data Fields:
            asym_dict_keys: asym calc and draw types
            data: dict of fitdata objects for drawing/fitting, keyed by run #
            draw_style: draw window types # stack, redraw, new
            draw_components: list of titles for labels, options to export, draw.
            draw_ppm: BoolVar for drawing as ppm shift
            draw_standardized_res: BoolVar for drawing residuals as standardized
            freq_unit_conv: conversion rate from original to display units
            hist_select: histogram selection for asym calcs (blank for defaults)
            label_default: StringVar() name of label defaults for fetch
            logger: logging object 
            logger_name: string of unique logger name
            ppm_reference: reference freq in Hz for ppm calulations
            probe_species: StringVar() name of probe species, bdata.life key.
            mainframe: main frame for the object
            notebook: contains all tabs for operations:
                fileviewer
                fetch_files
                fit_files
            root: tkinter root instance
            rounding: number of decimal places to round results to in display
            routine_mod: module with fitting routines
            update_period: update spacing in s. 
            volt_unit_conv: conversion rate from original to display units
    """
    probe_species = "8Li" # unused
    bnmr_archive_label = "BNMR_ARCHIVE"
    bnqr_archive_label = "BNQR_ARCHIVE"
    update_period = 20  # s
    ppm_reference = 41270000 # Hz
    rounding = 5       # number of decimal places to round results to in display
    hist_select = ''    # histogram selection for asym calculations
    freq_unit_conv = 1.e-6   # conversion rate from original to display units
    volt_unit_conv = 1.e-3   # conversion rate from original to display units
    
    asym_dict_keys = {'20':("Combined Helicity","Split Helicity",
                            "Matched Helicity","Raw Histograms"),
                      '1f':("Combined Helicity","Split Helicity","Raw Scans",
                            "Shifted Split","Shifted Combined","Raw Histograms"),
                      '1n':("Combined Helicity","Split Helicity","Raw Scans",
                            "Matched Peak Finding","Raw Histograms"),
                      '2e':("Combined Hel Raw","Combined Hel Slopes",      
                            "Combined Hel Diff","Split Hel Raw",
                            "Split Hel Slopes","Split Hel Diff"),
                      '2h':("Combined Helicity","Split Helicity",
                            "Matched Helicity",
                            "Alpha Diffusion",
                            "Combined Hel (Alpha Tag)","Split Hel (Alpha Tag)",
                            "Combined Hel (!Alpha Tag)","Split Hel (!Alpha Tag)",
                            "Raw Histograms")}
    
    data = {}   # for fitdata objects
    
    # define draw componeents in draw_param and labels
    draw_components = ['Temperature (K)','B0 Field (T)', 'RF Level DAC', 
                       'Platform Bias (kV)', 'Impl. Energy (keV)', 
                       'Run Duration (s)', 'Run Number','Sample', 'Start Time',
                       'Title']

    try: 
        bnmr_data_dir = os.environ[bnmr_archive_label]
        bnqr_data_dir = os.environ[bnqr_archive_label]
    except(AttributeError,KeyError):
        bnmr_data_dir = os.getcwd()
        bnqr_data_dir = os.getcwd()
        
        messagebox.showwarning("Set Environment Variables", 
            "Environment variables "+\
            "\n\nBNMR_ARCHIVE\n\nand\n\nBNQR_ARCHIVE\n\nnot found. "+\
            "\n\nSet these such that "+\
            "the data can be accessed in a manner such as "+\
            "\n\n$BNMR_ARCHIVE/year/datafile.msr")
        
    # ======================================================================= #
    def __init__(self):
        
        # logging
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing ' + '-'*50)
        
        # root 
        root = Tk()
        root.title("BFIT - BNMR/BNQR Data Fitting and Visualization "+\
                   "(version %s)" % __version__)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # icon
        try:
            img = PhotoImage(file=os.path.dirname(__file__)+'/../images/icon.gif')
            root.tk.call('wm', 'iconphoto', root._w, img)
        except Exception as err:
            print(err)
            
        # key bindings
        root.bind('<Return>',self.return_binder)             
        root.bind('<KP_Enter>',self.return_binder)
        root.bind('<Control-Key-Return>',self.draw_binder)      
        root.bind('<Control-Key-KP_Enter>',self.draw_binder)
        root.bind('<Shift-Key-Return>',self.draw_binder)
        root.bind('<Shift-Key-KP_Enter>',self.draw_binder)
        
        root.bind('<Control-Key-n>',self.set_style_new)
        root.bind('<Control-Key-s>',self.set_style_stack)
        root.bind('<Control-Key-r>',self.set_style_redraw)
        root.bind('<Control-Key-a>',self.set_check_all)
        
        root.bind('<Control-Key-1>',lambda x: self.set_focus_tab(idn=0))
        root.bind('<Control-Key-2>',lambda x: self.set_focus_tab(idn=1))
        root.bind('<Control-Key-3>',lambda x: self.set_focus_tab(idn=2))
        
        root.bind("<Button-4>",self.scroll_binder) 
        root.bind("<Button-5>",self.scroll_binder)
        
        # event bindings
        root.protocol("WM_DELETE_WINDOW",self.on_closing)
        
        # drawing styles
        self.style = {'linestyle':'None',
                      'linewidth':mpl.rcParams['lines.linewidth'],
                      'marker':'.',
                      'markersize':mpl.rcParams['lines.markersize'],
                      'capsize':0.,
                      'elinewidth':mpl.rcParams['lines.linewidth'],
                      'alpha':1.,
                      'fillstyle':'full'}
        
        # load default fitting routines
        self.routine_mod = importlib.import_module(
                                                'bfit.fitting.default_routines')
        # main frame
        mainframe = ttk.Frame(root,pad=5)
        mainframe.grid(column=0,row=0,sticky=(N,W,E,S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # Menu bar options ----------------------------------------------------
        root.option_add('*tearOff', FALSE)
        menubar = Menu(root)
        root['menu'] = menubar
        
        # File
        menu_file = Menu(menubar)
        menu_file.add_command(label='Search archive',command=self.search_archive)
        menu_file.add_command(label='BNMR Oscillating Field Calculator',\
                command=monikasCalculator)
        menu_file.add_command(label='BNQR Static Field Calculator',\
                command=zahersCalculator)
        menu_file.add_command(label='Export',command=self.do_export)
        menu_file.add_command(label='Exit',command=sys.exit)
        menubar.add_cascade(menu=menu_file, label='File')
        
        # Settings
        menu_settings = Menu(menubar)
        menubar.add_cascade(menu=menu_settings, label='Settings')
        menu_settings_dir = Menu(menu_settings)
        menu_settings_lab = Menu(menu_settings)
        menu_settings_probe = Menu(menu_settings)
        
        # Settings cascade commands
        menu_settings.add_cascade(menu=menu_settings_dir,label='Data directory')
        menu_settings.add_cascade(menu=menu_settings_lab,label='Default labels')
        menu_settings.add_command(label='Drawing style',
                command=self.set_draw_style)
        menu_settings.add_command(label='Fitting routines',
                command=self.set_fit_routines)
        menu_settings.add_command(label='Histograms',
                command=self.set_histograms)
        menu_settings.add_command(label='PPM Reference Frequecy',
                command=self.set_ppm_reference)
        menu_settings.add_cascade(menu=menu_settings_probe,label='Probe Species')
        menu_settings.add_command(label='Redraw period',
                command=self.set_redraw_period)
        menu_settings.add_command(label="System matplotlibrc",\
                command=self.set_matplotlib)
        
        # Settings: data directory
        menu_settings_dir.add_command(label="BNMR",command=self.set_bnmr_dir)
        menu_settings_dir.add_command(label="BNQR",command=self.set_bnqr_dir)
        
        # Settings: set label default
        self.label_default = StringVar()
        self.label_default.set('Run Number')
        for dc in self.draw_components:
            menu_settings_lab.add_radiobutton(label=dc,
                variable=self.label_default,value=dc,command=self.set_all_labels)
        
        # Settings: set probe species
        self.probe_species = StringVar()
        self.probe_species.set('Li8')
        lifekeys = list(bd.life.keys())
        lifekeys.sort()
        for k in lifekeys:
            if 'err' not in k: 
                menu_settings_probe.add_radiobutton(label=k,
                        variable=self.probe_species,
                        value=k,
                        command=self.set_probe_species)
        
        # Draw style
        self.draw_style = StringVar()
        self.draw_style.set("stack")
        self.draw_ppm = BooleanVar()
        self.draw_ppm.set(False)
        self.draw_standardized_res = BooleanVar()
        self.draw_standardized_res.set(False)
        
        menu_draw = Menu(menubar)
        menubar.add_cascade(menu=menu_draw,label='Draw Mode')
        menu_draw.add_radiobutton(label="Draw in new window",\
                variable=self.draw_style,value='new',underline=8)
        menu_draw.add_radiobutton(label="Stack in existing window",\
                variable=self.draw_style,value='stack',underline=0)
        menu_draw.add_radiobutton(label="Redraw in existing window",\
                variable=self.draw_style,value='redraw',underline=0)
        
        menu_draw.add_separator()
        menu_draw.add_checkbutton(label="Draw 1f as PPM shift",\
                variable=self.draw_ppm,underline=0)
        menu_draw.add_checkbutton(label="Draw residuals as standardized",\
                variable=self.draw_standardized_res,underline=0)
        
        # Help
        menu_help = Menu(menubar)
        menubar.add_cascade(menu=menu_help, label='Help')
        menu_help.add_command(label='Show help wiki',command=self.help)
        menu_help.add_command(label='Report an issue',command=self.report_issue)
        menu_help.add_command(label='Update bfit',command=self.update_bfit)
        
        # Top Notebook: File Viewer, Fit, Fit Viewer -------------------------
        noteframe = ttk.Frame(mainframe,relief='sunken',pad=5)
        notebook = ttk.Notebook(noteframe)
        file_viewer_tab = ttk.Frame(notebook)
        fetch_files_tab = ttk.Frame(notebook)
        fit_files_tab = ttk.Frame(notebook)
        
        notebook.add(file_viewer_tab,text='File Details')
        notebook.add(fetch_files_tab,text='Fetch Data')
        notebook.add(fit_files_tab,text='Fit Data')
        
        # set drawing styles
        notebook.bind("<<NotebookTabChanged>>",
            lambda event: self.set_tab_change(event.widget.index("current")))
    
        # gridding
        notebook.grid(column=0,row=0,sticky=(N,E,W,S))
        noteframe.grid(column=0,row=0,sticky=(N,E,W,S))
        noteframe.columnconfigure(0,weight=1)
        noteframe.rowconfigure(0,weight=1)
        
        # Notetabs
        self.fileviewer = fileviewer(file_viewer_tab,self)
        self.fetch_files = fetch_files(fetch_files_tab,self)
        self.fit_files = fit_files(fit_files_tab,self)
        
        # set instance variables ---------------------------------------------
        self.root = root
        self.mainframe = mainframe
        self.notebook = notebook
        
        # logging 
        self.logger.debug('Initialization success. Starting mainloop.')
        
        # runloop
        self.root.mainloop()
        
    # ======================================================================= #
    def __del__(self):
        if hasattr(self,'fileviewer'):  del self.fileviewer
        if hasattr(self,'fetch_files'): del self.fetch_files
        if hasattr(self,'fitviewer'):   del self.fitviewer
    
        try:
            plt.close('all')
        except ImportError:
            pass
    
    # ======================================================================= #
    def do_export(self):
        """Export selected files to csv format. Calls the appropriate function 
        depending on what tab is selected. """ 
        
        idx = self.notebook.index('current')
        self.logger.debug('Exporting for notebook index %d',idx)
        if idx == 0:        # data viewer
            self.fileviewer.export()
        elif idx == 1:        # data fetch_files
            self.fetch_files.export()
        elif idx == 2:        # fit viewer
            self.fit_files.export()
        else:
            pass
    
    # ======================================================================= #
    def draw(self,data,asym_type,rebin=1,option='',**drawargs):
        """Draw the selected file"""
        
        self.logger.info('Drawing run %d (%d). mode: %s, rebin: %d, '+\
                     'option: %s, style: %s, %s',
                     data.run,
                     data.year,
                     asym_type,
                     rebin,
                     option,
                     self.draw_style.get(),
                     drawargs)
        
        # Settings
        xlabel_dict={'20':"Time (s)",
                     '2h':"Time (s)",
                     '2e':'Frequency (MHz)',
                     '1f':'Frequency (MHz)',
                     '1n':'Voltage (V)'}
        ylabel_dict={'ad':r'$N_\alpha/N_\beta$', # otherwise, label as Asymmetry
                     'hs':r'Asym-Asym($\nu_{min}$)',
                     'cs':r'Asym-Asym($\nu_{min}$)',
                     'rhist':'Counts'}
        x_tag={'20':"time_s",
               '2h':"time_s",
               '2e':"time",
               '1f':'freq',
               '1n':'mV'}
        
        # get draw setting 
        draw_style = self.draw_style
        plt.ion()
        
        # default label value
        if 'label' not in drawargs.keys():
            label = str(data.run)
        else:
            label = drawargs.pop('label',None)
            
        # set drawing style arguments
        for k in self.style:
            if k not in drawargs.keys():
                drawargs[k] = self.style[k]
        
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
        
        # get asymmetry: raw scans
        if asym_type == 'r' and data.mode in ['1f','1n']:
            a = data.asym('raw',omit=option,hist_select=self.hist_select)
            x = np.arange(len(a.p[0]))
            idx_p = a.p[0]!=0
            idx_n = a.n[0]!=0
            
            xlabel = 'Bin'
            plt.errorbar(x[idx_p],a.p[0][idx_p],a.p[1][idx_p],
                    label=label+"($+$)",**drawargs)
            plt.errorbar(x[idx_n],a.n[0][idx_n],a.n[1][idx_n],
                    label=label+"($-$)",**drawargs)
        
        # do 2e mode
        elif '2e' in asym_type:
            
            # get asym
            a = data.asym(hist_select=self.hist_select)
        
            # draw
            if asym_type in ["2e_rw_c","2e_rw_h"]:
                
                # make 3D axes
                if type(plt.gcf()) == type(None):   plt.figure()
                ax = plt.gcf().add_subplot(111,projection='3d',
                                           label=str(len(plt.gcf().axes)))
                
                # get rid of bad draw options
                try:                del drawargs['capsize']
                except KeyError:    pass
                try:                del drawargs['elinewidth']
                except KeyError:    pass
                
                # for every frequency there is a multiple of times
                x = np.asarray([[t]*len(a.freq) for t in a.time])
                x = np.hstack(x)
                
                # for every time there is a set of frequencies
                y = np.asarray([a.freq for i in range(len(a.raw_c[0][0]))])*1e-6
                y = np.hstack(y)
                    
                # draw combined asym
                if asym_type == "2e_rw_c":
                
                    z = a.raw_c[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label,**drawargs)
                    
                elif asym_type == "2e_rw_h":
                
                    z = a.raw_p[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label+' ($+$)',**drawargs)

                    z = a.raw_n[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label+' ($-$)',**drawargs)
                
                # plot elements
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Frequency (MHz)')
                ax.set_zlabel('Asymmetry')
                ax.get_yaxis().get_major_formatter().set_useOffset(False)
                ax.get_xaxis().set_ticks(a.time)
            
            else:
                f = a.freq*1e-6 
                if asym_type == '2e_sl_c':
                    plt.errorbar(f,a.sl_c[0],a.sl_c[1],label=label,
                                 **drawargs)
                elif asym_type == '2e_di_c':
                    plt.errorbar(f,a.dif_c[0],a.dif_c[1],label=label,
                                 **drawargs)
                elif asym_type == '2e_sl_h':
                    plt.errorbar(f,a.sl_p[0],a.sl_p[1],
                                 label=label+' ($+$)',**drawargs)
                    plt.errorbar(f,a.sl_n[0],a.sl_n[1],
                                 label=label+' ($-$)',**drawargs)
                elif asym_type == '2e_di_h':
                    plt.errorbar(f,a.dif_p[0],a.dif_p[1],
                                 label=label+' ($+$)',**drawargs)
                    plt.errorbar(f,a.dif_n[0],a.dif_n[1],
                                 label=label+' ($-$)',**drawargs)
                    
                plt.xlabel(xlabel_dict[data.mode])
                plt.ylabel("Asymmetry")
            
        # get asymmetry: not raw scans, not 2e
        else:
            a = data.asym(omit=option,rebin=rebin,hist_select=self.hist_select)
            x = a[x_tag[data.mode]]
            xlabel = xlabel_dict[data.mode]
            
            # unit conversions
            if   data.mode == '1n': x *= self.volt_unit_conv
            elif data.mode == '1f': 
                if self.draw_ppm.get():
                    self.logger.info('Drawing as PPM shift with reference %s Hz',
                                     self.ppm_reference)
                    x = 1e6*(x-self.ppm_reference)/self.ppm_reference
                    xlabel = 'Frequency Shift (PPM)'
                else: 
                    x *= self.freq_unit_conv
                    
            # plot split helicities
            if asym_type == 'h':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
                
                # get average
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                
                # draw
                plt.errorbar(x[tag_p],ap[tag_p],a.p[1][tag_p],label=label+" ($+$)",**drawargs)
                plt.errorbar(x[tag_n],an[tag_n],a.n[1][tag_n],label=label+" ($-$)",**drawargs)
                plt.axhline(avg,color='k',linestyle='--')
                
            # plot split helicities, shifted by baseline
            elif asym_type == 'hs':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                ap = ap[tag_p]
                an = an[tag_n]
                
                # subtract first value
                loc = np.where(x==min(x))[0][0]
                ap -= ap[loc]
                an -= an[loc]
                
                plt.errorbar(x[tag_p],ap,a.p[1][tag_p],
                        label=label+" ($+$)",**drawargs)
                plt.errorbar(x[tag_n],an,a.n[1][tag_n],
                        label=label+" ($-$)",**drawargs)
            
            # plot split helicities, flipped about the average
            elif asym_type == 'hm':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
            
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                
                plt.errorbar(x[tag_p],a.p[0][tag_p],a.p[1][tag_p],
                        label=label+" ($+$)",**drawargs)
                plt.errorbar(x[tag_n],2*avg-a.n[0][tag_n],a.n[1][tag_n],
                        label=label+" ($-$)",**drawargs)
                plt.axhline(avg,color='k',linestyle='--')
            
            # plot split helicities, flipped about the average, find the largest 
            elif asym_type == 'hp':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                ap = ap[tag_p]
                an = an[tag_n]
                
                # get flipped asymmetries
                if np.mean(an) < avg:
                    an = 2*avg-an
                if np.mean(ap) < avg:
                    ap = 2*avg-ap
                
                # get largest asymmetry
                largest_p = max(ap)
                largest_n = max(an)
                
                if largest_p > largest_n:
                    largest = largest_p
                    vmax = x[np.where(ap==largest)[0][0]]
                else:
                    largest = largest_n
                    vmax = x[np.where(an==largest)[0][0]]
                
                # print
                print('Max asymmetry is %f at V = %f V' % (largest,vmax))
                
                # draw    
                plt.errorbar(x[tag_p],ap,a.p[1][tag_p],label=label+" ($+$)",**drawargs)
                plt.errorbar(x[tag_n],an,a.n[1][tag_n],label=label+" ($-$)",**drawargs)
                plt.axhline(largest,color='k',linestyle='--')
                plt.axvline(vmax,color='k',linestyle='--')
                plt.text(vmax+0.5,largest+0.0001,'%g V' % vmax)
            
            # plot comined helicities
            elif asym_type == 'c':
                tag = a.c[0]!=0 # remove zero asym
                plt.errorbar(x[tag],a.c[0][tag],a.c[1][tag],label=label,**drawargs)
                
            # plot combined helicities, shifted by baseline
            elif asym_type == 'cs':
                
                # remove zero asym
                ac = a.c[0]
                tag = ac!=0
                ac = ac[tag]
                
                # subtract first value
                x = x[tag]
                loc = np.where(x==min(x))[0][0]
                ac -= ac[loc]
                
                plt.errorbar(x,ac,a.c[1][tag],label=label,**drawargs)
            
            # attempting to draw raw scans unlawfully
            elif asym_type == 'r':
                return
                
            # draw alpha diffusion
            elif asym_type == 'ad':
                a = data.asym('adif',rebin=rebin,hist_select=self.hist_select)
                plt.errorbar(*a,label=label,**drawargs)
                plt.ylabel(r'$N_\alpha/N_\beta$')
                
            # draw alpha tagged runs
            elif asym_type in ['at_c','at_h','nat_c','nat_h']:
                
                a = data.asym('atag',rebin=rebin,hist_select=self.hist_select)
                t = a.time_s
                
                if asym_type == 'at_c':
                    plt.errorbar(t,a.c_wiA[0],a.c_wiA[1],
                                 label=label+r" $\alpha$",**drawargs)
                
                elif asym_type == 'nat_c':
                    plt.errorbar(t,a.c_noA[0],a.c_noA[1],
                                 label=label+r" !$\alpha$",**drawargs)
                                 
                elif asym_type == 'at_h':
                    plt.errorbar(t,a.p_wiA[0],a.p_wiA[1],
                                 label=label+r" $\alpha$ ($+$)",**drawargs)
                    plt.errorbar(t,a.n_wiA[0],a.n_wiA[1],
                                 label=label+r" $\alpha$ ($-$)",**drawargs)
                
                elif asym_type == 'nat_h':
                    plt.errorbar(t,a.p_noA[0],a.p_noA[1],
                                 label=label+r" !$\alpha$ ($+$)",**drawargs)
                    plt.errorbar(t,a.n_noA[0],a.n_noA[1],
                                 label=label+r" !$\alpha$ ($-$)",**drawargs)
            
            # draw raw histograms
            elif asym_type == 'rhist':
                
                # make a new figure
                style = draw_style.get()
                
                # get the histograms 
                hist = data.hist
                
                # draw
                keylist = ('F+','F-','B+','B-','L+','R+','L-','R-',
                             'NBMF+','NBMF-','NBMB+','NBMB-','AL0+','AL0-')
                for h in keylist:
                    
                    # get bins
                    try:
                        x = np.arange(len(hist[h].data))
                    except KeyError:
                        continue
                    
                    # check for non-empty histograms, then draw
                    if np.mean(hist[h].data) > 0:                        
                        plt.plot(x,hist[h].data,label=h)
                        
                plt.ylabel(ylabel_dict[asym_type])
                plt.xlabel('Bin')
                            
            # unknown run type
            else:
                raise RuntimeError("Unknown draw style")
                    
        # plot elements
        if data.mode != '2e' and asym_type != 'rhist':
            plt.xlabel(xlabel)
            
            if asym_type in ylabel_dict.keys():
                plt.ylabel(ylabel_dict[asym_type])
            else:
                plt.ylabel("Asymmetry")
                
        plt.tight_layout()
        plt.legend()
        self.logger.debug('Drawing success.')
    
    # ======================================================================= #
    def draw_binder(self,*args):
        """
            Switch between various functions of the shift+enter button. 
            Bound to ctrl+enter
        """
        
        idx = self.notebook.index('current')
        self.logger.debug('Drawing for notebook index %d',idx)
        if idx == 0:        # data viewer
            self.fileviewer.draw()
        elif idx == 1:        # data fetch_files
            self.fetch_files.draw_all()
        elif idx == 2:        # fit viewer
            self.fit_files.draw_param()
        else:
            pass
                 
    # ======================================================================= #
    def export(self,data,filename):
        """Export single data file as csv"""
        
        self.logger.info('Exporting single run (%d) as "%s"',data.run,filename)
        
        # settings
        title_dict = {'c':"combined",'p':"positive_helicity",
                        'n':"negative_helicity",'time_s':'time_s',
                        'freq':"freq_Hz",'mV':'voltage_mV'}
                        
        index_list = ['time_s','freq_Hz','voltage_mV'] 
        
        # get asymmetry
        asym = data.asym(hist_select=self.hist_select)
        
        # get new keys
        asym_out = {}
        for k in asym.keys():
            if len(asym[k]) == 2:
                asym_out[title_dict[k]] = asym[k][0]
                asym_out[title_dict[k]+"_err"] = asym[k][1]
            else:
                asym_out[title_dict[k]] = asym[k]
        
        # make pandas dataframe
        df = pd.DataFrame.from_dict(asym_out)
        
        # set index
        for i in index_list:
            if i in asym_out.keys():
                df.set_index(i,inplace=True)
                break
        
        # write to file
        try:
            df.to_csv(filename)
        except AttributeError:
            self.logger.exception('Export file write failed')
            pass
    
    # ======================================================================= #
    def get_label(self,data):
        """ Get label for plot
            Input: fitdata object. 
        """
        
        # the thing to switch on
        select = self.label_default.get()
        self.logger.debug('Fetching plot label for "%s" (run %d)',select,data.run)
        
        # Data file options
        if select == 'Temperature (K)':
            label = "%d K" % int(round(data.temperature.mean))
            
        elif select == 'B0 Field (T)':
            label = "%.2f T" % np.around(data.field,2)
            
        elif select == 'RF Level DAC':
            label = str(int(data.bd.camp.rf_dac.mean))
            
        elif select == 'Platform Bias (kV)':
            label = "%d kV" % int(np.round(data.bias))
                
        elif select == 'Impl. Energy (keV)':
            label = "%.2f keV" % np.around(data.bd.beam_kev())
            
        elif select == 'Run Duration (s)':
            label = "%d s" % int(data.bd.duration)
            
        elif select == 'Run Number':
            label = str(data.run)
            
        elif select == 'Sample':
            label = data.bd.sample
            
        elif select == 'Start Time':
            label = data.bd.start_date
        
        elif select == 'Title':
            label = data.bd.title
            
        else:
            label = str(data.run)
        
        return label
    
    # ======================================================================= #
    def get_latest_year(self):
        """Get the year which has the last data set in it."""
        
        # get the current year
        year = datetime.datetime.now().year
        
        # functions to check for data (NMR or NQR)
        no_nmr = lambda y: not os.path.isdir(os.path.join(
                                    os.environ[self.bnmr_archive_label],str(y)))
        no_nqr = lambda y: not os.path.isdir(os.path.join(
                                    os.environ[self.bnqr_archive_label],str(y)))
        
        # check data
        while (no_nmr(year) or no_nqr(year)) and year > 0:
            year -= 1
            
        self.logger.debug('Latest year with data: %d (NMR: %s, NQR: %s)',
                          year,not no_nmr(year),not no_nqr(year))
        return year
    
    # ======================================================================= #
    def get_run_key(self,data=None,r=-1,y=-1):
        """For indexing data dictionary"""
        
        if data is not None:
            return '.'.join(map(str,(data.year,data.run)))
        elif r>0 and y>0:
            return '.'.join(map(str,(y,r)))
        else:
            raise RuntimeError('Bad run key input')
    
    # ======================================================================= #
    def help(self):
        """Display help wiki"""
        self.logger.info('Opening help wiki')
        p = os.path
        webbrowser.open(p.split(p.abspath(p.realpath(__file__)))[0]+'/help.html')
    
    # ======================================================================= #
    def on_closing(self):
        """Excecute this when window is closed: destroy and close all plots."""
        self.logger.info('Closing all windows.')
        plt.close('all')
        self.root.destroy()
        self.logger.info('Finished     ' + '-'*50)
    
    # ======================================================================= #
    def report_issue(self):
        """Display github issue page"""
        self.logger.info('Opening github issue page: '+\
                         'https://github.com/dfujim/bfit/issues')
        webbrowser.open('https://github.com/dfujim/bfit/issues')
    
    # ======================================================================= #
    def return_binder(self,*args):
        """Switch between various functions of the enter button. """
        
        idx = self.notebook.index('current')
        self.logger.debug('Calling return key command for notebook index %d',idx)
        if idx == 0:        # data viewer
            self.fileviewer.get_data()
        elif idx == 1:        # data fetch_files
            self.fetch_files.return_binder()
        elif idx == 2:        # fit viewer
            self.fit_files.return_binder()
        else:
            pass
    
    # ======================================================================= #
    def scroll_binder(self,event):
        """
            Switch between various functions of the mousewheel button. 
            Bound to <Button-4> and <Button-5>
        """
        
        idx = self.notebook.index('current')
        
        if idx == 0:        # data viewer
            pass
        elif idx == 1:        # data fetch_files
            self.fetch_files.canvas_scroll(event)
        elif idx == 2:        # fit viewer
            self.fit_files.canvas_scroll(event)
        else:
            pass
               
    # ======================================================================= #
    def search_archive(self):  
        self.logger.info('Opening mud archive musr website')
        webbrowser.open('http://musr.ca/mud/runSel.html',new=1)
        
    # ======================================================================= #
    def set_bnmr_dir(self): 
        """Set directory location via environment variable BNMR_ARCHIVE."""
        self.logger.info('Setting BNMR environment directory')
        d = filedialog.askdirectory(parent=self.root,mustexist=True, 
                initialdir=self.bnmr_data_dir)
            
        if type(d) == str:
            self.bnmr_data_dir = d
            os.environ[self.bnmr_archive_label] = d
            self.logger.debug('Environment variable "%s" set to "%s"',
                              self.bnmr_archive_label,d)
        else:
            self.logger.error('Input was not of type string')
            
    # ======================================================================= #
    def set_bnqr_dir(self): 
        """Set directory location via environment variable BNQR_ARCHIVE."""
        self.logger.info('Setting BNQR environment directory')
        d = filedialog.askdirectory(parent=self.root,mustexist=True, 
                initialdir=self.bnqr_data_dir)
        
        if type(d) == str:
            self.bnqr_data_dir = d
            os.environ[self.bnqr_archive_label] = d
            self.logger.debug('Environment variable "%s" set to "%s"',
                              self.bnqr_archive_label,d)
        else:
            self.logger.error('Input was not of type string')
    
    # ======================================================================= #
    def set_fit_routines(self):
        """Set python module for fitting routines"""
        self.logger.info('Setting fitting backend routine')
        d = filedialog.askopenfilename(initialdir = "./",
                title = "Select fitting routine module",
                filetypes = (("python modules","*.py"),
                             ("cython modules","*.pyx"),
                             ("all files","*.*")))
        
        if type(d) == str:
            
            # empty condition
            if d == '':
                self.logger.error('Input was empty string.')
                return
            
            # get paths
            path = os.path.abspath(d)
            pwd = os.getcwd()
            
            # load the module
            self.logger.info('Loading module...')
            os.chdir(os.path.dirname(path))
            self.routine_mod = importlib.import_module(os.path.splitext(
                                                        os.path.basename(d))[0])
            os.chdir(pwd)
            
            # repopuate fitter
            self.logger.info('Repopulating fitter...')
            self.fit_files.fitter = self.routine_mod.fitter(self.probe_species.get())
            self.fit_files.populate()
        else:
            self.logger.error('Input was not of type string.')    
        self.logger.info('Success.')
        
    # ======================================================================= #
    def set_matplotlib(self): 
        """Edit matplotlib settings file, or give info on how to do so."""
        
        self.logger.info('Attempting to edit matplotlibrc file')
        
        # settings
        location = os.environ['HOME']+"/.config/matplotlib/"
        filename = "matplotlibrc"
        weblink = 'http://matplotlib.org/users/customizing.html'+\
                  '#the-matplotlibrc-file'
        
        # check for file existance
        if not os.path.isfile(location+filename):
            self.logger.debug('File not found.')
            value = messagebox.showinfo(parent=self.mainframe,
                    title="Get matplotlibrc",\
                    message="No matplotlibrc file found.",
                    detail="Press ok to see web resource.",
                    type='okcancel')
            
            if value == 'ok':
                webbrowser.open(weblink)
            return
        
        # if file exists, edit
        self.logger.debug('File found. Opening in external program.')
        subprocess.call(['xdg-open',location+filename])
            
    # ======================================================================= #
    def set_all_labels(self,*a):    self.fetch_files.set_all_labels()
    def set_check_all(self,x):  
        self.logger.info('Checking all files')
        state = self.fetch_files.check_state.get()
        self.fetch_files.check_state.set(not state)
        self.fetch_files.check_all()
    def set_draw_style(self):       drawstyle_popup(self)
    def set_histograms(self,*a):    set_histograms_popup(self)
    def set_focus_tab(self,idn,*a): self.notebook.select(idn)
    def set_ppm_reference(self,*a): set_ppm_reference_popup(self)
    def set_probe_species(self, *a): 
        self.fit_files.fitter.probe_species = self.probe_species.get()
        self.logger.info('Probe species changed to %s',self.probe_species.get())
    def set_redraw_period(self,*a): redraw_period_popup(self)
    def set_style_new(self,x):      
        self.logger.info('Setting draw style to "new"')
        self.draw_style.set('new')
    def set_style_stack(self,x):    
        self.logger.info('Setting draw style to "stack"')
        self.draw_style.set('stack')
    def set_style_redraw(self,x):   
        self.logger.info('Setting draw style to "redraw"')
        self.draw_style.set('redraw')
    def set_tab_change(self,tab_id):
        
        self.logger.debug('Changing to tab %d',tab_id)
        
        # fileviewer
        if tab_id == 0:
            try:
                self.set_asym_calc_mode_box(self.fileviewer.data.mode)
            except AttributeError:
                pass
            
        # fetch files
        elif tab_id == 1:
            try:
                k = list(self.data.keys())[0]
            except IndexError:
                pass
            else:   
                self.set_asym_calc_mode_box(self.data[k].mode)
            
        # fit files
        elif tab_id == 2:
            self.fit_files.populate()
     
    # ======================================================================= #
    def set_asym_calc_mode_box(self,mode,*args):
        """Set asym combobox values. Asymmetry calculation and draw modes."""
        
        self.logger.debug('Setting fileviewer asym combobox values for mode '+\
                         '"%s"',mode)
        fv = self.fileviewer
    
        # selection: switch if run mode not possible
        modes = self.asym_dict_keys[mode]
        if fv.asym_type.get() not in modes:
            fv.asym_type.set(modes[0])
    
        # fileviewer
        fv.entry_asym_type['values'] = self.asym_dict_keys[mode]
    
        # fetch files
        self.fetch_files.entry_asym_type['values'] = self.asym_dict_keys[mode]
    
    # ======================================================================= #
    def update_bfit(self):
        """Check pip for updated version"""
        self.logger.info('Using pip to update')
        subprocess.call([sys.executable, "-m", "pip", "install", "--user", 
                         "--upgrade", 'bfit'])
        print('Done. Restart to implement updates.')
        
# =========================================================================== #
if __name__ == "__main__":
    bfit()


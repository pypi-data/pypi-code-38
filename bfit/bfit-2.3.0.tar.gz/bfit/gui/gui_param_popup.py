# Set function paramters from gui window
# Derek Fujimoto
# April 2019

from tkinter import *
from tkinter import ttk
from bfit import logger_name
from bfit.fitting.FunctionPlacer import FunctionPlacer
from bfit.fitting.decay_31mg import fa_31Mg
import bfit.fitting.functions as fns

import matplotlib.pyplot as plt
import logging
import bdata as bd
import numpy as np

# ========================================================================== #
class gui_param_popup(object):
    """
        Popup window for graphically finding input parameters. 
        
        data:           bdata object 
        fig:            maplotlib figure object
        fitter:         fit_tab.fitter obje (defined in default_routines.py)
        first:          if True, first time through fixing parameters
        fname:          name of the function 
        logger:         logging variable
        mode:           1 or 2 to switch between run modes
        n_components:   number of components in the fit function
        parnames:       tuple of names of the parameters
        p0:             dictionary of StringVar objects to link parameters
        selection:      StringVar, track run selection
        win:            TopLevel window
        xy:             (x,asym,dasym) tuple
    """

    # parameter mapping
    parmap = {  '1/T1':'lam',
                'amp':'amp',
                'beta':'beta',
                'baseline':'base',
                'peak':'peak',
                'width':'width',
                'widthA':'widthA',
                'widthB':'widthB',
                'height':'amp',
                'heightA':'ampA',
                'heightB':'ampB',
                'sigma':'width',
                'mean':'peak',
             }

    # ====================================================================== #
    def __init__(self,bfit):
        self.bfit = bfit
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing gui param popup')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Find P0')
        frame = ttk.Frame(self.win,relief='sunken',pad=5)
        
        # Labels
        ttk.Label(frame,text="Select Run").grid(column=0,row=0,sticky=E)
        
        # box for run select
        self.selection = StringVar()
        select_box = ttk.Combobox(frame,textvariable=self.selection,
                                  state='readonly')
        select_box.bind('<<ComboboxSelected>>',self.setup)
        
        # get run list
        runlist = list(self.bfit.fit_files.fit_lines.keys())
        runlist.sort()
        # ~ runlist = ['('+r.split('.')[0]+') '+r.split('.')[1] for r in runlist]
        select_box['values'] = runlist
        
        # gridding
        frame.grid(column=0,row=1,sticky=(N,W,E,S))
        select_box.grid(column=0,row=1,sticky=E)
                
    # ====================================================================== #
    def setup(self,*args):
        """Get parameters for placing function and start the run squence"""
        
        # get run selection 
        run_id = self.selection.get()
        self.logger.info('Running P0 GUI finder on run %s',run_id)
        
        # get data
        self.data = self.bfit.data[run_id]
        mode = self.data.mode
        
        # mode switching
        if mode in ('20','2h'): self.mode = 2
        elif mode in ('1f',):   self.mode = 1
        else:
            self.logger.warning('P0 Finder not configured for run mode %s',mode)
            print('P0 Finder not configured for run mode %s'%mode)
        
        # make new window 
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111)
        
        # draw data
        omit = self.data.omit.get()
        if omit == self.bfit.fetch_files.bin_remove_starter_line:
            omit = ''
        self.xy = self.data.asym('c',rebin=self.data.rebin.get(),omit=omit)
        ax.errorbar(*self.xy,fmt='.',color='k',ecolor='k')
        
        # plot elements - don't do tight_layout here - blocks matplotlib signals
        ax.set_ylabel('Asymmetry')
        if self.mode == 2:     ax.set_xlabel('Time (s)')
        elif self.mode == 1:   ax.set_xlabel('Frequency (MHz)')
        self.fig.show()
        
        # get parameters list and run finder 
        fit_tab = self.bfit.fit_files
        self.fitter = fit_tab.fitter
        self.n_components = fit_tab.n_component.get()
        self.fname = fit_tab.fit_function_title.get()
        self.parnames = self.fitter.gen_param_names(fn_name=self.fname,
                                          ncomp=self.n_components)
        parentry = fit_tab.fit_lines[run_id].parentry
        
        # make initial paramter list
        self.p0 = {k:parentry[k]['p0'][0] for k in parentry.keys()}
        
        self.run()
        
    # ====================================================================== #
    def run(self):
        """
            Run the function placer
            
            comp = component number to run
        """
        
        try:
            del self.fplace
        except AttributeError:
            pass
        else:
            self.fig.axes[0].cla()
            self.fig.axes[0].errorbar(*self.xy,fmt='.')
        
        # ensure matplotlib signals work. Not sure why this is needed.
        self.fig.tight_layout()
                    
        # get paramters, translating the names
        p0 = []
        if self.n_components > 1:
            for i in range(self.n_components):
                p0.append({self.parmap[k.split('_')[0]]:self.p0[k] \
                            for k in self.p0.keys() if 'base' in k or str(i) in k})
        else:
            p0.append({self.parmap[k]:self.p0[k] for k in self.p0.keys()})
        
        # get fitting function 
        if self.fname == 'Lorentzian':
            fn = fns.lorentzian     # freq,peak,width,amp
        # ~ elif self.fname == 'BiLorentzian':
            # ~ fn = fns.bilorentzian   # freq, peak,widthA,ampA,widthB,ampB
        elif self.fname == 'Gaussian':
            fn = lambda freq,peak,width,amp : fns.gaussian(freq,peak,width,amp)
                
        elif self.fname in ('Exp', 'Str Exp'):
            
            # get function
            pulse = self.data.get_pulse_s()
            lifetime = bd.life[self.bfit.probe_species.get()]
        
            if self.fname == 'Exp':
                f1 = fns.pulsed_exp(lifetime=lifetime,pulse_len=pulse)
                
                if self.bfit.probe_species.get() == 'Mg31':
                    fn = lambda x,lam,amp : fa_31Mg(x,pulse)*f1(x,lam,amp)
                else:
                    fn = lambda x,lam,amp : f1(x,lam,amp)
            
            elif self.fname == 'Str Exp':
                f1 = fns.pulsed_strexp(lifetime=lifetime,pulse_len=pulse)
                
                if self.bfit.probe_species.get() == 'Mg31':
                    fn = lambda x,lam,amp,beta : fa_31Mg(x,pulse)*f1(x,lam,beta,amp)
                else:
                    fn = lambda x,lam,amp,beta : f1(x,lam,beta,amp)
        else:
            self.cancel()
            errormsg = 'Function "%s" not implemented in P0 Finder' % self.fname
            self.logger.warning(errormsg)
            messagebox.showerror("Error",errormsg)
            raise RuntimeError(errormsg)
        
        self.fig.canvas.mpl_connect('close_event',self.cancel)
        
        self.fplace = FunctionPlacer(fig=self.fig,
                                     data=self.data,
                                     fn_single=fn,
                                     ncomp=self.n_components,
                                     p0=p0,
                                     fnname=self.fname,
                                     endfn=self.endfn)
        
    # ====================================================================== #        
    def endfn(self,p0,base):
        """Set output fields"""
        
        # single component
        if len(p0) == 1:
            p0 = p0[0]
            for k in self.p0.keys():
                if 'base' not in k:
                    self.p0[k].set(p0[self.parmap[k]])
        # multi component
        else:
            for k in self.p0.keys():
                if 'base' not in k:
                    key,i = k.split('_')
                    self.p0[k].set(p0[int(i)][self.parmap[key]])
        
        # baseline
        if 'baseline' in self.p0.keys():
            self.p0['baseline'].set(base)
        
    # ====================================================================== #
    def cancel(self,*args):
        if hasattr(self,'fplace'):  del self.fplace
        if hasattr(self,'fig'):     
            plt.close(self.fig.number)
            del self.fig
        
        self.win.destroy()




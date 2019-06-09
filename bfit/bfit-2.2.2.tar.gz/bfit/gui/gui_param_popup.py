# Set function paramters from gui window
# Derek Fujimoto
# April 2019

from tkinter import *
from tkinter import ttk
from bfit import logger_name
from bfit.fitting.FunctionPlacer import FunctionPlacer
from bfit.fitting.decay_31mg import fa_31Mg

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
                'height':'amp',
                'sigma':'width',
                'mean':'peak',
             }

    # ====================================================================== #
    def __init__(self,bfit):
        self.bfit = bfit
        self.first = True   # default
        
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
        ax.errorbar(*self.xy,fmt='.')
        
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
    def run(self,comp=0):
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
        
        # end condition, or start the cycle again
        if comp >= self.n_components:
            if self.n_components > 1: 
                self.first = False
                comp = 0
            else: 
                return
        
        # get the number of components in the line (after first round, keep all)
        if self.first:  ncomp = comp+1
        else:           ncomp = self.n_components
        
        # ensure matplotlib signals work. Not sure why this is needed.
        self.fig.tight_layout()
    
        # get parameter names and fitting functions - multi component
        if self.n_components > 1:
            
            # get parameter names of all previously set components 
            parnames_prev = []
            for c in range(ncomp-1 if self.first else ncomp):
                if c == comp: continue
                parnames_prev.extend([p for p in self.parnames if str(c) in p])
            
            # get parameter names of components to set now
            parnames_now = [p for p in self.parnames if str(comp) in p]
            
            # baseline name 
            if self.mode == 1:
                if comp == 0 and self.first:    parnames_now.append('baseline')
                else:                           parnames_prev.append('baseline')
            
            # translate keynames: input to original
            parnames_now_conv = {self.parmap[k.split('_')[0]]:k for k in parnames_now}
            
            # static values 
            p = {p:float(self.p0[p].get()) for p in parnames_prev}  
            
            # p0 from current iteration
            p0 = {self.parmap[p.split('_')[0]]:self.p0[p] for p in parnames_now}
                        
            # get fitting function 
            if self.mode == 1:
                f1 = self.fitter.get_fn(self.fname,ncomp=ncomp)
                
                # make decorator for fitting function
                if comp == 0 and self.first:
                    def fn(x,peak,width,amp,base):
                        
                        # add to input dictionary
                        p[parnames_now_conv['peak']] = peak
                        p[parnames_now_conv['width']] = width
                        p[parnames_now_conv['amp']] = amp
                        p[parnames_now_conv['base']] = base
                        
                        # get the order right
                        p_in = [p[k] for k in self.parnames if k in p.keys()]
                        return f1(x,*p_in)
                else:
                    def fn(x,peak,width,amp):
                        
                        # add to input dictionary
                        p[parnames_now_conv['peak']] = peak
                        p[parnames_now_conv['width']] = width
                        p[parnames_now_conv['amp']] = amp
                        
                        # get the order right
                        p_in = [p[k] for k in self.parnames if k in p.keys()]
                        return f1(x,*p_in)
               
            elif self.mode == 2:
                pulse = self.data.get_pulse_s()
                f2 = self.fitter.get_fn(self.fname,ncomp=ncomp,
                                           pulse_len=pulse,
                                           lifetime=bd.life[self.bfit.probe_species.get()])
                
                # make new fit function if needed to account for daughters
                if self.bfit.probe_species.get() == 'Mg31':
                    f1 = lambda x,*par : fa_31Mg(x,pulse)*f2(x,*par)
                else:
                    f1 = f2
                
                # make decorator for fitting function
                if comp == 0 and self.first:
                    
                    if 'beta' in parnames_now_conv.keys():
                        def fn(x,lam,amp,beta):
                            
                            # add to input dictionary
                            p[parnames_now_conv['lam']] = lam
                            p[parnames_now_conv['amp']] = amp
                            p[parnames_now_conv['beta']] = beta
                            
                            # get the order right
                            p_in = [p[k] for k in self.parnames if k in p.keys()]
                            return f1(x,*p_in)
                    elif 'base' in parnames_now_conv.keys():
                        def fn(x,lam,amp,base):
                            
                            # add to input dictionary
                            p[parnames_now_conv['lam']] = lam
                            p[parnames_now_conv['amp']] = amp
                            p[parnames_now_conv['base']] = base
                            
                            # get the order right
                            p_in = [p[k] for k in self.parnames if k in p.keys()]
                            return f1(x,*p_in)               
                    else:
                        def fn(x,lam,amp):
                            
                            # add to input dictionary
                            p[parnames_now_conv['lam']] = lam
                            p[parnames_now_conv['amp']] = amp
                            
                            # get the order right
                            p_in = [p[k] for k in self.parnames if k in p.keys()]
                            return f1(x,*p_in)               
                else:
                    
                    if 'beta' in parnames_now_conv.keys():
                        def fn(x,lam,amp,beta):
                            
                            # add to input dictionary
                            p[parnames_now_conv['lam']] = lam
                            p[parnames_now_conv['amp']] = amp
                            p[parnames_now_conv['beta']] = beta
                            
                            # get the order right
                            p_in = [p[k] for k in self.parnames if k in p.keys()]
                            return f1(x,*p_in)
                    else:
                        def fn(x,lam,amp):
                            
                            # add to input dictionary
                            p[parnames_now_conv['lam']] = lam
                            p[parnames_now_conv['amp']] = amp
                            
                            # get the order right
                            p_in = [p[k] for k in self.parnames if k in p.keys()]
                            return f1(x,*p_in)               
                            
        # get parameter names and fitting functions - single component
        else:
            
            # get paramters, translating the names
            p0 = {self.parmap[k]:self.p0[k] for k in self.p0.keys()}
    
            # get fitting function 
            if self.mode == 1:
                f1 = self.fitter.get_fn(self.fname,ncomp=ncomp)
                fn = lambda x,peak,width,amp,base : f1(x,peak,width,amp,base)
                    
            elif self.mode == 2:
                pulse = self.data.get_pulse_s()
                f2 = self.fitter.get_fn(self.fname,ncomp=ncomp,
                                        pulse_len=pulse,
                                        lifetime=bd.life[self.bfit.probe_species.get()])
                
                # make new fit function if needed to account for daughters
                if self.bfit.probe_species.get() == 'Mg31':
                    f1 = lambda x,*par : fa_31Mg(x,pulse)*f2(x,*par)
                else:
                    f1 = f2
                
                if 'beta' in self.parnames:
                    fn = lambda x,lam,amp,beta : f1(x,lam,amp,beta)
                else:
                    fn = lambda x,lam,amp : f1(x,lam,amp)
            
        # start recursive function placement
        try:
            base = float(self.p0['baseline'].get())
        except KeyError:
            base = 0
        
        self.fig.canvas.mpl_connect('close_event',self.cancel)
        
        self.fplace = FunctionPlacer(fig=self.fig,
                                     data=self.data,
                                     fn=fn,
                                     p0=p0,
                                     endfn=lambda:self.run(comp+1),
                                     base = base)
        
    # ====================================================================== #
    def cancel(self,*args):
        if hasattr(self,'fplace'):  del self.fplace
        if hasattr(self,'fig'):     del self.fig
        
        self.win.destroy()




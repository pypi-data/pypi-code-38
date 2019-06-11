# Fit set of run combined asymmetry globally 
# Derek Fujimoto
# Nov 2018

from bfit.fitting.global_fitter import global_fitter
from bdata import bdata
import numpy as np
import collections

# =========================================================================== #
class global_bdata_fitter(global_fitter):
    
    # ======================================================================= #
    def __init__(self,runs,years,fn,sharelist,npar=-1,xlims=None,rebin=1):
        """
            runs:       list of run numbers
            
            years:      list of years corresponding to run numbers, or int which applies to all
            
            fn:         list of function handles to fit (or single which applies to all)
                        must specify inputs explicitly (do not do def fn(*par)!)
                        must have len(fn) = len(runs) if list
                        
            sharelist:  list of bool to indicate which parameters are shared. 
                        True if shared
                        len = number of parameters.
                        
            npar:       number of free parameters in each fitting function.
                        Set if number of parameters is not intuitable from 
                            function code.            
            
            xlims:      list of 2-tuples for (low,high) bounds on fitting range 
                            based on x values. If list is not depth 2, use this 
                            range on all runs.
            
            rebin:      rebinning factor on fitting and drawing data
        """
        
        # Set years
        if not isinstance(years,collections.Iterable):
            years = [years]*len(runs)
        
        # Get asymmetry
        data = [bdata(r,year=y).asym('c',rebin=rebin) for r,y in zip(runs,years)]
        
        # split into x,y,dy data sets
        x = np.array([d[0] for d in data])
        y = np.array([d[1] for d in data])
        dy = np.array([d[2] for d in data])
        
        # select subrange
        if xlims is not None:
            
            # check depth
            if len(np.array(xlims).shape) < 2:
                xlims = [xlims for i in range(len(x))]
            
            # initialize new inputs
            xnew = []
            ynew = []
            dynew = []
            
            # select subrange
            for i,xl in enumerate(xlims):
                tag = (xl[0]<x[i])*(x[i]<xl[1])
                xnew.append(x[i][tag])
                ynew.append(y[i][tag])
                dynew.append(dy[i][tag])
            
            # new arrays
            x = np.array(xnew)
            y = np.array(ynew)
            dy = np.array(dynew)
            
        # intialize
        super(global_bdata_fitter,self).__init__(x,y,dy,fn,sharelist,npar)

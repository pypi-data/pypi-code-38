# Fit list of bdata objects with function list
# Derek Fujimoto
# Nov 2018

import collections
import numpy as np
from bdata import bdata
from scipy.optimize import curve_fit
from tqdm import tqdm
from bfit.fitting.global_bdata_fitter import global_bdata_fitter

# ========================================================================== #
def fit_list(runs,years,fnlist,omit=None,rebin=None,sharelist=None,npar=-1,
              hist_select='',xlims=None,**kwargs):
    """
        Fit combined asymetry from bdata.
    
        runs:           list of run numbers
        
        years:          list of years corresponding to run numbers, or int which applies to all
        
        fnlist:         list of function handles to fit (or single which applies to all)
                        must specify inputs explicitly (do not do def fn(*par)!)
                        must have len(fn) = len(runs) if list
        
        omit:           list of strings of space-separated bin ranges to omit
        rebin:          list of rebinning of data prior to fitting. 
        
        sharelist:      list of bool to indicate which parameters are shared. 
                        True if shared
                        len = number of parameters.
        
        npar:           number of free parameters in each fitting function.
                        Set if number of parameters is not intuitable from 
                            function code.      
        
        hist_select:    string for selecting histograms to use in asym calc
        
        xlims:          list of 2-tuple for (low,high) bounds on fitting range 
                            based on x values
        
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: (par,cov,ch,gchi)
            par: best fit parameters
            cov: covariance matrix
            chi: chisquared of fits
            gchi:global chisquared of fits
    """
    
    nruns = len(runs)
    
    # get fnlist
    if not isinstance(fnlist,collections.Iterable):
        fnlist = [fnlist]
    
    # get number of parameters
    if npar < 0:
        npar = fnlist[0].__code__.co_argcount-1

    # get fnlist again
    fnlist.extend([fnlist[-1] for i in range(nruns-len(fnlist))])

    # get sharelist
    if sharelist is None:
        sharelist = np.zeros(npar,dtype=bool)

    # get omit
    if omit is None:
        omit = ['']*nruns
    elif len(omit) < nruns:
        omit = np.concatenate(omit,['']*(nruns-len(omit)))
        
    # get rebin
    if rebin is None:
        rebin = np.ones(nruns)
    elif type(rebin) is int:
        rebin = np.ones(nruns)*rebin
    elif len(rebin) < nruns:
        rebin = np.concatenate((rebin,np.ones(nruns-len(rebin))))
    
    rebin = np.asarray(rebin).astype(int)

    # get years
    if type(years) in (int,float):
        years = np.ones(nruns,dtype=int)*years
        
    # get p0 list
    if 'p0' in kwargs.keys():
        p0 = kwargs['p0']
        del kwargs['p0']
    else:
        p0 = [np.ones(npar)]*nruns

    # fit globally -----------------------------------------------------------
    if any(sharelist) and len(runs)>1:
        print('Running shared parameter fitting...')
        g = global_bdata_fitter(runs,years,fnlist,sharelist,npar,xlims)
        g.fit(p0=p0,**kwargs)
        gchi,chis = g.get_chi() # returns global chi, individual chi
        pars,covs = g.get_par()
        
    # fit runs individually --------------------------------------------------
    else:
        
        # get bounds
        if 'bounds' in kwargs.keys():
            bounds = kwargs['bounds']
            del kwargs['bounds']
        else:
            bounds = [(-np.inf,np.inf)]*nruns 
            
        # check p0 dimensionality
        if len(np.array(p0).shape) < 2:
            p0 = [p0]*nruns
        
        # check xlims shape - should match number of runs
        if len(np.array(xlims).shape) < 2:
            xlims = [xlims for i in range(len(runs))]
        else:
            xlims = list(xlims)
            xlims.extend([xlims[-1] for i in range(len(runs)-len(xlims))])
        
        
        pars = []
        covs = []
        chis = []
        gchi = 0.
        dof = 0.
        iter_obj = tqdm(zip(runs,years,fnlist,omit,rebin,p0,bounds,xlims),
                        total=len(runs),desc='Independent Fitting')
        for r,y,fn,om,re,p,b,xl in iter_obj:
            p,s,c = fit_single(r,y,fn,om,re,hist_select,p0=p,bounds=b,xlim=xl,**kwargs)
            pars.append(p)
            covs.append(s)
            chis.append(c)
            
            # get global chi 
            t,a,da = bdata(r,year=y).asym('c',rebin=re)
            
            if xl is None:  
                xl = [-np.inf,np.inf]
            else:
                if xl[0] is None: xl[0] = -np.inf
                if xl[1] is None: xl[1] = np.inf
            
            idx = (xl[0]<t)*(t<xl[1])
            gchi += np.sum(np.square((a[idx]-fn(t[idx],*p))/da[idx]))
            dof += len(t[idx])-len(p)
        gchi /= dof
        
    pars = np.asarray(pars)
    covs = np.asarray(covs)
    chis = np.asarray(chis)
            
    return(pars,covs,chis,gchi)

# =========================================================================== #
def fit_single(run,year,fn,omit='',rebin=1,hist_select='',xlim=None,**kwargs):
    """
        Fit combined asymetry from bdata.
    
        runs:           run number
        
        years:          year
        
        fn:             function handle to fit
        
        omit:           string of space-separated bin ranges to omit
        rebin:          rebinning of data prior to fitting. 
        
        hist_select:    string for selecting histograms to use in asym calc
        
        xlim:           2-tuple for (low,high) bounds on fitting range based on 
                            x values
        
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: (par,cov,chi)
            par: best fit parameters
            cov: covariance matrix
            chi: chisquared of fit
    """
    
    # Get data input
    data = bdata(run,year)
    x,y,dy = data.asym('c',omit=omit,rebin=rebin,hist_select=hist_select)
    
    # check for values with error == 0. Omit these values. 
    tag = dy != 0
    x = x[tag]
    y = y[tag]
    dy = dy[tag]
    
    # apply xlimits
    if xlim is not None:
        tag =(xlim[0]<x)*(x<xlim[1])
        x = x[tag]
        y = y[tag]
        dy = dy[tag]
    
    # p0
    if 'p0' not in kwargs.keys():
        kwargs['p0'] = np.ones(fn.__code__.co_argcount-1)
    
    # Fit the function 
    par,cov = curve_fit(fn,x,y,sigma=dy,absolute_sigma=True,**kwargs)
    dof = len(y)-fn.__code__.co_argcount+1
    
    # get chisquared
    chi = np.sum(np.square((y-fn(x,*par))/dy))/dof
    
    return (par,cov,chi)

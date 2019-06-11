# Set up default fitting routines. 
# Derek Fujimoto
# Aug 2018

from bfit.fitting.fit_bdata import fit_list
import bfit.fitting.functions as fns
from bfit.fitting.decay_31mg import fa_31Mg
from functools import partial
import numpy as np
import bdata as bd

class fitter(object):

    # needed to tell users what routine this is
    __name__ = 'default'
    
    # Define possible fit functions for given run modes
    function_names = {  '20':('Exp','Str Exp'),
                        '2h':('Exp','Str Exp'),
                        '1f':('Lorentzian','Gaussian'),
                        '1n':('Lorentzian','Gaussian')}
     
    # Define names of fit parameters:
    param_names = {     'Exp'       :('1/T1','amp'),
                        'Str Exp'   :('1/T1','beta','amp'),
                        'Lorentzian':('peak','width','height','baseline'),
                        'Gaussian'  :('mean','sigma','height','baseline'),}

    # dictionary of initial parameters
    par_values = {}
    fn_list = {}
    epsilon = 1e-9  # for fixing parameters

    # ======================================================================= #
    def __init__(self,probe_species='8Li'):
        """
            probe_species: one of the keys in the bdata.life dictionary.
        """
        
        self.probe_species = probe_species
        
    # ======================================================================= #
    def __call__(self,fn_name,ncomp,data_list,hist_select):
        """
            Fitting controller. 
            
            fn_name: name of function to fit
            ncomp : number of components to incude (2 = biexp, for example)
            data_list: list of [[bdata object,pdict,doptions],]
            hist_select: string for selection of histograms
            
                where pdict = {par:(init val,   # initial guess
                                    bound_lo,   # lower fitting bound
                                    bound_hi,   # upper fitting bound
                                    is_fixed,   # boolean, fix value?
                                    is_shared,  # boolean, share value globally?
                                   )
                              }
                where doptions = {  'omit':str,     # bins to omit in 1F calcs
                                    'rebin':int,    # rebinning factor
                                    'group':int,    # fitting group
                                 }
                                            
            returns dictionary of {run: [[par_names],[par_values],[par_errors],
                                        [chisquared],[fitfunction pointers]]}
        """

        # check ncomponents
        if ncomp < 1:
            raise RuntimeError('ncomp needs to be >= 1')
            
        # parameter names
        keylist = self.gen_param_names(fn_name,ncomp)
        npar = len(keylist)
        
        # gather list of data to fit 
        fn = []
        runs = []
        years = []
        p0 = []
        bounds = []
        omit = []
        rebin = []
        sharelist = np.zeros(npar,dtype=bool)
        
        for data in data_list:
            
            # split data list into parts
            dat = data[0]
            pdict = data[1]
            doptions = data[2]
            
            # probe lifetime
            life = bd.life[self.probe_species]
            
            # get fitting function for 20 and 2h
            if dat.mode in ['20','2h']: 
                pulse = dat.get_pulse_s()
                
                # fit function
                fn1 = self.get_fn(fn_name,ncomp,pulse,life)
                
                # add corrections for probe daughters
                if self.probe_species == 'Mg31':
                    fn.append(lambda x,*par : fa_31Mg(x,pulse)*fn1(x,*par))
                else:
                    fn.append(fn1)
                
            # 1f functions
            else:                       
                fn.append(self.get_fn(fn_name,ncomp,-1,life))
            
            # get year and run
            runs.append(dat.run)
            years.append(dat.year)
            
            # get initial parameters
            p0.append(tuple(pdict[k][0] for k in keylist))
            
            # get fitting bounds
            bound = [[],[]]
            shlist = []
            for k in keylist:
                
                # if fixed, set bounds to p0 +/- epsilon
                if pdict[k][3]:
                    p0i = pdict[k][0]
                    bound[0].append(p0i-self.epsilon)
                    bound[1].append(p0i+self.epsilon)
            
                # else set to bounds 
                else:
                    bound[0].append(pdict[k][1])
                    bound[1].append(pdict[k][2])
                    
                # sharelist
                shlist.append(pdict[k][4])
            bounds.append(bound)
            
            # look for any sharelist
            sharelist += np.array(shlist)
            
            # rebin and omit
            try:
                rebin.append(doptions['rebin'])
            except KeyError:
                rebin.append(1)
                
            try:
                omit.append(doptions['omit'])
            except KeyError:
                omit.append('')

        # fit data
        pars,covs,chis,gchi = fit_list(runs,years,fn,omit,rebin,sharelist,npar=npar,
                                   hist_select=hist_select,p0=p0,bounds=bounds)
        stds = [np.sqrt(np.diag(c)) for c in covs]
        
        # collect results
        return {'.'.join(map(str,(d[0].year,d[0].run))):[keylist,p,s,c,f] \
                    for d,p,s,c,f in zip(data_list,pars,stds,chis,fn)}

    # ======================================================================= #
    def gen_param_names(self,fn_name,ncomp):
        """
            Make a list of the parameter names based on the number of components.
            
            fn_name: name of function (should match those in param_names)
            ncomp: number of components
            
            return (names)
        """
        
        # get names
        names_orig = self.param_names[fn_name]
        
        # special case of one component
        if ncomp == 1: 
            return names_orig
        
        # multicomponent: make copies of everything other than the baselines
        names = []
        for c in range(ncomp): 
            for n in names_orig:
                if 'base' in n: continue
                names.append(n+'_%d' % c)
                
        if 'base' in names_orig[-1]:
            names.append(names_orig[-1])
        
        return tuple(names)
        
    # ======================================================================= #
    def gen_init_par(self,fn_name,ncomp,bdataobj):
        """Generate initial parameters for a given function.
        
            fname: name of function. Should be the same as the param_names keys
            ncomp: number of components
            bdataobj: a bdata object representative of the fitting group. 
            
            Set and return dictionary of initial parameters. 
                {par_name:par_value}
        """
        
        # set pulsed exp fit initial parameters
        if fn_name in ['Exp','Str Exp']:
            t,a,da = bdataobj.asym('c')
            
            # ampltitude average of first 5 bins
            amp = abs(np.mean(a[0:5])/ncomp)
            
            # T1: time after beam off to reach 1/e
            idx = int(bdataobj.ppg.beam_on.mean)
            beam_duration = t[idx]
            amp_beamoff = a[idx]
            target = amp_beamoff/np.exp(1)
            
            t_target = t[np.sum(a>target)]
            T1 = t_target-beam_duration
            
            # baseline: average of last 25% of runs
            base = np.mean(a[int(len(a)*0.75):])
            
            # set values
            par_values = {'amp':(amp,0,np.inf),
                          '1/T1':(1./T1,0,np.inf),
                          'baseline':(base,-np.inf,np.inf),
                          'beta':(0.5,0,1)}
                         
        # set time integrated fit initial parameters
        elif fn_name in ['Lorentzian','Gaussian']:
            
            f,a,da = bdataobj.asym('c')
            
            # get peak asym value
            amin = min(a[a>0])
            
            peak = f[np.where(a==amin)[0][0]]
            base = np.mean(a[:5])
            height = abs(amin-base)
            width = 2*abs(peak-f[np.where(a<amin+height/2)[0][0]])
            
            # set values
            if fn_name == 'Lorentzian':
                par_values = {'peak':(peak,min(f),max(f)),
                              'width':(width,0,np.inf),
                              'height':(height,0,np.inf),
                              'baseline':(base,-np.inf,np.inf)
                             }
            elif fn_name == 'Gaussian':
                par_values = {'mean':(peak,min(f),max(f)),
                              'sigma':(width,0,np.inf),
                              'height':(height,0,np.inf),
                              'baseline':(base,-np.inf,np.inf)
                              }
        else:
            raise RuntimeError('Bad function name.')
        
        # do multicomponent
        par_values2 = {}
        if ncomp > 1: 
            for c in range(ncomp): 
                for n in par_values.keys():
                    if 'baseline' not in n:
                        par_values2[n+'_%d' % c] = par_values[n]
                    else:
                        par_values2[n] = par_values[n]
        else:
            par_values2 = par_values
            
        return par_values2
        
    # ======================================================================= #
    def get_fn(self,fn_name,ncomp=1,pulse_len=-1,lifetime=-1):
        """
            Get the fitting function used.
            
                fn_name: string of the function name users will select. 
                ncomp: number of components, ex if 2, then return exp+exp
                pulse_len: duration of beam on in s
                lifetime: lifetime of probe in s
            
            Returns python function(x,*pars)
        """
        
        # set fitting function
        if fn_name == 'Lorentzian':
            fn =  fns.lorentzian
            self.mode='1f'
        elif fn_name == 'Gaussian':
            fn =  fns.gaussian
            self.mode='1f'
        elif fn_name == 'Exp':
            fn =  fns.pulsed_exp(lifetime,pulse_len)
            self.mode='20'
        elif fn_name == 'Str Exp':
            fn =  fns.pulsed_strexp(lifetime,pulse_len)
            self.mode='20'
        else:
            raise RuntimeError('Fitting function not found.')
        
        # Make final function based on number of components
        fnlist = [fn]*ncomp
        
        if self.mode in ['1f']:
            fnlist.append(lambda x,b: b)
        fn = fns.get_fn_superpos(fnlist)
        
        return fn
        
        
        
        
        

# Base functions used in fitting bnmr data
# Derek Fujimoto
# June 2018
from bfit.fitting.integrator import PulsedFns
import numpy as np

# =========================================================================== #
class code_wrapper(object):
    """Wrap code object such that attemps to access co_varnames excludes self"""
    def __init__(self,obj):
        self.co_varnames = obj.co_varnames[1:]
        self.co_argcount = obj.co_argcount-1
        self.obj = obj
    
    def __getattr__(self,name):
        try:
            return self.__dict__[name]
        except KeyError:
            return getattr(self.obj,name)

# =========================================================================== #
# TYPE 1 FUNCTIONS
# =========================================================================== #
def lorentzian(freq,peak,width,amp):
    return -amp*0.25*np.square(width)/(np.square(freq-peak)+np.square(0.5*width))

def bilorentzian(freq,peak,widthA,ampA,widthB,ampB):
    return -ampA*0.25*np.square(widthA)/(np.square(freq-peak)+np.square(0.5*widthA))\
           -ampB*0.25*np.square(widthB)/(np.square(freq-peak)+np.square(0.5*widthB))

def gaussian(freq,mean,sigma,amp):
    return -amp*np.exp(-np.square((freq-mean)/(sigma))/2)

# =========================================================================== #
# TYPE 2 PULSED FUNCTIONS 
# =========================================================================== #
class pulsed(object):
    """Pulsed function base class"""
    
    def __init__(self,lifetime,pulse_len):
        """
            lifetime: probe lifetime in s
            pulse_len: length of pulse in s
        """
        self.pulser = PulsedFns(lifetime,pulse_len)
    
    def __call__(self):pass
    
    def __getattr__(self,name):
        if name == '__code__':
            return code_wrapper(self.__call__.__code__)
        else:
            return getattr(self,name)

class pulsed_exp(pulsed):
    def __call__(self,time,lambda_s,amp):
        return amp*self.pulser.exp(time,lambda_s)
        
class pulsed_strexp(pulsed):
    def __call__(self,time,lambda_s,beta,amp):
        return amp*self.pulser.str_exp(time,lambda_s,beta)

# =========================================================================== #
# FUNCTION SUPERPOSITION
# =========================================================================== #
def get_fn_superpos(fn_handles):
    """
        Return a function which takes the superposition of a number of the same 
        function.
        
        fn_handles: list of function handles that should be superimposed
        
        return fn_handle
    """
    
    npars = np.cumsum([0]+[len(f.__code__.co_varnames)-1 for f in fn_handles])

    # make function
    def fn(x,*pars):
        return np.sum(f(x,*pars[l:h]) for f,l,h in zip(fn_handles,npars[:-1],npars[1:]))
    return fn

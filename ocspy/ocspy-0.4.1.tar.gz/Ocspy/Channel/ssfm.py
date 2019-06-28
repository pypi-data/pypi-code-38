import arrayfire as af
import numpy as np
from scipy.fftpack import fftfreq
from Ocspy.Base.SignalInterface import Signal
import math
def symmetric_ssfm(signal:Signal,setting:dict):
    '''
        :param:Signal a signal object
        :param:Setting: a dict contians the parameters of the fiber
        :Unit:
            alpha_lin: 1/km
            beta_2: s**2/km
            gamma: 1/w/km
            step_length:km
            fiber_length:km
    '''
    alpha_lin = setting['alpha_lin']
    beta2 = setting['beta2']
    gamma = setting['gamma']
    step_length = setting['step_length']
    fiber_length = setting['fiber_length']

    nsections = int(fiber_length / step_length)
    if nsections * step_length < fiber_length:
        last_step = fiber_length - nsections * step_length
    else:
        last_step = 0
    
    xpol = af.from_ndarray(signal[0,:])
    ypol = af.from_ndarray(signal[1, :])
    # xpol = samples[0,:]
    # ypol = samples[1,:]
    freq = fftfreq(len(xpol),1/signal.fs_in_fiber)
    omeg = 2*np.pi*freq
    omeg = af.from_ndarray(omeg)
    D = -1j/2 * beta2 * omeg**2
    step_length_eff = 1-math.exp(-alpha_lin*step_length)
    step_length_eff = step_length_eff / alpha_lin 
    for _ in range(nsections):
        xpol,ypol = linear_prop_arrayfire(xpol,ypol,step_length/2,D)
        xpol,ypol = nonlinear_prop(xpol,ypol,gamma,step_length_eff)
        xpol, ypol = linear_prop_arrayfire(xpol, ypol, step_length/2,D)
        xpol = xpol * math.exp(-alpha_lin/2 * step_length)
        ypol = ypol * math.exp(-alpha_lin/2 * step_length)
    if last_step:
        last_step_eff = 1-math.exp(-alpha_lin * last_step)
        last_step_eff = last_step_eff / alpha_lin
        xpol, ypol = linear_prop_arrayfire(xpol, ypol, last_step/2, D)
        xpol,ypol = nonlinear_prop(xpol,ypol,gamma,last_step_eff)
        xpol, ypol = linear_prop_arrayfire(xpol, ypol, last_step/2,D)
        xpol = xpol * math.exp(-alpha_lin/2 * last_step)
        ypol = ypol * math.exp(-alpha_lin/2 * last_step)

    xpol = xpol.to_ndarray()
    ypol = ypol.to_ndarray()
    xpol = np.asarray(xpol,order='C')
    ypol = np.asarray(ypol,order='C')
    return xpol,ypol

def nonlinear_prop(xpol,ypol,gamma,length):
    
    gamma = 1j*gamma* 8/9*length
    xpol = xpol * af.exp(gamma*(af.abs(xpol)**2 + af.abs(ypol)**2))
    ypol = ypol * af.exp(gamma*(af.abs(xpol)**2 + af.abs(ypol)**2))
    return xpol,ypol

def linear_prop_arrayfire(xpol,ypol,length,D):
    xpol_fft = af.fft(xpol)
    ypol_fft = af.fft(ypol)
    xpol_fft = xpol_fft * af.exp(D*length)
    ypol_fft = ypol_fft * af.exp(D*length)
    xpol =  af.ifft(xpol_fft)
    ypol =  af.ifft(ypol_fft)
    return xpol,ypol











import numpy as np

def interpu(x, xp, fp, left=None, right=None, period=None):
    ''' Wrapper for np.interp when using astropy units'''
    
    fp0 = fp.value
    x0 = x.value
    if x.unit == xp.unit:
        xp0 = xp.value
    else:
        xp0 = xp.to(x.unit).value

    result = np.interp(x0, xp0, fp0, left=left, right=right, period=period)
    return result * fp.unit

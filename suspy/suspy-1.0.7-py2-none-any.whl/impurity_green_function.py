#-*- coding: utf-8 -*-
import numpy as np
from scipy import integrate
import tqdm
import numba 
import multiprocessing as mp

@numba.jit(nopython=True)
def e(x, y, z, t1, t2, t4):
    return 2 * (t1 * (np.cos(x) + np.cos(y) + np.cos(z)) + t4 * (np.cos(2 * x) + np.cos(2 * y) + np.cos(2 * z)) 
                + 2 * t2 * (np.cos(x) * np.cos(y) + np.cos(z) * np.cos(x) + np.cos(y) * np.cos(z)))
@numba.jit(nopython=True)
def g0_real(x, y, z, t1, t2, t4, wn, sigma, mu):
    return (mu - e(x, y, z, t1, t2, t4) - sigma.real) / ((mu - e(x, y, z, t1, t2, t4) - sigma.real) ** 2 + (-wn + sigma.imag) ** 2)
@numba.jit(nopython=True)
def g0_imag(x, y, z, t1, t2, t4, wn, sigma, mu):
    return (-wn + sigma.imag) / ((mu - e(x, y, z, t1, t2, t4) - sigma.real) ** 2 + (-wn + sigma.imag) ** 2)

def f(funcs, args, x, opt, _dict, k): 
    return _integrate(funcs, args, x, opt, _dict, k)

def _integrate(funcs, args, x, opt, _dict, k):
    real = integrate.nquad(funcs[0], [x] * 3, args=args, opts=opt)
    imag = integrate.nquad(funcs[1], [x] * 3, args=args, opts=opt)
    _dict[k] = real[0] + 1j * imag[0]
    return _dict

def g_imp(t1, t2, t4, wn, num_iw, sigma=0, mu=0, limit=50):
    g0 = np.zeros(num_iw, dtype=np.complex64)
    if  type(sigma) == int:
        sigma = np.zeros(num_iw, dtype=np.complex64)
    V = 8 * np.pi**3
    opt = {'limit' : limit, 'epsrel' : 1e-8, 'epsabs' : 1e-8}
    x = [-np.pi, np.pi]
    m = mp.Manager()
    _dict = m.dict()
    p = [mp.Process(target=f, args=([g0_real, g0_imag], (t1, t2, t4, wn[k], sigma[k], mu), x, opt, _dict, k)) for k in range(mp.cpu_count() - 1)]
    for i in p:
        i.start()
    while k < num_iw:
        for i in range(mp.cpu_count() - 1):
            if not p[i].is_alive() and k < num_iw:
                p[i] = mp.Process(target=f, args=([g0_real, g0_imag], (t1, t2, t4, wn[k], sigma[k], mu), x, opt, _dict, k))
                p[i].start()
                k += 1
    for i in p:
        i.join()
    for k in range(num_iw):
        g0[k] = _dict[k]
    return g0 / V
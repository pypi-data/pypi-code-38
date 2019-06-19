from pytriqs.gf import *
from pytriqs.gf.meshes import MeshImTime, MeshImFreq
from scipy.optimize import curve_fit
import numpy as np
import pickle

def green_function(half_band, beta, num_iw=256, mu = 0):
    '''t, beta, num_iw'''
    gw = GfImFreq(mesh = MeshImFreq(beta, 'Fermion', num_iw), indices = [1])
    gw << SemiCircular(half_band)
    g0tilde_iw = GfImFreq(mesh = MeshImFreq(beta, 'Fermion', num_iw), indices = [1])
    g0tilde_iw << inverse(iOmega_n + mu -  (half_band / 2.0) ** 2 * gw )
    return g0tilde_iw.data[:,0,0][num_iw:]

def fourier(beta, G, num_iw):
    n_points = len(G)
    gt = GfImTime(mesh = MeshImTime(beta, 'Fermion', n_points), indices = [1])
    gt.data[:,0,0] = G
    gw = GfImFreq(mesh = MeshImFreq(beta, 'Fermion', num_iw), indices = [1])
    gw << Fourier(gt)
    return gw.data[:,0,0]

def inverse_fourier(beta, g0_iw, n_points=10000):
    '''beta, g0_iw,  num_iw'''
    num_iw = len(g0_iw) 
    gt = GfImTime(mesh = MeshImTime(beta, 'Fermion', n_points), indices = [1])
    gw = GfImFreq(mesh = MeshImFreq(beta, 'Fermion', num_iw), indices = [1])
    gw.data[:,0,0] = g0_iw
    gt << InverseFourier(gw)
    return gt.data[:,0,0].real
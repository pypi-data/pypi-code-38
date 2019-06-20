from pytriqs.gf import *
from pytriqs.gf.meshes import MeshImTime, MeshImFreq
import numpy as np

def fourier(beta, G, num_iw):
    statistic = 'Fermion'
    n_points = len(G)
    gt = GfImTime(mesh = MeshImTime(beta, statistic, n_points), indices = [1])
    gt.data[:,0,0] = G
    gw = GfImFreq(mesh = MeshImFreq(beta, statistic, num_iw//2), indices = [1])
    gw << Fourier(gt)
    return gw.data[:,0,0]

def inverse_fourier(beta, g0_iw, n_points=10000):
    '''beta, g0_iw,  num_iw'''
    statistic = 'Fermion'
    num_iw = len(g0_iw) 
    gt = GfImTime(mesh = MeshImTime(beta, statistic, n_points), indices = [1])
    gw = GfImFreq(mesh = MeshImFreq(beta, statistic, num_iw//2), indices = [1])
    gw.data[:,0,0] = g0_iw
    gt << InverseFourier(gw)
    return gt.data[:,0,0].real

def w2tau(temp, beta):
    '''Convert green function from matsubara frequencies to imaginary time'''
    temp = np.concatenate((np.conj(temp[::-1]), temp))
    return inverse_fourier(beta, temp, n_points=10000)
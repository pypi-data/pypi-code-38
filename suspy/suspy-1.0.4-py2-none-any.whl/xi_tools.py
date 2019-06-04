
import pyed.CubeTetras as CT
import numpy as np
import numba

from pytriqs.gf import Gf, GfImTime
from pytriqs.gf import MeshImTime, MeshProduct
from pyed.SparseExactDiagonalization import SparseExactDiagonalization


@numba.njit(fastmath=True, parallel=True)
def get_timeordered_three_tau_greens_function(G, taus, dops, E, Z, beta):
    
    op1, op2, op3, op4 = dops
    
    for i in numba.prange(len(G)):
        et_a = op1 * (np.exp((-beta + taus[0][i])*E)).reshape((len(E),1))
        et_b = op2 * (np.exp((taus[1][i]-taus[0][i])*E)).reshape((len(E),1))
        et_c = op3 * (np.exp((taus[2][i]-taus[1][i])*E)).reshape((len(E),1))
        et_d = op4 * (np.exp((-taus[2][i])*E)).reshape((len(E),1))
        G[i] = np.sum(np.diag(np.dot(et_a, np.dot(et_b, np.dot(et_c, et_d)))))
    G = G / Z
    return G

def set_g2_tau(ed, g_tau, ops):
    tau = np.array([tau.value for tau in g_tau.mesh])
    g_tau.data[:,0,0] = ed.get_tau_greens_function_component(tau, ops[0], ops[1])

def set_g4_tau(ed, g4_tau, ops):
    ops_mat = np.array(ops)
    for idxs, taus, perm, perm_sign in CT.CubeTetrasMesh(g4_tau):
        ops_perm_mat = ops_mat[perm + [3]]
        taus_perm = np.array(taus).T[perm]
        data = np.zeros((taus_perm.shape[-1]), dtype=np.complex)
        dops = [op.toarray() for op in ed._operators_to_eigenbasis(ops_perm_mat)]
        
        data = get_timeordered_three_tau_greens_function(data, taus_perm, dops, ed.E, ed.Z, ed.beta)
        
        for idx, d in zip(idxs, data):
            g4_tau[CT.Idxs(idx)] = perm_sign * d

def init_gfs(ed, n_tau, beta, ops):
    g2_tau1 = GfImTime(name=r'$G^{(2)}(\tau_1)$', beta=beta, statistic='Fermion', n_points=n_tau, indices=[1])
    g2_tau2 = GfImTime(name=r'$G^{(2)}(\tau_1)$', beta=beta, statistic='Fermion', n_points=n_tau, indices=[1])

    imtime = MeshImTime(beta, 'Fermion', n_tau)
    prodmesh = MeshProduct(imtime, imtime, imtime)
    g4_tau = Gf(name=r'$G^{(4)}(\tau_1,\tau_2,\tau_3)$', mesh=prodmesh, target_shape=[1, 1, 1, 1])

    set_g2_tau(ed, g2_tau1, ops[:2])
    set_g2_tau(ed, g2_tau2, ops[2:])
    set_g4_tau(ed, g4_tau, ops)
    
    return g2_tau1, g2_tau2, g4_tau

@numba.njit(parallel=True, fastmath=True)
def xi_mats(mtx, g2_1, g2_2, g4, wn, tau, dt):
    '''Compute susceptibility in matsubara frequencies'''
    
    size = len(tau)
    num_iw = len(wn)
    beta = np.sum(dt)
    for m in numba.prange(num_iw):
        for n in range(num_iw//2):
            for i in range(size):
                for j in range(size):    
                    mtx[m, n] -= np.exp(-1j*(wn[m] * tau[i] + wn[n] * tau[j])) * g2_1[i] * g2_2[j] * dt[i] * dt[j] * beta
                    for k in range(size):
                        mtx[m, n] += np.exp(-1j*(wn[m] * (tau[i] - tau[j]) + wn[n] * tau[k])) * g4[i, j, k] * dt[i] * dt[j] * dt[k]
            mtx[-m-1, -n-1] = np.conj(mtx[m, n])
            
@numba.njit(parallel=True, fastmath=True)
def xi_sc_iter(mtx, g4, wn, tau, dt):
    size = len(tau)
    num_iw = len(wn)
    for m in numba.prange(num_iw):
        for n in range(num_iw // 2):
            for i in range(size):
                for j in range(size):                     
                    for k in range(size):
                        mtx[m, n] += np.exp(-1j*(wn[m] * (tau[i] - tau[j]) + wn[n] * tau[k])) * g4[i, j, k] * dt[i] * dt[j] * dt[k]
            mtx[-m-1, -n-1] = np.conj(mtx[m, n])
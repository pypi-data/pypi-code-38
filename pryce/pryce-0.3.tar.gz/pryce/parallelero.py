import warnings
import psutil

import numpy as np
import numpy.random 
import scipy.optimize

from swutil.misc import split_integer
from swutil.hpc import EasyHPC
from swutil.np_tools import integral
from smolyak.applications.polynomials.polynomial_approximation import PolynomialSpace as PS

from pryce.ero import _scale

class EarlyTerminationException(Exception):
    pass

class ParallelPsi:
    '''
    Computational content is mostly in local function psi in __call__
    Everything else is parallelization.
    See simple_implementation.simple_ero for the core logic
    '''
    def __init__(self, model, k, M, random=np.random, parallel=False, save_memory=True, early_termination=False):
        self.poly_space = PS(n=1+model.d_eff, k=k)
        self.model = model
        self.M = M
        self.N = self.model.N
        self.B = self.poly_space.dimension
        self.parallel = parallel
        self.save_memory = save_memory
        self.early_termination = early_termination
        self.random = random
        self.new_samples()
        @EasyHPC(parallel=self.parallel)
        def gram(j):
            _, _, polynomials = self.path_slice(j)
            N, M = polynomials.shape[:2]
            X = polynomials.reshape(M*N, -1)
            return X.T@X/N
        G = np.sum(gram(range(self.nslices)), axis=0) / self.M
        self.scale = _scale(G)

    def new_samples(self):
        ncpus = psutil.cpu_count(logical=False) if self.parallel else 1
        memavail = psutil.virtual_memory()[1]
        min_nslices = int(8*self.M*self.N*5*self.B/(memavail/2))+1 if self.save_memory else 1
        self.slice_sizes = split_integer(self.M, length=ncpus*min_nslices)
        mempredicted = 8*self.N*5*self.B*sum(self.slice_sizes[:ncpus])
        if mempredicted > memavail:
            raise ValueError(f'Computation would require {mempredicted/2**30}GB memory but only {memavail/2**30}GB are available. Use save_memory=True')
        self.storage = {}
        self.rand_states = [np.random.RandomState(self.random.randint(2**32)) for j in self.slice_sizes]
        self.nslices = len(self.slice_sizes)
        self.n_calls = 0
        self.values = []
        self.derivatives = []
        self.value_stds = []
        self.coeffs = []

    def path_slice(self, j):
        if j not in self.storage:
            securities, times = self.model(self.slice_sizes[j], random=self.rand_states[j])
            payoffs = np.exp(-self.model.r * times)[:, None] * self.model.payoff(securities)
            N, M = securities.shape[:2]
            arrays = [np.tile(times, M)[:, None], securities.reshape((N * M, -1), order='F')]
            polynomials = self.poly_space.evaluate_basis(np.concatenate(arrays, axis=1)).reshape((N, M, -1), order='F')
            if not self.save_memory:
                self.storage[j] = times, payoffs, polynomials
        else:
            times, payoffs, polynomials = self.storage[j]
        return times, payoffs, polynomials

    def __call__(self, coeff=None, for_optimization=False):
        self.n_calls+=1
        self.coeffs.append(coeff)
        @EasyHPC(parallel=self.parallel)
        def psi(j):
            times, payoffs, polynomials = self.path_slice(j)
            if coeff is None:
                intensities = np.zeros(polynomials.shape[:2])
            else:
                warnings.filterwarnings("ignore")
                intensities = np.exp(np.einsum('ijk,k->ij', polynomials, self.scale@coeff))
            intensities[payoffs == 0] = 0
            dintensities = intensities[..., None]*polynomials
            survivals = np.exp(-integral(A=intensities, F=times, cumulative=True))
            early = np.sum((survivals[:-1] - survivals[1:]) * payoffs[:-1], axis=0)
            final = survivals[-1] * payoffs[-1]
            y = early + final
            if not self.early_termination:
                dsurvivals = -survivals[..., None] * integral(A=dintensities, F=times, cumulative=True)
                dsurvivals[np.isnan(dsurvivals)] = 0
                dearly = np.sum((dsurvivals[:-1]-dsurvivals[1:])*payoffs[:-1, :, None], axis=0)
                dfinal = dsurvivals[-1]*payoffs[-1, :, None]
                dy = dearly + dfinal
            return np.mean(y), np.std(y), np.nan if self.early_termination else self.scale.T@np.mean(dy, axis=0)
        values, stds, derivatives = zip(*psi(range(self.nslices)))
        self.values.append(np.average(values, axis=0, weights=self.slice_sizes))
        self.value_stds.append(np.sqrt(np.average(np.array(stds)**2, axis=0, weights=self.slice_sizes)/self.M))
        self.derivatives.append(np.average(derivatives, axis=0, weights=self.slice_sizes))
        if self.early_termination and self.n_calls>1 and self.values[-2]>self.values[-1]:
            raise EarlyTerminationException
        if for_optimization:
            return -self.values[-1], -self.derivatives[-1]
        else:
            return self.values[-1], self.value_stds[-1]

def pryce_parallelero(model, k, M, random=np.random, parallel=True, save_memory=True, maxfun=40):
    '''
    Compute American option prices using exercise rate optimization

    :param model: Market model
    :type model: Function that generates random market trajectories
    :param k: Polynomial degree
    :param M: Number of random market trajectories to be used in optimization
    :param parallel: Run computations in parallel
    :param save_memory: If you run out of memory
    '''
    psi = ParallelPsi(model, k, M, random=random, parallel=parallel, save_memory=save_memory)
    psi_earlytermination = ParallelPsi(model, k, M, random=random, parallel=parallel, save_memory=save_memory,early_termination = True)
    def callback(x):
        if psi.n_calls>8 and psi.n_calls%3==0:
            psi_earlytermination(x)
        print(f"{100*(psi.n_calls-1)/maxfun:.0f}%", end='\r')
    try:
        result = scipy.optimize.minimize(
            lambda x: psi(x, for_optimization=True),
            np.zeros(psi.B),
            method='L-BFGS-B',
            jac=True,
            callback=callback,
            options={'disp': False, 'gtol': 0, 'ftol': 0, 'maxfun': maxfun}
        )
    except EarlyTerminationException:
        print(f'Early termination after {len(psi.values)} steps')
    v_train,coeff = psi.values[-1],psi.coeffs[-1]
    psi.new_samples()
    v_test, std = psi(coeff)
    v_europ, _ = psi()
    return v_test, std, v_train, v_europ

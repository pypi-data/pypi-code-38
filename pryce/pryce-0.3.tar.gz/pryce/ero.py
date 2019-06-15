import warnings

import numpy as np
from scipy.optimize import minimize

from smolyak.applications.polynomials.polynomial_approximation import PolynomialSpace

def _scale(G):
    try:
        return np.linalg.inv(np.linalg.cholesky(G).T)
    except Exception:
        w, v = [np.real(x) for x in np.linalg.eig(G)]
        return v@np.diag(1/np.sqrt(np.maximum(w, 1e-16)))

def pryce_ero(model, k, M, random=np.random, maxfun=20, verbose=False):
    '''
    Compute American option prices using Exercise Rate Optimization

    :param model: Market model
    :type model: Function that generates random market trajectories
    :param k: Polynomial degree
    :param M: Number of random market trajectories to be used in optimization
    :param maxfun: Number of optimization steps
    '''
    class Samples:
        def __init__(self,model,k,scale = None, random=random):
            self.poly_space = PolynomialSpace(n=1+model.d_eff, k=k, probability_distribution = 't')
            securities, times = model(M,random)
            self.payoffs = np.exp(-model.r * times)[:, None] * model.payoff(securities)
            arrays = [np.tile(times, M)[:, None], securities.reshape((model.N *M, -1), order='F')]
            self.polynomials = self.poly_space.evaluate_basis(np.concatenate(arrays, axis=1))
            self.scale = scale if scale is not None else _scale(self.polynomials.T@self.polynomials/model.N/M)
            self.dt = model.T/(model.N-1)
        def psi(self,coeff,std = False):
            warnings.filterwarnings("ignore")
            intensities = np.exp(self.polynomials@(self.scale@coeff)).reshape((model.N, M), order='F')
            intensities[self.payoffs==0] = 0
            dintensities = intensities[..., None]*self.polynomials.reshape((model.N, M, -1), order='F')
            survivals = np.exp(np.concatenate([np.zeros((1, M)), -np.cumsum(intensities[:-1]*self.dt, axis=0)], axis=0))
            if std:
                p = np.sum((survivals[:-1] - survivals[1:]) * self.payoffs[:-1],axis=0)+survivals[-1]*self.payoffs[-1]
                return np.mean(p),np.std(p)/np.sqrt(M)
            early = np.sum((survivals[:-1] - survivals[1:]) * self.payoffs[:-1])/M
            final = np.mean(survivals[-1] * self.payoffs[-1])
            dsurvivals = -survivals[..., None] * np.concatenate([np.zeros((1, M, self.poly_space.dimension)), np.cumsum(dintensities[:-1]*self.dt, axis=0)], axis=0)
            dsurvivals[np.isnan(dsurvivals)] = 0
            dearly = np.mean(np.sum((dsurvivals[:-1]-dsurvivals[1:])*self.payoffs[:-1, :, None], axis=0), axis=0)
            dfinal = np.mean(dsurvivals[-1]*self.payoffs[-1, :, None], axis=0)
            return -(early+final), -self.scale.T@(dearly+dfinal)
    training_samples = Samples(model, k, random=random)
    trained = minimize(
        training_samples.psi,
        np.zeros(training_samples.poly_space.dimension),
        method='L-BFGS-B',
        jac=True,
        options={'disp': verbose, 'gtol': 0, 'ftol': 0, 'maxfun': maxfun}
    )
    scale = training_samples.scale
    del training_samples
    test_samples = Samples(model, k, scale=scale, random=random)
    return (*test_samples.psi(trained.x, std=True), -trained.fun, np.mean(test_samples.payoffs[-1]))


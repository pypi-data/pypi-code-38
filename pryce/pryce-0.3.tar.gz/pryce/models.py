'''
Models that are passed to pryce must return a tuple 
(securities,times) when called with argument M, where `securities`
contains M random trajectories of the modelled securities 
sampled at the times in `times`

`securities` must have shape (len(times),M,self.d_eff) 
where self.d_eff is the effective dimensionality of the model
(i.e. the number of securities plus possible stochastic 
volatility components or their historic values for non-Markovian models)

Mandatory members of a model class:
self.d_eff 
self.payoff
__call__(self,M)
'''
from pprint import pformat

import numpy as np

from swutil.stochastic_processes import black_scholes, r_bergomi, heston 

class BlackScholes:

    def __init__(self, d, T, sigma, r, S0, N, payoff=None, dividend=0):
        self.d = d
        self.d_eff = self.d
        self.T = T
        self.sigma = sigma
        self.r = r
        self.S0 = S0
        self.N = N
        self.payoff = payoff
        self.dividend = dividend

    def __call__(self, M, random=np.random):
        times = np.linspace(0, self.T, self.N)
        securities = np.log(black_scholes(
            times,
            self.r - self.dividend,
            self.sigma,
            self.S0,
            self.d,
            M,
            random=random,
        )).transpose([1, 0, 2])
        return securities, times

    def __repr__(self):
        return pformat(vars(self))

class Heston:

    def __init__(self, d, T, nu0, theta, r, kappa, xi, rho, S0, N, payoff):
        self.d = d
        self.d_eff = d + 1
        self.T = T
        self.nu0 = nu0
        self.theta = theta
        self.kappa = kappa
        self.rho = rho
        self.xi = xi
        self.r = r
        self.S0 = S0
        self.N = N
        self.payoff = payoff
        self.payoff.d = self.d

    def __call__(self, M, random=np.random):
        times = np.linspace(0, self.T, self.N)
        securities = np.log(heston(
            times,
            mu=self.r,
            rho=self.rho,
            kappa=self.kappa,
            theta=self.theta,
            xi=self.xi,
            S0=self.S0,
            nu0=self.nu0,
            d=self.d,
            M=M,
            random=random,
        )).transpose([1,0,2])
        return securities, times

    def __repr__(self):
        return pformat(vars(self))

class RoughBergomi:

    def __init__(self, H, T, eta, xi, rho, S0, N, r, payoff, J, memory):
        self.H = H
        self.T = T
        self.eta = eta
        self.xi = xi
        self.rho = rho
        self.S0 = S0
        self.N = N
        self.r = r
        self.J = J
        self.memory = memory
        self.d = 1  # Supports only 1d markets at the moment
        self.d_eff = 2*self.d * (self.J+1)
        self.payoff = payoff
        self.payoff.d = self.d
        lags = np.linspace(0, self.memory, self.J + 2)[:-1]
        lag_indices = np.rint(lags*(self.N-1)).astype(int)
        self.lag_indices = np.unique(lag_indices)
        if len(self.lag_indices)<self.J+1:
            raise ValueError('Cannot use that many lags; increase N or memory') 
        
    def __call__(self, M, random=np.random):
        times = np.linspace(0, self.T, self.N)
        rb = np.log(r_bergomi(
            H=self.H, T=self.T, eta=self.eta, xi=self.xi, rho=self.rho,
            S0=self.S0, r=self.r,N=self.N, M=M, return_v=True, random=random,
        )).transpose([1,0,2])
        rb_extended = np.concatenate(
            [np.tile(rb[[0]], (self.N-1, 1, 1)), rb],
            axis=0,
        )
        securities_and_lags = np.concatenate(
            [rb_extended[self.N-1-li:2*(self.N-1)+1-li] for li in self.lag_indices],
            axis=2,
        )
        return securities_and_lags, times

    def __repr__(self):
        return pformat(vars(self))

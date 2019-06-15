import warnings
import numpy as np
from smolyak.applications.polynomials.polynomial_approximation import PolynomialSpace

def pryce_ls(model, k, M, random=np.random):
    '''
    Compute American option prices using the Longstaff--Schwartz algorithm

    :param model: Market model
    :type model: Function that generates random market trajectories
    :param k: Polynomial degree
    :param M: Number of random market trajectories to be used in optimization
    :param random: RandomState
    '''
    poly_space = PolynomialSpace(n=model.d_eff, k=k)
    securities, times = model(M,random)
    N = model.N
    continuation_values = [lambda x: np.zeros(len(x))]
    C = model.payoff(securities[-1])
    for i in range(N-2, -1, -1):
        print(f'{10+(N-2-i)/(N-2)*60:.0f}%', end='\r')
        C *= np.exp(-model.r * (times[i + 1] - times[i]))
        x = securities[i]
        payoffs = model.payoff(x)
        cv = poly_space.get_approximation(X=x[payoffs > 0], Y=C[payoffs > 0])
        continuation_values.append(cv)
        exercise = (payoffs > cv(x)) & (payoffs > 0)
        C[exercise] = payoffs[exercise]
    v_train = np.mean(C)
    securities, times = model(M,random)
    exercised = np.zeros(M, dtype=bool)
    C = np.nan*np.zeros(M)
    for i in range(N):
        print(f'{80+20*i/(N-1):.0f}%', end='\r')
        x = securities[i]
        payoffs = model.payoff(x)
        exercise = (payoffs > continuation_values[~i](x)) & (payoffs > 0)
        C[~exercised & exercise] = np.exp(-model.r*times[i])*payoffs[~exercised & exercise]
        exercised |= exercise
    C[~exercised] = np.exp(-model.r*times[-1])*payoffs[~exercised]
    return np.mean(C), np.std(C)/np.sqrt(M), v_train, np.exp(-model.r*model.T)*np.mean(payoffs)

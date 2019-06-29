import Bayest as BayestInterp
from KDTree import *
import numpy as np

def bayest_Test(S, V, Snew):

    # pick the first Power point to interpolate (because we know that the solution is V[0, :])
    sample = np.array([S[0, :]])

    # interpolate
    Vnew = BayestInterp.interpolate(S, sample, V, 0.01)

    # compute the difference
    diff = Vnew[0, :] - V[0, :]

    print('Error: ', max(abs(diff)))

    # Repeat test with a larger sample
    Vnew = BayestInterp.interpolate(S, Snew, V, 0.1)

    return Vnew


def KDTree_test(S, V, Snew):

    Nnear = 18  # 8 2d, 11 3d => 5 % chance one-sided -- Wendel, mathoverflow.com
    leafsize = 25
    eps = 1e-3  # approximate nearest, dist <= (1 + eps) * true nearest
    p = 1  # weights ~ 1 / distance**p
    # cycle = .25
    # seed = 1
    invdisttree = InvDistTree(S, V, leafsize=leafsize, stat=1)

    # pick the first Power point to interpolate (because we know that the solution is V[0, :])
    sample = np.array([S[0, :]])

    # interpolate
    Vnew = invdisttree(sample, nnear=Nnear, eps=eps, p=p)

    # compute the difference
    diff = Vnew[0, :] - V[0, :]

    print('Error: ', max(abs(diff)))

    # Repeat test with a larger sample
    Vnew = invdisttree(Snew, nnear=Nnear, eps=eps, p=p)

    return Vnew

if __name__ == '__main__':
    import time

    print('Test')
    res = np.load('Bus6_stochastic_voltages.npz')

    V = res['V']
    S = res['S']

    Snew = list()
    dim = len(S.transpose())
    p_min = np.array([np.min(S[:, i]) for i in range(dim)])
    p_max = np.array([np.max(S[:, i]) for i in range(dim)])
    rnd = np.random.random_sample(1000).transpose()
    for r in rnd:
        Snew.append(p_min + (p_max - p_min) * r)
    Snew = np.array(Snew)


    # KDTree
    print('KDTree')
    start_time = time.time()
    Vk = KDTree_test(S, V, Snew)
    tk = time.time() - start_time
    print("--- %s seconds ---" % tk)

    # Bayest
    print('Bayest')
    start_time = time.time()
    Vb = bayest_Test(S, V, Snew)
    tb = time.time() - start_time
    print("--- %s seconds ---" % tb)

    print(tb / tk)

    diff = Vk - Vb
    print('\nMax abs difference: ', np.max(diff))
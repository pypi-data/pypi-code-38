import cPickle
import numpy as np
from scipy.stats import binom, scoreatpercentile


def calc_sf_all(v, n, p):
    sf_values = np.log10(1 / binom.sf(v, n, p))
    sf_values[np.isinf(sf_values)] = 1
    return sf_values

v_arr, n_arr, p, names_arr = cPickle.load(open('/home/mark/tmp.pickle', 'r'))

all_pvals = calc_sf_all(v_arr, n_arr, p)
idx_best_100 = np.argsort(-all_pvals)
v_arr = v_arr[idx_best_100]
n_arr = n_arr[idx_best_100]
names_arr = names_arr[idx_best_100]
all_pvals = all_pvals[idx_best_100]

# def calc_F(X1, n, lenF):
#     F = [0] * lenF#np.zeros(lenF)
#     F[0] = 1
#     inrange = range(lenF-1, -1, -1)
#     for j in xrange(0, n, 1):
#         diffv = X1[j]
#         for jj in inrange[:-diffv]:
#             F[jj] += F[jj-diffv]
#     return F

def calc_F(X1, n, lenF):
    F = np.zeros(lenF, dtype=np.int32)
    F[0] = 1
    # inrange = range(lenF-1, -1, -1)
    for j in xrange(0, n, 1):
        diffv = X1[j]
        ar_shift = shift5(F, X1[j], 0)
        F = F + ar_shift
        # for jj in inrange[:-diffv]:
        #     F[jj] += F[jj-diffv]
    return F

def shift5(arr, num, fill_value=np.nan):
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result = arr
    return result

for idx, nm in enumerate(names_arr[:1000]):

    # D1 = np.array([1, 0, 0])
    # Q1 = np.array([0.1, 0.1, 0.1])
    n_t = int(n_arr[idx])
    n_m = int(v_arr[idx])
    n_d = n_t - n_m
    D1 = np.array([1] * n_m + [0] * n_d)
    Q1 = np.array([p] * n_t)
    B_prob1 = np.prod(Q1 * D1 + (1 - D1)) * np.prod((1 - Q1) * (1 - D1) + (D1))
    X1_s = np.log((1-Q1)/Q1)
    k = np.max(X1_s) / 1000
    X1 = np.round(X1_s / k).astype(int)
    Q = np.sum(np.log(Q1))
    Y1_s = np.log(B_prob1) - Q
    Y1 = int(np.round(Y1_s / k))
    S1_s = np.sum(X1 * (1 - D1))
    lenF = int(1 + np.sum(X1))
    n = n_t#len(D1)

    F = calc_F(X1, n, lenF)

    Sr = np.arange(0, Y1 + 1, 1)
    eSr = np.exp(k * Sr + Q)
    Prob_final = np.sum(F[:Y1+1]*eSr)
    # prots_spc[nm] = Prob_final#all_pvals[idx]
    print(nm, Prob_final, n_m, n_t, all_pvals[idx])

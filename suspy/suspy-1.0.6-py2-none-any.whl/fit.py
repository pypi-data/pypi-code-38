#-*- coding: utf-8 -*-
import numpy as np
import numba
import copy
import fft
from scipy.optimize import minimize
@numba.jit(fastmath=True)
def get_param(g0, beta, wn, size, mu, V=None, ei=None, bound_v=(-2.0, 2.0), bound_e=(-2.0, 1.5), shift=0.1, erabs=1e-08):
    '''
    Возвращает значение параметров фиттированной функции Грина
    -------
    g0 : Функция Грина :: np.array(compex)
    wn : Матцубаровские частоты :: np.array(float)
    size : Число узлов фермионной ванны :: int
    V, ei : Фитируемые параметры (перескоки с кластера на ванну и затравочная энегрия на ванне) :: 0 or np.array(float)
    bound_v, bound_e : Границы для искомых параметров :: tuple
    \\\\\ Параметры для варьирования хим потенциала
    shift : шаг :: float
    erabs : точность ::  float
    -----
    Returns: V, e, mu :: np.array(float), np.array(float), float
    '''
    # Параметры для минимизации
    if type(V) != int:
        V = V.copy()
        ei = ei.copy()
        V += 0.5 * (2 * np.random.rand(size) - 1) # Добавляем шум к уже найденным параметрам 
        ei += 0.5 * (2 * np.random.rand(size) - 1)
    else:
        V = np.random.rand(size) # Работает при первой итерации
        ei = np.random.rand(size)
    init = np.concatenate((V, ei))
    bounds = [bound_v] * size + [bound_e] * size
    model = minimize(diff, args=(g0, wn, mu), x0=init, tol=1e-08, bounds=bounds)
    V = np.concatenate((model.x[:size],model.x[:size]))
    e = np.concatenate((model.x[size:],-model.x[size:]))
    #mu = find_mu(g0, beta, wn, V, e, mu, shift, erabs)
    return abs(V), e #, mu

@numba.autojit(fastmath=True)
def diff(par, g0, wn, mu):
    '''
    Рассчитывает разность между извесной гибридизационной функцией (g0 ** -1 - 1j*wn)
    и фиттируемой функции delta с произвольными начальными параметрами c учетом веса weight = 1 / wn
    '''
    delta = np.zeros(len(wn), dtype=np.complex64) 
    edge = len(par) // 2 
    V = par[:edge]
    e = par[edge:]
    for i in range(edge):
        delta -= V[i] ** 2 / (1j * wn - e[i])
        delta -= V[i] ** 2 / (1j * wn + e[i])
    return np.sum(abs((g0 ** -1).imag*1j - 1j*wn - mu - delta)**2 / wn)

def _func(wn, V, e, mu):
    res = np.zeros(len(wn), dtype=np.complex128)
    for i in range(len(V)):
        res -= (V[i]) ** 2 / (1j * wn  - e[i])
    return (res + mu + 1.0j * wn) ** -1

def find_mu(temp, beta, wn, Vcd, ec, mu, shift=0.1, erabs=1e-08):
    '''Find value of mu corresponding to half filling'''
    cur = prev = fft.w2tau(temp, beta)[0] + 0.5
    while abs(prev) > erabs:           
        if cur * prev > 0 and prev > 0:
            mu -= shift
        elif cur * prev > 0 and prev < 0:
            mu += shift
        elif cur * prev < 0 and prev > 0:
            shift /= 2
            mu -= shift
        else:
            shift /= 2
            mu += shift
        cur, prev = fft.w2tau(_func(wn, Vcd, ec, mu), beta)[0] + 0.5, cur
    return mu
        
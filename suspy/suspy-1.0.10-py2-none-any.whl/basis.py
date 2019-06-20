#-*- coding: utf-8 -*-
import numpy as np
import itertools
import copy
from math import factorial as fact


def bose(m, n):
    '''Возвращает базис для Бозе-статистики. m - число узлов, n - число частиц'''
    R = fact(n + m - 1)/fact(n)/fact(m - 1)
    b = np.zeros((R,m), dtype=np.int8)
    b[0,m-1] = n
    for i in range(R-1):
        j = m - 1
        while j > 0:
            if b[i,j] in range(2,n+1) :
                b[i+1,:] = b[i,:]
                b[i+1,j] = 0
                b[i+1,j-1] = b[i+1,j-1] + 1
                b[i+1,m-1] = b[i,j] - 1
                break
            elif b[i,j] > 0:
                b[i+1,:] = b[i,:]
                b[i+1,j-1] = b[i+1,j-1] + 1
                b[i+1,j] = b[i,j] - 1
                break
            j -= 1
    return b

def limit_basis(m, n, n_max):
    '''Возвращает базис для Бозе-статистики с ограничением числа частиц на узле. 
    m - число узлов, n - число частиц, n_max - максимальное число частиц на узле.'''
    # Размерность базиса
    R = fact(n + m - 1)/fact(n)/fact(m - 1)
    b = bose(m,n)
    f = np.zeros((R,m), dtype=np.int8)
    j = 0
    # Откиддываем функции, в которых на узлах частиц больше n_max
    for i in range(b.shape[0]):
        if any(b[i] > n_max): 
            continue
        else:
            f[j] = b[i]
            j += 1
    return f[:j]

def bose_unsave(m, n):
    '''Возвращает базис для Бозе статистики с несохраняющимся числом частиц.
    m - число узлов, n - максимальное число частиц на узле
    '''
    return np.array( map(list, itertools.product(range(n+1),repeat=m)) )

def fermi(m, n_up, n_down):
    '''Возвращает базис для Ферми-статистики с учетом спина.'''
    R = (fact(m)/fact(n_up)/fact(m-n_up))*(fact(m)/fact(n_down)/fact(m-n_down)) 
    fs = np.zeros((R,2*m), dtype=np.int8)
    part_1 = limit_basis(m,n_up,1)
    if n_up == n_down:
        part_2 = copy.copy(part_1)
    else:
        part_2 = limit_basis(m,n_down,1)
    size_1, size_2 = part_1.shape[0], part_2.shape[0]
    for i in range(size_1):
        for j in range(size_2):
            fs[i*size_2+j] = np.concatenate((part_1[i],part_2[j]), axis=0)
    return fs

def full_basis_save(m_d, m_c, m_b, n_down, n_up, n_max):
    '''
    Возвращает базис с сохраняющимся числом частиц
    ----------------------------------
    md - число узлов в кластере, 
    mc - число узлов в Ферми ванне, 
    mb - число узлов в Бозе ванне,
    n_up - число частиц со спином вверх, n_down - число частиц со спином вниз,
    n_max - максимум частиц на узле в Бозе ванне
    '''
    mtx_1 = fermi(m_d+m_c, n_up,n_down)
    mtx_2 = bose_unsave(m_b,n_max)
    size_1, size_2 = mtx_1.shape[0], mtx_2.shape[0]
    fb = np.zeros((size_1*size_2,mtx_1.shape[1]+m_b),dtype=np.int8)
    for i in range(size_1):
        for j in range(size_2):
            fb[i*size_2+j] = np.concatenate((mtx_1[i],mtx_2[j]), axis=0)
    return fb
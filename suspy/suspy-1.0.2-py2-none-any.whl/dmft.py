#-*- coding: utf-8 -*-
import numpy as np
import tqdm
import impurity_green_function as igf
from scipy.optimize import minimize
from pyed.SparseExactDiagonalization import SparseExactDiagonalization
from holstein import A
import fit
import fft 
import bethe_green_function as bgf
import copy
#warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt

class DMFT(A):
    def __init__(self, mc, n_max, Ud, beta, num_iw, Vcd, gamma_bd, ec, eb, mu, delta):
        '''
            g0 : Функция Грина :: np.array(compex)
            wn : Матцубаровские частоты :: np.array(float)
        '''
        A.__init__(self, mc, n_max, Ud, Vcd, gamma_bd, ec, eb, mu, delta)
        self.num_iw = num_iw // 2
        self.beta = beta
        self.wn = np.pi / self.beta * (2 * np.arange(0, self.num_iw) + 1)
        
  
    def main_loop(self, n_loops, mu, temp, tot=0.5):
        '''
        Запускает DMFT цикл
        ------
        n_loops : Число иттераций :: int
        temp : Начальная функция Грина (ождиается только для положительных матцубаровских частот) :: np.array(dtype=compex)
        '''
        self.g0 = temp
        self.g0_cl_prev = temp
        self.g_list = np.zeros((n_loops, self.num_iw), dtype=np.complex64)
        self.g0_list = np.zeros((n_loops+1, self.num_iw), dtype=np.complex64)
        self.g0_list[0, :] = self.g0
        self.all_tot = []
        #for l in tqdm.tqdm_notebook(range(n_loops), leave=False):
        for l in range(n_loops):
            print "loop {0} / {1}\r".format(l+1, n_loops)
            self.g0, self.g_list[l, :] = self._iter(mu, tot)
            self.g0_list[l+1, :] = self.g0
        
    def _iter(self, mu, tot):
        while True:    
            try:
                k, d = 0, 100  # k и d нужны для проверки точности найденных параметров v, e
                while d > tot and k < 1000:                                                                                                        
                    #v, e, mu, shift = fit.get_param(self.g0, self.beta, self.wn, self.mc, self.mu, 0, 0, (-4.0, 4.0), (-4.0, 4.0), shift=0.1, erabs=1e-14)              
                    v, e = fit.get_param(self.g0, self.beta, self.wn, self.mc//2, 0., 0, 0, (-4.0, 4.0), (-4.0, 4.0), shift=0.2, erabs=1e-14)  
                    d = fit.diff(np.concatenate((v[:self.mc//2],e[:self.mc//2])), self.g0, self.wn, 0.).real                                                              
                    k += 1
                assert k < 1000
                self.all_tot.append((d, tot))
                break
            except:
                tot += 0.05
        #print "before fitting \n<n>={}\ntot={}".format(np.round(fft.w2tau(self.g0, self.beta)[-1], 10), self.all_tot[-1])
        self.Vcd, self.ec = v, e
        self.init_calc()
        self.g0_cl_prev = fit._func(self.wn,self.Vcd,self.ec,0.)
        #print "\nAfter fiting \n<n>={}\nmu={}\n".format(np.round(fft.w2tau(fit._func(self.wn, self.Vcd, self.ec, 0.), self.beta)[-1], 10), 0.)
    
    def get_g0(self):
        ''' Возвращает свободную функцию Грина '''
        return np.concatenate((np.conj(self.g0[::-1]), self.g0))
    
    def get_g(self):
        ''' Возвращает итоговую функцию Грина '''
        return np.concatenate((np.conj(self.g_list[-1][::-1]), self.g_list[-1]))

class Square(DMFT):
    
    def __init__(self, t, mc, n_max, Ud, beta, num_iw, Vcd, gamma_bd, ec, eb, mu, delta):
        DMFT.__init__(self, mc, n_max, Ud, beta, num_iw, Vcd, gamma_bd, ec, eb, mu, delta)
        assert (type(t) == tuple or type(t) == list) and len(t) == 3, 'Expect that t is tuple or list with length 3'
        self.t1, self.t2, self.t4 = t
        self.g0 = igf.g_imp(self.t1, self.t2, self.t4, self.wn, self.num_iw, mu=self.mu)
    
    def _iter(self, mu, tot):
        ''' Единичная итерация в цикле DMFT '''
        DMFT._iter(self, mu, tot)
        self.ed = SparseExactDiagonalization(self.get_H(), self.get_blocks(), self.beta)
        g = self.ed.get_frequency_greens_function_component(1j * self.wn, self.c_up(), self.c_dag_up(), -1.0) # xi parametr in new version of pyed
        self.sigma = self.g0_cl_prev ** -1 - g ** -1
        g = igf.g_imp(self.t1, self.t2, self.t4, self.wn, self.num_iw, self.sigma, mu)
        return (self.sigma + g ** -1) ** -1, g
    
    def main_loop(self, n_loops, mu, temp, tot):
        DMFT.main_loop(self, n_loops, mu, temp, tot)
        
        self.DO = self.ed.get_expectation_value(self.n_up().dot(self.n_down()))
        self.nb_mean = self.ed.get_expectation_value(self.b_dag().dot(self.b()))
        self.b_dag_mean = self.ed.get_expectation_value(self.b_dag())

class Bethe(DMFT):
    
    def __init__(self, t, mc, n_max, Ud, beta, num_iw, Vcd, gamma_bd, ec, eb, mu,delta): 
        DMFT.__init__(self, mc, n_max, Ud, beta, num_iw, Vcd, gamma_bd, ec, eb, mu,delta)
        self.t = t
        #self.g0 = bgf.green_function(2.0 * self.t, self.beta, self.num_iw, self.mu)
    
    def _iter(self, mu, tot):
        ''' Единичная итерация в цикле DMFT '''
        DMFT._iter(self, mu, tot)
        self.ed = SparseExactDiagonalization(self.get_H(), self.get_blocks(), self.beta)
        g = self.ed.get_frequency_greens_function_component(1j * self.wn, self.c_up(), self.c_dag_up(), -1.0) # xi parametr in new version of pyed
        #print 'n_claster =  ', fft.w2tau(g, self.beta)[-1]
        return (1j*self.wn + mu - self.t ** 2 * g) ** -1, g
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 19:02:42 2019

@author: ys
"""

import matplotlib.pyplot as plt
import numpy as np

def logistics_f(x, pars):
    L = pars[0]
    k = pars[1]
    x0 = pars[2]
    return L / (1 + np.exp(-k*(x-x0)))

def main():
    
    pars = [1,1,0]
    x = np.arange(-10, 10, 0.01)

    plt.plot(x, logistics_f(x, pars))
    plt.ylabel('some numbers')
    plt.show()


if __name__ == '__main__':
    main()
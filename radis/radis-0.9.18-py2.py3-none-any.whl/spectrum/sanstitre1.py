# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 16:59:50 2018

@author: erwan
"""

N = 1000        # number of individuals
M = 100         # number of generations
from numpy.random import rand, randint
import matplotlib.pyplot as plt
import numpy as np

thr = 0.3

# Initiation
chrom_list = []
for i in range(N):
    x = 'b' if rand()<thr else 'k'
    y = 'b' if rand()<thr else 'k'
    chrom_list.append((x,y))

# Expression
phen_list = []
for (x,y) in chrom_list:
    expr = 'b' if x==y=='b' else 'k'
    phen_list.append(expr)
    
fraction = sum([i == 'b' for i in phen_list])/len(phen_list)
print("Initial population: {0:.2f}% blue eyes".format(fraction*100))
fraction_list = [fraction]
    
for i, generation in enumerate(range(M)):
    
    # Reproduction
    new_chrom_list = []
    for j in range(N):
        xx = chrom_list[randint(N)][randint(2)]   # father
        xy = chrom_list[randint(N)][randint(2)]   # mother
        new_chrom_list.append((xx,xy))
    
    # Expression
    phen_list = []
    for (x,y) in chrom_list:
        expr = 'b' if x==y=='b' else 'k'
        phen_list.append(expr)
        
    fraction = sum([i == 'b' for i in phen_list])/len(phen_list)
    print("Generation {0}: {1:.2f}% blue eyes".format(i+1, fraction*100))
    fraction_list.append(fraction)
    
    chrom_list = new_chrom_list


plt.figure()
plt.plot(range(1,M+2), np.array(fraction_list)*100, 'ok')
plt.ylabel('Blue eyed individuals')
plt.xlabel('Generations')


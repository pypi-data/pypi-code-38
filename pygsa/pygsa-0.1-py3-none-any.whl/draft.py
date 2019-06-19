import brightway2 as bw
import numpy as np
import pandas as pd
import sys

from scipy.stats import lognorm, norm, triang

from pypardiso import spsolve
from itertools import compress

from constants import *
from saindices.sobol_indices import sobol_indices


###1. LCA model
bw.projects.set_current('Sobol indices')

method = ('IPCC 2013', 'climate change', 'GWP 100a')
ei = bw.Database('ecoinvent 3.5 cutoff')
bs = bw.Database('biosphere3')
demand_act = [act for act in ei if 'market for electricity, high voltage'==act['name'] and 'CH' in act['location']][0]
demand_amt = 1
demand = {demand_act: demand_amt}

lca = bw.LCA(demand,method)
lca.lci()
lca.lcia()

q_low  = (1-THREE_SIGMA_Q)/2
q_high = (1+THREE_SIGMA_Q)/2

A = lca.technosphere_matrix
B = lca.biosphere_matrix
c = sum(lca.characterization_matrix)
lca.build_demand_array()
d = lca.demand_array

cB = c*B
score_initial = cB*spsolve(A,d) #run it before MC to factorize matrix A

def get_distr_indices_params(lca,id_distr):
    list_ = lca.tech_params['uncertainty_type']==id_distr
    indices = list(compress(range(len(list_)), list_))
    params = lca.tech_params[indices]
    return indices,params

indices_lognor,params_lognor = get_distr_indices_params(lca,ID_LOGNOR)
indices_normal,params_normal = get_distr_indices_params(lca,ID_NORMAL)
indices_triang,params_triang = get_distr_indices_params(lca,ID_TRIANG)

n_params = len(lca.tech_params)
n_lognor = len(params_lognor)
n_normal = len(params_normal)
n_triang = len(params_triang)


def score_from_sample(lca,sobol_sample):
    
    vector = lca.tech_params['amount']

    q = (q_high-q_low)*sobol_sample[:n_normal] + q_low
    params_normal_new  = norm.ppf(q,loc=params_normal['loc'],scale=params_normal['scale'])
    np.put(vector,indices_normal,params_normal_new)
    del q

    q = sobol_sample[n_normal:n_normal+n_triang]
    loc   = params_triang['minimum']
    scale = params_triang['maximum']-params_triang['minimum']
    c     = (params_triang['loc']-loc)/scale
    params_triang_new = triang.ppf(q,c=c,loc=loc,scale=scale)
    np.put(vector,indices_triang,params_triang_new)
    del q

    #TODO implement group sampling
#     q = (q_high-q_low)*samples[:,:n_lognor] + q_low
    q = (q_high-q_low)*np.random.rand(n_lognor) + q_low
    params_lognor_new = lognorm.ppf(q,s=params_lognor['scale'],scale=np.exp(params_lognor['loc']))
    np.put(vector,indices_lognor,params_lognor_new)

    lca.rebuild_technosphere_matrix(vector)
    score = (cB*spsolve(lca.technosphere_matrix,d))[0]
        
    return score
    

def lca_model(sample):
    score = score_from_sample(lca,sample)
    return score



n_samples    = int(input("Enter number of MC runs: "))
n_dimensions = int(input("Enter number of parameters: "))

t = sobol_indices(n_samples,n_dimensions,lca_model)

print(t)



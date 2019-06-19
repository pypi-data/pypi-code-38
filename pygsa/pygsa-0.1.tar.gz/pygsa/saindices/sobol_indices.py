from sampling.sobol_sequence import SobolSample
import numpy as np
import time
from copy import copy


def sobol_indices_one(Sampler,Model):
    """
    Run Monte Carlo simulations and compute Sobol indices while generating samples one at a time.

    Parameters
    ----------
    Sampler : class
        Class that generates one sample of size n_dimension at a time using method __next__ or 
        all samples simultaneously as a matrix of size n_samples x n_dimensions    
    Model
        Object that generates scalar model output given one sample of size n_dimension

    Returns
    -------
    first_index : np.array
        An array object that contains first-order Sobol indices for all n_dimensions
    total_index : np.array
        An array object that contains total order Sobol indices for all n_dimensions

    Literature
    ----------
    [2009] Saltelli et al 
    Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index
    https://doi.org/10.1016/j.cpc.2009.09.018

    """

	#Sampler generates n_samples number of samples, actual number of MC runs is n_samples//2
    n_runs = Sampler.n_samples//2
    next(Sampler) #TODO change later, some bug

    """C: Ideally these would be defined in the docstring"""
    """S: didn't understand this comment"""

    y_A = np.zeros(n_runs)
    y_B = np.zeros(n_runs)
    y_j = np.zeros([n_runs,Sampler.n_dimensions])

    total_index = np.zeros(Sampler.n_dimensions)
    first_index = np.zeros(Sampler.n_dimensions)

    #Monte Carlo simulations
    for i, sample_A, sample_B in zip(range(n_runs), Sampler, Sampler):

        y_A[i]   = Model(sample_A)
        y_B[i]   = Model(sample_B)

        for j in range(Sampler.n_dimensions):

            sample_j = copy(sample_A)
            sample_j[j] = sample_B[j]
            y_j[i][j] = Model(sample_j)

    #Total indices computation for all dimensions
    for j in range(Sampler.n_dimensions):

        total_index_temp = [(y_A[i]-y_j[i,j])**2 for i in range(n_runs)]
        total_index[j] = sum(total_index_temp) / 2 / n_runs

        first_index_temp = [y_B[i]*(y_j[i,j]-y_A[i]) for i in range(n_runs)]
        first_index[j] = sum(first_index_temp) / n_runs

    return first_index,total_index


def sobol_indices_all(Sampler,Model):
    """
    Run Monte Carlo simulations and compute Sobol indices while generating all samples at the same time.

    Parameters
    ----------
    Sampler : class
        Class that generates one sample of size n_dimension at a time using method __next__ or 
        all samples simultaneously as a matrix of size n_samples x n_dimensions    
    Model
        Object that generates scalar model output given one sample of size n_dimension

    Returns
    -------
    first_index : np.array
        An array object that contains first-order Sobol indices for all n_dimensions
    total_index : np.array
        An array object that contains total order Sobol indices for all n_dimensions

    Literature
    ----------
    [2009] Saltelli et al 
    Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index
    https://doi.org/10.1016/j.cpc.2009.09.018

    """

	#Sampler generates n_samples number of samples, actual number of MC runs is n_samples//2
    n_runs = Sampler.n_samples//2

    samples = Sampler.generate_all_samples() #TODO check whether there's a bug

    y_A = np.zeros(n_runs)
    y_B = np.zeros(n_runs)
    y_j = np.zeros(n_runs)

    total_index = np.zeros(Sampler.n_dimensions)
    first_index = np.zeros(Sampler.n_dimensions)

    A = samples[:n_runs]
    B = samples[n_runs:]

    #Monte Carlo simulations without resampling
    for i in range(n_runs):
        y_A[i] = Model(A[i])
        y_B[i] = Model(B[i])

    #Monte Carlo simulations of resampled inputsm and total indices computation for all dimensions
    for j in range(Sampler.n_dimensions): 

        J = copy(A)
        J[:,j] = B[:,j]
        y_j = [Model(J[i]) for i in range(n_runs)]

        total_index_temp = [(y_A[k]-y_j[k])**2 for k in range(n_runs)]
        total_index[j] = sum(total_index_temp) / 2 / n_runs

        first_index_temp = [y_B[k]*(y_j[k]-y_A[k]) for k in range(n_runs)]
        first_index[j] = sum(first_index_temp) / n_runs

    return first_index,total_index


def sobol_indices(n_runs,n_dimensions,Model,Sampler=None):
    """
    Wrapper function that chooses how to calculate Sobol indices depending on the problem.
    #For now, if problem has <1000 dimensions, generate all samples simultaneously. Otherwise, one sample at a time.

    Parameters
    ----------
    n_runs : int
        Number of Monte Carlo runs
    n_dimensions : int
        Number of parameters in the model that vary when performing sensitivity analysis
    Model
        Object that generates scalar model output given one sample of size n_dimension
    Sampler : class
        Class that generates one sample of size n_dimension at a time using method __next__ or 
        all samples simultaneously as a matrix of size n_samples x n_dimensions. 
        If not specified, will be chosen as Sobol quasi random sequences Sampler

    Returns TODO now returns time, change to return first and total order indices
    -------
    first_index : np.array
        An array object that contains first-order Sobol indices for all n_dimensions
    total_index : np.array
        An array object that contains total order Sobol indices for all n_dimensions
    """

    if n_dimensions < 1000:
        if Sampler is None:
        	Sampler = SobolSample(n_runs*2,n_dimensions)
        t0 = time.time()
        first_index,total_index = sobol_indices_all(Sampler,Model)
        t = time.time()-t0
    else:
        if Sampler is None:
        	Sampler = SobolSample(n_runs*2+1,n_dimensions) #TODO +1 is added due to a bug
        t0 = time.time()
        first_index,total_index = sobol_indices_one(Sampler,Model)
        t = time.time()-t0
    print(t)
    return first_index,total_index















## THIS FILE IS FOR DEBUGGING PURPOSES!
## IF THIS IS EVER COMMITED BY ACCIDENT PLEASE IGNORE :)

import numpy as np
import numpy.random as rng

import matplotlib.cm as cm
import matplotlib.pyplot as plt

import dynmix.dlm as dlm
import dynmix.independent as independent

rng.seed(1)
T = 62
n_a = 12
n_b = 8
n = 20

y_a, theta_a = dlm.simulate(T, np.eye(1), np.eye(1), np.eye(1) * 5, np.eye(1) * 2,
                            theta_init=np.ones(1) * 5, n=n_a)
y_b, theta_b = dlm.simulate(T, np.eye(1), np.eye(1), np.eye(1) * 8, np.eye(1) * 2,
                            theta_init=np.ones(1) * 11, n=n_b)

Y = np.hstack((y_a, y_b))

rng.seed(1)
F_list = [np.eye(1), np.eye(1)]
G_list = [np.eye(1), np.eye(1)]

rng.seed(1)
idx, theta, phi, eta = independent.estimator(Y, F_list, G_list)

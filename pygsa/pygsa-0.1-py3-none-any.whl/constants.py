from math import exp, pi
from scipy.integrate import quad
import numpy as np

###1. MATHS
#Calculate area under normal distribution within +-3 sigma interval from the mean. 
#Probability of a value to fall within this interval is THREE_SIGMA_Q = 99.7%. 
#This way tails of normal/lognormal distribution can be neglected.
m, s = 0, 1 #mean and standard deviation
THREE_SIGMA_Q = quad(lambda x: 1/np.sqrt(2*pi*s**2)*exp(-(x-m)**2/(2*s**2)),-3*s, 3*s)[0]

###2. DISTRIBUTIONS
#IDs for distributions from stats_array
ID_NODIST = 0 #no distribution available
ID_LOGNOR = 2 #lognormal
ID_NORMAL = 3 #normal
ID_TRIANG = 5 #triangular
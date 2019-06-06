#from Network_fetch import fetch1
#Net = fetch1(11)
#import numpy as np
#NetA = np.asarray(Net['A'])
#from Model import time_constant
##combine the Model and DataModel in a file
import numpy as np
from numpy import linalg as LA
import scipy
from scipy import sparse
from scipy.sparse import csc_matrix
from numpy import linalg as LA
class DataModel:
	def alpha(*arg):
		currentval = None
		if currentval is None:
			currentval = 0.01
		if len(arg) !=0:
			currentval = arg[0]
		val = currentval
		return val
	def type(*arg):
		currentval = None
		if currentval is None:
			currentval = 'directed'
		if len(arg) !=0:
			currentval = arg[0]
		val = currentval
		return val
	def tol(*arg):
		currentval = None
		if currentval is None:
			currentval = np.finfo(float).eps
		if len(arg) !=0:
			currentval = arg[0]
		val = currentval
		return val
	


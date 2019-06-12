"""rang = range"""
"""use dataRunParameters().alpha to call the variables"""
import numpy as np

class dataRunParameters:
	def __init__(self):
		self.alpha = 0.05
		self.cls = 'fcls'
		self.variable = 'SNRm'
		self.rang = np.logspace(-1,3,base=10,num=5)
		self.zetavec = np.logspace(-6,0,base=10,num=100)
		self.looco = False
		self.nit = np.arange(1,101)
		self.method = ''
		self.dataset = '' 
		self.network = ''  
    

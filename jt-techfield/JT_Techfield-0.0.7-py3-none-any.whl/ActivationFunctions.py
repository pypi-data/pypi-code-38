'''
Jacob Thompson

Activation Functions
'''
import numpy as np

class Activation():		
	def __init_subclass__(cls):
		cls.Eval = cls.Evaluate
		cls.__call__ = cls.Evaluate
		
		cls.D = cls.Derivative
	
class Sigmoid(Activation):
	def Evaluate(self, z):
		'''
		Evaluates the sigmoid of z:
			1 / (1 + e^(-z))
		'''
		return 1 / (1 + np.exp(-z))
		
	def Derivative(self, z):
		'''
		Evaluates the derivative of sigmoid of z:
			Sigmoid(z) * (1 - Sigmoid(z))
		'''
		sig = self.Evaluate(z)
		return sig * (1 - sig)
		


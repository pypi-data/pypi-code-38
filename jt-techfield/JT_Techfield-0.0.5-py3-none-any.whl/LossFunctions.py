'''
Jacob Thompson

LossFunctions.py
'''
import numpy as np

class SumOfSquaredResidual():
	'''
	Class that contains the formula for calculating the Sum of Squared Residual (aka Sum of Squared Error)
	'''
	def __init__(self):
		'''
		Initializes the object
		
		Note: Nothing really goes on here, but this will be the format for other loss functions
		'''
		self.name = 'Sum of Squared Residuals'
		
	def Evaluate(self, w_hat, x, y, y_hat):
		'''
		Evaluates the loss function given all the arguments
		
		Note: 	w_hat and x are unused, but they are used in other loss functions so we keep them as 
				input parameters for consistent formatting
		'''
		return ((y - y_hat).T @ (y - y_hat)).trace()
	
	def Derivative(self, w_hat, x, y, y_hat):
		'''
		Evaluates the derivative of the loss function given all the arguments
		
		Note: 	w_hat and x are unused, but they are used in other loss functions so we keep them as 
				input parameters for consistent formatting
		'''
		return x.T @ (y_hat - y)
		
class SumOfSquaredError(SumOfSquaredResidual):
	'''
	Alias for SumOfSquaredResidual
	'''
	pass
		
class L1SumOfSquaredResidual():
	'''
	Class that contains the formula for calculating the L1 Penalized Sum of Squared Residual (aka Sum of Squared Error)
	'''
	def __init__(self, lamb):
		'''
		Initializes the object and stores the parameter for lambda - the penalty modifier
		'''
		self.name = 'L1 Penalized Sum of Squared Residuals'
		self.lamb = lamb
		
	def Evaluate(self, w_hat, x, y, y_hat):
		'''
		Evaluates the loss function given all the arguments
		
		Note: 	x is unused, but it is used in other loss functions so we keep it as 
				an input parameter for consistent formatting
		'''
		return (
			((y - y_hat).T @ (y - y_hat)).trace() + 	# This is the formula for the typical Sum of Squared Residual
			self.lamb * np.sum(abs(w_hat))				# This is the formula for the L1 penalty
			)
	
	def Derivative(self, w_hat, x, y, y_hat):
		'''
		Evaluates the derivative of the loss function given all the arguments
		'''
		return (
			x.T @ (y_hat - y) + 			# This is the formula for the typical Sum of Squared Residual derivative
			self.lamb * np.sign(w_hat)		# This is the formula for the L1 penalty derivative
			)
			
class L1SumOfSquaredError(L1SumOfSquaredResidual):
	'''
	Alias for L1SumOfSquaredResidual
	'''
	pass
		
class L2SumOfSquaredResidual():
	'''
	Class that contains the formula for calculating the L2 Penalized Sum of Squared Residual (aka Sum of Squared Error)
	'''
	def __init__(self, lamb):
		'''
		Initializes the object and stores the parameter for lambda - the penalty modifier
		'''
		self.name = 'L2 Penalized Sum of Squared Residuals'
		self.lamb = lamb
		
	def Evaluate(self, w_hat, x, y, y_hat):
		'''
		Evaluates the loss function given all the arguments
		
		Note: 	x is unused, but it is used in other loss functions so we keep it as 
				an input parameter for consistent formatting
		'''
		return (
			((y - y_hat).T @ (y - y_hat)).trace() + 	# This is the formula for the typical Sum of Squared Residual
			self.lamb * float(w_hat.T @ w_hat)			# This is the formula for the L2 penalty
			)
	
	def Derivative(self, w_hat, x, y, y_hat):
		'''
		Evaluates the derivative of the loss function given all the arguments
		'''
		return (
			x.T @ (y_hat - y) + 	# This is the formula for the typical Sum of Squared Residual derivative
			self.lamb * w_hat		# This is the formula for the L2 penalty derivative
			)

class L2SumOfSquaredError(L2SumOfSquaredResidual):
	'''
	Alias for L2SumOfSquaredResidual
	'''
	pass

			
class L1L2SumOfSquaredResidual():
	'''
	Class that contains the formula for calculating the L1 and L2 Penalized Sum of Squared Residual (aka Sum of Squared Error) (aaka ElasticNet)
	'''
	def __init__(self, lamb_1 = None, lamb_2 = None, reg_rate = None, lamb = None):
		'''
		Initializes the object and stores the parameter for:
			lambda_1 - the penalty modifier for L1 penalization
			lambda_2 - the penalty modifier for L2 penalization
		'''
		if reg_rate and lamb:
			self.lamb_1 = reg_rate * lamb
			self.lamb_2 = reg_rate * (1-lamb)
		elif lamb_1 and lamb_2:
			self.lamb_1 = lamb_1
			self.lamb_2 = lamb_2
		self.name = 'L1 and L2 Penalized Sum of Squared Residuals'
		
		
	def Evaluate(self, w_hat, x, y, y_hat):
		'''
		Evaluates the loss function given all the arguments
		
		Note: 	x is unused, but it is used in other loss functions so we keep it as 
				an input parameter for consistent formatting
		'''
		return (
			((y - y_hat).T @ (y - y_hat)).trace() + 	# This is the formula for the typical Sum of Squared Residual
			self.lamb_1 * np.sum(abs(w_hat)) + 			# This is the formula for the L1 penalty
			self.lamb_2 * (w_hat.T @ w_hat).trace()		# This is the formula for the L2 penalty
			)
	
	def Derivative(self, w_hat, x, y, y_hat):
		'''
		Evaluates the derivative of the loss function given all the arguments
		'''
		return (
			x.T @ (y_hat - y) + 				# This is the formula for the typical Sum of Squared Residual derivative
			self.lamb_1 * np.sign(w_hat) + 		# This is the formula for the L1 penalty derivative
			self.lamb_2 * w_hat					# This is the formula for the L2 penalty derivative
			)
			
class L1L2SumOfSquaredError(L1L2SumOfSquaredResidual):
	'''
	Alias for L1L2SumOfSquaredResidual
	'''
	pass
			
class ElasticNet(L1L2SumOfSquaredResidual):
	'''
	Alias for L1L2SumOfSquaredResidual
	'''
	pass
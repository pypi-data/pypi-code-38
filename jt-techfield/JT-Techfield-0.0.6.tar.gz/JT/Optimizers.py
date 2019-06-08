'''
Jacob Thompson

Optimizers.py
'''
from JT.LossFunctions import *

import numpy as np


class Optimizer():
	
	def Echo(self, *args):
		if self.echo:
			args = list(args)
			for i in range(len(args)):
				if type(args[i]) != 'str':
					args[i] = str(args[i])
			print(' '.join(args))
			

class Linear_Regression(Optimizer):
	def __init__(self, lamb = 0, echo = False):
		self.name = 'Linear Regression'
		self.lamb = lamb
		
	
	def Train(self, x, y, echo = None):
		self.weights = np.linalg.inv(x.T @ x + np.eye(x.shape[1]) * self.lamb) @ x.T @ y	# Calculates weights based on the closed form formula for linear regression
		return self.weights

class Gradient_Descent(Optimizer):
	'''
		Runs Gradient Descent on the data
		
			rate: 				learning rate of the optimizer (eta)
			stop_difference: 	The minimum difference between each epoch's loss that will keep the optimizer running
			max_epochs: 		The maximum allowed epochs (the optimizer will stop after this many iterations)
			loss_func:			The loss function used for optimization. Loss functions can be found in LossFunctions.py
			
		Returns the calculated weights
	'''
	
	def __init__(self, rate, stop_difference = 1e-5, max_epochs = 1e6, loss_func = SumOfSquaredResidual(), echo = False):
		self.name = 'Gradient Descent'
		self.rate = rate
		self.stop_difference = stop_difference
		self.max_epochs = max_epochs
		self.loss_func = loss_func
		self.echo = echo
	
	def Train(self, training_set, validation_set = None,  echo = None):
		'''
			training_set: (x, y)
			validation_set: [validation_x, validation_y]
		'''
		if type(echo) != type(None):
			self.echo = echo
			
		x, y = training_set
		if not 'loss' in dir(self):
			self.loss = [0, np.inf]
		
		if type(validation_set) != type(None):
			val_x, val_y = validation_set
			if not 'val_loss' in dir(self):
				self.val_loss = [0, np.inf]
		
		if not 'weights' in dir(self):																	# Checks if the optimizer already has weights
			self.weights = np.random.randn(x.shape[1], y.shape[1])										# If it doesn't, initializes random weights
		
		i = 1
		while (abs(self.loss[i] - self.loss[i-1]) > self.stop_difference) and (i < self.max_epochs):	# While loop that stops when either the max epochs have elapsed or the stop difference is met
			y_hat = x @ self.weights																	# Calculates y_hat from the current weights
			gradient = self.loss_func.Derivative(self.weights, x, y, y_hat)								# Calcuates the gradient by calling the derivative of the loss function
			self.weights -= self.rate * gradient														# Adjusts the weights based on the gradient and the training rate
			self.loss.append(self.loss_func.Evaluate(self.weights, x, y, y_hat))						# Calculates loss and keeps track of it
			
			if type(validation_set) != type(None):
				val_y_hat = val_x @ self.weights
				self.val_loss.append(self.loss_func.Evaluate(self.weights, val_x, val_y, val_y_hat))
			
			self.Echo('Iteration:', i, '\tLoss:', self.loss[-1])										# If self.echo is True, will print the latest loss
			i += 1
			
		return self.weights
	
class Batch_Gradient_Descent(Optimizer):
	def __init__(self, rate, batch_size = 10, stop_difference = 1e-5, max_epochs = 1e6, loss_func = SumOfSquaredResidual(), echo = False):
		self.name = 'Batch Gradient Descent'
		self.rate = rate
		self.batch_size = batch_size
		self.stop_difference = stop_difference
		self.max_epochs = max_epochs
		self.loss_func = loss_func
		self.echo = echo
	
	def Train(self, training_set, validation_set = None,  echo = None):
		'''
		Runs Gradient Descent on the data
		
			rate: 				learning rate of the optimizer (eta)
			stop_difference: 	The minimum difference between each epoch's loss that will keep the optimizer running
			max_epochs: 		The maximum allowed epochs (the optimizer will stop after this many iterations)(
			loss_func:			The loss function used for optimization. Loss functions can be found in LossFunctions.py
			
		Calls self.Upkeep to update everything
		Returns the calculated weights
		'''
		
		if type(echo) != type(None):
			self.echo = echo
			
		x, y = training_set
		if not 'loss' in dir(self):
			self.loss = [0, np.inf]
		
		if type(validation_set) != type(None):
			val_x, val_y = validation_set
			if not 'val_loss' in dir(self):
				self.val_loss = [0, np.inf]
		
		if not 'weights' in dir(self):																	# Checks if the optimizer already has weights
			self.weights = np.random.randn(x.shape[1], y.shape[1])												# If it doesn't, initializes random weights
		
		i = 1
		
		while (abs(self.loss[i] - self.loss[i-1]) > self.stop_difference) and (i < self.max_epochs):	# While loop that stops when either the max epochs have elapsed or the stop difference is met
			batch_indices = (np.random.rand(self.batch_size) * x.shape[0]).astype(int)
			batch_x = x[batch_indices]
			batch_y = y[batch_indices]
			batch_y_hat = batch_x @ self.weights															# Calculates y_hat from the current weights
			gradient = self.loss_func.Derivative(self.weights, batch_x, batch_y, batch_y_hat)				# Calcuates the gradient by calling the derivative of the loss function
			diff = self.rate * gradient
			self.weights -= diff																# Adjusts the weights based on the gradient and the training rate
			self.loss.append(self.loss_func.Evaluate(self.weights, batch_x, batch_y, batch_y_hat))		# Calculates loss and keeps track of it
			
			if type(validation_set) != type(None):
				val_y_hat = val_x @ self.weights
				self.val_loss.append(self.loss_func.Evaluate(self.weights, val_x, val_y, val_y_hat))
			
			self.Echo('Iteration:', i, '\tLoss:', self.loss[-1])										# If self.echo is True, will print the latest loss
			i += 1
		return self.weights

class Stochastic_Gradient_Descent(Batch_Gradient_Descent):
	def __init__(self, rate, stop_difference = 1e-5, max_epochs = 1e6, loss_func = SumOfSquaredResidual(), echo = False):
		self.name = 'Stochastic Gradient Descent'
		self.rate = rate
		self.batch_size = 1
		self.stop_difference = stop_difference
		self.max_epochs = max_epochs
		self.loss_func = loss_func
		self.echo = echo


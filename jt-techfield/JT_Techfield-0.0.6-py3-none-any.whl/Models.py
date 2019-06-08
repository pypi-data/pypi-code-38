'''
Jacob Thompson

Models.py
'''

from JT.Transforms import Transform
from JT.Interactions import Interaction

# Downloaded Modules
import numpy as np
import matplotlib.pyplot as plot


class Model():

	def __init__(self, x, y, input_names = None, echo = True, norm = False, optimizer = None):
		self.x = x
		if not np.ones([self.x.shape[0], 1]) in self.x:					# Checks if the x array contains a column of ones for the intercept
			self.x = np.hstack([np.ones([self.x.shape, 1]), self.x])	# If there isn't a column of ones, adds one
		self.y = y
		self.input_names = input_names
		self.echo = echo
		self.residuals = None
		self.optimizer = optimizer
		
		# self.transform_map = []
		# self.interaction_map = []
		# for i in range(self.x.shape[1]):
			# row = []
			# for j in range(self.x.shape[1]):
				# row.append([])
			# self.interaction_map.append(row)	
			# self.transform_map.append([])
		
		if norm:
			self.Normalize()
	
	def AddTransform(self, transform, col_index):
		self.transform_map[col_index].append(transform)
	
	def BuildTransforms(self):
		self.transform_list = [[]] * self.x.shape[1]
		i = 0
		for transform_stack in self.transform_map:
			for transform in transform_stack:
				self.transform_list[i].append(transform(x[:, [i]]))
			i += 1
			
		return self.transform_list
	
	def ApplyTransforms(self, subset = None):
		if type(subset) == type(None):
			subset = self.x
			
		i = 0
		for transform_stack in self.transform_list:
			if transform_stack:
				transform_feature = subset[:, [i]]
				for transform in transform_stack:
					transform_feature = transform.Evaluate(transform_feature)
				subset = np.hstack([subset[:, :i], transform_feature, subset[:, (i + 1):]])
				i += transform_feature.shape[1]
			else:
				i += 1
		return subset
	
	def AddInteraction(self, interaction, col_index_1, col_index_2):
		self.interaction_map[col_index_1, col_index_2].append(interaction)
		
	def BuildInteractions(self):
		self.interaction_array = [[[]] * self.x.shape[1]] * self.x.shape[1]
		i = 0
		j = 0
		for interaction_row in self.interaction_map:
			for interaction_stack in interaction_row:
				for interaction in interaction_stack:
					self.interaction_array[i][j].append(interaction(x[:, [i]], x[:, [j]]))
				j += 1
			i += 1
	
	def ApplyInteractions(self, subset = None):
		'''
		WIP
		'''
		if type(subset) == type(None):
			subset = self.x
	
	def ApplyAll(self, subset = None):
		if type(subset) == type(None):
			subset = self.x
		i = 0
		j = 0
		for row in map:
			for stack in row:
				for operation in stack:
					if type(operation.super) == Interaction():
						interacted_feature = operation(subset[:, [i]], subset[:, [j]])
						subset = np.hstack()
	
	
	def Normalize(self):
		self.x_max = self.x.max()
		self.x_min = self.x.min()
		
		self.y_max = self.y.max()
		self.y_min = self.y.min()
		
		self.x = (self.x - self.x_min) / (self.x_max - self.x_min)
		self.y = (self.y - self.y_min) / (self.y_max - self.y_min)
		if 'y_hat' in dir(self):
			self.y_hat = (self.y_hat - self.y_min) / (self.y_max - self.y_min)
		
	def Denormalize(self):
		self.x = self.x * (self.x_max - self.x_min) + self.x_min
		self.y = self.y * (self.y_max - self.y_min) + self.y_min
		if 'y_hat' in dir(self):
			self.y_hat = self.y_hat * (self.y_max - self.y_min) + self.y_min
			
	def CategoryEncode(self, col_index):
		'''
		Expands a column of the explanitory variables into multiple columns of categorized variables:
			[	[red], 			[	[True,	False,	False], 
				[green], 			[False,	True, 	False], 
				[blue], 	->		[False,	False,	True ], 
				[red], 				[True,	False,	False], 
				[blue],	]			[False,	False,	True ], ]
				
		col_index:	The index of the column that will be categorized
		
		The categories will be derived from each unique entry in the given column
		Expands the column in place - actually changes self.x
		'''
		col = self.x[:, [col_index]]																			# Extracts the column ad col_index
		categories = list(set(col.flatten()))																	# Extracts the categories from the column by making a set() out of the flattened column and turning into a list (so we can iterate over it)
		categorical_columns = (col == categories)																# Expands the column into it's categorized array using '==' operator between two arrays (this makes it work like matrix multiplication but instead of mutliplying it does the == check)
		self.x = np.hstack([self.x[:, :col_index], categorical_columns, self.x[:, (col_index + 1):]])			# Replaces the column with the categorized array
		if self.input_names:																					# Checks if we are using input_names
			self.input_names = self.input_names[:col_index] + categories + self.input_names[(col_index + 1):]	# Replaces the input_names at the col_index with our category names
		return self.x	
		
	def BinnedEncode(self, col_index, bins = 50):
		col = self.x[:, [col_index]]
		bin_bounds = np.linspace(col.min(), col.max(), bins)
		bin_bounds_lower = bin_bounds[:-1]
		bin_bounds_upper = bin_bounds[1:]
		bin_bounds_upper[-1] = np.inf
		categorical_columns = (col >= bin_bounds_lower) & (col < bin_bounds_upper)
		self.x = np.hstack([x[:, :col_index], categorical_columns, x[:, (col_index + 1):]])
		return self.x
	
	def Train(self, echo = None):
		if type(echo) == type(None):
			echo = self.echo
			
		
		# self.BuildTransforms()
		# self.x = self.ApplyTransforms()
		
		self.weights = self.optimizer.Train((self.x, self.y), echo = echo)
		self.Upkeep()
		return self.weights
		
	def TrainAndValidate(self, ratio = [7, 1.5, 1.5], echo = None):
		if type(echo) == type(None):
			echo = self.echo
			
	
		# self.BuildTransforms()
		# self.ApplyTransforms()
		
		ratio = np.array(ratio)
		ratio = ratio / sum(ratio)
		indices = (ratio * self.y.shape[0]).astype(int)
		print(indices)
		
		
		train_x = self.x[:indices[0]]
		train_y = self.y[:indices[0]]
		
		test_x = self.x[indices[0]:-indices[-1]]
		test_y = self.y[indices[0]:-indices[-1]]
		
		validate_x = self.x[-indices[-1]:]
		validate_y = self.y[-indices[-1]:]
		
		self.weights = self.optimizer.Train((train_x, train_y), (validate_x, validate_y), echo)
		self.Upkeep()
		return self.weights
		
	def BatchTrain(self, batch_size, echo = None):
		if type(echo) == type(None):
			echo = self.echo
			
		batch_indices = (np.random.rand(batch_size) * x.shape[0]).astype(int)
		batch_x = x[batch_indices]
		batch_y = y[batch_indices]
		
		self.BuildTransforms()
		batch_x = self.ApplyTransforms(batch_x)
		self.weights = self.optimizer.Train((batch_x, batch_y), echo = echo)
		self.Upkeep()
		return self.weights
		'''
		=======		WIP		=======
		'''
	
	def RSquared(self):
		if type(self.residuals) == type(None):
			self.residuals = self.y - self.y_hat
		if not 'y_bar' in dir(self):	
			self.y_bar = np.mean(self.y)
		top = (self.residuals.T @ self.residuals).trace()
		bottom = ((self.y - self.y_bar).T @(self.y - self.y_bar)).trace()
		self.r_squared = 1 - top/bottom
		return self.r_squared
		
	def SSR(self):
		if type(self.residuals) == type(None):
			self.residuals = self.y - self.y_hat
		self.ssr = (self.residuals.T @ self.residuals).trace()
		return self.ssr
		
	def Fit(self):
		self.y_hat = self.x @ self.weights
		return self.y_hat
		
	def Predict(self, new_data):
		if not np.ones([self.x.shape[0], 1]) in new_data:
			new_data = np.hstack([np.ones([new_data.shape, 1]), new_data])
		if new_data.shape != self.x.shape:
			raise NameError("Data Shape doesn't match model")
		prediction = new_data @ self.weights
		return prediction
		
	def Test(self, test_data, test_results):
		prediction = self.Predict(test_data)
		loss = loss_func.eval(self.w_hat, new_data, test_results, prediction)
		print('Loss:', loss)
		return prediction
		
	def Upkeep(self):
		self.Fit()
		self.RSquared()
		self.SSR()
		
	def Echo(self, *args):
		if self.echo:
			args = list(args)
			for i in range(len(args)):
				if type(args[i]) != 'str':
					args[i] = str(args[i])
			print(' '.join(args))
			
	def Summary(self):
		print('Optimizer:\t\t', self.optimizer.name)
		if 'loss_func' in dir(self.optimizer):
			print('Loss Function:\t', self.optimizer.loss_func.name)
			print('Iterations:\t', len(self.optimizer.loss) - 1)
		if type(self.input_names) != type(None):
			print('\t'.join(self.input_names.flatten()[:5]))
		else:
			print('\t'.join([ 'w%g' % i for i in list(np.arange(self.x.shape[1])) ][:5]))
		print('\t'.join([ '%.2f' % weight for weight in list(self.weights.flatten())][:5]))
		print('--')
		print('R^2:\t', self.r_squared)
		print('SSR:\t', self.ssr)
		print()
			
	### Plotting
		
	def PlotLoss(self):
		if 'loss' in dir(self.optimizer):
			plot.plot(self.optimizer.loss[2:])
		if 'val_loss' in dir(self.optimizer):
			plot.plot(self.optimizer.val_loss[2:], 'r')
		
		plot.show()
		
	def WeightHistogram(self, bins = 10):
		plot.hist(self.weights, bins = bins)
		plot.show()
	
	def ResidualHistogram(self, bins = 10):
		if type(self.residuals) == type(None):
			self.residuals = self.y - self.y_hat
		plot.hist(self.residuals, bins = bins)
		plot.show()	

	def ResidualPlot(self):
		plot.plot(self.y, self.y)
		plot.plot(self.y, self.y_hat)
		
			
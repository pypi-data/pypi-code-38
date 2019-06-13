'''
Jacob Thompson

Models.py
'''
from copy import copy


from JT.Transforms import Transform
from JT.Interactions import Interaction
from JT.Timer import Timer

# Downloaded Modules
import numpy as np
import matplotlib.pyplot as plot


class Model():

	def __init__(self, x, y, val_x = None, val_y = None, input_names = None, echo = True, norm = False, optimizer = None):
		self.x = x
		self.y = y
		self.val_x = val_x
		self.val_y = val_y
		self.input_names = input_names
		self.echo = echo
		self.residuals = None
		self.optimizer = optimizer
		self.timer = Timer()
	
	def Train(self, echo = None):
		if type(echo) == type(None):
			echo = self.echo
		
		self.timer.tic()
		self.weights = self.optimizer.Train((self.x, self.y), echo = echo)
		self.loss = self.optimizer.loss[-1]
		
		self.elapsed = self.timer.toc()
		self.Upkeep()
		return self.weights
		
	def TrainAndValidate(self, ratio = [7, 1.5, 1.5], echo = None):
		if type(echo) == type(None):
			echo = self.echo
			
		if type(echo) != type(None):
			self.echo = echo
			
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
		self.timer.tic()
		self.weights = self.optimizer.Train((train_x, train_y), (validate_x, validate_y), echo)
		self.elapsed = self.timer.toc()
		self.Upkeep()
		return self.weights
		
	def CrossValidate(self, fold_number = 5, echo = None):
		if type(echo) == type(None):
			echo = self.echo
			
		if type(echo) != type(None):
			self.echo = echo
		sort_arg = np.argsort(self.y[:, 0])
		y = self.y[sort_arg, :]
		x = self.x[sort_arg, :]
	
		folds_x = []
		folds_y = []
		for i in range(fold_number):
			sample_indices = np.arange(i, x.shape[0], fold_number)
			folds_x.append(x[sample_indices, :])
			folds_y.append(y[sample_indices, :])
			
		loss_agg = 0
		acc_agg = 0
		self.Echo('Preforming Cross-Fold Validation with', fold_number, 'folds')
		self.timer.tic()
		for i in range(fold_number):
			self.Echo(f'\tFold {i+1}/{fold_number}') 
			train_x = copy(folds_x)
			train_y = copy(folds_y)
			
			val_x = train_x.pop(i)
			val_y = train_y.pop(i)
			
			train_x = np.vstack(train_x)
			train_y = np.vstack(train_y)
			
			self.weights = self.optimizer.Train((train_x, train_y), (val_x, val_y), False)
			
			self.Upkeep()
			
			loss_agg += self.optimizer.val_loss[-1]
			acc_agg += self.Accuracy()
			
			self.Echo('\t\tAverage Loss:', loss_agg / (i+1))
			self.Echo('\t\tAverage Accuracy:', acc_agg / (i+1))
		self.elapsed = self.timer.toc()
		
		self.avg_loss = loss_agg / fold_number
		self.avg_acc = acc_agg / fold_number
		return self.avg_loss
		
		
		
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
		print('R^2:\t\t\t\t', self.r_squared)
		print('Loss:\t\t\t\t', self.optimizer.loss[-1])
		print('Time Elapsed:\t', round(self.elapsed, 2))
		print()
			
	### Plotting
		
	def PlotLoss(self):
		if 'loss' in dir(self.optimizer):
			plot.plot(self.optimizer.loss[2:])
		if 'val_loss' in dir(self.optimizer):
			plot.plot(self.optimizer.val_loss[2:], 'r')
		
		plot.show()
		
	def WeightHistogram(self, bins = 10, non_zero_threshold = 0):
		plot.hist(self.weights[abs(self.weights) >= non_zero_threshold], bins = bins)
		plot.show()
		
	
	def ResidualHistogram(self, bins = 10):
		if type(self.residuals) == type(None):
			self.residuals = self.y - self.y_hat
		plot.hist(self.residuals, bins = bins)
		plot.show()	

	def ResidualPlot(self):
		plot.plot(self.y, self.y)
		plot.plot(self.y, self.y_hat)
		
	def ROC(self, step_size = 0.01):
		p_hat = self.optimizer.loss_func.activation(self.y_hat)
		y = np.round(self.y) == 1
		tpr = []
		fpr = []
		min_dist = np.inf
		auc = 0
		for t in np.arange(0, 1 + step_size, step_size):
			y_cat = p_hat >= t
			tp = np.sum(y & y_cat)
			fp = np.sum((y == False) & y_cat)
			tn = np.sum((y == False) & (y_cat == False))
			fn = np.sum(y & (y_cat == 0))
			
			tpr.append(tp / (tp + fn))
			fpr.append(fp / (fp + tn))
			
			dist = (np.sqrt((1 - tpr[-1]) ** 2 + fpr[-1] ** 2))
			
			if dist < min_dist:
				min_dist = dist
				opt_t = t

			auc += tpr[-1] * step_size
		
		opt_i = int(opt_t / step_size)
		plot.plot(fpr, tpr)
		plot.plot([0, 1], [0, 1], 'k:')
		plot.scatter(fpr[opt_i], tpr[opt_i], c='g')
		
		print('Area Under Curve:\t', round(auc, 3))
		print('Optimal Threshold:\t', opt_t)
		print('At this threshold:')
		print('\tAccuracy:', round(self.Accuracy(opt_t), 3))
		print('\tPrecision:', round(self.Precision(opt_t), 3))
		print('\tRecall:', round(self.Recall(opt_t), 3))
		print('\tF1 Score:', round(self.F1Score(opt_t), 3))
		return auc
	
	def OutcomeMatrix(self, threshold = 0.5):
		p_hat = self.optimizer.loss_func.activation(self.y_hat)
		y_cat = p_hat >= threshold
		y = np.round(self.y) == 1
		
		tp = np.sum(y & y_cat)
		fp = np.sum((y == False) & y_cat)
		tn = np.sum((y == False) & (y_cat == False))
		fn = np.sum(y & (y_cat == 0))
		return tp, tn, fp, fn
	
	def Accuracy(self, threshold = 0.5):
		tp, tn, fp, fn = self.OutcomeMatrix(threshold)
		return (tp + tn) / (tp + tn + fp + fn)
		
	def Precision(self, threshold = 0.5):
		tp, tn, fp, fn = self.OutcomeMatrix(threshold)
		return tp / (tp + fp)
	
	def Recall(self, threshold = 0.5):
		tp, tn, fp, fn = self.OutcomeMatrix(threshold)
		return tp / (tp + fn)
		
	def F1Score(self, threshold = 0.5):
		tp, tn, fp, fn = self.OutcomeMatrix(threshold)
		precision = tp / (tp + fp)
		recall = tp / (tp + fn)
		return 2 * precision * recall / (precision + recall)
	
import numpy as np
from .base import ContiniousLearningRate

class ExponentialLearningRate(ContiniousLearningRate):

	@property
	def factor(self):
		return pow(10, np.log10(self._target / self._lr) / self._epochs)

	def new_lr(self, epoch):
		return self._lr * self.factor ** epoch

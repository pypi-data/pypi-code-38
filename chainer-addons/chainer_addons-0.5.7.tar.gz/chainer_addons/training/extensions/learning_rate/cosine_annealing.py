import numpy as np
from .base import ContiniousLearningRate

class CosineAnnealingLearningRate(ContiniousLearningRate):

	@property
	def factor(self):
		return 0.5 * (self._lr - self._target)

	def new_lr(self, epoch):
		epochs = self._epochs - self._offset
		return self._target + self.factor * (1 + np.cos(np.pi * (epoch) / epochs))

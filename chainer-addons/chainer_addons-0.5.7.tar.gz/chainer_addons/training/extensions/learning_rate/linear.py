from .base import ContiniousLearningRate

class LinearLearningRate(ContiniousLearningRate):

	def new_lr(self, epoch):
		return self._lr - (self.factor * epoch)

	@property
	def factor(self):
		return (self._lr - self._target) / self._epochs

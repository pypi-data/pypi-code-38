from chainer.training import extension

from abc import ABC, abstractmethod, abstractproperty

class ContiniousLearningRate(extension.Extension, ABC):
	trigger = 1, 'epoch'

	def _get_optimizer(self, trainer):
		return self._optimizer or trainer.updater.get_optimizer('main')

	def initialize(self, trainer):
		self.set_lr(trainer, self._lr)

	def set_lr(self, trainer, value):
		optimizer = self._get_optimizer(trainer)
		setattr(optimizer, self._attr, max(value, self._target))

	def __init__(self, attr, lr, target, epochs, offset, optimizer=None):
		super(ContiniousLearningRate, self).__init__()
		self._optimizer = optimizer
		self._attr = attr
		self._lr = lr
		self._target = target
		self._epochs = epochs
		self._offset = offset

	@abstractproperty
	def factor(self):
		raise NotImplementedError

	@abstractmethod
	def new_lr(self, epoch):
		raise NotImplementedError

	def __call__(self, trainer):
		if trainer.updater.epoch - self._offset < 0: return
		if trainer.updater.epoch - self._offset > self._epochs: return
		self.set_lr(trainer, self.new_lr(trainer.updater.epoch - self._offset))


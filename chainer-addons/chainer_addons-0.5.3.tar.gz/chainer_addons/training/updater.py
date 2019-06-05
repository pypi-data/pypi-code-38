from chainer.training import StandardUpdater

class MiniBatchUpdater(StandardUpdater):
	"""
		The iterator outputs batches in mini-batch sizes. This updater
		cummulates the gradients of these mini-batches until the
		batch_size is reached. Then a parameter update is performed
	"""
	def __init__(self, batch_size, *args, **kwargs):
		super(MiniBatchUpdater, self).__init__(*args, **kwargs)
		self.batch_size = batch_size
		self.iteration_counter = 0

	def update_core(self):
		optimizer = self._optimizers['main']
		loss_func = self.loss_func or optimizer.target
		it = self._iterators['main']
		batch = it.next()
		data = self.converter(batch, self.device)

		use_cleargrads = getattr(optimizer, '_use_cleargrads', True)
		if use_cleargrads and self.iteration_counter == 0:
			optimizer.target.cleargrads()

		self.iteration_counter += it.batch_size
		loss = loss_func(*data)
		loss.backward()

		if self.iteration_counter >= self.batch_size:
			self.iteration_counter = 0
			optimizer.update()

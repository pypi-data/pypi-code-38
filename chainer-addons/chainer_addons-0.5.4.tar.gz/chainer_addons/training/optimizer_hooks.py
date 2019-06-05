from chainer.optimizer_hooks import WeightDecay

class SelectiveWeightDecay(WeightDecay):

	def __init__(self, rate, selection=None):
		self.rate = rate
		self.selection = selection or (lambda _: True)

	def __call__(self, rule, param):
		if not self.selection(param): return
		return super(SelectiveWeightDecay, self).__call__(rule, param)



import chainer
from chainer.functions.connection import linear

from chainer import links as L

def copy_weighted(p1, p2, tau):
	p1.copydata(p1 * (1-tau) + p2 * tau)

class ObservableLinear(L.Linear):

	def __init__(self, *args, **kw):
		super(ObservableLinear, self).__init__(*args,  **kw)
		self.func = linear.LinearFunction()

	def __call__(self, x):
		self.func = linear.LinearFunction()
		if self.W.data is None:
			self._initialize_params(x.size // x.shape[0])
		if self.b is None:
			return self.func(x, self.W)
		else:
			return self.func(x, self.W, self.b)

	def copyparams_weighted(self, other, tau):
		copy_weighted(self.W, other.W, tau)
		if self.b is not None:
			copy_weighted(self.b, other.b, tau)

	@property
	def inputs(self):
		return self.func.inputs


class ObservableLinearBN(chainer.Chain):

	def __init__(self, in_size, out_size=None, *args, **kw):
		super(ObservableLinearBN, self).__init__()
		kw["nobias"] = True
		with self.init_scope():
			self.fc = ObservableLinear(in_size, out_size, *args,  **kw)
			self.bn = L.BatchNormalization(out_size or in_size)

	def __call__(self, x):
		return self.bn(self.fc(x))

	def copyparams_weighted(self, other, tau):
		self.fc.copyparams_weighted(other.fc, tau)
		copy_weighted(self.bn.beta, other.bn.beta, 1)
		copy_weighted(self.bn.gamma, other.bn.gamma, 1)

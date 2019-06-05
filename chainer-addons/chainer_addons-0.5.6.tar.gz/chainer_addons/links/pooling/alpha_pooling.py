import chainer.functions as F

from chainer import variable
from chainer.initializers import Constant
from chainer_addons.functions import alpha_prod

from .compact_bilinear import CompactBilinearPooling

class AlphaPooling(CompactBilinearPooling):
	"""
		AlphaPooling implementation based on CompactBilinearPooling and
		Simon et al. (https://arxiv.org/abs/1705.00487)
	"""
	def __init__(self, init_alpha=1.0, eps=1e-5, use_built_ins=False, *args, **kwargs):
		super(AlphaPooling, self).__init__(*args, **kwargs)

		with self.init_scope():
			self.alpha = variable.Parameter(
				initializer=Constant(init_alpha), shape=(1,), name="alpha")
			self.add_persistent("eps", eps)

		self.use_built_ins = use_built_ins

	def __call__(self, x):

		if self.use_built_ins:
			sgn_x = F.sign(x)
			abs_x = F.absolute(x) + self.eps
			big_a = F.broadcast_to(self.alpha - 1, x.shape)
			x_hat = sgn_x * (abs_x ** big_a)
		else:
			x_hat = alpha_prod(x, self.alpha, eps=self.eps)

		res = super(AlphaPooling, self).__call__(x_hat, x)
		return res


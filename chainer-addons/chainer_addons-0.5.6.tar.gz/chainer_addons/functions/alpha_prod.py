from chainer.function import Function
from chainer import cuda

import numpy as np

class AlphaProd(Function):
	"""
		Implementation as it is in the Paper:
			with an epsilon for numerical stability
	"""
	def __init__(self, eps):
		super(AlphaProd, self).__init__()
		self.eps = eps

	def forward(self, inputs):
		xp = cuda.get_array_module(*inputs)
		x, alpha = inputs

		abs_x = xp.abs(x) + self.eps
		return xp.sign(x) * xp.power(abs_x, alpha - 1),

	def backward_cpu(self, inputs, gys):
		xp = cuda.get_array_module(*inputs)
		x, alpha = inputs
		gy = gys[0]

		abs_x = xp.abs(x) + self.eps
		sgn_x = xp.sign(x)

		gx = xp.power(abs_x, alpha - 2) * xp.power(sgn_x, 2) * (alpha - 1)
		ga = xp.power(abs_x, alpha - 1) * sgn_x * xp.log(abs_x)

		gx = gx*gy
		ga = (ga*gy).sum().reshape(1)

		return gx, ga

	def backward_gpu(self, inputs, gys):
		x, alpha = inputs
		xp = cuda.cupy

		gx = xp.zeros_like(gys[0])
		ga = xp.zeros_like(gys[0])

		cuda.elementwise(
			in_params="B mask, T abs_x, T sgn_x, T alpha, T gy",
			out_params="T gx, T ga",
			operation="""
				gx = mask ? 0 : gy * pow(abs_x, alpha - 2) * (alpha - 1) ;
				ga = mask ? 0 : gy * pow(abs_x, alpha - 1) * sgn_x * log(abs_x) ;
			""",
			name="alpha_prod_bwd")(
				x==0, xp.abs(x) + self.eps, xp.sign(x), alpha, gys[0],
				gx, ga)

		return gx, ga.sum().reshape(1)


class AlphaProd2(Function):
	"""
		Implementation with the assumption that all inputs are positive

		as the consequence following holds:
		- x == abs(x)
		- sign(x) == sign(x)**2
		- the gradient for all x == 0 is 0 as well
		- sign(x) * <anything> == <anything> for all x != 0

		hence we only compute gradient for x != 0
	"""
	def forward(self, inputs):
		xp = cuda.get_array_module(*inputs)
		x, alpha = inputs
		return xp.power(x, alpha - 1),

	def backward_cpu(self, inputs, gys):
		x, alpha = inputs
		gy = gys[0]

		mask = x != 0
		gx = np.zeros_like(gy)
		ga = np.zeros_like(gy)

		if mask.any():
			gx[mask] = np.power(x[mask], alpha - 2) * (alpha - 1)
			ga[mask] = np.power(x[mask], alpha - 1) * np.log(x[mask])

		gx = gx*gy
		ga = (ga*gy).sum().reshape(1)
		return gx, ga

	def backward_gpu(self, inputs, gys):
		x, alpha = inputs

		gx = cuda.cupy.zeros_like(gys[0])
		ga = cuda.cupy.zeros_like(gys[0])

		cuda.elementwise(
			in_params="B mask, T x, T alpha, T gy",
			out_params="T gx, T ga",
			operation="""
				gx = mask ? 0 : gy * pow(x, alpha - 2) * (alpha - 1) ;
				ga = mask ? 0 : gy * pow(x, alpha - 1) * log(x) ;
			""",
			name="alpha_prod2_bwd")(
				x==0, x, alpha, gys[0],
				gx, ga)

		return gx, ga.sum().reshape(1)


def alpha_prod(x, alpha, eps=1e-5):
	# return AlphaProd(eps)(x, alpha)
	return AlphaProd2()(x, alpha)

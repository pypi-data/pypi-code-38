from chainer.function import Function
from chainer import cuda
import numpy as np

class SignedSquareRoot(Function):

	def forward(self, inputs):
		xp = cuda.get_array_module(*inputs)
		x, = inputs
		return xp.sign(x) * xp.sqrt(xp.abs(x)),

	def backward_cpu(self, inputs, gys):
		x, gy = inputs[0], gys[0]#.copy()
		gx = np.zeros_like(gy)

		mask = x!=0
		gx[mask] = gy[mask] / (2 * np.sqrt(np.abs(x[mask])))
		return gx,

	def backward_gpu(self, inputs, gys):

		x = inputs[0]
		gx = cuda.elementwise(
			in_params="B mask, T x, T gy",
			out_params="T gx",
			operation="""
				gx = mask ? 0 : gy / (2 * sqrt(abs(x)));
			""",
			name="signed_square_root_bwd")(x==0, x, gys[0])

		return gx,


def signed_square_root(x):
	return SignedSquareRoot()(x)

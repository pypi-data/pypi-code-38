import chainer
from chainer import link
from chainer import variable
from chainer import functions as F

from chainer_addons.functions import signed_square_root

import numpy as np


class CompactBilinearPooling(link.Link):
	"""
		Compact Bilinear Pooling based on
		https://github.com/ronghanghu/tensorflow_compact_bilinear_pooling
		and https://arxiv.org/abs/1511.06062
	"""
	def __init__(self, input_dim, output_dim, sum_pool=True, normalize=False, seed=2564643, **kw):
		super(CompactBilinearPooling, self).__init__()

		self.input_dim = input_dim
		self.output_dim = output_dim

		rnd = np.random.RandomState(seed)

		h1 = rnd.randint(output_dim, size=input_dim).astype(np.int32)
		s1 = rnd.choice([-1, 1], size=input_dim).astype(np.int32)

		h2 = rnd.randint(output_dim, size=input_dim).astype(np.int32)
		s2 = rnd.choice([-1, 1], size=input_dim).astype(np.int32)

		m1 = self._sketch_matrix(h1, s1)
		m2 = self._sketch_matrix(h2, s2)

		self.add_persistent("sketch_matrix1", m1)
		self.add_persistent("sketch_matrix2", m2)

		self.add_persistent("sum_pool", sum_pool)
		self.add_persistent("normalize", normalize)

	def __call__(self, x1, x2=None):
		if x2 is None:
			x2 = x1

		sketch1 = self._sketch(self.sketch_matrix1, x1)
		sketch2 = self._sketch(self.sketch_matrix2, x2)

		fft_s1, fft_s2 = self._fft(sketch1), self._fft(sketch2)

		res = self._ifft(self._mul_imag(fft_s1, fft_s2))

		if self.sum_pool:
			res = F.mean(res, axis=(1,2))

		if self.normalize:
			res = signed_square_root(res)
			# res = F.sign(res) * F.sqrt(F.absolute(res))
			res = F.normalize(res)

		return res

	def _fft(self, var):
		imag = self.xp.zeros_like(var.data)
		return F.fft((var, imag))

	def _ifft(self, var):
		real, imag = F.ifft(var)
		return real

	def _mul_imag(self, xy, uv):
		x, y = xy
		u, v = uv
		real = x*u - y*v
		imag = x*v + y*u
		return real, imag

	def _sketch_matrix(self, h, s):
		shape = (self.input_dim, self.output_dim)
		res = self.xp.zeros(shape, dtype=np.float32)
		ys = self.xp.arange(self.input_dim)
		res[ys, h] = s
		return res

	def _sketch(self, mat, x):
		x = F.transpose(x, axes=(0,2,3,1))
		x_flat = F.reshape(x, (-1, x.shape[-1]))
		res = F.tensordot(x_flat, mat, axes=1)
		res_shape = x.shape[:-1] + (-1,)
		return F.reshape(res, res_shape)






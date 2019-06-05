#### Tensorflow implementation based on
#### https://github.com/ronghanghu/tensorflow_compact_bilinear_pooling

import numpy as np

from scipy import sparse as np_sparse
from cupy  import sparse as cupy_sparse

def timing(func):
	import time
	def inner(*args, **kwargs):
		t = time.time()
		res = func(*args, **kwargs)
		t = time.time() - t
		print("Timing for {}: {:.5f}".format(func.__name__, t))
		return res
	return inner

# @timing
def bilinear_pooling_ref(x1, x2, xp, sum_pool=True):
	assert x1.shape[:-1] == x2.shape[:-1], \
		"Shape must be equal ({0.shape:} != {1.shape})!".format(x1, x2)
	n, h, w = x1.shape[:-1]
	c1, c2 = x1.shape[-1], x2.shape[-1]

	idxs = xp.unravel_index(xp.arange(n*h*w), (n, h, w))
	output = xp.zeros((n, h, w, c1*c2), dtype=x1.dtype)
	for i in zip(*idxs):
		output[i] = xp.outer(x1[i], x2[i]).ravel()
	if sum_pool:
		return output.sum(axis=(1,2))

	return output

def _csr(s, h, xp=np, *args, **kwargs):
	csr = (np_sparse if xp == np else cupy_sparse).csr_matrix
	indptr = xp.arange(h.shape[0] + 1)
	return csr((s, h, indptr), *args, **kwargs)

def _issparse(x, xp=np):
	module = np_sparse if xp == np else cupy_sparse
	return module.issparse(x)

def _sketch_matrix(h, s, output_dim, sparse=False, xp=np):
	input_dim = h.shape[0]

	shape = (input_dim, output_dim)

	if sparse:
		res = _csr(s, h, xp, shape=shape, dtype=np.float32)
	else:
		res = xp.zeros(shape, dtype=np.float32)
		ys = xp.arange(input_dim)
		res[ys, h] = s

	return res

def _sketch_matmul(mat, x, xp=np):
	# is too slow:
	# return np.einsum("nhwc,co->nhwo", x, mat)
	x_flat = x.reshape(-1, x.shape[-1])
	if _issparse(mat, xp):
		res = x_flat * mat
		# res = (mat.T * x_flat.T).T
	else:
		res = x_flat.dot(mat)

	res = res.reshape(*x.shape[:-1], -1)

	return res


def _fft(x, xp=np):
	# flat_x = x.reshape(-1, output_dim)
	# import pdb; pdb.set_trace()
	return xp.fft.fft(x.to_array() if _issparse(x, xp) else x)

def _ifft(x, xp=np):
	return xp.fft.ifft(x).real

# @timing
def compact_bilinear_pooling_ref(x1, x2, output_dim, xp, sum_pool=True, seed=2564643, sparse=True):
	assert x1.shape[:-1] == x2.shape[:-1], \
		"Shape must be equal ({0.shape:} != {1.shape})!".format(x1, x2)
	n, h, w = x1.shape[:-1]
	c1, c2 = x1.shape[-1], x2.shape[-1]

	rnd = xp.random.RandomState(seed)

	H1 = rnd.randint(output_dim, size=c1).astype(np.int32)
	S1 = rnd.choice([-1, 1], size=c1).astype(np.int32)
	M1 = _sketch_matrix(H1, S1, output_dim, sparse=sparse, xp=xp)

	H2 = rnd.randint(output_dim, size=c2).astype(np.int32)
	S2 = rnd.choice([-1, 1], size=c2).astype(np.int32)
	M2 = _sketch_matrix(H2, S2, output_dim, sparse=sparse, xp=xp)

	sketch1 = _sketch_matmul(M1, x1, xp=xp)
	sketch2 = _sketch_matmul(M2, x2, xp=xp)

	fft_res = _fft(sketch1, xp) * _fft(sketch2, xp)
	res = _ifft(fft_res, xp)#.reshape(n, h, w,-1)

	if sum_pool:
		return res.sum(axis=(1,2))
	return res


###### Chainer implementation

import chainer
import cupy
import chainer.functions as F

from chainer import cuda
from chainer.function import Function
from chainer.utils import type_check


class BilinearPooling(Function):

	def __init__(self):
		super(BilinearPooling, self).__init__()

	def check_type_forward(self, in_types):
		type_check.expect(in_types.size() == 2)

		x1_type, x2_type = in_types

		ndim = type_check.eval(x1_type.ndim)
		if ndim not in [4, 2]:
			raise type_check.InvalidType(
				expect='%s or %s' % (x1_type.ndim == 4, x1_type.ndim == 2),
				actual='%s == %s' % (x1_type.ndim, ndim))

		type_check.expect(
			x1_type.dtype == "f",
			x1_type.dtype == x2_type.dtype,

			x1_type.ndim == x2_type.ndim,
			x1_type.shape == x2_type.shape,
		)

	# @timing
	def forward(self, inputs):
		self.retain_inputs([0,1])
		x1, x2 = inputs

		xp = cuda.get_array_module(*inputs)

		n, h, w = x1.shape[:-1]
		c1, c2 = x1.shape[-1], x2.shape[-1]

		# same as
		# xp.einsum("nhwi,nhwj->nhwij", x1, x2).reshape(n, h, w, c1*c2)
		# but is more memory efficient
		idxs = xp.unravel_index(xp.arange(n*h*w), (n, h, w))
		output = xp.zeros((n, h, w, c1*c2), dtype=x1.dtype)
		for i in zip(*idxs):
			# same as
			# x1[i].reshape(-1, 1).dot(x2[i].reshape(1, -1))
			output[i] = xp.outer(x1[i], x2[i]).ravel()

		return output,


	def backward(self, inputs, gys):
		x1, x2 = inputs
		gy = gys[0]

		xp = cuda.get_array_module(*inputs)

		n, h, w = x1.shape[:-1]
		c1, c2 = x1.shape[-1], x2.shape[-1]

		idxs = xp.unravel_index(xp.arange(n*h*w), (n, h, w))
		gx1, gx2 = [xp.zeros((n, h, w, c), dtype=x1.dtype) for c in [c1, c2]]
		gy = gy.reshape(n,h,w,c1,c2)
		for i in zip(*idxs):
			gx1[i] = x2[i].dot(gy[i].T)
			gx2[i] = x1[i].dot(gy[i])

		return gx1, gx2

def bilinear_pooling(x1, x2, sum_pool=True):
	res = BilinearPooling()(x1, x2)

	if sum_pool:
		res = F.sum(res, axis=(1,2))

	return res

def compact_bilinear_pooling(x1, x2, output_dim, xp, sum_pool=True, seed=2564643, sparse=True):
	n, h, w = x1.shape[:-1]
	c1, c2 = x1.shape[-1], x2.shape[-1]

	rnd = xp.random.RandomState(seed)

	H1 = rnd.randint(output_dim, size=c1).astype(np.int32)
	S1 = rnd.choice([-1, 1], size=c1).astype(np.int32)

	H2 = rnd.randint(output_dim, size=c2).astype(np.int32)
	S2 = rnd.choice([-1, 1], size=c2).astype(np.int32)

	def sketch_matrix(h, s, output_dim):
		input_dim = h.shape[0]
		shape = (input_dim, output_dim)

		res = xp.zeros(shape, dtype=np.float32)
		ys = xp.arange(input_dim)
		res[ys, h] = s

		return chainer.as_variable(res)

	def sketch_matmul(mat, var):
		var_flat = F.reshape(var, (-1, var.shape[-1]))
		res = F.tensordot(var_flat, mat, axes=1)

		return F.reshape(res, var.shape[:-1] +(-1,))

	def fft(var):
		imag = chainer.as_variable(xp.zeros_like(var.data))
		return F.fft((var, imag))

	def ifft(var):
		real, imag = F.ifft(var)
		return real

	def mul_imag(xy, uv):
		x, y = xy
		u, v = uv
		real = x*u - y*v
		imag = x*v + y*u
		return real, imag


	M1 = sketch_matrix(H1, S1, output_dim)

	M2 = sketch_matrix(H2, S2, output_dim)

	sketch1 = sketch_matmul(M1, x1)#, xp=xp)
	sketch2 = sketch_matmul(M2, x2)#, xp=xp)

	fft_s1, fft_s2 = fft(sketch1), fft(sketch2)

	res = ifft(mul_imag(fft_s1, fft_s2))

	if sum_pool:
		res = F.sum(res, axis=(1,2))

	return res


#### Testing Functions


def test_compare_to_ref(x1, x2, y1, y2, xp=np):
	global output_dim
	v1, v2 = map(chainer.Variable, [x1,x2])

	bp_x = bilinear_pooling(v1, v2)
	bp_x_ref = bilinear_pooling_ref(x1, x2, xp)

	assert xp.isclose(bp_x.data, bp_x_ref).all(), "BilinearPooling does not match!"
	print("BilinearPooling matches reference implementation!")

	v1, v2 = map(chainer.Variable, [x1,x2])
	cbp_x = compact_bilinear_pooling(v1, v2, output_dim, xp)
	cbp_x_ref = compact_bilinear_pooling_ref(x1, x2, output_dim, xp, sparse=False)

	assert xp.isclose(cbp_x.data, cbp_x_ref, atol=1e-3).all(), "CompactBilinearPooling does not match!"
	print("CompactBilinearPooling matches reference implementation!")


def test_cbp_ref(x1, x2, y1, y2, xp=np):
	global output_dim

	cbp_x = compact_bilinear_pooling_ref(x1, x2, output_dim, xp)
	cbp_y = compact_bilinear_pooling_ref(y1, y2, output_dim, xp)

	bp_x = bilinear_pooling_ref(x1, x2, xp)
	bp_y = bilinear_pooling_ref(y1, y2, xp)

	cbp_kernel = xp.sum(cbp_x * cbp_y, axis=1)
	bp_kernel = xp.sum(bp_x * bp_y, axis=1)

	ratio = cbp_kernel / bp_kernel
	print("ratio between Compact Bilinear Pooling (CBP) and Bilinear Pooling (BP):")
	print(ratio)
	assert xp.all(xp.abs(ratio - 1) < 2e-2), "Test Failed!"
	print("Passed.")


def test_cbp(x1, x2, y1, y2, xp=np):
	global output_dim

	v1, v2 = map(chainer.Variable, [x1,x2])
	u1, u2 = map(chainer.Variable, [x1,x2])
	bp_x = bilinear_pooling(v1, v2)
	bp_y = bilinear_pooling(u1, u2)
	# bp_x_ref = bilinear_pooling_ref(cuda.to_cpu(x1), cuda.to_cpu(x2), xp)
	# bp_x.to_cpu()

	# assert np.isclose(bp_x.data, bp_x_ref).all()


	cbp_x = compact_bilinear_pooling(v1, v2, output_dim, xp=xp)
	cbp_y = compact_bilinear_pooling(u1, u2, output_dim, xp=xp)

	cbp_kernel = xp.sum(cbp_x.array * cbp_y.array, axis=1)
	bp_kernel = xp.sum(bp_x.array * bp_y.array, axis=1)

	ratio = cbp_kernel / bp_kernel
	print("ratio between Compact Bilinear Pooling (CBP) and Bilinear Pooling (BP):")
	print(ratio)
	assert xp.all(xp.abs(ratio - 1) < 2e-2), "Test Failed!"
	print("Passed.")

if __name__ == '__main__':
	input_dim = 2048//4
	output_dim = 16000
	c, h, w = 16, 14, 14

	xp = np
	xp = cupy

	# features MUST be positive!
	x1, x2 = [xp.abs(xp.random.rand(c, h, w, input_dim)).astype(xp.float32) for _ in range(2)]
	y1, y2 = [xp.abs(xp.random.rand(c, h, w, input_dim)).astype(xp.float32) for _ in range(2)]

	# test_cbp_ref(x1, x2, y1, y2, xp=xp)
	# test_cbp(x1, x2, y1, y2, xp=xp)
	test_compare_to_ref(x1, x2, y1, y2, xp=xp)







import chainer
from chainer import link
from chainer import function
from chainer import initializers
from chainer import functions as F
from chainer.variable import Parameter

import numpy as np

class FVLayer(link.Link):
	"""Fisher Vector Encoding Layer"""
	def __init__(self,
		in_size, n_components,
		init_sigmas=1,
		eps=1e-6):
		super(FVLayer, self).__init__()

		self.n_components = n_components
		self.in_size = in_size

		# init mu with uniform in a range, e.g. [-1, 1] ?
		mu_init = initializers.Uniform(scale=1, dtype=np.float32)
		w_init = initializers.Constant(1 / n_components, dtype=np.float32)
		sig_init = initializers.Constant(init_sigmas, dtype=np.float32)

		with self.init_scope():
			self.mu = Parameter(mu_init,
				shape=(in_size, n_components),
				name="mu")

			self.sig = Parameter(sig_init,
				shape=(in_size, n_components),
				name="sigma")

			self.w = Parameter(w_init,
				shape=(n_components,),
				name="weights")

			self.add_persistent("eps", eps)

		self.two_sq_pi = np.sqrt(2 * np.pi)

	def _expand_params(self, shape):
		_f = lambda param: \
			F.broadcast_to(
				F.expand_dims(
					F.expand_dims(param, axis=0), axis=0), shape)

		return map(_f, [self.mu, self.sig, F.expand_dims(self.w, axis=0)])

	def __call__(self, x):
		n, t, _in_size = x.shape

		shape = (n, t, self.in_size, self.n_components)
		shape2 = (n, self.in_size, self.n_components)

		_x = F.broadcast_to(F.expand_dims(x, -1), shape)
		_mu, _sig, _w = self._expand_params(shape)
		_w2 = F.broadcast_to(
				F.expand_dims(
					F.expand_dims(self.w, axis=0), axis=0), shape2)

		# for numerical stability
		_sig = F.absolute(_sig) + self.eps
		_w = F.elu(_w) + 2 + self.eps
		_w2 = F.elu(_w2) + 2 + self.eps

		# now let the magic begin!

		_g = (_x - _mu) / _sig
		_u = F.exp(-0.5 * _g**2) / (self.two_sq_pi * _sig)

		_wu =  _u * _w
		_wu_sum = F.broadcast_to(F.sum(_wu, axis=2, keepdims=True), shape)

		_gamma = _wu / (_wu_sum + self.eps)


		G_mu = F.sum(_gamma * _g, axis=1)
		G_mu /= self.n_components * F.sqrt(_w2)

		G_sig = F.sum(_gamma * (_g**2 - 1), axis=1)
		G_sig /= self.n_components * F.sqrt(2 * _w2)

		return F.concat([G_mu.reshape(n, -1), G_sig.reshape(n, -1)])

# class FVFunction(function.Function):
# 	def forward(self, inputs):
# 		import pdb; pdb.set_trace()

#	def backward(self, inputs):
#		import pdb; pdb.set_trace()


if __name__ == '__main__':

	from chainer.computational_graph import build_computational_graph
	class Model(chainer.Chain):
		def __init__(self):
			super(Model, self).__init__()
			with self.init_scope():
				self.link=FVLayer(2048, 5)

		def __call__(self, x):
			return self.link(x)

	model = Model()
	model.cleargrads()

	X = model.xp.ones((12, 3, 2048), dtype=np.float32)
	X = chainer.Variable(X)
	y = model(X)

	import pdb; pdb.set_trace()
	F.sum(y).backward()
	import pdb; pdb.set_trace()

	g = build_computational_graph([y])

	with open("graph.dot", "w") as out:
		out.write(g.dump())

	print(y)

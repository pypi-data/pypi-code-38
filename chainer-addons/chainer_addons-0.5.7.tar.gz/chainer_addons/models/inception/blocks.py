import chainer
import chainer.functions as F
import chainer.links as L

from chainer_addons.links.pooling import PoolingType

class Conv2D_BN(chainer.Chain):
	def __init__(self, insize, outsize, ksize, stride=1, pad=0, activation=F.relu):
		super(Conv2D_BN, self).__init__()
		assert callable(activation)

		with self.init_scope():
			self.conv = L.Convolution2D(insize, outsize,
				ksize=ksize, stride=stride, pad=pad, nobias=True)
			self.bn = L.BatchNormalization(outsize,
				use_gamma=False, eps=2e-5)

		self.activation = activation

	def __call__(self, x):
		x = self.conv(x)
		x = self.bn(x)
		return self.activation(x)

class InceptionHead(chainer.Chain):
	def __init__(self):
		super(InceptionHead, self).__init__()
		with self.init_scope():
			# input 3 x 299 x 299
			self.conv1 = Conv2D_BN(3,   32, ksize=3, stride=2)
			# input 32 x 149 x 149
			self.conv2 = Conv2D_BN(32,  32, ksize=3)
			# input 32 x 147 x 147
			self.conv3 = Conv2D_BN(32,  64, ksize=3, pad=1)
			# input 64 x 147 x 147
			self.pool4 = PoolingType.new("max", ksize=3, stride=2)

			# input 64 x 73 x 73
			self.conv5 = Conv2D_BN(64,  80, ksize=1)
			# input 80 x 73 x 73
			self.conv6 = Conv2D_BN(80, 192, ksize=3)
			# input 192 x 71 x 71
			self.pool7 = PoolingType.new("max", ksize=3, stride=2)
			# output 192 x 35 x 35

	def __call__(self, x):
		x = self.conv1(x)
		x = self.conv2(x)
		x = self.conv3(x)
		x = self.pool4(x)
		x = self.conv5(x)
		x = self.conv6(x)
		x = self.pool7(x)
		return x

class Inception1(chainer.Chain):
	def __init__(self, insize, sizes, outputs, **pool_args):
		super(Inception1, self).__init__()

		out1x1, out5x5, out3x3, out_pool = outputs
		s5x5, s3x3_1, s3x3_2 = sizes

		with self.init_scope():
			self.conv1x1   = Conv2D_BN(insize, out1x1, ksize=1)

			self.conv5x5_1 = Conv2D_BN(insize, s5x5,   ksize=1)
			self.conv5x5_2 = Conv2D_BN(s5x5,   out5x5, ksize=5, pad=2)

			self.conv3x3_1 = Conv2D_BN(insize, s3x3_1, ksize=1)
			self.conv3x3_2 = Conv2D_BN(s3x3_1, s3x3_2, ksize=3, pad=1)
			self.conv3x3_3 = Conv2D_BN(s3x3_2, out3x3, ksize=3, pad=1)

			self.pool_conv = Conv2D_BN(insize, out_pool, ksize=1)
		self.pool = PoolingType.new(**pool_args)

	def __call__(self, x):

		y0 = self.conv1x1(x)
		y1 = self.conv5x5_2(self.conv5x5_1(x))
		y2 = self.conv3x3_3(self.conv3x3_2(self.conv3x3_1(x)))
		y3 = self.pool_conv(self.pool(x))
		return F.concat([y0, y1, y2, y3])

class Inception2(chainer.Chain):
	def __init__(self, insize, sizes, outputs, **pool_args):
		super(Inception2, self).__init__()

		out1, out2 = outputs
		size1, size2 = sizes
		with self.init_scope():
			self.conv3x3   = Conv2D_BN(insize, out1 , ksize=3, stride=2)

			self.conv3x3_1 = Conv2D_BN(insize, size1, ksize=1)
			self.conv3x3_2 = Conv2D_BN(size1,  size2, ksize=3, pad=1)
			self.conv3x3_3 = Conv2D_BN(size2,  out2,  ksize=3, stride=2)

		self.pool = PoolingType.new(**pool_args)

	def __call__(self, x):
		y0 = self.conv3x3(x)
		y1 = self.conv3x3_3(self.conv3x3_2(self.conv3x3_1(x)))
		y2 = self.pool(x)
		return F.concat([y0, y1, y2])

class Inception3(chainer.Chain):
	def __init__(self, insize, sizes, outputs, **pool_args):
		super(Inception3, self).__init__()

		out1x1, out7x7, out7x7x2, out_pool = outputs
		s7x7_1, s7x7_2, s7x7x2_1, s7x7x2_2, s7x7x2_3, s7x7x2_4 = sizes

		with self.init_scope():
			self.conv1x1 = Conv2D_BN(insize,       out1x1, ksize=1)

			self.conv7x7_1 = Conv2D_BN(insize,     s7x7_1, ksize=1)
			self.conv7x7_2 = Conv2D_BN(s7x7_1,     s7x7_2, ksize=(1,7), pad=(0,3))
			self.conv7x7_3 = Conv2D_BN(s7x7_2,     out7x7, ksize=(7,1), pad=(3,0))

			self.conv7x7x2_1 = Conv2D_BN(insize,   s7x7x2_1, ksize=1)
			self.conv7x7x2_2 = Conv2D_BN(s7x7x2_1, s7x7x2_2, ksize=(7,1), pad=(3,0))
			self.conv7x7x2_3 = Conv2D_BN(s7x7x2_2, s7x7x2_3, ksize=(1,7), pad=(0,3))
			self.conv7x7x2_4 = Conv2D_BN(s7x7x2_3, s7x7x2_4, ksize=(7,1), pad=(3,0))
			self.conv7x7x2_5 = Conv2D_BN(s7x7x2_4, out7x7x2, ksize=(1,7), pad=(0,3))

			self.pool_conv = Conv2D_BN(insize, out_pool, ksize=1)

		self.pool = PoolingType.new(**pool_args)

	def __call__(self, x):
		y0 = self.conv1x1(x)
		y1 = self.conv7x7_3(self.conv7x7_2(self.conv7x7_1(x)))
		y2 = self.conv7x7x2_5(self.conv7x7x2_4(self.conv7x7x2_3(self.conv7x7x2_2(self.conv7x7x2_1(x)))))
		y3 = self.pool_conv(self.pool(x))

		return F.concat([y0, y1, y2, y3])

class Inception4(chainer.Chain):
	def __init__(self, insize, sizes, outputs, **pool_args):
		super(Inception4, self).__init__()

		out3x3, out7x7 = outputs
		s3x3, s7x7_1, s7x7_2, s7x7_3 = sizes

		with self.init_scope():
			self.conv3x3_1 = Conv2D_BN(insize, s3x3, ksize=1)
			self.conv3x3_2 = Conv2D_BN(s3x3, out3x3, ksize=3, stride=2)

			self.conv7x7_1 = Conv2D_BN(insize, s7x7_1, ksize=1)
			self.conv7x7_2 = Conv2D_BN(s7x7_1, s7x7_2, ksize=(1, 7), pad=(0, 3))
			self.conv7x7_3 = Conv2D_BN(s7x7_2, s7x7_3, ksize=(7, 1), pad=(3, 0))
			self.conv7x7_4 = Conv2D_BN(s7x7_3, out7x7, ksize=3, stride=2)

		self.pool = PoolingType.new(**pool_args)

	def __call__(self, x):

		y0 = self.conv3x3_2(self.conv3x3_1(x))
		y1 = self.conv7x7_4(self.conv7x7_3(self.conv7x7_2(self.conv7x7_1(x))))
		y2 = self.pool(x)

		return F.concat([y0, y1, y2])

class Inception5(chainer.Chain):
	def __init__(self, insize, sizes, outputs, **pool_args):
		super(Inception5, self).__init__()

		out1x1, out3x3, out3x3x2, out_pool = outputs
		s3x3, s3x3x2_1, s3x3x2_2 = sizes

		with self.init_scope():

			self.conv1x1 = Conv2D_BN(insize, out1x1, ksize=1)

			self.conv3x3_1 = Conv2D_BN(insize, s3x3, ksize=1)
			self.conv3x3_2 = Conv2D_BN(s3x3, out3x3, ksize=(1, 3), pad=(0,1))
			self.conv3x3_3 = Conv2D_BN(s3x3, out3x3, ksize=(3, 1), pad=(1,0))

			self.conv3x3x2_1 = Conv2D_BN(insize  , s3x3x2_1, ksize=1)
			self.conv3x3x2_2 = Conv2D_BN(s3x3x2_1, s3x3x2_2, ksize=3, pad=1)
			self.conv3x3x2_3 = Conv2D_BN(s3x3x2_2, out3x3x2, ksize=(1, 3), pad=(0,1))
			self.conv3x3x2_4 = Conv2D_BN(s3x3x2_2, out3x3x2, ksize=(3, 1), pad=(1,0))

			self.pool_conv = Conv2D_BN(insize, out_pool, ksize=1)

		self.pool = PoolingType.new(**pool_args)


	def __call__(self, x):
		y0 = self.conv1x1(x)


		y1 = self.conv3x3_1(x)
		y1 = F.concat([self.conv3x3_2(y1), self.conv3x3_3(y1)])

		y2 = self.conv3x3x2_2(self.conv3x3x2_1(x))
		y2 = F.concat([self.conv3x3x2_3(y2), self.conv3x3x2_4(y2)])

		y3 = self.pool_conv(self.pool(x))

		return F.concat([y0, y1, y2, y3])


class AuxilaryClassifier(chainer.Chain):
	def __init__(self, n_classes):
		super(AuxilaryClassifier, self).__init__()
		with self.init_scope():
			self.conv1 = Conv2D_BN(768, 128, ksize=1, pad=1)
			self.conv2 = Conv2D_BN(128, 768, ksize=7)

			self.fc = L.Linear(n_classes)


	def __call__(self, x):
		x = F.average_pooling_2d(x, ksize=5, stride=3)
		x = self.conv1(x)
		x = self.conv2(x)
		return self.fc(x)


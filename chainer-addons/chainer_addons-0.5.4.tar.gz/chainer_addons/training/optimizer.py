from enum import Enum, EnumMeta
import chainer
from chainer.optimizers import MomentumSGD, Adam, RMSprop
from chainer.training import extensions

from chainer.optimizer_hooks import GradientClipping
from chainer.optimizer_hooks import WeightDecay

from cvargparse.utils.enumerations import BaseChoiceType


class OptimizerType(BaseChoiceType):
	SGD = MomentumSGD
	RMSPROP = RMSprop
	ADAM = Adam
	Default = SGD

def optimizer(opt_type_name, model, lr=1e-2, decay=5e-3, gradient_clipping=True, *args, **kw):
	opt_type = OptimizerType.get(opt_type_name)
	opt_args = dict(alpha=lr) if opt_type == OptimizerType.ADAM else dict(lr=lr)
	kw.update(opt_args)
	opt = opt_type.value(*args, **kw)
	opt.setup(model)
	if decay:
		opt.add_hook(WeightDecay(decay))

	if gradient_clipping:
		opt.add_hook(GradientClipping(10))
	return opt

def lr_shift(opt, init, rate, target):
	attr = "alpha" if isinstance(opt, Adam) else "lr"

	return extensions.ExponentialShift(
		optimizer=opt, attr=attr,
		init=init, rate=rate, target=target)

def no_grad(arr):
	return arr.data if isinstance(arr, chainer.Variable) else arr

if __name__ == '__main__':
	print(optimizer("adam", chainer.Chain()))

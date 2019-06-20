try:
	import chainer
except ImportError:
	has_chainer = False
else:
	has_chainer = True

from abc import ABC

class BaseChainerMixin(ABC):

	def chainer_check(self):
		global has_chainer
		assert has_chainer, "Please install chainer!"

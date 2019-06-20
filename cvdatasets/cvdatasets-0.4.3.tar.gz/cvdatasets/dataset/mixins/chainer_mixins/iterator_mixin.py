import numpy as np
import logging

from .base import BaseChainerMixin
from cvdatasets.utils import new_iterator

class IteratorMixin(BaseChainerMixin):
	def new_iterator(self, **kwargs):
		self.chainer_check()
		return new_iterator(data=self, **kwargs)

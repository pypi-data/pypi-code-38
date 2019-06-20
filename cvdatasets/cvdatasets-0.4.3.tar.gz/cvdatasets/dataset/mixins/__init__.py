from abc import ABC, abstractmethod

import numpy as np
import six

from matplotlib.patches import Rectangle

class BaseMixin(ABC):

	@abstractmethod
	def get_example(self, i):
		s = super(BaseMixin, self)
		if hasattr(s, "get_example"):
			return s.get_example(i)

	def plot_bounding_box(self, i, ax, fill=False, linestyle="--", **kwargs):
		x, y, w, h = self.bounding_box(i)
		ax.add_patch(Rectangle(
			(x,y), w, h,
			fill=False,
			linestyle="-.",
			**kwargs
		))

	def __getitem__(self, index):
		if isinstance(index, slice):
			current, stop, step = index.indices(len(self))
			return [self.get_example(i) for i in
					six.moves.range(current, stop, step)]
		elif isinstance(index, list) or isinstance(index, np.ndarray):
			return [self.get_example(i) for i in index]
		else:
			return self.get_example(index)

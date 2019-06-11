

class IModel(object):

	@property
	def name(self): return self._name
	@name.setter
	def name(self, value): self._name = value

	@property
	def directory(self): return None


	def save(self, data, path): return data
	def load(self, data, path): return data
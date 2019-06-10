from . import axonaIO
import dacq2py
class TetrodeDict(dict):
	def __init__(self, filename_root, *args, **kwargs):
		self.filename_root = filename_root
		self.valid_keys = range(1, 33)
		self.update(*args, **kwargs)
		if 'volts' in kwargs:
			self._volts = kwargs['volts']
		else:
			self._volts = True
		
	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).items():
			self[k] = v
			
	def __getitem__(self, key):
		if isinstance(key, int):
			try:
				val = dict.__getitem__(self, key)
				return val
			except KeyError:
				if key in self.valid_keys:
					try:
						val = dacq2py.axonaIO.Tetrode(self.filename_root, key, self._volts)
						self.__setitem__(key, val)
						return val
					except IOError:
						print("IOError for file {} on tetrode {}".format(self.filename_root, key))
						
	def __setitem__(self, key, val):
		dict.__setitem__(self, key, val)
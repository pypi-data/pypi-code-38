class InvalidLengthException(Exception):
	def __init__(self, message=None):
		if message:
			self.message = message
		else:
			self.message = "Invalid length specified for int (length)"

	def __str__(self):
		return self.message


class InvalidBooleanException(Exception):
	def __init__(self, message=None):
		if message:
			self.message = message
		else:
			self.message = "Invalid value specified for boolean (shuffle)"

	def __str__(self):
		return self.message
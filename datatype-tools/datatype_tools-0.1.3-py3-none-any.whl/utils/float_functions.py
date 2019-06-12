#: Scientific Rounding

def s_round(self, places=2):
	"""
	Correctly round float to n decimal places.
	>>> s_round(4.055, 2)
	4.06
	>>> s_round(4.054, 2)
	4.05
	"""
	return round(self + 10**(-2*6), places)

#::: END PROGRAM :::

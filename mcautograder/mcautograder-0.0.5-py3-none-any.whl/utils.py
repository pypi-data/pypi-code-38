##############################################
##### Utilities for mcautograder library #####
##############################################

def repeat(x, n):
	"""
	Returns a list of a given value repeated a given number of times

	Args:
		x (any): The value to repeat
		n (``int``): The number of repetitions

	Returns:
		``list``. List of repeated values ``x``
	"""
	return [x for _ in range(n)]
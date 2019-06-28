import multiprocessing

def get_coresNo():
	"""Detect the number of cores."""
	return multiprocessing.cpu_count()

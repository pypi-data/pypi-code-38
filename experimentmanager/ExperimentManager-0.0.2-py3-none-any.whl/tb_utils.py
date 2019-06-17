import numpy as np
from tensorflow import HistogramProto, Summary

def log_scalar(tb_writer, tag, value, step):
	"""Log a scalar variable. Credits : Michael Gygli
	Parameter
	----------
	tag : basestring
		Name of the scalar
	value
	step : int
		training iteration
	"""

	summary = Summary(value=[Summary.Value(tag=tag, simple_value=value)])
	tb_writer.add_summary(summary, step)


def log_histogram(tb_writer, tag, values, step, bins=1000):
	"""Logs the histogram of a list/vector of values. Credits : Michael Gygli
	
	This only logs to tensorboard. Hence it will do nothing if tensorboard support is not activated.
	
	"""
	
	# Convert to a numpy array
	values = np.array(values)
	
	# Create histogram using numpy        
	counts, bin_edges = np.histogram(values, bins=bins)

	# Fill fields of histogram proto
	hist = HistogramProto()

	if len(values)==0:
		values = np.array([0])


	hist.min = float(np.min(values))
	hist.max = float(np.max(values))
	hist.num = int(np.prod(values.shape))
	hist.sum = float(np.sum(values))
	hist.sum_squares = float(np.sum(values**2))

	# Requires equal number as bins, where the first goes from -DBL_MAX to bin_edges[1]
	# See https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/framework/summary.proto#L30
	# Thus, we drop the start of the first bin
	bin_edges = bin_edges[1:]

	# Add bin edges and counts
	for edge in bin_edges:
		hist.bucket_limit.append(edge) 
	for c in counts:
		hist.bucket.append(c)

	# Create and write Summary
	summary = Summary(value=[Summary.Value(tag=tag, histo=hist)])
	tb_writer.add_summary(summary, step)
	tb_writer.flush()

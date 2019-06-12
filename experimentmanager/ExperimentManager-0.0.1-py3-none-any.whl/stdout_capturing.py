import logging
import sys

from ExperimentManager.utils import setup_logger

class StreamToLogger(object):
	"""
	Fake file-like stream object that redirects writes to a logger instance.
	"""
	def __init__(self, logger, log_level=logging.INFO, std_orig = None):
		self.logger = logger
		self.log_level = log_level
		self.linebuf = ''
		self.std_orig = std_orig

	def write(self, buf):
		if self.std_orig is not None:
			_ = self.std_orig.write(buf)
		for line in buf.rstrip().splitlines():
			self.logger.log(self.log_level, line.rstrip())

	def flush(self):
		if self.std_orig is not None:
			self.std_orig.flush()
			pass
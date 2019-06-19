import logging
import sys

methods = ["close","flush","fileno","isatty","read","readable","readline","readlines","reconfigure","seek","seekable","tell","truncate","writable","writelines"]

class StreamToLogger(object):
	"""
	Fake file-like stream object that redirects writes to a logger instance.
	"""
	def __init__(self, logger, ref_std, log_level=logging.INFO):
		self.logger = logger
		self.log_level = log_level
		self.ref_std = ref_std

		# Inherinting the ref_stds methods
		for attribute in methods:
			if hasattr(self.ref_std,attribute):
				setattr(self,attribute,getattr(self.ref_std,attribute))

	def write(self, buf):
		self.ref_std.write(buf)
		for line in buf.rstrip().splitlines():
			self.logger.log(self.log_level, line.rstrip())
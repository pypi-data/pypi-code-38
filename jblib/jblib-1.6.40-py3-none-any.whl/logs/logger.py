import logging

class StreamToLogger(object):
	'''
    DESCRIPTION:
        Fake file-like stream object that redirects writes to a logger instance.
        
    CLASS:
        StreamToLogger(object)
    EXAMPLE: 
        if log_enabled: ## If true, all standard output and standard error to the console will be disabled
            # create logger
            logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%Y%m%d %H:%M:%S', filename=log_file)
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)

            logger.propagate = False
            fh = logging.FileHandler(log_file, "a")
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            keep_fds = [fh.stream.fileno()]

            stdout_logger = logging.getLogger('STDOUT')
            sl = StreamToLogger(stdout_logger, logging.INFO)
            sys.stdout = sl

            stderr_logger = logging.getLogger('STDERR')
            sle = StreamToLogger(stderr_logger, logging.ERROR)
            sys.stderr = sle
	'''
	def __init__(self, logger, log_level=logging.INFO):
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.DEBUG)
		self.log_level = log_level
		self.linebuf = ''

	def write(self, buf):
		for line in buf.rstrip().splitlines():
			self.logger.log(self.log_level, line.rstrip())

	def flush(self):
		pass
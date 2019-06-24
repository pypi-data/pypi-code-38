# coding=utf-8
from __future__ import print_function
import logging
import tempfile

name = 'ibm-apidocs-cli'

logging_temp_file = tempfile.NamedTemporaryFile(suffix='{0}.log'.format(name), delete=False)


ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)-15s %(name)-12s %(levelname)s - %(message)s'))
ch.setLevel(logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(logging_temp_file.name)
fh.setFormatter(logging.Formatter('%(asctime)-15s %(name)-12s %(levelname)s - %(message)s'))
fh.setLevel(logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(ch)


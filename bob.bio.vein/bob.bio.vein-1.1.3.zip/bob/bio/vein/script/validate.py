#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


'''Utilities for command-line option validation'''


import os
import glob
import schema
import logging
logger = logging.getLogger(__name__)


def setup_logger(name, level):
  '''Sets up and checks a verbosity level respects min and max boundaries


  Parameters:

    name (str): The name of the logger to setup

    v (int): A value indicating the verbosity that must be set


  Returns:

    logging.Logger: A standard Python logger that can be used to log messages


  Raises:

    schema.SchemaError: If the verbosity level exceeds the maximum allowed of 4

  '''

  import bob.core
  logger = bob.core.log.setup(name)

  if not (0 <= level < 4):
    raise schema.SchemaError("there can be only up to 3 -v's in a command-line")

  # Sets-up logging
  bob.core.log.set_verbosity_level(logger, level)

  return logger


def make_dir(p):
  '''Checks if a path exists, if it doesn't, creates it


  Parameters:

    p (str): The path to check


  Returns

    bool: ``True``, always

  '''

  if not os.path.exists(p):
    logger.info("Creating directory `%s'...", p)
    os.makedirs(p)

  return True


def check_path_does_not_exist(p):
  '''Checks if a path exists, if it does, raises an exception


  Parameters:

    p (str): The path to check


  Returns:

    bool: ``True``, always


  Raises:

    schema.SchemaError: if the path exists

  '''

  if os.path.exists(p):
    raise schema.SchemaError("path to {} exists".format(p))

  return True


def check_path_exists(p):
  '''Checks if a path exists, if it doesn't, raises an exception


  Parameters:

    p (str): The path to check


  Returns:

    bool: ``True``, always


  Raises:

    schema.SchemaError: if the path doesn't exist

  '''

  if not os.path.exists(p):
    raise schema.SchemaError("path to {} does not exist".format(p))

  return True


def check_model_does_not_exist(p):
  '''Checks if the path to any potential model file does not exist


  Parameters:

    p (str): The path to check


  Returns:

    bool: ``True``, always


  Raises:

    schema.SchemaError: if the path exists

  '''

  files = glob.glob(p + '.*')
  if files:
    raise schema.SchemaError("{} already exists".format(files))

  return True


def open_multipage_pdf_file(s):
  '''Returns an opened matplotlib multi-page file


  Parameters:

    p (str): The path to the file to open


  Returns:

    matplotlib.backends.backend_pdf.PdfPages: with the handle to the multipage
    PDF file


  Raises:

    schema.SchemaError: if the path exists

  '''
  import matplotlib.pyplot as mpl
  from matplotlib.backends.backend_pdf import PdfPages
  return PdfPages(s)


class validate_protocol(object):
  '''Validates the protocol for a given database


  Parameters:

    name (str): The name of the database to validate the protocol for


  Raises:

    schema.SchemaError: if the database is not supported

  '''

  def __init__(self, name):

    self.dbname = name

    if name == 'fv3d':
      import bob.db.fv3d
      self.valid_names = bob.db.fv3d.Database().protocol_names()
    elif name == 'verafinger':
      import bob.db.verafinger
      self.valid_names = bob.db.verafinger.Database().protocol_names()
    else:
      raise schema.SchemaError("do not support database {}".format(name))


  def __call__(self, name):

    if name not in self.valid_names:
      msg = "{} is not a valid protocol for database {}"
      raise schema.SchemaError(msg.format(name, self.dbname))

    return True


class validate_group(object):
  '''Validates the group for a given database


  Parameters:

    name (str): The name of the database to validate the group for


  Raises:

    schema.SchemaError: if the database is not supported

  '''

  def __init__(self, name):

    self.dbname = name

    if name == 'fv3d':
      import bob.db.fv3d
      self.valid_names = bob.db.fv3d.Database().groups()
    elif name == 'verafinger':
      import bob.db.verafinger
      self.valid_names = bob.db.verafinger.Database().groups()
    else:
      raise schema.SchemaError("do not support database {}".format(name))


  def __call__(self, name):

    if name not in self.valid_names:
      msg = "{} is not a valid group for database {}"
      raise schema.SchemaError(msg.format(name, self.dbname))

    return True

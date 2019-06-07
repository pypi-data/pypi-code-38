'''
This module contains common exceptions when dealing with Google Cloud services.
'''


class UnknownProtocolVersion(Exception):
  '''
  This exception is used when services interact with message queues and encounter an unsupported protocol version.
  '''

  def __init__(self, message, *errors):
    '''
    Creates a new exception object.

    :param message: the error message
    :param errors:  the inner errors
    '''

    # Call the base class constructor with the parameters it needs
    super().__init__(message, errors)


class ConfigError(Exception):
  '''
  Base error that all configuration related errors inherit from.
  '''

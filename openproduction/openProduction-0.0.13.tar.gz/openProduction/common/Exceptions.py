# define Python user-defined exceptions
class OpenProductionAssertionError(Exception):
   """Base class for other exceptions"""
   def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(OpenProductionAssertionError, self).__init__(message)


class OpenProductionAbortError(Exception):
   """Base class for other exceptions"""
   def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(OpenProductionAbortError, self).__init__(message)

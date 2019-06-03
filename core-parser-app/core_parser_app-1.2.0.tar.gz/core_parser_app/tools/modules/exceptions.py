""" Modules Exceptions
"""


class ModuleError(Exception):
    """
        Exception raised by the module system
    """
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)

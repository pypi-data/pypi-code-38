class Error(Exception):
    """ Error class. """
    def __init__(self, message=''):
        self.__message = message

    @property
    def message(self):
        """ message property """
        return self.__message

class ItemNotFoundException(Exception):
    '''Raised when an item was not found'''
    pass

class InvalidParametersException(Exception):
    '''Raised when parameters where invalid'''
    pass

class DatabaseSaveFailedException(Exception):
    '''Raised when saving to database fails'''
    pass

class RoomHasDataException(Exception):
    '''Raised when a room that should be deleted has data left'''
    pass

class AbstractFunctionCallException(Exception):
    '''Raised when a abstract method is called'''
    pass

class NoSuchTypeException(Exception):
    '''Raised when a devicetype is used that does not exist'''
    pass

class NoPermissionException(Exception):
    '''Raised when a user is not allowed to do the given task'''
    pass

class RoomHasItemsException(Exception):
    '''Raised when the room that should be deleted has items'''
    pass

class AlreadyTrainingException(Exception):
    '''Raised when an AI-agent is already training'''
    pass
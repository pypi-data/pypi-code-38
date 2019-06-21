class BaseError(Exception):
    """Just a bare error"""

class CategoryNotFound(BaseError):
    """Defined Category not found"""
    pass

class NotFound(BaseError):
    """Something that couldn't be found"""
    pass

class NotValid(BaseError):
    """An Object that is not valid"""
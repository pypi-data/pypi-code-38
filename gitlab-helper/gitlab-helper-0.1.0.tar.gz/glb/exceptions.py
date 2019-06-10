class GLBError(Exception):
    """Base class for exceptions in this module."""

    pass


class TokenError(GLBError):
    """Exception raised for errors configuring a token
    """

    pass


class GroupNotFound(GLBError):
    """Exception raised for errors configuring a token
    """

    pass

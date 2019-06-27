class InvalidCredentialsException(Exception):
    """Thrown when authentication fails with the provided username and password"""
    pass


class InvalidServiceException(Exception):
    """Thrown whenever the selected service is not in the service registry (or the service registry is empty)"""
    pass

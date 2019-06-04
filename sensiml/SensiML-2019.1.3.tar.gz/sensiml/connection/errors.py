
class LoginError(Exception):
    pass


class MethodDeprecatedError(LoginError):
    def __init__(self, message='This method is no longer allowed.', *args):
        super(MethodDeprecatedError, self).__init__(message, *args)


class LoginAttemptsExceededError(LoginError):
    def __init__(self,
                 message='Maximum number of login attempts exceeded.',
                 *args):
        super(LoginAttemptsExceededError, self).__init__(message, *args)


class ConnectionAbortedError(LoginError):
    def __init__(self, message='The connection was aborted by the user.', *args):
        super(ConnectionAbortedError, self).__init__(message, *args)

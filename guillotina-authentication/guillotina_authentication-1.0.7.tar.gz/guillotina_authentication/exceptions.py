class AuthenticationException(Exception):
    def __init__(self, provider):
        super().__init__(provider)
        self.provider = provider


class ProviderNotSupportedException(AuthenticationException):
    pass


class ProviderNotConfiguredException(AuthenticationException):
    pass


class ProviderMisConfiguredException(AuthenticationException):
    pass

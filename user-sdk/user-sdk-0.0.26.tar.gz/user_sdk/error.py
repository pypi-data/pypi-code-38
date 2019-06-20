class ClientError(Exception):
    def __init__(self, error=None):
        self.error = error


class NoSuchUser(ClientError):
    pass


class NoSuchProfile(ClientError):
    pass


class NoRoleFound(ClientError):
    pass


class ProfileCreationError(ClientError):
    pass


class ProfileUpdateError(ClientError):
    pass


class UserAlreadyExists(ClientError):
    pass


class InvalidOTPError(ClientError):
    pass


class InvalidRoleRequest(ClientError):
    pass


class ProfileAlreadyExists(ClientError):
    pass


class ServerError(Exception):
    def __init__(self, error=None):
        self.error = error


class OTPSendFailure(ServerError):
    pass


class UserCreationFailed(ServerError):
    pass


class UserAuthenticationError(ServerError):
    pass

from cdiserrors import AuthNError as CDISAuthNError


class AuthError(CDISAuthNError):

    pass


class JWTError(AuthError):

    pass


class JWTExpiredError(AuthError):

    pass


class JWTPurposeError(JWTError):

    pass


class JWTAudienceError(JWTError):

    pass

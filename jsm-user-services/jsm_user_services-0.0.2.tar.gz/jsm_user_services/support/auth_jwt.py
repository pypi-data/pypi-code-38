import jwt


def get_decoded_jwt_token(jwt_token: str) -> dict:
    """
    Gets a decoded JWT token.
    """

    return jwt.decode(jwt_token, verify=False)

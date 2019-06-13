from alfa_sdk.common.session import Session
from alfa_sdk.common.stores import AuthStore


def create_session(*, cache_token=True):
    session = Session()
    token, token_type = session.auth.get_token()

    if cache_token:
        AuthStore.set_value(token_type, token, group="cache")

    return session


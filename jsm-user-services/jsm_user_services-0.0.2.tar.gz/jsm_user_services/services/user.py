from typing import List
from typing import Optional

from django.conf import settings
from jsm_user_services import local_threading
from jsm_user_services.support.auth_jwt import get_decoded_jwt_token
from jsm_user_services.support.http_utils import get_response_body
from jsm_user_services.support.http_utils import request


def jwt_has_required_roles(jwt_required_roles: List[str], assert_all=True) -> bool:
    """
    Asserts that the jwt token has all the required roles.
    """
    jsm_token_data = get_jsm_user_data_from_jwt()

    if not jsm_token_data:
        return False

    try:
        jwt_token_roles = jsm_token_data["roles"]
    except KeyError:
        return False

    if not jwt_token_roles:
        return False

    if assert_all:
        return all([(jwt_token_role in jwt_required_roles) for jwt_token_role in jwt_token_roles])

    return any([(jwt_token_role in jwt_required_roles) for jwt_token_role in jwt_token_roles])


def current_jwt_token() -> Optional[str]:
    return getattr(local_threading, "authorization_token", None)


def get_jsm_token() -> Optional[str]:
    token = current_jwt_token()
    if token:
        return get_decoded_jwt_token(token)["jsm_identity"]

    return None


def get_ltm_token() -> Optional[str]:
    token = current_jwt_token()
    if token:
        return get_decoded_jwt_token(token)["yuntiandu"]

    return None


def get_jsm_user_data_from_jwt() -> Optional[dict]:
    token = get_jsm_token()

    if token:
        return get_decoded_jwt_token(token)

    return None


def get_ltm_user_data_from_jwt() -> Optional[dict]:
    token = get_ltm_token()

    if token:
        return get_decoded_jwt_token(token)

    return None


def get_user_email_from_jwt() -> Optional[str]:
    user_data = get_jsm_user_data_from_jwt()
    if user_data:
        return user_data.get("email")

    return None


def get_user_data_from_server(cpf: str) -> dict:

    user_url = settings.USER_API_HOST

    with request() as r:
        response = r.get(f"{user_url}/users/?email={cpf}@loyaltyJSM.com")
        return get_response_body(response)

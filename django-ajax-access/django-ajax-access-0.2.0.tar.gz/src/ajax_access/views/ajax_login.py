from django.contrib.auth import get_user_model, authenticate, login
from ratelimit.decorators import ratelimit

from ..utils import response
from ..settings import (
    LOGIN_RATELIMIT_KEY,
    LOGIN_RATELIMIT_RATE,
    LOGIN_RATELIMIT_BLOCK,
)

USER_MODEL = get_user_model()
USERNAME_FIELD = USER_MODEL.USERNAME_FIELD


@ratelimit(
    key=LOGIN_RATELIMIT_KEY,
    rate=LOGIN_RATELIMIT_RATE,
    block=LOGIN_RATELIMIT_BLOCK
)
def ajax_login(request):
    if request.is_ajax():
        if request.method == "POST":
            if request.user.is_anonymous:
                username = request.POST.get(USERNAME_FIELD, None)
                password = request.POST.get("password", None)
                if username is None or password is None:
                    if username is None and password is None:
                        return response(400, [
                            "No {} provided.".format(USERNAME_FIELD),
                            "No password provided.",
                        ])
                    if username is None:
                        return response(400, "No {} provided.".format(USERNAME_FIELD))
                    if password is None:
                        return response(400, "No password provided.")
                else:
                    authenticated_user = authenticate(request, **{
                        USERNAME_FIELD: username,
                        "password": password,
                    })
                    if authenticated_user is not None:
                        if authenticated_user.is_active:
                            login(request, authenticated_user)
                            return response()
                        else:
                            return response(409, "User is not active.")
                    else:
                        found_user = USER_MODEL.objects.get(**{
                            USERNAME_FIELD: username
                        })
                        if not found_user.check_password(password):
                            return response(409, "Password is incorrect.")
                        else:
                            return response(404, "User does not exist.")
            else:
                return response(403, "User is already authenticated.")
        else:
            return response(405, "Not a POST request.")
    else:
        return response(412, "Not an AJAX request.")

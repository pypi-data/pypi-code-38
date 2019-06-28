from django.contrib.auth import logout
from ratelimit.decorators import ratelimit

from ..utils import response
from ..settings import (
    LOGOUT_RATELIMIT_KEY,
    LOGOUT_RATELIMIT_RATE,
    LOGOUT_RATELIMIT_BLOCK,
)


@ratelimit(
    key=LOGOUT_RATELIMIT_KEY,
    rate=LOGOUT_RATELIMIT_RATE,
    block=LOGOUT_RATELIMIT_BLOCK
)
def ajax_logout(request):
    if request.is_ajax():
        if request.method == "POST":
            if request.user.is_authenticated:
                logout(request)
                return response()
            else:
                return response(403, "User is not authenticated.")
        else:
            return response(405, "Not a POST request.")
    else:
        return response(412, "Not an AJAX request.")

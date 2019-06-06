import base64

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from shipmnts_utils.misc.utils import standardize_response


def basicauth(view):
    def wrap(request, *args, **kwargs):
        if "HTTP_AUTHORIZATION" in request.META:
            auth = request.META["HTTP_AUTHORIZATION"].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1]).decode("utf-8").split(":")
                    user = User.objects.filter(
                        Q(username=uname) & Q(password=passwd) & Q(is_active=True)
                    )
                    if user.exists():
                        request.user = user.get()
                        return view(request, *args, **kwargs)

        return standardize_response(Response(status=status.HTTP_401_UNAUTHORIZED))

    return wrap

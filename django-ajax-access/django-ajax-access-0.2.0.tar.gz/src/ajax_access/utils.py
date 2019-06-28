from json import dumps
from django.http import HttpResponse


def response(status=204, details=None):
    content = None
    if details is not None:
        content = dumps({"details": details})
    return HttpResponse(
        content,
        content_type="application/json",
        status=status
    )

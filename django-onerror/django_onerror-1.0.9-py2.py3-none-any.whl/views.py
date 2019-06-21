# -*- coding: utf-8 -*-

import json

from django.conf import settings
from django_onerror.models import OnerrorReportInfo
from django_response import response


def err_report(request):
    if not (not hasattr(settings, 'DJANGO_ONERROR_ACCEPT_REPORT') or settings.DJANGO_ONERROR_ACCEPT_REPORT):
        return response()

    errmsg = request.body

    if not errmsg:
        return response()

    try:
        payload = json.loads(errmsg)
    except ValueError:
        return response()

    errormessage = payload.get('errorMessage', '')

    if hasattr(settings, 'DJANGO_ONERROR_IGNORE_ERROR_MESSAGES') and errormessage in settings.DJANGO_ONERROR_IGNORE_ERROR_MESSAGES:
        return response()

    OnerrorReportInfo.objects.create(
        href=payload.get('href', ''),
        ua=payload.get('ua', ''),
        lineNo=payload.get('lineNo', -1) or 0,
        columnNo=payload.get('columnNo', -1) or 0,
        scriptURI=payload.get('scriptURI', ''),
        errorMessage=errormessage,
        stack=payload.get('stack', ''),
        extra=payload.get('extra', ''),
    )

    return response()

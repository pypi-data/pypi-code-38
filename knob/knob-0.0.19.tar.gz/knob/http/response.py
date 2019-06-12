# -*- coding:utf-8 -*-

# responses.py
import os, sys
import re
import mimetypes
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, \
                        HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, \
                        HttpResponseServerError, Http404, \
                        StreamingHttpResponse, JsonResponse

from krust.file_utils import *
from krux.random import random_str


def file_response(fname, save_name=None, content_type=None, remove_on_finish=False):
    del_tmp = False
    if re.match(r'^s3[c]?://.*', fname):
        try:
            tmpfile = '/tmp/tmp.%s%s' % (random_str(8), get_ext(fname))
            CP(fname, tmpfile)
            fname = tmpfile
            del_tmp = True
        except Exception as e:
           return HttpResponseNotFound()
    elif not os.path.exists(fname):
        return HttpResponseNotFound()

    if content_type is None:
        content_type, encoding = mimetypes.guess_type(fname)
    response = HttpResponse(open(fname, 'rb').read(), content_type)
    if save_name is None:
        response['Content-Disposition'] = 'attachment;'
    else:
        response['Content-Disposition'] = 'attachment; filename="%s"' % save_name
    if del_tmp and fname.startswith('/tmp/tmp.'):
        RM(fname)
    if remove_on_finish and os.path.isfile(fname):
        RM(fname)
    return response


def string_response(s, save_name=None, content_type=None):
    if save_name is None:
        save_name = 'tmpstr'

    if not content_type :
        if save_name:
            content_type, encoding = mimetypes.guess_type(save_name)
        else:
            content_type = 'application/octet-stream'
    else:
        if len(content_type) < 6:
            if not content_type.startswith('.'):
                content_type = '.' + content_type
            content_type, encoding = mimetypes.guess_type(content_type)

    response = HttpResponse(s, content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % save_name

    return response


class ExceptionJsonResponse(JsonResponse):
    status_code = 400


class ErrorJsonResponse(JsonResponse):
    status_code = 500



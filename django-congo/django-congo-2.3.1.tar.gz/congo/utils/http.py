# -*- coding: utf-8 -*-
from django.http.response import HttpResponse

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseServiceUnavailable(HttpResponse):
    status_code = 503

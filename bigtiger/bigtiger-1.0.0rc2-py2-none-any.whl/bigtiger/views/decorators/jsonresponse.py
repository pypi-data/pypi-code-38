# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals, print_function

import functools

from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder


def jsonresponse(encoder=DjangoJSONEncoder, safe=True, **kwargs):
    """
    return result jsonResponse.
    """

    def _jsonresponse(fn):
        @functools.wraps(fn)
        def __jsonresponse(*args, **kwargs):
            result = fn(*args, **kwargs)
            return JsonResponse(result, encoder, safe, **kwargs)
        return __jsonresponse
    return _jsonresponse

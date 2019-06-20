# -*- coding: utf-8 -*-
from congo.utils.decorators import secure_allowed
from importlib import import_module
from django.http.response import Http404, JsonResponse
from congo.utils.classes import UserDevice

@secure_allowed
def ajax(request, action):
    module = import_module(__name__)
    view_name = "__%s" % action.replace('-', '_')

    if hasattr(module, view_name):
        return getattr(module, view_name)(request, action)
    else:
        raise Http404()

def __set_device_screen(request, action):
    # @og do kasacji

    result = {'reload' : False}

    screen_size = request.GET.get('screen_size', None)
    if screen_size:
        change = UserDevice.set_device_screen(request, screen_size)
        if change:
            result['reload'] = True

    return JsonResponse(result)

""" ajax file
"""
import json

from django.http.response import HttpResponse, HttpResponseBadRequest

import core_main_app.components.data.api as data_api
import core_main_registry_app.components.data.api as data_registry_api
from core_main_app.commons import exceptions
from core_main_app.utils.access_control.exceptions import AccessControlError


def switch_data_status(request):
    """ switch the data status

    Returns:

    """
    try:
        data_id = request.POST.get('data_id', None)
        new_status = request.POST.get('new_status', None)
        if data_id is not None and new_status is not None:
            data = data_api.get_by_id(data_id, request.user)
            data_registry_api.set_status(data, new_status, request.user)
        else:
            return HttpResponseBadRequest(json.dumps({'message': 'The data id and the new status are required'}),
                                          content_type='application/javascript')
    except exceptions.DoesNotExist, dne:
        return HttpResponseBadRequest(json.dumps({'message': dne.message}),
                                      content_type='application/json')
    except Exception, e:
        return HttpResponseBadRequest(json.dumps({'message': e.message}),
                                      content_type='application/javascript')
    return HttpResponse(json.dumps({}), content_type='application/javascript')


def publish(request):
    """ Publish a resource.

    Returns:

    """
    try:
        data_id = request.POST.get('data_id', None)
        if data_id is not None:
            data = data_api.get_by_id(data_id, request.user)
            data_registry_api.publish(data, request.user)
        else:
            return HttpResponseBadRequest(json.dumps({'message': 'The data id is required'}),
                                          content_type='application/javascript')
    except exceptions.DoesNotExist, dne:
        return HttpResponseBadRequest(json.dumps({'message': dne.message}),
                                      content_type='application/json')
    except AccessControlError, ace:
        return HttpResponseBadRequest(json.dumps({'message': 'You don\'t have enough right to perform this action.'}),
                                      content_type='application/json')
    except Exception, e:
        return HttpResponseBadRequest(json.dumps({'message': e.message}),
                                      content_type='application/javascript')
    return HttpResponse(json.dumps({}), content_type='application/javascript')

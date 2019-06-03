"""AJAX views
"""
import json
from django.http.response import HttpResponseBadRequest, HttpResponse
from core_parser_app.components.module import api as module_api
from core_main_app.components.template import api as template_api


def delete_module(request):
    """
    Deletes a module from a template
    :param request:
    :return:
    """
    try:
        # get the parameters
        template_id = request.POST.get('templateID', None)
        xpath = request.POST.get('xpath', None)

        # get the template
        template = template_api.get(template_id)

        # delete the module
        module_api.delete_module(template, xpath)
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')

    return HttpResponse(json.dumps({}), content_type='application/javascript')


def insert_module(request):
    """
    Insert a module in a template
    :param request:
    :return:
    """
    try:
        # get the parameters
        module_id = request.POST.get('moduleID', None)
        template_id = request.POST.get('templateID', None)
        xpath = request.POST.get('xpath', None)

        # get the template
        template = template_api.get(template_id)

        # add the module
        module_api.add_module(template, module_id, xpath)
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')

    return HttpResponse(json.dumps({}), content_type='application/javascript')

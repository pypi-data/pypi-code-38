"""
    Ajax views for the admin part
"""
from django.http import HttpResponse
import json
from core_main_app.commons import exceptions as main_exceptions
from core_website_app.commons import exceptions
import core_website_app.components.account_request.api as account_request_api
import core_website_app.components.contact_message.api as contact_message_api


def accept_request(request):
    """
    Accepts a request and creates the user account
    :param request:
    :return:
    """
    try:
        request_id = request.POST['requestid']
        account_request_from_api = account_request_api.get(request_id)
        account_request_api.accept(account_request_from_api)
        message = "Request Accepted"
    except main_exceptions.ApiError as error:
        raise exceptions.WebsiteAjaxError(error.message)
    except Exception as exception:
        raise exceptions.WebsiteAjaxError(exception.message)

    return HttpResponse(json.dumps({"message": message}), content_type='application/json')


def deny_request(request):
    """
    Denies an account request
    :param request:
    :return:
    """

    try:
        request_id = request.POST['requestid']
        account_request_from_api = account_request_api.get(request_id)
        account_request_api.deny(account_request_from_api)
        message = "Request denied"
    except main_exceptions.ApiError as error:
        raise exceptions.WebsiteAjaxError(error.message)
    except Exception as exception:
        raise exceptions.WebsiteAjaxError(exception.message)

    return HttpResponse(json.dumps({"message": message}), content_type='application/json')


def remove_message(request):
    """
    Remove a message from the list of messages
    :param request:
    :return:
    """

    try:
        contact_message = contact_message_api.get(request.POST['messageid'])
        contact_message_api.delete(contact_message)
        message = "Message deleted"
    except exceptions.WebsiteAjaxError as error:
        message = error.message
    except Exception as exception:
        message = exception.message

    return HttpResponse(json.dumps({"message": message}), content_type='application/json')


def account_request_count(request):
    """


    Returns:

    """
    return HttpResponse(json.dumps({"count": account_request_api.get_count()}), content_type='application/json')


def contact_message_count(request):
    return HttpResponse(json.dumps({"count": contact_message_api.get_count()}), content_type='application/json')

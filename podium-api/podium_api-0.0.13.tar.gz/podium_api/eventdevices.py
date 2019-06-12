#!/usr/bin/env python
# -*- coding: utf-8 -*-
from podium_api.types.eventdevice import get_eventdevice_from_json

try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode
from podium_api.async import make_request_custom_success, get_json_header_token
from podium_api.types.paged_response import get_paged_response_from_json
from podium_api.types.redirect import get_redirect_from_json
from podium_api.types.exceptions import NoEndpointOrIdsProvided
import podium_api

def make_eventdevices_get(token, event_id=None,
                          endpoint=None,
                          start=None, per_page=None,
                          expand=True, quiet=None,
                          success_callback=None,
                          redirect_callback=None,
                          failure_callback=None,
                          progress_callback=None):
    """
    Request that returns a PodiumPagedRequest of event devices. 
    By default a get request to 
    'https://podium.live/api/v1/events/{event_id}/devices' will be made.

    Args:
        token (PodiumToken): The authentication token for this session.

    Kwargs:
        expand (bool): Expand all objects in response output. Defaults to True

        quiet (object): If not None HTML layout will not render endpoint
        description. Defaults to None.

        success_callback (function): Callback for a successful request,
        will have the signature:
            on_success(PodiumPagedResponse)
        Defaults to None.

        failure_callback (function): Callback for failures and errors. 
        Will have the signature:
            on_failure(failure_type (string), result (dict), data (dict))
        Values for failure type are: 'error', 'failure'. Defaults to None.

        redirect_callback (function): Callback for redirect, 
        Will have the signature:
            on_redirect(result (dict), data (dict))
        Defaults to None.

        progress_callback (function): Callback for progress updates,
        will have the signature:
            on_progress(current_size (int), total_size (int), data (dict))
        Defaults to None.

        start (int): Starting index for events list. 0 indexed.

        per_page (int): Number per page of results, max of 100.

        endpoint (str): If provided this endpoint will be used instead of
        the default: 'https://podium.live/api/v1/events/{event_id}/devices'

        event_id (int): If an endpoint is not provided you should provide
        the id of the event for which you want to look up the devices.

    Return:
        UrlRequest: The request being made.

    """
    if endpoint is None:
        if event_id is None:
            raise NoEndpointOrIdsProvided()
        endpoint = '{}/api/v1/events/{}/devices'.format(
            podium_api.PODIUM_APP.podium_url,
            event_id
            )
    params = {}
    if expand is not None:
        params['expand'] = expand
    if quiet is not None:
        params['quiet'] = quiet
    if start is not None:
        params['start'] = start
    if per_page is not None:
        per_page = min(per_page, 100)
        params['per_page'] = per_page

    header = get_json_header_token(token)
    return make_request_custom_success(endpoint, eventdevices_success_handler,
                                       method='GET',
                                       success_callback=success_callback,
                                       failure_callback=failure_callback,
                                       progress_callback=progress_callback,
                                       redirect_callback=redirect_callback,
                                       params=params, header=header)



def make_livestreams_get(token,
                          endpoint=None,
                          start=None, per_page=None,
                          expand=True, quiet=None,
                          success_callback=None,
                          redirect_callback=None,
                          failure_callback=None,
                          progress_callback=None):
    """
    Request that returns a PodiumPagedRequest of event devices for current livestreams. 
    By default a get request to 
    'https://podium.live/api/v1/livestreams' will be made.

    Args:
        token (PodiumToken): The authentication token for this session.

    Kwargs:
        expand (bool): Expand all objects in response output. Defaults to True

        quiet (object): If not None HTML layout will not render endpoint
        description. Defaults to None.

        success_callback (function): Callback for a successful request,
        will have the signature:
            on_success(PodiumPagedResponse)
        Defaults to None.

        failure_callback (function): Callback for failures and errors. 
        Will have the signature:
            on_failure(failure_type (string), result (dict), data (dict))
        Values for failure type are: 'error', 'failure'. Defaults to None.

        redirect_callback (function): Callback for redirect, 
        Will have the signature:
            on_redirect(result (dict), data (dict))
        Defaults to None.

        progress_callback (function): Callback for progress updates,
        will have the signature:
            on_progress(current_size (int), total_size (int), data (dict))
        Defaults to None.

        start (int): Starting index for events list. 0 indexed.

        per_page (int): Number per page of results, max of 100.

        endpoint (str): If provided this endpoint will be used instead of
        the default: 'https://podium.live/api/v1/eventdevices'

    Return:
        UrlRequest: The request being made.

    """
    if endpoint is None:
        endpoint = '{}/api/v1/livestreams'.format(
            podium_api.PODIUM_APP.podium_url)
    params = {}
    if expand is not None:
        params['expand'] = expand
    if quiet is not None:
        params['quiet'] = quiet
    if start is not None:
        params['start'] = start
    if per_page is not None:
        per_page = min(per_page, 100)
        params['per_page'] = per_page

    header = get_json_header_token(token)
    return make_request_custom_success(endpoint, eventdevices_success_handler,
                                       method='GET',
                                       success_callback=success_callback,
                                       failure_callback=failure_callback,
                                       progress_callback=progress_callback,
                                       redirect_callback=redirect_callback,
                                       params=params, header=header)

def make_eventdevice_update(token, eventdevice_uri, name=None,
                            success_callback=None, failure_callback=None,
                            progress_callback=None, redirect_callback=None):
    """
    Request that updates a PodiumEventDevice.

    Args:
        token (PodiumToken): The authentication token for this session.

        eventdevice_uri (str): URI for the eventdevice you are updating.

    Kwargs:
        name (str): Name of the device for this particular event, allows for
        car number/name to change between events. If blank/missing, will
        default to device name.

        success_callback (function): Callback for a successful request,
        will have the signature: 
            on_success(result (dict), updated_uri (str))
        Defaults to None..

        failure_callback (function): Callback for failures and errors. 
        Will have the signature:
            on_failure(failure_type (string), result (dict), data (dict))
        Values for failure type are: 'error', 'failure'. Defaults to None.

        redirect_callback (function): Callback for redirect, 
        Will have the signature:
            on_redirect(redirect_object (PodiumRedirect))
        Defaults to None.

        progress_callback (function): Callback for progress updates,
        will have the signature:
            on_progress(current_size (int), total_size (int), data (dict))
        Defaults to None.

    Return:
        UrlRequest: The request being made.

    """
    body = {}
    if name is not None:
        body['eventdevice[name]'] = name
    header = get_json_header_token(token)
    return make_request_custom_success(
        eventdevice_uri, eventdevice_update_success_handler,
        method='PUT',
        success_callback=success_callback,
        redirect_callback=redirect_callback,
        failure_callback=failure_callback,
        progress_callback=progress_callback,
        body=body, header=header,
        data={'updated_uri': eventdevice_uri}
        )


def make_eventdevice_get(token, eventdevice_uri, expand=True,
                         quiet=None, success_callback=None,
                         redirect_callback=None,
                         failure_callback=None, progress_callback=None):


    """
    Request that returns a PodiumEventDevice for the provided eventdevice_uri

    Args:
        token (PodiumToken): The authentication token for this session.

        eventdevice_uri (str): URI for the eventdevice you want.

    Kwargs:

        expand (bool): Expand all objects in response output. Defaults to True

        quiet (object): If not None HTML layout will not render endpoint
        description. Defaults to None.

        success_callback (function): Callback for a successful request,
        will have the signature:
            on_success(PodiumEvent)
        Defaults to None.

        failure_callback (function): Callback for failures and errors.
        Will have the signature:
            on_failure(failure_type (string), result (dict), data (dict))
        Values for failure type are: 'error', 'failure'. Defaults to None.

        redirect_callback (function): Callback for redirect,
        Will have the signature:
            on_redirect(result (dict), data (dict))
        Defaults to None.

        progress_callback (function): Callback for progress updates,
        will have the signature:
            on_progress(current_size (int), total_size (int), data (dict))
        Defaults to None.

    Return:
        UrlRequest: The request being made.

    """
    params = {}
    if expand is not None:
        params['expand'] = expand
    if quiet is not None:
        params['quiet'] = quiet
    header = get_json_header_token(token)
    return make_request_custom_success(eventdevice_uri, eventdevice_success_handler,
                                       method='GET',
                                       success_callback=success_callback,
                                       failure_callback=failure_callback,
                                       progress_callback=progress_callback,
                                       redirect_callback=redirect_callback,
                                       params=params, header=header)

def eventdevice_success_handler(req, results, data):
    """
    Creates and returns a PodiumDevice to the success_callback found in data
    if there is one.

    Called automatically by **make_device_get**

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a
        'success_callback' key.

    Return:
        None, this function instead calls a callback.
    """
    if data['success_callback'] is not None:
        data['success_callback'](get_eventdevice_from_json(results['eventdevice']))


def make_eventdevice_delete(token, eventdevice_uri,
                            success_callback=None, failure_callback=None,
                            progress_callback=None, redirect_callback=None):

    """
    Deletes the device for the provided URI.

    Args:
        token (PodiumToken): The authentication token for this session.

        eventdevice_uri (str): URI for the eventdevice you want.

    Kwargs:
        success_callback (function): Callback for a successful request,
        will have the signature:
            on_success(deleted_uri (str))
        Defaults to None.

        failure_callback (function): Callback for failures and errors.
        Will have the signature:
            on_failure(failure_type (string), result (dict), data (dict))
        Values for failure type are: 'error', 'failure'. Defaults to None.

        redirect_callback (function): Callback for redirect,
        Will have the signature:
            on_redirect(result (dict), data (dict))
        Defaults to None.

        progress_callback (function): Callback for progress updates,
        will have the signature:
            on_progress(current_size (int), total_size (int), data (dict))
        Defaults to None.

    Return:
        UrlRequest: The request being made.

    """
    header = get_json_header_token(token)
    return make_request_custom_success(
        eventdevice_uri, eventdevice_delete_handler,
        method='DELETE',
        success_callback=success_callback,
        redirect_callback=redirect_callback,
        failure_callback=failure_callback,
        progress_callback=progress_callback,
        header=header,
        data={'deleted_uri': eventdevice_uri}
    )

def eventdevice_delete_handler(req, results, data):
    """
    Returns the URI for the deleted resource to the user set success_callback

    Called automatically by **make_eventdevice_delete**

    Args:
        req (UrlRequest): Instance of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a
        'success_callback' key.

    Return:
        None, this function instead calls a callback.
    """
    if data['success_callback'] is not None:
        data['success_callback'](data['deleted_uri'])


def make_eventdevice_create(token, event_id, device_id, name,
                            success_callback=None, failure_callback=None,
                            progress_callback=None, redirect_callback=None):
    """
    Request that creates a new PodiumEventDevice.

    The uri for the newly created event device will be provided to the
    redirect_callback if one is provided in the form of a PodiumRedirect.

    Args:
        token (PodiumToken): The authentication token for this session.

        event_id (int): Id of the event to add the device to.

        device_id (int): Id of the device to add to the event.

        name (str): Name of the device for this particular event, allows for
        car number/name to change between events. If blank/missing, will
        default to device name.

    Kwargs:
        success_callback (function): Callback for a successful request,
        will have the signature: 
            on_success(result (dict), data (dict))
        Defaults to None..

        failure_callback (function): Callback for failures and errors. 
        Will have the signature:
            on_failure(failure_type (string), result (dict), data (dict))
        Values for failure type are: 'error', 'failure'. Defaults to None.

        redirect_callback (function): Callback for redirect, 
        Will have the signature:
            on_redirect(redirect_object (PodiumRedirect))
        Defaults to None.

        progress_callback (function): Callback for progress updates,
        will have the signature:
            on_progress(current_size (int), total_size (int), data (dict))
        Defaults to None.

    Return:
        UrlRequest: The request being made.

    """
    endpoint = '{}/api/v1/events/{}/devices'.format(
        podium_api.PODIUM_APP.podium_url,
        event_id
        )
    body = {'eventdevice[device_id]': device_id, 'eventdevice[name]': name}
    header = get_json_header_token(token)
    return make_request_custom_success(
        endpoint, None, method='POST',
        success_callback=success_callback,
        redirect_callback=create_eventdevice_redirect_handler,
        failure_callback=failure_callback,
        progress_callback=progress_callback,
        body=body, header=header,
        data={'_redirect_callback': redirect_callback}
        )


def create_eventdevice_redirect_handler(req, results, data):
    """
    Handles the success redirect of a **make_event_device_create** call.

    Returns a PodiumRedirect with a uri for the newly created event to the
    _redirect_callback found in data. 

    Automatically called by **make_event_device_create**, will call the
    redirect_callback passed in to **make_event_device_create** if there is on.

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a 
        'success_callback' key.

    Return:
        None, this function instead calls a callback.

    """
    if data['_redirect_callback'] is not None:
        data['_redirect_callback'](get_redirect_from_json(results,
                                                          'eventdevice'))


def eventdevice_update_success_handler(req, results, data):
    """
    Success callback after updating an event. Will return the message from
    the server and the event uri to the success_callback.

    Called automatically by **make_eventdevice_update**.

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a 
        'success_callback' key.

    Return:
        None, this function instead calls a callback.

    """
    if data['success_callback'] is not None:
        data['success_callback'](results, data['updated_uri'])


def eventdevices_success_handler(req, results, data):
    """
    Creates and returns a PodiumPagedResponse with PodiumEventDevice as the
    payload
    to the success_callback found in data if there is one.

    Called automatically by **make_eventdevices_get**.

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a 
        'success_callback' key.

    Return:
        None, this function instead calls a callback.

    """
    if data['success_callback'] is not None:
        data['success_callback'](get_paged_response_from_json(results,
                                                              'eventdevices'))

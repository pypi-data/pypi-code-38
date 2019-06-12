#!/usr/bin/env python
# -*- coding: utf-8 -*-
from podium_api.async import make_request_custom_success, get_json_header_token
from podium_api.types.paged_response import get_paged_response_from_json
from podium_api.types.event import get_event_from_json
from podium_api.types.redirect import get_redirect_from_json
import podium_api

def make_event_update(token, event_uri, title=None, start_time=None,
                      end_time=None, venue_id=None,
                      success_callback=None, failure_callback=None,
                      progress_callback=None, redirect_callback=None):
    """
    Request that updates a PodiumEvent.

    Args:
        token (PodiumToken): The authentication token for this session.

        event_uri (str): URI for the event you are updating.

    Kwargs:
        venue_id(str): ID for the venue of event.

        title (str): title for the vent.

        start_time (str): Starting time, use ISO 8601 format.

        end_time (str): Ending time, use ISO 8601 format.

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
    if title is not None:
        body['event[title]'] = title
    if start_time is not None:
        body['event[start_time]'] = start_time
    if end_time is not None:
        body['event[end_time]'] = end_time
    if venue_id is not None:
        body['event[venue_id]'] = venue_id
    header = get_json_header_token(token)
    return make_request_custom_success(
        event_uri, event_update_success_handler,
        method="PUT",
        success_callback=success_callback,
        redirect_callback=redirect_callback,
        failure_callback=failure_callback,
        progress_callback=progress_callback,
        body=body, header=header,
        data={'updated_uri': event_uri}
        )


def make_event_create(token, title, start_time, end_time, venue_id=None,
                      success_callback=None, failure_callback=None,
                      progress_callback=None, redirect_callback=None):
    """
    Request that creates a new PodiumEvent.

    The uri for the newly created event will be provided to the
    redirect_callback if one is provided in the form of a PodiumRedirect.

    Args:
        token (PodiumToken): The authentication token for this session.

        title (str): title for the vent.

        start_time (str): Starting time, use ISO 8601 format.

        end_time (str): Ending time, use ISO 8601 format.

    Kwargs:
        venue_id(str): ID for the venue of event.

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
    endpoint = '{}/api/v1/events'.format(podium_api.PODIUM_APP.podium_url)
    body = {'event[title]': title, 'event[start_time]': start_time,
            'event[end_time]': end_time}
    if venue_id is not None:
        body['event[venue_id]'] = venue_id
    header = get_json_header_token(token)
    return make_request_custom_success(
        endpoint, None, method='POST',
        success_callback=success_callback,
        redirect_callback=create_event_redirect_handler,
        failure_callback=failure_callback,
        progress_callback=progress_callback,
        body=body, header=header,
        data={'_redirect_callback': redirect_callback}
        )


def make_event_delete(token, event_uri,
                      success_callback=None, redirect_callback=None,
                      failure_callback=None, progress_callback=None):
    """
    Deletes the event for the provided URI.

    Args:
        token (PodiumToken): The authentication token for this session.

        event_uri (str): URI for the event you want.

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
    return make_request_custom_success(event_uri, event_delete_handler,
                                       method='DELETE',
                                       success_callback=success_callback,
                                       failure_callback=failure_callback,
                                       progress_callback=progress_callback,
                                       redirect_callback=redirect_callback,
                                       header=header,
                                       data={'deleted_uri': event_uri})



def make_event_get(token, event_uri, expand=True,
                   quiet=None, success_callback=None,
                   redirect_callback=None,
                   failure_callback=None, progress_callback=None):
    """
    Request that returns a PodiumEvent for the provided event_uri. 

    Args:
        token (PodiumToken): The authentication token for this session.

        event_uri (str): URI for the event you want.

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
    return make_request_custom_success(event_uri, event_success_handler,
                                       method='GET',
                                       success_callback=success_callback,
                                       failure_callback=failure_callback,
                                       progress_callback=progress_callback,
                                       redirect_callback=redirect_callback,
                                       params=params, header=header)


def make_events_get(token, start=None, per_page=None,
                    endpoint=None, expand=True,
                    quiet=None, success_callback=None,
                    redirect_callback=None,
                    failure_callback=None, progress_callback=None):
    """
    Request that returns a PodiumPagedRequest of events. 
    By default a get request to 
    'https://podium.live/api/v1/events' will be made.

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
        the default: 'https://podium.live/api/v1/events'

    Return:
        UrlRequest: The request being made.

    """
    if endpoint is None:
        endpoint = '{}/api/v1/events'.format(podium_api.PODIUM_APP.podium_url)
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
    return make_request_custom_success(endpoint, events_success_handler,
                                       method='GET',
                                       success_callback=success_callback,
                                       failure_callback=failure_callback,
                                       progress_callback=progress_callback,
                                       redirect_callback=redirect_callback,
                                       params=params, header=header)


def event_delete_handler(req, results, data):
    """
    Returns the URI for the deleted resource to the user set success_callback

    Called automatically by **make_event_delete**

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
        data['success_callback'](data['deleted_uri'])


def event_success_handler(req, results, data):
    """
    Creates and returns a PodiumEvent to the success_callback found in data
    if there is one.

    Called automatically by **make_event_get**

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
        data['success_callback'](get_event_from_json(results['event']))


def events_success_handler(req, results, data):
    """
    Creates and returns a PodiumPagedResponse with PodiumEvent as the payload
    to the success_callback found in data if there is one.

    Called automatically by **make_events_get**.

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
                                                              'events'))

def create_event_redirect_handler(req, results, data):
    """
    Handles the success redirect of a **make_event_create** call.

    Returns a PodiumRedirect with a uri for the newly created event to the
    _redirect_callback found in data. 

    Automatically called by **make_event_create**, will call the
    redirect_callback passed in to **make_event_create** if there is on.

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
        data['_redirect_callback'](get_redirect_from_json(results, 'event'))


def event_update_success_handler(req, results, data):
    """
    Success callback after updating an event. Will return the message from
    the server and the event uri to the success_callback.

    Called automatically by **make_event_update**.

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

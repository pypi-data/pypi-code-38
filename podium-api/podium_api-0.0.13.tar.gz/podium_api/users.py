#!/usr/bin/env python
# -*- coding: utf-8 -*-
from podium_api.async import make_request_custom_success, get_json_header_token
from podium_api.types.user import get_user_from_json

def make_user_get(token, endpoint,
                   expand=False, quiet=None, success_callback=None,
                   failure_callback=None, progress_callback=None,
                   redirect_callback=None):
    """
    Returns a PodiumUser object found at the uri provided in the endpoint
    arg.

    Args:
        token (PodiumToken): The authentication token for this session.

        endpoint (str): The URI to make the request to. Typically should be
        provided by some api object.

    Kwargs:
        expand (bool): Expand all objects in response output. Defaults to False

        quiet (object): If not None HTML layout will not render endpoint
        description. Defaults to None.

        success_callback (function): Callback for a successful request,
        will have the signature:
            on_success(token (string))
        Defaults to None.

        failure_callback (function): Callback for redirects, failures, and
        errors. Will have the signature:
            on_failure(failure_type (string), result (dict), data (dict))
        Values for failure type are: 'error', 'redirect', 'failure'. Defaults
        to None.

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
    return make_request_custom_success(endpoint, users_success_handler,
                                       method="GET",
                                       success_callback=success_callback,
                                       failure_callback=failure_callback,
                                       progress_callback=progress_callback,
                                       redirect_callback=redirect_callback,
                                       params=params, header=header)


def users_success_handler(req, results, data):
    """
    Creates and returns a  PodiumToken to the success_callback found in data.

    Called automatically by **make_login_request**.

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
        data['success_callback'](get_user_from_json(results['user']))

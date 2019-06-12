#!/usr/bin/env python
# -*- coding: utf-8 -*-
from podium_api.types.token import get_token_from_json
from podium_api.async import make_request_custom_success, get_json_header
import podium_api
def make_login_post(username, password, success_callback=None,
                    failure_callback=None, progress_callback=None,
                    redirect_callback=None):
    """
    Request that hits the /oauth/token endpoint to log a user in. Will 
    internally use **make_request_custom_success**.

    Args:
        username (string): The username to login

        password (string): The password for user.

    Kwargs:
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
    endpoint = '{}/oauth/token'.format(podium_api.PODIUM_APP.podium_url)
    body = {'grant_type': 'password', 'username': username,
            'password': password}
    header = get_json_header()
    return make_request_custom_success(endpoint, login_success_handler,
                                       method='POST',
                                       success_callback=success_callback,
                                       failure_callback=failure_callback,
                                       progress_callback=progress_callback,
                                       redirect_callback=redirect_callback,
                                       body=body, header=header)


def login_success_handler(req, results, data):
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
        data['success_callback'](get_token_from_json(results))

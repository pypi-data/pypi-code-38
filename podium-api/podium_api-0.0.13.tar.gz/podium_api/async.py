#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.network.urlrequest import UrlRequest
import podium_api
try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode
from podium_api.types.exceptions import PodiumApplicationNotRegistered

def get_json_header_token(token):
    """
    Returns a header prepared with the app_id and app_secret set to tell
    the server to return json. Content-Type will be
    'application/x-www-form-urlencoded'

    Return:
        dict: Dict containing the header data for a request.

    """
    if podium_api.PODIUM_APP is None:
        raise PodiumApplicationNotRegistered()
    return {"Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer {}".format(token.token),
            "Accept": "application/json"}


def get_json_header():
    """
    Returns a header prepared with the app_id and app_secret set to tell
    the server to return json. Content-Type will be
    'application/x-www-form-urlencoded'

    Return:
        dict: Dict containing the header data for a request.

    """
    if podium_api.PODIUM_APP is None:
        raise PodiumApplicationNotRegistered()
    return {"Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic {}:{}".format(
                podium_api.PODIUM_APP.app_id,
                podium_api.PODIUM_APP.app_secret),
            "Accept": "application/json"}

def make_request(endpoint, method="GET", on_success=None, on_failure=None,
                 on_error=None, on_redirect=None, on_progress=None,
                 body=None, header=None, data=None, params=None):
    """
    Creates and starts a UrlRequest.

    Args:
        endpoint (str): The endpoint the request will go to.

    Kwargs:
        method (str): The type of request being made. Defaults to 'GET'

        on_success (function): Callback for a successful request, will have
        the signature: 
            on_success(request (UrlRequest), result (dict), data (dict))
        Defaults to None.

        on_failure (function): Callback for request that fails, will have
        the signature:
            on_failure(request (UrlRequest), result (dict), data (dict))
        Defaults to None.

        on_error (function): Callback for request that handles errors, will have
        the signature:
            on_error(request (UrlRequest), result (dict), data (dict))
        Defaults to None.

        on_redirect (function): Callback for request that redirects, will have
        the signature:
            on_redirect(request (UrlRequest), result (dict), data (dict))
        Defaults to None.

        on_progress (function): Callback for request in progress, will have
        the signature:
            on_progress(request (UrlRequest), current (int), total (int),
                        data (dict))
        Defaults to None.

        body (dict): Body of the request, will be encoded using 
        urllib.urlencode. Defaults to None.

        header (dict): The header for the request. Defaults to None.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Each callback will receive the
        data in here. Defaults to empty dict.

    Return:
        UrlRequest: The request being made.

    """
    if body is not None:
        body = urlencode(body)
    if params is not None and params != {}:
        params = urlencode(params)
        if "?" in endpoint:
            endpoint = '{}&{}'.format(endpoint, params)
        else:
            endpoint = '{}?{}'.format(endpoint, params)
    return UrlRequest(
        endpoint, method=method, req_body=body, req_headers=header,
        on_success=(lambda req, res: on_success(
                    req, res, data)) if on_success is not None else None,
        on_failure=(lambda req, res: on_failure(
                    req, res, data)) if on_failure is not None else None,
        on_redirect=(lambda req, res: on_redirect(
                     req, res, data)) if on_redirect is not None else None,
        on_progress=(lambda req, cur, tot:
            on_progress(req, cur, tot, data)
            ) if on_progress is not None else None,
        on_error=(lambda req, res: on_error(
                  req, res, data)) if on_error is not None else None
        )

def make_request_default(endpoint, method="GET", success_callback=None,
                         failure_callback=None, progress_callback=None,
                         redirect_callback=None,
                         data=None, body=None, header=None, params=None):
    """
    Creates a URL Request with simplified, default callbacks. Error,
    failure, and redirect will be condensed into one callback. 

    Args:
        endpoint (str): The endpoint the request will go to.

    Kwargs:
        method (str): The type of request being made. Defaults to 'GET'

        success_callback (function): Callback for a successful request,
        will have the signature: 
            on_success(result (dict), data (dict))
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

        body (dict): Body of the request, will be encoded using 
        urllib.urlencode. Defaults to None.

        header (dict): The header for the request. Defaults to None.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Each callback will receive the
        data in here. Defaults to empty dict.

    Return:
        UrlRequest: The request being made.

    """
    if data is None:
        data = {}
    data['success_callback'] = success_callback
    data['failure_callback'] = failure_callback
    data['progress_callback'] = progress_callback
    data['redirect_callback'] = redirect_callback
    return make_request(endpoint, method=method, on_success=default_success,
                        on_failure=default_failure, on_error=default_error,
                        on_redirect=default_redirect,
                        on_progress=default_progress,
                        body=body, header=header, data=data,
                        params=params)

def make_request_custom_success(endpoint, success_handler, method="GET",
                                success_callback=None, failure_callback=None,
                                redirect_callback=None,
                                progress_callback=None, data=None, body=None,
                                header=None, params=None):
    """
    Creates a request with a custom success handler and the default failure
    and progress handlers.

    Args:
        endpoint (str): The endpoint the request will go to.

        success_handler (function): Callback for a successful request,
        will have the signature. Typically used to modify the args being sent
        to the success_callback. Your success_handler should call the
        success_callback provided as a kwarg if available.
            on_success(request (UrlRequest), result (dict), data (dict))

    Kwargs:
        method (str): The type of request being made. Defaults to 'GET'

        success_callback (function): Callback for a successful request,
        will have a signature determined by the success_handler.
        Defaults to None.

        failure_callback (function): Callback for redirects, failures, and
        errors. Will have the signature:
            on_failure(failure_type (string), result (dict), data (dict))
        Values for failure type are: 'error', 'redirect', 'failure'. Defaults
        to None.

        redirect_callback (function): Callback for redirect, 
        Will have the signature:
            on_redirect(result (dict), data (dict))
        Defaults to None.

        progress_callback (function): Callback for progress updates,
        will have the signature:
            on_progress(current_size (int), total_size (int), data (dict))
        Defaults to None.

        body (dict): Body of the request, will be encoded using 
        urllib.urlencode. Defaults to None.

        header (dict): The header for the request. Defaults to None.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Each callback will receive the
        data in here. Defaults to empty dict.

    Return:
        UrlRequest: The request being made.

    """
    if data is None:
        data = {}
    data['success_callback'] = success_callback
    data['failure_callback'] = failure_callback
    data['progress_callback'] = progress_callback
    data['redirect_callback'] = redirect_callback
    return make_request(endpoint, method=method, on_success=success_handler,
                        on_failure=default_failure, on_error=default_error,
                        on_redirect=default_redirect,
                        on_progress=default_progress,
                        body=body, header=header, data=data, params=params)


def default_redirect(req, results, data):
    """
    Default handler for a redirect callback. Will call the 'redirect_callback'
    provided in data with the args: response headers (dict), data (dict)

    If the value of 'failure_callback' is None, nothing will be called.

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a 
        'redirect_callback' key.

    Return:
        None, this function instead calls a callback.

    """
    if data['redirect_callback'] is None:
        return
    data['redirect_callback'](req, req._resp_headers, data)

def default_success(req, results, data):
    """
    Default handler for a success callback. Will call the 'failure_callback'
    provided in data with the args: results, data

    If the value of 'success_callback' is None, nothing will be called.

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a 
        'success_callback' key.

    Return:
        None, this function instead calls a callback.
        
    """
    if data['success_callback'] is None:
        return
    data['success_callback'](results, data)

def default_failure(req, results, data):
    """
    Default handler for a failure callback. Will call the 'success_callback'
    provided in data with the args: 'failure', results, data

    If the value of 'failure_callback' is None, nothing will be called.

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a 
        'failure_callback' key.

    Return:
        None, this function instead calls a callback.
        
    """
    if data['failure_callback'] is None:
        return
    data['failure_callback']('failure', results, data)

def default_error(req, results, data):
    """
    Default handler for an error callback. Will call the 'failure_callback'
    provided in data with the args: 'error', results, data

    If the value of 'failure_callback' is None, nothing will be called.

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a 
        'failure_callback' key.

    Return:
        None, this function instead calls a callback.
        
    """
    if data['failure_callback'] is None:
        return
    data['failure_callback']('error', results, data)

def default_progress(req, current_size, total_size, data):
    """
    Default handler for a progress callback. Will call the 'progress_callback'
    provided in data with the args: current_size, total_size, data

    If the value of 'progress_callback' is None, nothing will be called.

    Args:
        req (UrlRequest): Instace of the request that was made.

        results (dict): Dict returned by the request.

        data (dict): Wildcard dict for containing data that needs to be passed
        to the various callbacks of a request. Will contain at least a 
        'progress_callback' key.

    Return:
        None, this function instead calls a callback.
        
    """
    if data['progress_callback'] is None:
        return
    data['progress_callback'](current_size, total_size, data)

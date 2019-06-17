"""
Introduction
------------
Various Python exceptions thrown by the ``rockset`` module are explained in
this section, along with possible reasons and remedies to assist in
trouble-shooting.

.. _AuthError:

Authentication Errors
---------------------
The server is rejecting your request because you have either an expired or
an invalid token. Ensure you have a valid API key or generate a new one
using the Rockset Console before trying your request again.

.. autoclass:: rockset.exception.AuthError

.. _InputError:

Input Errors
------------
The server is unable to understand the API request as it was sent. This most
likely means the API was badly formed (like the input query has a syntax error).
When you encounter this error, please refer to the relevant documentation and
verify if the request is constructed properly and if the resource is still
present.

.. autoclass:: rockset.exception.InputError

.. _LimitReached:

Limit Reached
-------------
The server could understand the input request but refuses to execute it.
This commonly happens when an account limit has been reached. Please reach
out to Rockset Support with more details to alter your account limit.

.. autoclass:: rockset.exception.LimitReached

.. _NotYetImplemented:

Not Yet Implemented
-------------------
Your API request needs a feature that is not present in your cluster for it to
complete. Your cluster needs an upgrade or this feature is in our roadmap but
we haven't gotten around to implementing it yet. Please reach out to Rockset
support with more details to help us prioritize this feature.

.. autoclass:: rockset.exception.NotYetImplemented

.. _RequestTimeout:

Request Timeouts
----------------
The server did not complete the API request before the timeout you set for
the request expired. To troubleshoot, see if your request succeeds when you
don't set a timeout. If it does then you need to recalibrate your timeout value.
If it doesn't, then debug the issue based on the new error you receive.

.. autoclass:: rockset.exception.RequestTimeout

.. _ServerError:

Server Errors
-------------
These errors mean the server correctly parsed the input request, but couldn't
process it for some reason.  If a particular request or application is seeing
this while other requests are fine, then you probably uncovered a bug with
Rockset. Please contact Rockset support to report the bug and we will provide
a time estimte for resolution and send you a t-shirt.

.. autoclass:: rockset.exception.ServerError

.. _TransientServerError:

Transient Server Errors
-----------------------

When many of your requests are failing with TransientServerErrors, it means our
servers are going through a period of instability or unplanned downtime.
This always means our alerts are firing, our pagers are ringing, phones are
buzzing, and little adorable kittens are getting lost in the woods. We are
actively investigating and fixing this issue. Look for upates on our status
page with estimates on time to resolution. Sorry.

.. autoclass:: rockset.exception.TransientServerError

"""
import json


class Error(Exception):
    """Base class for all rockset exceptions"""

    def __init__(self, **kwargs):
        message = kwargs.pop('message', None)
        if message is None:
            message = 'Unexpected error'
        super(Error, self).__init__(message)
        kwargs['message'] = message
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        parts = []
        if hasattr(self, 'code'):
            parts.append('{}'.format(self.code))
        if hasattr(self, 'type'):
            parts.append('{}'.format(self.type))
        parts.append(self.message)
        return ' '.join(parts)


class HTTPError(Error):
    """Error returned by swagger API call.

    Attributes:
        code (int): HTTP status code obtained from server
        message (str): error message with more details
        type (str): error sub-category
    """

    def __init__(self, **kwargs):
        kwargs['message'] = kwargs.get(
            'message', 'Unexpected error from server'
        )
        super(HTTPError, self).__init__(**kwargs)


class AuthError(HTTPError):
    """API key or access token is missing, expired or invalid.
    Re-authenticating with a valid API key should normally fix this.

    Attributes:
        code (int): HTTP status code obtained from server
        message (str): error message with more details
    """
    pass


class InputError(HTTPError):
    """User request has a missing or invalid parameter and cannot be
    processed as is. Syntax errors in queries fall in this category.

    Attributes:
        code (int): HTTP status code obtained from server
        message (str): error message with more details
        type (str): error sub-category
    """
    pass


class LimitReached(HTTPError):
    """The API request has exceeded some user-defined limit (such as
    max deadline set for a query) or a system limit. Refer to
    documentation to increase the limit or reach out to Rockset support
    with more details to alter your account limit.

    Attributes:
        code (int): HTTP status code obtained from server
        message (str): error message with more details
        type (str): error sub-category
    """
    pass


class NotYetImplemented(HTTPError):
    """Your request is expecting a feature that has not been deployed in your
    cluster or has not yet been implemented. Please reach out to Rockset
    support with more details to help us prioritize this feature. Thank you.

    Attributes:
        code (int): HTTP status code obtained from server
        message (str): error message with more details
        type (str): error sub-category
    """
    pass


class ServerError(HTTPError):
    """Something totally unexpected happened on our servers while processing
    your request and most likely you have encountered a bug in Rockset.
    Please contact Rockset support and provide all the details you received
    along with the error for quick diagnosis, resolution, and to collect your
    t-shirt.

    Attributes:
        code (int): HTTP status code obtained from server
        message (str): error message with more details
        type (str): error sub-category
    """
    pass


class TransientServerError(HTTPError):
    """Some transient hiccup made us fail this request. This means our
    oncall engineers are actively working on this issue and should resolve
    the issue soon. Please retry after sometime. Sorry.

    Attributes:
        code (int): HTTP status code obtained from server
        message (str): error message with more details
        type (str): error sub-category
    """
    pass


class ResourceSuspendedError(HTTPError):
    """ Target collection was suspended due to inactivity. A query
    issued against the resource will automatically trigger reactivation of
    the target collection. Please retry the query once the resource
    has been unsuspended. Use the Rockset Console or the CLI or contact
    Rockset support to configure the auto suspend behavior.

    Attributes:
        message (str): error message
    """
    pass


class RequestTimeout(Error):
    """Request timed out.

    Many API calls allow a client side timeout to be specified.
    When specified, this exception will be thrown when the timeout
    expires and the API call has not received a valid response
    or an error from the servers.

    Attributes:
        message (str): timeout error message
        timeout (int): timeout specfied with API call in seconds
    """

    def __init__(self, **kwargs):
        kwargs['message'] = kwargs.get('message', 'Request timed out')
        kwargs['timeout'] = kwargs.get('timeout', None)
        super(RequestTimeout, self).__init__(**kwargs)


__all__ = [
    'AuthError',
    'InputError',
    'LimitReached',
    'NotYetImplemented',
    'RequestTimeout',
    'ServerError',
    'TransientServerError',
]

# Copyright (c) 2014 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

'''
rest_client provides exactly one public type called RestClient, which wraps all
REST requests in qumulo.rest.*

For each function qumulo.rest.xxx.yyy(conninfo, credentials, a, b, c),
there will be a method RestClient.xxx.yyy(a, b, c). The conninfo and
credentials parameters are set up in the RestClient constructor, should they be
provided.

Moreover, the return type from these requests is not a (dict, etag) tuple,
but a python object with the fields set to the key, value items from the dict,
along with an etag field. (Nobody is returning an etag field.)
'''

import functools
import types

from qumulo.lib.auth import Credentials

import qumulo.lib.request as request

class ETagStripperIterator(object):
    def __init__(self, iterator, etag_strip_function):
        self.iterator = iterator
        self.etag_strip_function = etag_strip_function

    def __iter__(self):
        return self

    def __reversed__(self):
        return ETagStripperIterator(
            reversed(self.iterator), self.etag_strip_function)

    def __next__(self):
        return self.etag_strip_function(next(self.iterator))

    next = __next__ # python2

def _wrap_rest_request(request_method):
    '''
    Wrap a function that begins with the two parameters conninfo and credentials
    returning a function suitable for use as a method on a rest module class.
    '''
    @functools.wraps(request_method)
    def wrapper(self, *args, **kwargs):
        with_etag = kwargs.pop('with_etag', False)

        # If the user asked for us to include the etag, they will get it;
        # otherwise, it's more useful to just return the decoded JSON response.
        def etag_stripper(response):
            if not (hasattr(response, 'data') and hasattr(response, 'etag')):
                return ETagStripperIterator(response, etag_stripper)

            if with_etag:
                return response
            else:
                return response.data

        try:
            response = request_method(
                self.client.conninfo,
                self.client.credentials,
                *args,
                **kwargs)
        except request.RequestError as e:
            self.client.handle_request_error(e)
            response = request_method(
                self.client.conninfo,
                self.client.credentials,
                *args,
                **kwargs)

        return etag_stripper(response)

    return wrapper

class RestClient(object):
    '''
    Provide access to the entire QEFS REST API surface.

    N.B. The class is partially defined here, then filled out with reflection
         over the qumulo.rest namespace to add properties for each module.
    '''
    Error = request.RequestError

    def __init__(
            self,
            address,
            port,
            credentials=None,
            timeout=None,
            reuse_connection=None):

        self.conninfo = request.Connection(
            address, port, timeout=timeout, reuse=reuse_connection)
        self.client = self  # for request, make this class act like a RestModule
        self.credentials = credentials
        self.timeout = timeout
        self.reuse_connection = reuse_connection

    def clone(self):
        return RestClient(
            self.conninfo.host,
            self.conninfo.port,
            self.credentials,
            self.timeout)

    @property
    def port(self):
        return self.conninfo.port

    @property
    def chunked(self):
        return self.conninfo.chunked

    @chunked.setter
    def chunked(self, new_value):
        self.conninfo.chunked = new_value

    @property
    def chunk_size(self):
        return self.conninfo.chunk_size

    @chunk_size.setter
    def chunk_size(self, new_value):
        self.conninfo.chunk_size = new_value

    # Use the real wrapper for the base rest_request
    request = _wrap_rest_request(request.rest_request)

    def handle_request_error(self, _request_error):
        #pylint: disable=misplaced-bare-raise
        raise

    def _set_credentials_from_login_response_data(self, login_response_data):
        self.credentials = Credentials.from_login_response(login_response_data)

    def login(self, username, password):
        response_data = self.auth.login(username, password)
        self._set_credentials_from_login_response_data(response_data)
        return self.credentials

    # A lot of HTTPExceptions cause the connection always fail after being
    # receiving the error over it. Create a new connection if this occurs.
    def refresh_connection(self):
        address = self.conninfo.host
        port = self.conninfo.port
        chunked = self.conninfo.chunked
        chunk_size = self.conninfo.chunk_size
        self.conninfo = request.Connection(address, port, chunked, chunk_size,
            timeout=self.timeout)

def _wrap_rest_module(module, existing_property):
    '''
    Given a module, return a property that mimics it.

    This is tricky because we want to wrap each function in the module, and bind
    its first two arguments with fields in the RestClient object. However, we
    don't have the RestClient object instantiated at this point. So, what we
    return is the ability to create the mimicking class, instead of the class
    itself.
    '''
    class RestModule(object):
        __doc__ = module.__doc__

        def __init__(self, client):
            self.client = client

    if existing_property is None:
        wrapped_class = RestModule
    else:
        wrapped_class = existing_property.fget  # get the existing class

    for name, method in vars(module).items():
        if callable(method) and getattr(method, 'request', False):
            setattr(wrapped_class, name, _wrap_rest_request(method))

    return property(wrapped_class)

def _wrap_all_rest_modules(root, cls):
    '''
    Wrap all rest modules loaded in the provided root module, adding a property
    to the RestClient type for each. If a property already exists, it will not
    be overwritten.

    This allows the private modules to dominate the public ones.
    '''
    for name, module in vars(root).items():
        if isinstance(module, types.ModuleType):
            existing_property = getattr(cls, name, None)
            setattr(cls, name, _wrap_rest_module(module, existing_property))


# Pull in all the REST client modules and methods
import qumulo.rest

# Wrap them all.
_wrap_all_rest_modules(qumulo.rest, RestClient)

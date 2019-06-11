# -*- coding: utf-8 -*-

import json
import requests
import urllib
import webbrowser
import logging_helper
from apiutil.json_api import JsonApiRequestResponse
from classutils.observer import ObservableObserverMixIn
from timingsutil import Timeout, ONE_SECOND
from networkutil.web_socket import WebSocketSubscriber
from .._exceptions import APIError, APIMissing, APIUnresponsive

logging = logging_helper.setup_logging()


class BaseSupportApi(ObservableObserverMixIn):

    # PATH must be defined in subclass for versioned api's
    PATH = u''

    ALLOW_REDIRECTS = True  # Note: does not apply to websockets currently!

    # Request timeout settings
    TIMEOUT_MULTIPLIER = 1
    LONG_TIMEOUT = 1
    MEDIUM_TIMEOUT = 0.5
    SHORT_TIMEOUT = 0.1
    # Note minimum timeout will be SHORT_TIMEOUT * TIMEOUT_MULTIPLIER.

    # Custom Exceptions (DO NOT OVERRIDE exceptions here, these will be set by api_support_layer)
    API_ERROR = APIError
    API_MISSING = APIMissing
    API_UNRESPONSIVE = APIUnresponsive

    # Response object class that takes request & response as parameters
    API_RESPONSE_OBJECT = JsonApiRequestResponse

    def __init__(self,
                 api_root,
                 cache,
                 cache_host,
                 *args,
                 **kwargs):  # args & kwargs provided here to sink any extra params that get passed to the api

        self._api_root = api_root

        self.last_request = None
        self._websockets = {}
        self._ws_notifications = {}

        # Setup cache
        self._cache = cache
        self._cache_host = cache_host

    @property
    def api_path(self):
        api_parts = [self._api_root]

        if self.PATH:
            api_parts.append(self.PATH)

        return u'/'.join(api_parts)

    @staticmethod
    def merge_request_parameters(quote=False,
                                 parameters=None,
                                 **additional_parameters):
        """
        Helper function to requesters to easily combine a
        dictionary of parameters and additional parameters
        supplied as keyword values

        Note: If the request itself takes a parameter called
              'parameters', it must be supplied inside
              a dict.
              i.e. parameters={u'parameters': <parameters values')

        :param quote: bool : Set to True to use urllib.quote
                              default False allows requests to
                              use the standard quote_plus encoding
        :param parameters: dict
        :param additional_parameters:
        :return: dict
        """
        merged_params = {}

        if parameters:
            merged_params.update(parameters)

        for param_name, param_value in iter(additional_parameters.items()):
            if param_name in merged_params:
                try:
                    merged_params[param_name].append(param_value)
                except AttributeError:
                    merged_params[param_name] = [merged_params[param_name],
                                                 param_value]
            else:
                merged_params[param_name] = param_value

        if not quote or not merged_params:
            return merged_params

        param_parts = []
        for param_name, param_value in iter(merged_params.items()):
            if isinstance(param_value, (list, tuple)):
                for field in param_value:
                    if param_value is None:
                        continue
                    try:
                        param_parts.append(u'{n}={v}'
                                           .format(n=param_name,
                                                   v=urllib.quote(field)))
                    except AttributeError:
                        param_parts.append(u'{n}={v}'
                                           .format(n=param_name,
                                                   v=field))
            elif param_value is None:
                continue
            else:
                try:
                    param_parts.append(u'{n}={v}'
                                       .format(n=param_name,
                                               v=urllib.quote(param_value)))
                except AttributeError:
                    param_parts.append(u'{n}={v}'
                                       .format(n=param_name,
                                               v=param_value))

        return u'&'.join(param_parts)

    def make_api_request(self,
                         method,
                         request,
                         data=None,
                         json_data=None,
                         timeout=None,
                         in_browser=False,
                         request_params=None,
                         headers=None,
                         auth=None,
                         **_):

        request = u'http://{api}/{request}'.format(api=self.api_path,
                                                   request=request)

        self.last_request = request

        logging.debug(u'{method}: {request}'.format(method=method,
                                                    request=request))

        if in_browser:
            webbrowser.open_new_tab(request)

        # Setup headers with default content type
        default_headers = {u'content-type': u'text/plain; charset=utf-8'}

        # Add request headers
        if headers:
            default_headers.update(headers)

        params = dict(method=method.upper(),
                      url=request,
                      headers=default_headers,
                      allow_redirects=self.ALLOW_REDIRECTS)

        if request_params is not None:
            params[u'params'] = request_params

        if timeout is not None:
            params[u'timeout'] = timeout * self.TIMEOUT_MULTIPLIER

        if timeout is None or params[u'timeout'] < self.SHORT_TIMEOUT:
            params[u'timeout'] = self.SHORT_TIMEOUT * self.TIMEOUT_MULTIPLIER

        if data is not None:
            try:
                # TODO: this try block should be removed but has been put in to ensure compatibility for now!
                params[u'data'] = json.dumps(data)
                params[u'headers'].update({u'content-type': u'application/json',
                                           u'Accept': u'text/plain'})

            except Exception:
                # Going forward this will be the correct way if you want to pass json use the json_data param!
                params[u'data'] = data

        if json_data is not None:
            params[u'json'] = json_data
            params[u'headers'].update({u'content-type': u'application/json'})

        if auth is not None:
            params['auth'] = auth

        try:
            logging_helper.LogLines(level=logging_helper.DEBUG,
                                    lines=[u'{method} parameters:'.format(method=method.upper()),
                                           params])

            response = requests.request(**params)
            response.encoding = u'utf-8'

        except (requests.ConnectionError, requests.exceptions.ReadTimeout) as err:
            logging.exception(err)
            raise self.API_UNRESPONSIVE(u'{r} - {e}'.format(r=request,
                                                            e=err))

        logging.debug(u'Response Code: {rc}'.format(rc=response.status_code))

        if (200 > int(response.status_code)) or (int(response.status_code) >= 300):
            raise self.API_ERROR(u'API Request Failed: {req} returned HTTP {code}'.format(code=response.status_code,
                                                                                          req=request),
                                 response=response)

        return self.API_RESPONSE_OBJECT(request=request,
                                        response=response)

    def make_request(self,
                     method,
                     request,
                     cache=False,
                     **params):

        if cache:
            return self._cache.fetch(api=self,
                                     cache_host=self._cache_host,
                                     method=method,
                                     request=request,
                                     **params)

        else:
            return self.make_api_request(method=method,
                                         request=request,
                                         **params)

    def get(self,
            # request,
            # timeout=None,
            # in_browser=False
            *args,
            **kwargs):
        return self.make_request(method=u'GET',
                                 *args,
                                 **kwargs)

    def post(self,
             # request,
             # data=None,
             # timeout=None
             *args,
             **kwargs):
        return self.make_request(method=u'POST',
                                 *args,
                                 **kwargs)

    def put(self,
            # request,
            # data=None,
            # timeout=None
            *args,
            **kwargs):
        return self.make_request(method=u'PUT',
                                 *args,
                                 **kwargs)

    def delete(self,
               # request,
               # data=None,
               # timeout=None
               *args,
               **kwargs):
        return self.make_request(method=u'DELETE',
                                 *args,
                                 **kwargs)

    def ws_request(self,
                   request,
                   auto_close=False,
                   close_ws=False,
                   register_observer=None,
                   unregister_observer=None):

        """ Setup WebSocket.

        :param request:                    The WS path for the request.
        :param auto_close:                 Auto close the WS when there are no more observers.
        :param close_ws:                   Set True to close an existing WS.
        :param register_observer:          An observer object to be registered to the websocket.
        :param unregister_observer:        An observer object to be unregistered from the websocket.
        :return:                           Nothing if closing or unregistering otherwise the last_message.
        """

        logging.debug(self._websockets)

        # If provided unregister the passed observer from WS notifications
        if unregister_observer and request in self._websockets:
            self._websockets[request].unregister_observer(unregister_observer)

            if self._no_external_references(request) and auto_close:
                logging.debug(u'Closing WS ({url}) as there are no remaining references'.format(url=request))
                self.close_ws(ws=request)

        # Close the WS if required
        if close_ws and request in self._websockets:
            self.close_ws(ws=request)

        # If unregister or close_ws is set then just return
        if close_ws or unregister_observer:
            return

        # If we are not unregistering or closing then we can continue

        # Setup full request url
        request_url = (u'ws://{api}/{request}'.format(api=self.api_path,
                                                      request=request))
        logging.debug(u'Request: {r}'.format(r=request_url))

        # Update last request.
        # So long we are not closing or unregistering we should always
        # do this otherwise repeat calls will not be taken into account.
        self.last_request = request_url

        if request not in self._websockets:
            # Create websocket if not already created
            self._websockets[request] = WebSocketSubscriber(request=request_url,
                                                            name=request)

            # Register this API to receive WS notifications
            self._websockets[request].register_observer(self)

            # If provided register the passed observer to receive WS notifications
            if register_observer:
                self._websockets[request].register_observer(register_observer)

            # Wait very short time for last_message to be updated
            timer = Timeout(ONE_SECOND * 3)

            while not timer.expired and self._websockets[request].last_message is None:
                pass

        last_message = self._websockets[request].last_message

        if self._no_external_references(request) and auto_close:
            logging.debug(u'Closing WS ({url}) as there are no remaining references'.format(url=request_url))
            self.close_ws(ws=request)

        # Return last message on the websocket to match existing functionality
        return last_message

    def notification(self,
                     **kwargs):

        # If we have ws_name, lookup correct notification method and send notification
        if WebSocketSubscriber.WS_NAME in kwargs:
            request = kwargs[WebSocketSubscriber.WS_NAME]

            # Send notification to request specific notification method
            if request in self._ws_notifications:
                for notify_function in self._ws_notifications[request]:
                    notify_function(**kwargs)

        # If websocket closes, unregister observation of websocket
        if WebSocketSubscriber.WS_STATE in kwargs:
            if kwargs[WebSocketSubscriber.WS_STATE] == WebSocketSubscriber.WS_CLOSED:
                kwargs[self.NOTIFIER_KEY].unregister_observer(self)

                if kwargs[self.NOTIFIER_KEY].name in self._ws_notifications:
                    del self._ws_notifications[kwargs[self.NOTIFIER_KEY].name]

    def _reference_count(self,
                         request):
        return len(self._ws_notifications.get(request, [])) + self._websockets[request].observer_count

    def _no_external_references(self,
                                request):
        return self._reference_count(request) == 1 and self._websockets[request].observed_by(self)

    def close_ws(self,
                 ws):
        self._websockets[ws].close()
        del self._websockets[ws]

    def close(self):
        for ws in list(self._websockets.keys()):
            self.close_ws(ws=ws)

    def __del__(self):
        self.close()

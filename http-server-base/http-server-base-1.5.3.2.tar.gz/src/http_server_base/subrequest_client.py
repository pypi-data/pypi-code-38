import json
import random
import string
from asyncio import sleep
from json import JSONDecodeError
from math import log2
from typing import Union, Callable, Optional, Tuple, Any, Dict, Collection, List

from tornado.httpclient import HTTPResponse, HTTPRequest, AsyncHTTPClient
from tornado.httputil import HTTPHeaders, HTTPServerRequest
from tornado.web import RequestHandler, HTTPError

from . import RequestLoggerClient, ErrorMatcher
from http_server_base.tools import revrange, ConfigLoader
from http_server_base.tools import RequestLogger, SubrequestFailedErrorCodes
from http_server_base.tools import JsonSerializable
from http_server_base.tools import SubrequestFailedError
from http_server_base.tools import HttpSubrequest, HttpSubrequestResponse

class SubrequestClient(RequestLoggerClient, ErrorMatcher):
    
    logger: RequestLogger
    _async_http_client: AsyncHTTPClient = None
    request_id_header_name: str = 'X-Request-Id'
    
    @property
    def async_http_client(self) -> AsyncHTTPClient:
        if (self._async_http_client is None):
            self._async_http_client = AsyncHTTPClient()
        
        return self._async_http_client
    
    #region Fetching
    async def _fetch__form_request(self, request: Union[str, HTTPRequest], *, add_request_id: bool, **kwargs) -> HttpSubrequest:
        if (not isinstance(request, HttpSubrequest)):
            request = HttpSubrequest(url=request, request_id=self.generate_request_id(), parent_request_id=getattr(self, 'request_id', None), base_logger=self.logger, **kwargs)
        
        if (add_request_id):
            await self._fetch__form_request__add_request_id(request)
        
        return request
    async def _fetch__form_request__add_request_id(self, request: HttpSubrequest):
        if (not isinstance(request.headers, HTTPHeaders)):
            request.headers = HTTPHeaders(request.headers)
        request.headers.add(self.request_id_header_name, request.request_id)
    async def _fetch__retries_logic(self, request: HttpSubrequest, *, attempts, exponential_retries, intercept_connection_errors, retry_timeout):
        response = None
        _to = retry_timeout
        for i in revrange(attempts):
            _last_attempt = i == 0
            _intercept_connection_errors = intercept_connection_errors if (_last_attempt) else False
            
            try:
                response = await self._fetch__fetch_request(request, intercept_connection_errors=_intercept_connection_errors)
            except Exception as e:
                if (_last_attempt):
                    raise
                else:
                    request.logger.warning(f"Subrequest failed (reason: {e}), retrying in {_to}ms...")
                    await sleep(_to / 1000)
                    if (exponential_retries):
                        _to *= 2
            else:
                break
        return response
    async def _fetch__fetch_request(self, request: HttpSubrequest, intercept_connection_errors: bool) -> HttpSubrequestResponse:
        request.logger.debug(f"Request: {request.method} {request.url}")
        _client = self.async_http_client
        
        future = _client.fetch(request, raise_error=False)
        try:
            response = await future
        except Exception as e:
            if (intercept_connection_errors):
                response = self.match_error(request, e)
            else:
                raise
        
        response = HttpSubrequestResponse(response)
        request.logger.debug(f"Response: {response.request.method} {response.request.url}; Code: {response.code}; Content-length: {len(response.body or '')}")
        self.dump_response(response, request_name=f"Subrequest {request.request_id}", logger=request.logger, prefix='resp')
        return response
    async def _fetch__check_response(self, response: HttpSubrequestResponse, *, expected_codes: Collection[int], expected_content_type: Optional[str]):
        response.request.logger.trace("Checking response...")
        alert = None
        
        if (alert is None and response.code not in expected_codes):
            alert = dict(expected_codes=expected_codes)
        
        if (alert is None and expected_content_type):
            if ('Content-Type' not in response.headers):
                alert = dict(message="Missing 'Content-Type' header in the response", expected_mime_type=expected_content_type)
            elif (expected_content_type not in { _h.partition(';')[0] for _h in response.headers.get_list('Content-Type') }):
                alert = dict(message=f"Missing '{expected_content_type}' in 'Content-Type' headers of the response ({','.join(response.headers.get_list('Content-Type'))})", expected_mime_type=expected_content_type)
        
        if (alert is not None):
            exception = SubrequestFailedError(response, **alert)
            response.request.logger.warning(str(exception))
            if (response.error and not isinstance(response.error, HTTPError)):
                response.request.logger.warning(f"Base error: {str(response.error)}")
            raise exception
    async def fetch \
    (
        self,
        request: Union[str, HTTPRequest],
        *,
        
        # Retries
        attempts: int = None,
        retry_timeout: int = None,
        retry_max_time: int = None,
        exponential_retries: bool = None,
        
        # Response Validation
        intercept_connection_errors: bool = True,
        raise_error: bool = True,
        expected_codes: Union[int, Collection[int]] = 200,
        expected_content_type: str = None,
        
        # Options
        configuration_prefix: Union[str, Tuple[str, str]] = 'HTTP/',
        add_request_id: bool = True,
        **kwargs,
    ) -> HttpSubrequestResponse:
        """
        Fetches the specified request and asynchronously returns response.
        Minorly logs both request and response objects.
        Response is the instance of HttpSubrequestResponse (child of HTTPResponse).
        
        If the `intercept_connection_errors` option is set, the default errors will be intercepted by the client.
        If the `raise_error` option is set, the request status code is checked to be one of `expected_codes` parameter.
        If the `raise_error` option is set, the mime type of response will be checked to have value of `expected_content_type` parameter.
        If the `add_request_id` option is set, the request object will have appropriate.
        All other parameters are nested from the original `tornado.httpclient.AsyncHTTPClient.fetch()`.
        
        Retries
        :param attempts: int
        A maximum number of attempts for a request.
        Default: calculated from retry_max_time, or from configuration (parameter 'retries/maxAttempts'), or 1
        :param retry_timeout: int
        An initial wait time (in ms) before the first retry.
        Default: from configuration (parameter 'retries/timeout'), or 100ms
        :param retry_max_time: int
        Max total wait time (in ms) for the request retries.
        If both attempts and retry_max_time are present, attempts is prioritized.
        Default: calculated from attempts.
        :param exponential_retries: bool
        If set, each of the next retries wait intervals will be twice as longer than previous.
        Default: from configuration (parameter 'retries/exponentialRetries'), or True
        
        Response validation:
        :param intercept_connection_errors:  bool
        :param request: str or HTTPRequest
        :param raise_error: bool
        :param expected_codes: int or Collection[int]
        :param expected_content_type: str or None
        
        Options:
        :param configuration_prefix: str, or tuple [str, str]
        A prefix for the subrequests configuration.
        If tuple is given, the second argument is counted as config name.
        Default: 'HTTP/'
        :param add_request_id: bool
        If True, a request id will be added to the subrequest
        Default: True
        
        :raises: SubrequestFailedError
        :raises: ValueError
        :returns: HttpSubrequestResponse
        """
        
        if (isinstance(configuration_prefix, tuple)):
            configuration_prefix, config_name = configuration_prefix
        else:
            config_name = 'main'
        
        request = await self._fetch__form_request(request, add_request_id=add_request_id, **kwargs)
        
        if (retry_timeout is None):
            retry_timeout = ConfigLoader.get_from_config(f'{configuration_prefix}retries/timeout', config_name, default=100)
        if (not isinstance(retry_timeout, (int, float))):
            raise ValueError(f"Retry timeout should be int or float, not {type(retry_timeout)}.")
        elif (retry_timeout < 0):
            raise ValueError(f"Retry timeout should not be negative, got {retry_timeout}.")
        
        if (exponential_retries is None):
            exponential_retries = ConfigLoader.get_from_config(f'{configuration_prefix}retries/exponentialRetries', config_name, default=True)
        
        if (attempts is None and retry_max_time is None):
            attempts = ConfigLoader.get_from_config(f'{configuration_prefix}retries/maxAttempts', config_name, default=1)
        elif (attempts is None):
            attempts = int(retry_max_time / retry_timeout) + 1
            if (exponential_retries):
                attempts = log2(attempts) + 1
            attempts = int(attempts)
        if (not isinstance(attempts, (int, float))):
            raise ValueError(f"Attempts should be int, not {type(attempts)}.")
        elif (attempts < 1):
            raise ValueError(f"Attempts should be 1 or higher, not {attempts}.")
        
        response = await self._fetch__retries_logic(request, attempts=attempts, exponential_retries=exponential_retries, intercept_connection_errors=intercept_connection_errors, retry_timeout=retry_timeout)
        
        if (raise_error):
            if (expected_codes is None):
                expected_codes = [ 200 ]
            elif (isinstance(expected_codes, int)):
                expected_codes = [ expected_codes ]
            await self._fetch__check_response(response, expected_codes=expected_codes, expected_content_type=expected_content_type)
        
        return response
    async def fetch_json(self, request: Union[str, HTTPRequest], *, check_content_type_header: bool = True, json_load_options: Dict[str, Any] = None, **kwargs) -> Tuple[HttpSubrequestResponse, JsonSerializable]:
        """
        Fetches the specified request for the JSON data and asynchronously returns both response and loaded JSON object.
        Minorly logs both request and response objects.
        Response is the instance of HttpSubrequestResponse (child of HTTPResponse).
        
        The `raise_error` is always overridden to True.
        If the `check_content_type_header` option is set, the request headers will be checked to have 'Content-Type: application/json'.
        The `json_load_options` parameter is expanded to keyword-params of the json.loads() method.
        All other parameters are nested from the `fetch()` method above.
        
        :param request: str or HTTPRequest
        :param check_content_type_header: bool
        :param json_load_options: kwargs 
        
        :raises: SubrequestFailedError
        :returns: Tuple[HttpSubrequestResponse, JsonSerializable]
        """
        
        base_error: Optional[SubrequestFailedError] = None
        kwargs.pop('raise_error', None)
        try:
            response = await self.fetch(request, raise_error=True, expected_content_type='application/json' if (check_content_type_header) else None, **kwargs)
        except SubrequestFailedError as e:
            base_error = e
            response = base_error.response
        
        alert = None
        resp_data = None
        resp_json = None
        
        if (response.body is None):
            alert = dict(message="Server responded empty body while JSON was expected to be", error_code=SubrequestFailedErrorCodes.InvalidResponseBody)
        
        if (alert is None and (not base_error or base_error.error_code != SubrequestFailedErrorCodes.MimeTypeMismatch)):
            if (json_load_options is None):
                json_load_options = dict()
            
            try:
                resp_data = response.body.decode()
                resp_json: Dict[str, Any] = json.loads(resp_data, **json_load_options)
            except JSONDecodeError:
                alert = dict(message=f"Cannot decode JSON from the response: '{resp_data}'", server_response=str(resp_data), error_code=SubrequestFailedErrorCodes.InvalidResponseBody)
            except Exception as e:
                alert = dict(code=500, error="Unknown Error", message=f"Unknown error: {e}")
        
        if (alert is None and base_error):
            if (resp_json is not None):
                alert = dict(message=resp_json.get('reason') or resp_json.get('error') or resp_json.get('message'), server_response=resp_json, error_code=SubrequestFailedErrorCodes.InvalidResponseBody)
            else:
                alert = dict(server_response=response.body.decode())
        
        if (alert is not None):
            raise SubrequestFailedError(response, base_error=base_error, **alert)
        
        return response, resp_json
    async def fetch_binary_data(self, request: Union[str, HTTPRequest], **kwargs) -> Tuple[HttpSubrequestResponse, bytes]:
        """
        Fetches the specified request for the binary data and asynchronously returns both response and loaded bytes.
        Minorly logs both request and response objects.
        Response is the instance of HttpSubrequestResponse (child of HTTPResponse).
        
        The `raise_error` is always overridden to True.
        All other parameters are nested from the `fetch()` method above.
        
        :param request: str or HTTPRequest
        
        :raises: SubrequestFailedError
        :returns: Tuple[HttpSubrequestResponse, bytes]
        """
        
        base_error: Optional[SubrequestFailedError] = None
        kwargs.pop('raise_error', None)
        try:
            response = await self.fetch(request, raise_error=True, **kwargs)
        except SubrequestFailedError as e:
            base_error = e
            response = base_error.response
        
        alert = None
        resp_data = None
        
        if (response.body is None):
            alert = dict(message="Server responded empty body", error_code=SubrequestFailedErrorCodes.InvalidResponseBody)
        if (not alert and base_error):
            try:
                resp_data = response.body.decode()
                resp_json: Dict[str, Any] = json.loads(resp_data)
            except JSONDecodeError:
                alert = dict(code=503, message=f"Unexpected error code: {response.code}, response is not JSON: '{resp_data}'", server_response=str(resp_data))
            except Exception as e:
                alert = dict(code=500, error="Unknown Error", message=f"Unknown error: {e}")
            else:
                alert = dict(message=resp_json.get('reason') or resp_json.get('error') or resp_json.get('message'), server_response=resp_json)
        
        if (alert):
            raise SubrequestFailedError(response, base_error=base_error, **alert)
        
        return response, response.body
    #endregion
    
    @classmethod
    def generate_random_string(cls, N):
        return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=N))
    def generate_request_id(self) -> str:
        return "{0:x}".format(random.randint(0x10000000, 0xffffffff))

#    Boilerplate commons for django based web api application.
#    Copyright (C) 2017 Logicify
#    The MIT License (MIT)
#    
#    Permission is hereby granted, free of charge, to any person obtaining
#    a copy of this software and associated documentation files
#    (the "Software"), to deal in the Software without restriction,
#    including without limitation the rights to use, copy, modify, merge,
#    publish, distribute, sublicense, and/or sell copies of the Software,
#    and to permit persons to whom the Software is furnished to do so,
#    subject to the following conditions:
#    
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#    
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import collections
import logging
import sys
from json import JSONEncoder
from typing import Union
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.http import HttpResponse
from rest_framework import status as HttpStatus
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, MethodNotAllowed
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.status import is_client_error, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .dto import BaseDto, ApiResponseDto
from .error import InvalidPaginationOptionsError, InvalidInputDataError, ErrorCode

DtoOrMessageOrErrorCode = Union[BaseDto, str, ErrorCode]
Payload = Union[collections.Iterable, BaseDto, None]

logger = logging.getLogger(__name__)


class ApiResponse(Response):
    __SECRET = object()

    def __init__(self, payload: Payload = None, status=None, template_name=None, headers=None, exception=False,
                 content_type='application/json',
                 secret=None) -> None:
        if secret != self.__SECRET:
            raise ValueError(
                "Using constructor of the ApiResponse is not allowed, please "
                "use static methods instead. See .success()")

        assert payload is None \
               or isinstance(payload, collections.Iterable) \
               or isinstance(payload, BaseDto), "payload should be subclass of ApiResponse"
        super().__init__(None, status, template_name, headers, exception, content_type)
        api_response_dto = ApiResponseDto(payload)
        self.data = api_response_dto

    @classmethod
    def __update_response_for_error(cls, response, dto_or_error_message: DtoOrMessageOrErrorCode, error_code,
                                    default_message):
        if isinstance(dto_or_error_message, ErrorCode):
            error_code = dto_or_error_message.error_code
            dto_or_error_message = dto_or_error_message.dto_or_error_message
        if isinstance(dto_or_error_message, BaseDto):
            response.data.service.validation_errors = dto_or_error_message.errors
        response.data.service.error_code = error_code if error_code is not None else response.status_code
        response.data.service.error_message = default_message \
            if isinstance(dto_or_error_message, BaseDto) else str(dto_or_error_message)

    @classmethod
    def not_found(cls, dto_or_error_message: DtoOrMessageOrErrorCode, error_code=None):
        return cls.client_error(HttpStatus.HTTP_404_NOT_FOUND, dto_or_error_message, error_code, "Entity not found")

    @classmethod
    def success(cls, payload: [BaseDto, None] = None, status: int = HttpStatus.HTTP_200_OK):
        return ApiResponse(payload, status=status, secret=cls.__SECRET)

    @classmethod
    def not_authenticated(cls, *args):
        response = ApiResponse(None, status=HttpStatus.HTTP_401_UNAUTHORIZED, secret=cls.__SECRET)
        if len(args) > 0:
            message = args[0]
        else:
            message = "Unauthorized"
        response.data.service.error_message = message
        return response

    @classmethod
    def bad_request(cls, dto_or_error_message: Union[BaseDto, str], error_code: int = None):
        return cls.client_error(
            HTTP_400_BAD_REQUEST,
            dto_or_error_message,
            error_code,
            "Bad request. Check service.validation_errors for details"
        )

    @classmethod
    def client_error(cls, status_code: int, dto_or_error_message: DtoOrMessageOrErrorCode = None,
                     error_code: int = None, default_message: str = None):
        assert is_client_error(status_code)
        response = ApiResponse(None, status=status_code, secret=cls.__SECRET)
        cls.__update_response_for_error(
            response,
            dto_or_error_message=dto_or_error_message,
            error_code=error_code,
            default_message=default_message
        )
        return response

    @classmethod
    def internal_server_error(cls, exception: Exception = None):
        response = ApiResponse(None, status=HttpStatus.HTTP_500_INTERNAL_SERVER_ERROR, secret=cls.__SECRET)
        response.data.service.error_code = HttpStatus.HTTP_500_INTERNAL_SERVER_ERROR
        return response


class JsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseDto):
            return o.to_dict()
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request: HttpRequest):
        pass


class JsonRenderer(JSONRenderer):
    encoder_class = JsonEncoder
    media_type = 'application/json'
    format = 'json'
    ensure_ascii = not api_settings.UNICODE_JSON
    compact = api_settings.COMPACT_JSON

    def get_indent(self, accepted_media_type, renderer_context: dict):
        return None if self.compact else 4

    def render(self, api_response: ApiResponseDto, accepted_media_type=None, renderer_context=None):
        assert isinstance(api_response, ApiResponseDto), "api_response should be an instance of ApiResponseDto"
        return super().render(api_response, accepted_media_type, renderer_context)


class BaseController(APIView):
    renderer_classes = [JsonRenderer]
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_int(self, str_value, field_name=None) -> int:
        try:
            return int(str_value)
        except ValueError:
            raise InvalidInputDataError('Invalid {} value. Should be integer.'.format(field_name), str_value)

    def parse_int_pk(self, str_value, field_name=None) -> int:
        pk = self.parse_int(str_value)
        if pk <= 0:
            raise InvalidInputDataError('Invalid {} value. Should be positive integer'.format(field_name), str_value)
        return pk

    def parse_bool_value(self, str_value, field_name=None) -> bool:
        try:
            return str_value.lower() not in ['false', 'no', '1', 'False']
        except ValueError:
            raise InvalidInputDataError('Invalid {} value. Should be boolean'.format(field_name), str_value)

    def get_bool_param_from_url(self, request, param):
        create_node = True
        if request.query_params.get(param) is not None:
            create_node = self.parse_bool_value(request.query_params[param], param)
        return create_node

    def get_string_param_from_url(self, request, param):
        if request.query_params.get(param) is not None:
            return request.query_params[param]


class BasicAuthController(BaseController):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def exception_handler(exc: Exception, context):
    logger.warning("Incoming request processing was terminated due to handled exception:", exc_info=exc)
    if isinstance(exc, InvalidPaginationOptionsError):
        return ApiResponse.bad_request('Bad limit and/or offset')
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return ApiResponse.not_authenticated()
    if isinstance(exc, ObjectDoesNotExist):
        return ApiResponse.not_found(exc)
    if isinstance(exc, InvalidInputDataError):
        return ApiResponse.bad_request(str(exc))
    if isinstance(exc, MethodNotAllowed):
        return ApiResponse.client_error(HttpStatus.HTTP_405_METHOD_NOT_ALLOWED, ErrorCode(None, 'Method Not Allowed'))
    logger.exception(str(exc))
    return ApiResponse.internal_server_error(exc)


def __set_response_attributes(response: HttpResponse):
    response.accepted_renderer = JsonRenderer()
    response.accepted_media_type = JsonRenderer.media_type
    response.renderer_context = {"data": None}
    return response.render()


def error_500_handler(request: HttpRequest):
    exec_info = sys.exc_info()
    logger.error('Internal Server Error: %s.', str(exec_info[1]),
                 exc_info=exec_info,
                 extra={
                     'status_code': 500,
                     'rs.path': request.path,
                     'request': request
                 })
    return __set_response_attributes(ApiResponse.internal_server_error(exec_info[1]))


def error_404_handler(request: HttpRequest, exception: Exception):
    logger.warning('Not Found: %s. %s', request.path, str(exception),
                   extra={
                       'status_code': 404,
                       'path': request.path,
                       'request': request
                   })
    return __set_response_attributes(ApiResponse.not_found(""))

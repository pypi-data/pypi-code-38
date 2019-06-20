# -*- coding: utf-8 -*-
from congo.conf import settings
from django.utils.deprecation import MiddlewareMixin
import decimal
import os
from congo.utils.text import strip_comments, strip_emptylines, strip_spaces
from congo.utils.files import is_static_path

class CommonMiddleware(MiddlewareMixin):
    def process_request(self, request):
        admin_path = settings.CONGO_ADMIN_PATH
        if request.path.startswith(admin_path):
            request.is_admin_backend = True
        else:
            request.is_admin_backend = False

class DecimalRoundingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        decimal_context = decimal.getcontext()
        decimal_context.rounding = decimal.ROUND_HALF_UP
#        decimal_context.rounding = decimal.ROUND_HALF_EVEN
        return None

class TextImageMiddleware(MiddlewareMixin):
    """
    Middleware wkleja zawartość pliku txt zdefiniowanego w CONGO_TEXT_IMAGE_PATH 
    na górę każdego wysyłanego response text/html.
    """

    def process_response(self, request, response):
        file_path = settings.CONGO_TEXT_IMAGE_PATH
        if os.path.exists(file_path) and 'text/html' in response['Content-Type'] and response.status_code == 200:
            with open(file_path, 'r') as myfile:
                text = myfile.read()
                response.content = text + response.content
                return response
        else:
            return response

class SpacelessMiddleware(MiddlewareMixin):
    """
    Middleware ucina wszystkie białe znaki z miejsc, w których są one nie potrzebne zmniejszając tym samym
    wielkość response'a.
    """
    def process_response(self, request, response):
        if settings.LOCAL and is_static_path(request):
            return response

        if any(pattern.search(request.path) for pattern in settings.CONGO_IGNORABLE_SPACELESS_URLS):
            return response

        if 'text/html' in response['Content-Type'] and response.status_code == 200 and settings.CONGO_SPACELESS_ENABLED:

            response.content = strip_comments(response.content)
            # response.content = strip_lines(response.content)
            response.content = strip_emptylines(response.content)
            response.content = strip_spaces(response.content)
        return response


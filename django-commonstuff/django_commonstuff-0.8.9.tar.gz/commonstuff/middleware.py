# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.utils.deprecation import MiddlewareMixin


class AddXDomainHeaderMiddleware(MiddlewareMixin):
    """Нужно, чтобы правильно работало кеширование на разных доменах

    Добавить этот класс перед CommonMiddleware
    в настройках MIDDLEWARE.

    При вызове декоратора @cache_page также добавить
    from django.views.decorators.vary import vary_on_headers
    @vary_on_headers('X-Domain')
    """
    def process_request(self, request):
        request.META['HTTP_X_DOMAIN'] = request.get_host()

    def process_response(self, request, response):
        try:
            x_domain = request.META['HTTP_X_DOMAIN']
        except KeyError:
            x_domain = request.get_host()
        response['X-Domain'] = x_domain
        return response


class AddXFlavourHeaderMiddleware(MiddlewareMixin):
    """Нужно для провайдерских прокси, чтобы не убить их кеширование
    
    Добавляет заголовок X-Flavour в response, чтобы разные прокси различали
    мобильную и десктопную версии сайта, отдающиеся по 1 url'у, но с разным
    кодом. Этого функционала в django_mobile нет.
    
    Мы только добавляем заголовок в response. Информация в request и response.vary
    пишется встроенным django_mobile.cache.middleware.CacheFlavourMiddleware
    
    Добавлять в MIDDLEWARE после django_mobile.cache.middleware.CacheFlavourMiddleware
    """
    def process_response(self, request, response):
        try: # detected
            flavour = request.META['HTTP_X_FLAVOUR']
        except KeyError: # default one
            flavour = 'full'
        response['X-Flavour'] = flavour
        return response


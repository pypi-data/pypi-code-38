import datetime
import re

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.translation import LANGUAGE_SESSION_KEY

from saleboxdjango.lib.basket import SaleboxBasket


class SaleboxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # kick out inactive (i.e. banned) users
        if request.user.is_authenticated and not request.user.is_active:
            request.session['saleboxbasket'] = None
            logout(request)
            return redirect('/')

        # init shopping basket
        sb = SaleboxBasket(request)

        # set product_list_order
        request.session.setdefault(
            'product_list_order',
            settings.SALEBOX['SESSION']['DEFAULT_PRODUCT_LIST_ORDER']
        )
        if 'product_list_order' in request.GET:
            valid_orders = [
                'bestseller_low_to_high',
                'bestseller_high_to_low',
                'price_low_to_high',
                'price_high_to_low',
                'rating_high_to_low',
                'rating_low_to_high',
            ]
            if request.GET['product_list_order'] in valid_orders:
                request.session['product_list_order'] = request.GET['product_list_order']
                if re.search(r'\d+\/$', request.path):
                    return redirect(re.sub(r'\d+\/$', '', request.path))

        # create response
        response = self.get_response(request)
        if sb.get_cookie_action(request) == 'add':
            response.set_cookie(
                'psessionid',
                value=request.session.session_key,
                max_age=60 * 60 * 24 * 365
            )
        elif sb.get_cookie_action(request) == 'remove':
            response.delete_cookie('psessionid')
        return response


"""
This middleware sets whatever language is in the URL, e.g. /en/about-us = 'en'
and stores it in the session[LANGUAGE_SESSION_KEY]. This means django
can 'remember' the language of the non-language specific URLs, e.g. /basket/
"""
class SaleboxI18NSessionStoreMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        available_languages = [l[0].lower() for l in settings.LANGUAGES]
        key = getattr(settings, 'LANGUAGE_SESSION_KEY', LANGUAGE_SESSION_KEY)
        prev_language = request.session.get(key, None)
        curr_language = prev_language

        # set a default language if none exists
        if curr_language is None:
            curr_language = available_languages[0]

        # attempt to set the language from the path
        try:
            prefix = request.path.lower().strip('/').split('/')[0]
            if prefix in available_languages:
                curr_language = prefix
        except:
            pass

        # update the session if applicable
        if prev_language != curr_language:
            request.session[key] = curr_language

        # create response
        return self.get_response(request)

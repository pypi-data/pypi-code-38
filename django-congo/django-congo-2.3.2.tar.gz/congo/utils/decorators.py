# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect

def ajax_required(view_func):
    """
    Dekorator który wymaga, aby request był ajaxem.
    """

    def wrapped_view(request, *args, **kwargs):
        if request.is_ajax() or settings.DEBUG:
            return view_func(request, *args, **kwargs)
        else:
            raise SuspiciousOperation
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

def secure_required(view_func):
    """
    Dekorator który wymusza użycie https.
    """

    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    wrapped_view.secure = True
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

def secure_allowed(view_func):
    """
    Dekorator który pozwala na użycie https.
    """

    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    wrapped_view.secure = None
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

def staff_required(view_func):
    """
    Dekorator który odrzuca userów którzy nie są staff (is_staff).
    """

    decorator = user_passes_test(lambda u: u.is_staff)
    return decorator(view_func)

def superuser_required(view_func):
    """
    Dekorator który odrzuca userów którzy nie są superuser (is_superuser).
    """

    decorator = user_passes_test(lambda u: u.is_superuser)
    return decorator(view_func)

def active_required(view_func):
    """
    Dekorator który odrzuca userów którzy nie są aktywni (is_active)
    """

    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.is_active:
                return view_func(request, *args, **kwargs)
            else:
                message = _(u"Twoje konto jest nieaktywne. Aby korzystać ze wszystkich funkcji serwisu, kliknij link w wiadomości otrzymanej podczas rejestracji lub skontaktuj się z obsługą klienta.")
                messages.warning(request, message)
                return HttpResponseRedirect(reverse('accounts_account'))
        else:
            return redirect_to_login(request.build_absolute_uri())
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

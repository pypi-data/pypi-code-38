# -*- coding: utf-8 -*-
from congo.utils.classes import MetaData
from congo.utils.decorators import secure_allowed, staff_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation, PermissionDenied
from django.http.response import HttpResponseRedirect, Http404
from django.template import loader
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _


@secure_allowed
def redirect(request, content_type_id, object_id):
    try:
        obj = ContentType.objects.get_for_id(content_type_id).get_object_for_this_type(id = object_id)
        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
            return HttpResponseRedirect(url)
    except ObjectDoesNotExist:
        pass
    raise Http404()

@secure_allowed
def http_error(request, error_no):
    """
    Generyczny widok wyświetlający strony błędów.
    """

    error_dict = {
        400: {
            'title': _("Niepoprawne zapytanie"),
            'description': _("Niestety Twoje zapytanie wydaje się być niepoprawne i nie może być przetworzone."),
            'http_response': 'django.http.HttpResponseBadRequest',
        },
        401: {
            'title': _("Problem z zabezpieczeniami"),
            'description': _("Wystąpił problem z zabezpieczeniami. Być może dane uwierzytelniające są już nieaktualne. Odśwież stronę i spróbuj ponownie."),
            'http_response': 'congo.utils.http.HttpResponseUnauthorized',
        },
        403: {
            'title': _("Odmowa dostępu"),
            'description': _("Niestety dostęp do miejsca, którego szukasz jest zablokowany."),
            'http_response': 'django.http.HttpResponseForbidden',
        },
        404: {
            'title': _("Strona nie została znaleziona"),
            'description': _("Niestety strona, której szukasz nie została odnaleziona. Prawdopodobnie została usunięta z powodu wygaśnięcia."),
            'http_response': 'django.http.HttpResponseNotFound',
        },
        500: {
            'title': _("Wewnętrzny błąd serwera"),
            'description': _("Wystąpił wewnętrzny błąd serwera. Robimy co w naszej mocy, aby rozwiązać problem. Przepraszamy za wszelkie niedogodności."),
            'http_response': 'django.http.HttpResponseServerError',
        },
        503: {
            'title': _("Serwis jest tymczasowo niedostępny"),
            'description': _("Planowana przebudowa strony jest w toku. Przepraszamy za wszelkie niedogodności i zapraszamy nieco później."),
            'http_response': 'congo.utils.http.HttpResponseServiceUnavailable',
        },
    }

    meta = MetaData(request, error_dict[error_no]['title'])

    context = {
        'meta' : meta,
        'error_no': error_no,
        'description': error_dict[error_no]['description'],
    }

    template = loader.get_template('congo/maintenance/http_error.html')
    HttpResponse = import_string(error_dict[error_no]['http_response'])
    return HttpResponse(template.render(context))


@staff_required
def http_error_test(request, error_no):
    """
    Widok podnosi prawdziwy błąd, aby można był sprawdzić, czy handler Djangowy zadziała i obsłuży go właściwym widokiem.
    """

    if error_no == 400:
        # ustawic w urls:
        # handler400 = 'congo.maintenance.views.bad_request'
        raise SuspiciousOperation("Testujemy błędy HTTP...")
    elif error_no == 403:
        # ustawic w urls:
        # handler403 = 'congo.maintenance.views.permission_denied'
        raise PermissionDenied("Testujemy błędy HTTP...")
    elif error_no == 404:
        # ustawic w urls:
        # handler404 = 'congo.maintenance.views.page_not_found'
        raise Http404("Testujemy błędy HTTP...")
    elif error_no == 500:
        # ustawic w urls:
        # handler500 = 'congo.maintenance.views.server_error'
        raise Exception("Testujemy błędy HTTP...")


@secure_allowed
def bad_request(request, *args, **kwargs):
    return http_error(request, 400)

@secure_allowed
def unauthorized(request, *args, **kwargs):
    return http_error(request, 401)

@secure_allowed
def permission_denied(request, *args, **kwargs):
    return http_error(request, 403)

@secure_allowed
def page_not_found(request, *args, **kwargs):
    return http_error(request, 404)

@secure_allowed
def server_error(request, *args, **kwargs):
    return http_error(request, 500)

@secure_allowed
def service_unavailable(request, *args, **kwargs):
    return http_error(request, 503)

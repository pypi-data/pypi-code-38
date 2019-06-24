# -*- coding: utf-8 -*-
import sys
import logging

from pyramid.view import (
    view_config,
    notfound_view_config
)

from oe_geoutils.views import ValidationFailure

log = logging.getLogger(__name__)


@view_config(context=Exception, renderer='json', accept='application/json')
def internal_server_error(exc, request):
    log.error(str(exc), exc_info=sys.exc_info())
    request.response.status_int = 500
    return {'message': 'Er ging iets fout in de server. Onze excuses. '
                       'Stel je fouten vast of heb je een vraag? Mail dan naar ict@onroerenderfgoed.be',
            'detail': str(exc)}


@notfound_view_config(renderer='json', accept='application/json')
def not_found(request):
    request.response.status_int = 404
    return {
        'message':
            'De door u gevraagde resource kon niet gevonden worden.'
    }


@view_config(
    context=ValidationFailure,
    renderer='json'
)
def failed_validation(exc, request):
    log.debug(exc.msg)
    log.debug(exc.errors)
    request.response.status_int = 400
    formated_errors = []
    for node in exc.errors:
        formated_errors.append(' '.join(list(reversed(node.split('.')))).capitalize().replace('_', ' ') + ': ' +
                               exc.errors[node] if node != '' else exc.errors[node])
    return {'message': exc.msg, 'errors': formated_errors}
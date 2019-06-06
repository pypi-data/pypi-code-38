# -*- coding: utf-8 -*-
import functools
import json
import logging
from datetime import datetime

import hashlib
from pyramid import renderers
from pytz import timezone

log = logging.getLogger(__name__)


def _action_from_request(request):
    if request.method == 'POST':
        return 'aanmaken'
    elif request.method == 'PUT':
        return 'bewerken'
    elif request.method == 'DELETE':
        return 'verwijderen'
    elif request.method == 'GET':
        return 'opvragen'
    else:
        return 'onbekend'


def _get_versie_hash(wijziging):
    timestamp = datetime.now(tz=timezone('CET'))
    inputversie = "{0}{1}{2}".format(timestamp, wijziging.resource_object_id, wijziging.updated_by)
    versie = hashlib.sha256(bytearray(inputversie, "utf-8")).hexdigest()
    return versie


def _get_id_from_result(r_id, result, kwarg):
    if kwarg.get('result_id_key'):
        return int(result[kwarg.get('result_id_key')])
    return result['id'] if not r_id else int(r_id)


def audit(**kwargs):
    """
    use this decorator to audit an operation
    """

    def wrap(fn):

        @functools.wraps(fn)
        def advice(parent_object, *args, **kw):
            request = parent_object.request
            wijziging = request.audit_manager.create_revision()

            result = fn(parent_object, *args, **kw)

            if hasattr(request, 'user') and request.user is not None and 'actor' in request.user:
                actor = request.user['actor']
                attributes = request.user['attributes']
                wijziging.updated_by = actor.get('uri', None)
                if actor.get('uri') == actor.get('instantie_actor_uri'):
                    wijziging.updated_by_omschrijving = (
                        attributes.get('displayname')
                        or attributes.get('mail')
                        or actor.get('omschrijving'))
                else:
                    wijziging.updated_by_omschrijving = actor.get(
                        'omschrijving')
            else:
                wijziging.updated_by = 'publiek'
                wijziging.updated_by_omschrijving = 'publiek'

            r_id = request.matchdict.get('id')
            wijziging.resource_object_id = r_id
            if result is not None:
                try:
                    renderer_name = request.registry.settings.get(
                        'audit.pyramid.json.renderer',
                        'jsonrenderer')
                    json_string = renderers.render(renderer_name, result,
                                                   request=request)
                    result_object_json = json.loads(json_string)
                    wijziging.resource_object_json = result_object_json
                    wijziging.resource_object_id = _get_id_from_result(r_id, result_object_json, kwargs)
                except Exception as e:
                    log.error(e)

            wijziging.versie = _get_versie_hash(wijziging)
            wijziging.actie = kwargs.get('actie') if kwargs.get('actie') else _action_from_request(request)

            request.audit_manager.save(wijziging)

            return result

        return advice

    return wrap


def audit_with_request(**kwargs):
    """
    use this decorator to audit an operation with a request as input variable
    """
    def wrap(fn):
        @audit(**kwargs)
        def operation(parent_object, *args, **kw):
            return fn(parent_object.request, *args, **kw)

        @functools.wraps(fn)
        def advice_with_request(the_request, *args, **kw):
            class ParentObject:
                request = the_request

            return operation(ParentObject(), *args, **kw)

        return advice_with_request

    return wrap

# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import datetime

from flask.views import MethodView
from flask import request, jsonify, g
from werkzeug.exceptions import BadRequest

from odcs.server import app, db, log, conf, version
from odcs.server.errors import NotFound
from odcs.server.models import Compose
from odcs.common.types import (
    COMPOSE_RESULTS, COMPOSE_FLAGS, COMPOSE_STATES, PUNGI_SOURCE_TYPE_NAMES,
    PungiSourceType, MULTILIB_METHODS)
from odcs.server.api_utils import (
    pagination_metadata, filter_composes, validate_json_data,
    raise_if_input_not_allowed)
from odcs.server.auth import requires_role, login_required
from odcs.server.auth import require_scopes

try:
    from odcs.server.celery_tasks import (
        generate_pulp_compose, generate_pungi_compose)
    CELERY_AVAILABLE = True
except ImportError:
    log.exception(
        "Cannot import celery_tasks. The Celery support is turned off.")
    CELERY_AVAILABLE = False


api_v1 = {
    'composes': {
        'url': '/api/1/composes/',
        'options': {
            'defaults': {'id': None},
            'methods': ['GET'],
        }
    },
    'compose': {
        'url': '/api/1/composes/<int:id>',
        'options': {
            'methods': ['GET'],
        }
    },
    'composes_post': {
        'url': '/api/1/composes/',
        'options': {
            'methods': ['POST'],
        }
    },
    'compose_regenerate': {
        'url': '/api/1/composes/<int:id>',
        'options': {
            'methods': ['PATCH'],
        }
    },
    'composes_delete': {
        'url': '/api/1/composes/<int:id>',
        'options': {
            'methods': ['DELETE'],
        }
    },
    'about': {
        'url': '/api/1/about/',
        'options': {
            'methods': ['GET']
        }
    },
}


class ODCSAPI(MethodView):
    def _get_compose_owner(self):
        if conf.auth_backend == "noauth":
            log.warning(
                "Cannot determine the owner of compose, because "
                "'noauth' auth_backend is used.")
            return "unknown"
        else:
            return g.user.username

    def _get_seconds_to_live(self, request_data):
        if "seconds-to-live" in request_data:
            try:
                return min(int(request_data['seconds-to-live']),
                           conf.max_seconds_to_live)
            except ValueError:
                err = 'Invalid seconds-to-live specified in request: %s' % \
                    request_data
                log.error(err)
                raise ValueError(err)
        else:
            return conf.seconds_to_live

    def get(self, id):
        if id is None:
            p_query = filter_composes(request)

            json_data = {
                'meta': pagination_metadata(p_query, request.args),
                'items': [item.json() for item in p_query.items]
            }

            return jsonify(json_data), 200

        else:
            compose = Compose.query.filter_by(id=id).first()
            if compose:
                return jsonify(compose.json()), 200
            else:
                raise NotFound('No such compose found.')

    @login_required
    @require_scopes('renew-compose')
    @requires_role('allowed_clients')
    def patch(self, id):
        if request.data:
            data = request.get_json(force=True)
        else:
            data = {}
        validate_json_data(data)

        seconds_to_live = self._get_seconds_to_live(data)

        old_compose = Compose.query.filter(
            Compose.id == id,
            Compose.state.in_(
                [COMPOSE_STATES["removed"],
                    COMPOSE_STATES["done"],
                    COMPOSE_STATES["failed"]])).first()

        if not old_compose:
            err = "No compose with id %s found" % id
            log.error(err)
            raise NotFound(err)

        raise_if_input_not_allowed(
            source_types=old_compose.source_type, sources=old_compose.source,
            results=old_compose.results, flags=old_compose.flags,
            arches=old_compose.arches)

        has_to_create_a_copy = old_compose.state in (
            COMPOSE_STATES['removed'], COMPOSE_STATES['failed'])
        if has_to_create_a_copy:
            log.info("%r: Going to regenerate the compose", old_compose)
            compose = Compose.create_copy(db.session,
                                          old_compose,
                                          self._get_compose_owner(),
                                          seconds_to_live)
            db.session.add(compose)
            # Flush is needed, because we use `before_commit` SQLAlchemy
            # event to send message and before_commit can be called before
            # flush and therefore the compose ID won't be set.
            db.session.flush()
            db.session.commit()

            if CELERY_AVAILABLE and conf.celery_broker_url:
                if compose.source_type == PungiSourceType.PULP:
                    generate_pulp_compose.delay(compose.id)
                else:
                    generate_pungi_compose.delay(compose.id)

            return jsonify(compose.json()), 200
        else:
            # Otherwise, just extend expiration to make it usable for longer
            # time.
            extend_from = datetime.datetime.utcnow()
            old_compose.extend_expiration(extend_from, seconds_to_live)
            log.info('Extended time_to_expire for compose %r to %s',
                     old_compose, old_compose.time_to_expire)
            # As well as extending those composes that reuse this this compose,
            # and the one this compose reuses.
            reused_compose = old_compose.get_reused_compose()
            if reused_compose:
                reused_compose.extend_expiration(extend_from, seconds_to_live)
            for c in old_compose.get_reusing_composes():
                c.extend_expiration(extend_from, seconds_to_live)
            db.session.commit()
            return jsonify(old_compose.json()), 200

    @login_required
    @require_scopes('new-compose')
    @requires_role('allowed_clients')
    def post(self):
        data = request.get_json(force=True)
        if not data:
            raise ValueError('No JSON POST data submitted')

        validate_json_data(data)

        seconds_to_live = self._get_seconds_to_live(data)

        source_data = data.get('source', None)
        if not isinstance(source_data, dict):
            err = "Invalid source configuration provided: %s" % str(data)
            log.error(err)
            raise ValueError(err)

        needed_keys = ["type"]
        for key in needed_keys:
            if key not in source_data:
                err = "Missing %s in source configuration, received: %s" % (key, str(source_data))
                log.error(err)
                raise ValueError(err)

        source_type = source_data["type"]
        if source_type not in PUNGI_SOURCE_TYPE_NAMES:
            err = 'Unknown source type "%s"' % source_type
            log.error(err)
            raise ValueError(err)

        source_type = PUNGI_SOURCE_TYPE_NAMES[source_type]

        source = []
        if "source" in source_data:
            # Use list(set()) here to remove duplicate sources.
            source = list(set(source_data["source"].split(" ")))

        if not source and source_type != PungiSourceType.BUILD:
            err = "No source provided for %s" % source_type
            log.error(err)
            raise ValueError(err)

        # Validate `source` based on `source_type`.
        if source_type == PungiSourceType.RAW_CONFIG:
            if len(source) > 1:
                raise ValueError(
                    'Only single source is allowed for "raw_config" '
                    'source_type')

            source_name_hash = source[0].split("#")
            if (len(source_name_hash) != 2 or not source_name_hash[0] or
                    not source_name_hash[1]):
                raise ValueError(
                    'Source must be in "source_name#commit_hash" format for '
                    '"raw_config" source_type.')

            source_name, source_hash = source_name_hash
            if source_name not in conf.raw_config_urls:
                raise ValueError(
                    'Source "%s" does not exist in server configuration.' %
                    source_name)
        elif source_type == PungiSourceType.MODULE:
            for module_str in source:
                nsvc = module_str.split(":")
                if len(nsvc) < 2:
                    raise ValueError(
                        'Module definition must be in "n:s", "n:s:v" or '
                        '"n:s:v:c" format, but got %s' % module_str)
                if nsvc[0] in conf.base_module_names:
                    raise ValueError(
                        "ODCS currently cannot create compose with base "
                        "modules, but %s was requested." % nsvc[0])

        source = ' '.join(source)

        packages = None
        if "packages" in source_data:
            packages = ' '.join(source_data["packages"])

        builds = None
        if "builds" in source_data:
            builds = ' '.join(source_data["builds"])

        sigkeys = ""
        if "sigkeys" in source_data:
            sigkeys = ' '.join(source_data["sigkeys"])
        else:
            sigkeys = ' '.join(conf.sigkeys)

        flags = 0
        if "flags" in data:
            for name in data["flags"]:
                if name not in COMPOSE_FLAGS:
                    raise ValueError("Unknown flag %s", name)
                flags |= COMPOSE_FLAGS[name]

        results = COMPOSE_RESULTS["repository"]
        if "results" in data:
            for name in data["results"]:
                if name not in COMPOSE_RESULTS:
                    raise ValueError("Unknown result %s", name)
                results |= COMPOSE_RESULTS[name]

        arches = None
        if "arches" in data:
            arches = ' '.join(data["arches"])
        else:
            arches = " ".join(conf.arches)

        multilib_arches = ""
        if "multilib_arches" in data:
            multilib_arches = " ".join(data["multilib_arches"])

        lookaside_repos = ""
        if "lookaside_repos" in data:
            lookaside_repos = " ".join(data["lookaside_repos"])

        multilib_method = MULTILIB_METHODS["none"]
        if "multilib_method" in data:
            for name in data["multilib_method"]:
                if name not in MULTILIB_METHODS:
                    raise ValueError("Unknown multilib method \"%s\"" % name)
                multilib_method |= MULTILIB_METHODS[name]

        modular_koji_tags = None
        if "modular_koji_tags" in source_data:
            modular_koji_tags = ' '.join(source_data["modular_koji_tags"])

        module_defaults_url = None
        if "module_defaults_url" in source_data:
            module_defaults_url = source_data["module_defaults_url"]

        module_defaults_commit = None
        if "module_defaults_commit" in source_data:
            module_defaults_commit = source_data["module_defaults_commit"]

        module_defaults = None
        # The "^" operator is logical XOR.
        if bool(module_defaults_url) ^ bool(module_defaults_commit):
            raise ValueError(
                'The "module_defaults_url" and "module_defaults_commit" '
                'must be used together.')
        elif module_defaults_url and module_defaults_commit:
            module_defaults = "%s %s" % (module_defaults_url, module_defaults_commit)

        raise_if_input_not_allowed(
            source_types=source_type, sources=source, results=results,
            flags=flags, arches=arches)

        compose = Compose.create(
            db.session, self._get_compose_owner(), source_type, source,
            results, seconds_to_live,
            packages, flags, sigkeys, arches, multilib_arches=multilib_arches,
            multilib_method=multilib_method, builds=builds,
            lookaside_repos=lookaside_repos,
            modular_koji_tags=modular_koji_tags,
            module_defaults_url=module_defaults)
        db.session.add(compose)
        # Flush is needed, because we use `before_commit` SQLAlchemy event to
        # send message and before_commit can be called before flush and
        # therefore the compose ID won't be set.
        db.session.flush()
        db.session.commit()

        if CELERY_AVAILABLE and conf.celery_broker_url:
            if source_type == PungiSourceType.PULP:
                generate_pulp_compose.delay(compose.id)
            else:
                generate_pungi_compose.delay(compose.id)

        return jsonify(compose.json()), 200

    @login_required
    @require_scopes('delete-compose')
    @requires_role('admins')
    def delete(self, id):
        compose = Compose.query.filter_by(id=id).first()
        if compose:
            # can remove compose that is in state of 'done' or 'failed'
            deletable_states = {n: COMPOSE_STATES[n] for n in ['done', 'failed']}
            if compose.state not in deletable_states.values():
                raise BadRequest('Compose (id=%s) can not be removed, its state need to be in %s.' %
                                 (id, deletable_states.keys()))

            # change compose.time_to_expire to now, so backend will
            # delete this compose as it's an expired compose now
            compose.time_to_expire = datetime.datetime.utcnow()
            compose.removed_by = g.user.username
            db.session.add(compose)
            db.session.commit()
            message = ("The delete request for compose (id=%s) has been accepted and will be"
                       " processed by backend later." % compose.id)
            response = jsonify({'status': 202,
                                'message': message})
            response.status_code = 202
            return response
        else:
            raise NotFound('No such compose found.')


class AboutAPI(MethodView):
    def get(self):
        json = {'version': version}
        config_items = ['auth_backend']
        for item in config_items:
            config_item = getattr(conf, item)
            # All config items have a default, so if doesn't exist it is
            # an error
            if not config_item:
                raise ValueError(
                    'An invalid config item of "%s" was specified' % item)
            json[item] = config_item
        return jsonify(json), 200


def register_api_v1():
    """ Registers version 1 of ODCS API. """
    composes_view = ODCSAPI.as_view('composes')
    about_view = AboutAPI.as_view('about')
    for key, val in api_v1.items():
        if key.startswith("compose"):
            app.add_url_rule(val['url'],
                             endpoint=key,
                             view_func=composes_view,
                             **val['options'])
        elif key.startswith("about"):
            app.add_url_rule(val['url'],
                             endpoint=key,
                             view_func=about_view,
                             **val['options'])
        else:
            raise ValueError("Unhandled API key: %s." % key)


register_api_v1()

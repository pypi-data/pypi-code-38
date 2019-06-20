# -*- coding: utf-8 -*-
# Copyright (c) 2016  Red Hat, Inc.
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
# Written by Petr Šabata <contyk@redhat.com>
#            Matt Prahl <mprahl@redhat.com>

""" The module build orchestrator for Modularity, API.
This is the implementation of the orchestrator's public RESTful API.
"""

import json
import module_build_service.auth
from flask import request, url_for
from flask.views import MethodView
from six import string_types
from io import BytesIO

from module_build_service import app, conf, log, models, db, version, api_version as max_api_version
from module_build_service.utils import (
    pagination_metadata,
    filter_module_builds,
    filter_component_builds,
    submit_module_build_from_scm,
    submit_module_build_from_yaml,
    get_scm_url_re,
    cors_header,
    validate_api_version,
    import_mmd,
    get_mmd_from_scm,
    str_to_bool,
)
from module_build_service.errors import ValidationError, Forbidden, NotFound, ProgrammingError
from module_build_service.backports import jsonify
from module_build_service.monitor import monitor_api


api_routes = {
    "module_builds": {
        "url": "/module-build-service/<int:api_version>/module-builds/",
        "options": {"methods": ["POST"]},
    },
    "module_builds_list": {
        "url": "/module-build-service/<int:api_version>/module-builds/",
        "options": {"defaults": {"id": None}, "methods": ["GET"]},
    },
    "module_build": {
        "url": "/module-build-service/<int:api_version>/module-builds/<int:id>",
        "options": {"methods": ["GET", "PATCH"]},
    },
    "component_builds_list": {
        "url": "/module-build-service/<int:api_version>/component-builds/",
        "options": {"defaults": {"id": None}, "methods": ["GET"]},
    },
    "component_build": {
        "url": "/module-build-service/<int:api_version>/component-builds/<int:id>",
        "options": {"methods": ["GET"]},
    },
    "about": {
        "url": "/module-build-service/<int:api_version>/about/",
        "options": {"methods": ["GET"]},
    },
    "rebuild_strategies_list": {
        "url": "/module-build-service/<int:api_version>/rebuild-strategies/",
        "options": {"methods": ["GET"]},
    },
    "import_module": {
        "url": "/module-build-service/<int:api_version>/import-module/",
        "options": {"methods": ["POST"]},
    },
}


class AbstractQueryableBuildAPI(MethodView):
    """ An abstract class, housing some common functionality. """

    @cors_header()
    @validate_api_version()
    def get(self, api_version, id):
        id_flag = request.args.get("id")
        if id_flag:
            endpoint = request.endpoint.split("s_list")[0]
            raise ValidationError(
                'The "id" query option is invalid. Did you mean to go to "{0}"?'.format(
                    url_for(endpoint, api_version=api_version, id=id_flag)
                )
            )
        verbose_flag = request.args.get("verbose", "false").lower()
        short_flag = request.args.get("short", "false").lower()
        json_func_kwargs = {}
        json_func_name = "json"

        if id is None:
            # Lists all tracked builds
            p_query = self.query_filter(request)
            json_data = {"meta": pagination_metadata(p_query, api_version, request.args)}

            if verbose_flag == "true" or verbose_flag == "1":
                json_func_name = "extended_json"
                json_func_kwargs["show_state_url"] = True
                json_func_kwargs["api_version"] = api_version
            elif short_flag == "true" or short_flag == "1":
                if hasattr(p_query.items[0], "short_json"):
                    json_func_name = "short_json"
            json_data["items"] = [
                getattr(item, json_func_name)(**json_func_kwargs) for item in p_query.items
            ]

            return jsonify(json_data), 200
        else:
            # Lists details for the specified build
            instance = self.model.query.filter_by(id=id).first()
            if instance:
                if verbose_flag == "true" or verbose_flag == "1":
                    json_func_name = "extended_json"
                    json_func_kwargs["show_state_url"] = True
                    json_func_kwargs["api_version"] = api_version
                elif short_flag == "true" or short_flag == "1":
                    if getattr(instance, "short_json", None):
                        json_func_name = "short_json"
                return jsonify(getattr(instance, json_func_name)(**json_func_kwargs)), 200
            else:
                raise NotFound("No such %s found." % self.kind)


class ComponentBuildAPI(AbstractQueryableBuildAPI):
    kind = "component"
    query_filter = staticmethod(filter_component_builds)
    model = models.ComponentBuild


class ModuleBuildAPI(AbstractQueryableBuildAPI):
    kind = "module"
    query_filter = staticmethod(filter_module_builds)
    model = models.ModuleBuild

    @staticmethod
    def check_groups(username, groups, allowed_groups=conf.allowed_groups):
        # If the user is part of the whitelist, then the group membership check is skipped
        if username in conf.allowed_users:
            return
        if allowed_groups and not (allowed_groups & groups):
            raise Forbidden("%s is not in any of %r, only %r" % (username, allowed_groups, groups))

    # Additional POST and DELETE handlers for modules follow.
    @validate_api_version()
    def post(self, api_version):
        data = _dict_from_request(request)
        if "modulemd" in data or (hasattr(request, "files") and "yaml" in request.files):
            handler = YAMLFileHandler(request, data)
        else:
            handler = SCMHandler(request, data)

        if conf.no_auth is True and handler.username == "anonymous" and "owner" in handler.data:
            handler.username = handler.data["owner"]

        self.check_groups(handler.username, handler.groups)

        handler.validate()
        modules = handler.post()
        if api_version == 1:
            # Only show the first module build for backwards-compatibility
            rv = modules[0].extended_json(True, api_version)
        else:
            rv = [module.extended_json(True, api_version) for module in modules]
        return jsonify(rv), 201

    @validate_api_version()
    def patch(self, api_version, id):
        username, groups = module_build_service.auth.get_user(request)

        try:
            r = json.loads(request.get_data().decode("utf-8"))
        except Exception:
            log.exception("Invalid JSON submitted")
            raise ValidationError("Invalid JSON submitted")

        if "owner" in r:
            if conf.no_auth is not True:
                raise ValidationError(
                    "The request contains 'owner' parameter, however NO_AUTH is not allowed"
                )
            elif username == "anonymous":
                username = r["owner"]

        self.check_groups(username, groups)

        module = models.ModuleBuild.query.filter_by(id=id).first()
        if not module:
            raise NotFound("No such module found.")

        if module.owner != username and not (conf.admin_groups & groups):
            raise Forbidden("You are not owner of this build and therefore cannot modify it.")

        if not r.get("state"):
            log.error("Invalid JSON submitted")
            raise ValidationError("Invalid JSON submitted")

        if module.state == models.BUILD_STATES["failed"]:
            raise Forbidden("You can't cancel a failed module")

        if r["state"] == "failed" or r["state"] == str(models.BUILD_STATES["failed"]):
            module.transition(conf, models.BUILD_STATES["failed"], "Canceled by %s." % username)
        else:
            log.error('The provided state change of "{}" is not supported'.format(r["state"]))
            raise ValidationError("The provided state change is not supported")
        db.session.add(module)
        db.session.commit()

        return jsonify(module.extended_json(True, api_version)), 200


class AboutAPI(MethodView):
    @cors_header()
    @validate_api_version()
    def get(self, api_version):
        json = {"version": version, "api_version": max_api_version}
        config_items = ["auth_method"]
        for item in config_items:
            config_item = getattr(conf, item)
            # All config items have a default, so if doesn't exist it is a programming error
            if not config_item:
                raise ProgrammingError('An invalid config item of "{0}" was specified'.format(item))
            json[item] = config_item
        return jsonify(json), 200


class RebuildStrategies(MethodView):
    @cors_header()
    @validate_api_version()
    def get(self, api_version):
        items = []
        # Sort the items list by name
        for strategy in sorted(models.ModuleBuild.rebuild_strategies.keys()):
            default = False
            if strategy == conf.rebuild_strategy:
                default = True
                allowed = True
            elif (
                conf.rebuild_strategy_allow_override and strategy in conf.rebuild_strategies_allowed
            ):
                allowed = True
            else:
                allowed = False
            items.append({
                "name": strategy,
                "description": models.ModuleBuild.rebuild_strategies[strategy],
                "allowed": allowed,
                "default": default,
            })

        return jsonify({"items": items}), 200


class ImportModuleAPI(MethodView):
    @validate_api_version()
    def post(self, api_version):
        # disable this API endpoint if no groups are defined
        if not conf.allowed_groups_to_import_module:
            log.error(
                "Import module API is disabled. Set 'ALLOWED_GROUPS_TO_IMPORT_MODULE'"
                " configuration value first."
            )
            raise Forbidden("Import module API is disabled.")

        # auth checks
        username, groups = module_build_service.auth.get_user(request)
        ModuleBuildAPI.check_groups(
            username, groups, allowed_groups=conf.allowed_groups_to_import_module)

        # process request using SCM handler
        handler = SCMHandler(request)
        handler.validate(skip_branch=True, skip_optional_params=True)

        mmd = get_mmd_from_scm(handler.data["scmurl"])
        build, messages = import_mmd(db.session, mmd)
        json_data = {"module": build.json(show_tasks=False), "messages": messages}

        # return 201 Created if we reach this point
        return jsonify(json_data), 201


class BaseHandler(object):
    valid_params = set([
        "branch",
        "buildrequire_overrides",
        "modulemd",
        "module_name",
        "owner",
        "rebuild_strategy",
        "require_overrides",
        "scmurl",
        "scratch",
        "srpms",
    ])

    def __init__(self, request, data=None):
        self.username, self.groups = module_build_service.auth.get_user(request)
        self.data = data or _dict_from_request(request)

        # canonicalize and validate scratch option
        if "scratch" in self.data and str_to_bool(str(self.data["scratch"])):
            self.data["scratch"] = True
            if conf.modules_allow_scratch is not True:
                raise Forbidden("Scratch builds are not enabled")
        else:
            self.data["scratch"] = False

        # canonicalize and validate srpms list
        if "srpms" in self.data and self.data["srpms"]:
            if not self.data["scratch"]:
                raise Forbidden("srpms may only be specified for scratch builds")
            if not isinstance(self.data["srpms"], list):
                raise ValidationError("srpms must be specified as a list")
        else:
            self.data["srpms"] = []

    def _validate_dep_overrides_format(self, key):
        """
        Validate any dependency overrides provided to the API.

        :param str key: the override key to validate
        :raises ValidationError: when the overrides are an invalid format
        """
        if not self.data.get(key):
            return
        invalid_override_msg = (
            'The "{}" parameter must be an object with the keys as module '
            "names and the values as arrays of streams".format(key)
        )
        if not isinstance(self.data[key], dict):
            raise ValidationError(invalid_override_msg)
        for streams in self.data[key].values():
            if not isinstance(streams, list):
                raise ValidationError(invalid_override_msg)
            for stream in streams:
                if not isinstance(stream, string_types):
                    raise ValidationError(invalid_override_msg)

    def validate_optional_params(self):
        forbidden_params = [k for k in self.data if k not in self.valid_params]
        if forbidden_params:
            raise ValidationError(
                "The request contains unspecified parameters: {}".format(
                    ", ".join(forbidden_params))
            )

        if not conf.no_auth and "owner" in self.data:
            raise ValidationError(
                "The request contains 'owner' parameter, however NO_AUTH is not allowed")

        if not conf.rebuild_strategy_allow_override and "rebuild_strategy" in self.data:
            raise ValidationError(
                'The request contains the "rebuild_strategy" parameter but '
                "overriding the default isn't allowed"
            )

        if "rebuild_strategy" in self.data:
            if self.data["rebuild_strategy"] not in conf.rebuild_strategies_allowed:
                raise ValidationError(
                    'The rebuild method of "{0}" is not allowed. Choose from: {1}.'.format(
                        self.data["rebuild_strategy"], ", ".join(conf.rebuild_strategies_allowed))
                )

        self._validate_dep_overrides_format("buildrequire_overrides")
        self._validate_dep_overrides_format("require_overrides")


class SCMHandler(BaseHandler):
    def validate(self, skip_branch=False, skip_optional_params=False):
        if "scmurl" not in self.data:
            log.error("Missing scmurl")
            raise ValidationError("Missing scmurl")

        url = self.data["scmurl"]
        allowed_prefix = any(url.startswith(prefix) for prefix in conf.scmurls)
        if not conf.allow_custom_scmurls and not allowed_prefix:
            log.error("The submitted scmurl %r is not allowed" % url)
            raise Forbidden("The submitted scmurl %s is not allowed" % url)

        if not get_scm_url_re().match(url):
            log.error("The submitted scmurl %r is not valid" % url)
            raise ValidationError("The submitted scmurl %s is not valid" % url)

        if not skip_branch and "branch" not in self.data:
            log.error("Missing branch")
            raise ValidationError("Missing branch")

        if not skip_optional_params:
            self.validate_optional_params()

    def post(self):
        return submit_module_build_from_scm(self.username, self.data, allow_local_url=False)


class YAMLFileHandler(BaseHandler):
    def __init__(self, request, data=None):
        super(YAMLFileHandler, self).__init__(request, data)
        if not self.data["scratch"] and not conf.yaml_submit_allowed:
            raise Forbidden("YAML submission is not enabled")

    def validate(self):
        if (
            "modulemd" not in self.data
            and (not hasattr(request, "files") or "yaml" not in request.files)
        ):
            log.error("Invalid file submitted")
            raise ValidationError("Invalid file submitted")
        self.validate_optional_params()

    def post(self):
        if "modulemd" in self.data:
            handle = BytesIO(self.data["modulemd"].encode("utf-8"))
            if self.data.get("module_name"):
                handle.filename = self.data["module_name"]
        else:
            handle = request.files["yaml"]
        return submit_module_build_from_yaml(self.username, handle, self.data)


def _dict_from_request(request):
    if "multipart/form-data" in request.headers.get("Content-Type", ""):
        data = request.form.to_dict()
    else:
        try:
            data = json.loads(request.get_data().decode("utf-8"))
        except Exception:
            log.exception("Invalid JSON submitted")
            raise ValidationError("Invalid JSON submitted")
    return data


def register_api():
    """ Registers the MBS API. """
    module_view = ModuleBuildAPI.as_view("module_builds")
    component_view = ComponentBuildAPI.as_view("component_builds")
    about_view = AboutAPI.as_view("about")
    rebuild_strategies_view = RebuildStrategies.as_view("rebuild_strategies")
    import_module = ImportModuleAPI.as_view("import_module")
    for key, val in api_routes.items():
        if key.startswith("component_build"):
            app.add_url_rule(val["url"], endpoint=key, view_func=component_view, **val["options"])
        elif key.startswith("module_build"):
            app.add_url_rule(val["url"], endpoint=key, view_func=module_view, **val["options"])
        elif key.startswith("about"):
            app.add_url_rule(val["url"], endpoint=key, view_func=about_view, **val["options"])
        elif key == "rebuild_strategies_list":
            app.add_url_rule(
                val["url"], endpoint=key, view_func=rebuild_strategies_view, **val["options"]
            )
        elif key == "import_module":
            app.add_url_rule(val["url"], endpoint=key, view_func=import_module, **val["options"])
        else:
            raise NotImplementedError("Unhandled api key.")

    app.register_blueprint(monitor_api)


register_api()

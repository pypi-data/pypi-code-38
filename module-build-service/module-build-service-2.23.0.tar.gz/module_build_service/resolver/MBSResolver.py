# -*- coding: utf-8 -*-


# Copyright (c) 2018  Red Hat, Inc.
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
# Written by Martin Curlej <mcurlej@redhat.com>

"""MBS handler functions."""

import logging
import kobo.rpmlib
import requests

from module_build_service import db, conf
from module_build_service import models
from module_build_service.errors import UnprocessableEntity
from module_build_service.resolver.base import GenericResolver
from module_build_service.utils.general import import_mmd, load_mmd

log = logging.getLogger()


class MBSResolver(GenericResolver):

    backend = "mbs"

    def __init__(self, config):
        self.mbs_prod_url = config.mbs_url
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount(self.mbs_prod_url, adapter)
        self._generic_error = "Failed to query MBS with query %r returned HTTP status %s"

    def _query_from_nsvc(self, name, stream, version=None, context=None, state="ready"):
        """
        Generates dict with MBS params query.

        :param str name: Name of the module to query.
        :param str stream: Stream of the module to query.
        :param str version/int: Version of the module to query.
        :param str context: Context of the module to query.
        """
        query = {
            "name": name,
            "stream": stream,
            "state": state,
            "verbose": True,
            "order_desc_by": "version",
        }
        if version is not None:
            query["version"] = str(version)
        if context is not None:
            query["context"] = context
        return query

    def _get_modules(
        self, name, stream, version=None, context=None, state="ready", strict=False, **kwargs
    ):
        """Query and return modules from MBS with specific info

        :param str name: module's name.
        :param str stream: module's stream.
        :kwarg str version: a string or int of the module's version. When None,
            latest version will be returned.
        :kwarg str context: module's context. Optional.
        :kwarg str state: module's state. Defaults to ``ready``.
        :kwarg bool strict: Normally this function returns None if no module can be
            found. If strict=True, then an UnprocessableEntity is raised.
        :return: final list of module_info which pass repoclosure
        :rtype: list[dict]
        :raises UnprocessableEntity: if no modules are found and ``strict`` is True.
        """
        query = self._query_from_nsvc(name, stream, version, context, state)
        query["page"] = 1
        query["per_page"] = 10
        query.update(kwargs)
        modules = []

        while True:
            res = self.session.get(self.mbs_prod_url, params=query)
            if not res.ok:
                raise RuntimeError(self._generic_error % (query, res.status_code))

            data = res.json()
            modules_per_page = data["items"]
            modules += modules_per_page

            if not data["meta"]["next"]:
                break

            query["page"] += 1

        # Error handling
        if not modules:
            if strict:
                raise UnprocessableEntity("Failed to find module in MBS %r" % query)
            else:
                return modules

        if version is None and "stream_version_lte" not in kwargs:
            # Only return the latest version
            return [m for m in modules if m["version"] == modules[0]["version"]]
        else:
            return modules

    def _get_module(self, name, stream, version, context, state="ready", strict=False):
        rv = self._get_modules(name, stream, version, context, state, strict)
        if rv:
            return rv[0]

    def get_module_count(self, **kwargs):
        """
        Determine the number of modules that match the provided filter.

        :return: the number of modules that match the provided filter
        :rtype: int
        """
        query = {"page": 1, "per_page": 1, "short": True}
        query.update(kwargs)
        res = self.session.get(self.mbs_prod_url, params=query)
        if not res.ok:
            raise RuntimeError(self._generic_error % (query, res.status_code))

        data = res.json()
        return data["meta"]["total"]

    def get_latest_with_virtual_stream(self, name, virtual_stream):
        """
        Get the latest module with the input virtual stream based on the stream version and version.

        :param str name: the module name to search for
        :param str virtual_stream: the module virtual stream to search for
        :return: the module's modulemd or None
        :rtype: Modulemd.ModuleStream or None
        """
        query = {
            "name": name,
            "order_desc_by": ["stream_version", "version"],
            "page": 1,
            "per_page": 1,
            "verbose": True,
            "virtual_stream": virtual_stream,
        }
        res = self.session.get(self.mbs_prod_url, params=query)
        if not res.ok:
            raise RuntimeError(self._generic_error % (query, res.status_code))

        data = res.json()
        if data["items"]:
            return load_mmd(data["items"][0]["modulemd"])

    def get_module_modulemds(
        self,
        name,
        stream,
        version=None,
        context=None,
        strict=False,
        stream_version_lte=False,
        virtual_streams=None,
    ):
        """
        Gets the module modulemds from the resolver.
        :param name: a string of the module's name
        :param stream: a string of the module's stream
        :param version: a string or int of the module's version. When None, latest version will
            be returned.
        :param context: a string of the module's context. When None, all contexts will
            be returned.
        :kwarg strict: Normally this function returns [] if no module can be
            found.  If strict=True, then a UnprocessableEntity is raised.
        :kwarg stream_version_lte: If True and if the `stream` can be transformed to
            "stream version", the returned list will include all the modules with stream version
            less than or equal the stream version computed from `stream`.
        :kwarg virtual_streams: a list of the virtual streams to filter on. The filtering uses "or"
            logic. When falsy, no filtering occurs.
        :return: List of Modulemd metadata instances matching the query
        """
        yaml = None

        local_modules = models.ModuleBuild.local_modules(db.session, name, stream)
        if local_modules:
            return [m.mmd() for m in local_modules]

        extra_args = {}
        if stream_version_lte and (
            len(str(models.ModuleBuild.get_stream_version(stream, right_pad=False))) >= 5
        ):
            stream_version = models.ModuleBuild.get_stream_version(stream)
            extra_args["stream_version_lte"] = stream_version

        if virtual_streams:
            extra_args["virtual_stream"] = virtual_streams

        modules = self._get_modules(name, stream, version, context, strict=strict, **extra_args)
        if not modules:
            return []

        mmds = []
        for module in modules:
            if module:
                yaml = module["modulemd"]

            if not yaml:
                if strict:
                    raise UnprocessableEntity(
                        "Failed to find modulemd entry in MBS for %r" % module)
                else:
                    return None

            mmds.append(load_mmd(yaml))
        return mmds

    def get_buildrequired_modulemds(self, name, stream, base_module_nsvc):
        """
        Returns modulemd metadata of all module builds with `name` and `stream` buildrequiring
        base module defined by `base_module_nsvc` NSVC.

        :param str name: Name of module to return.
        :param str stream: Stream of module to return.
        :param str base_module_nsvc: NSVC of base module which must be buildrequired by returned
            modules.
        :rtype: list
        :return: List of modulemd metadata.
        """
        modules = self._get_modules(name, stream, strict=False, base_module_br=base_module_nsvc)
        return [load_mmd(module["modulemd"]) for module in modules]

    def resolve_profiles(self, mmd, keys):
        """
        :param mmd: Modulemd.ModuleStream instance of module
        :param keys: list of modulemd installation profiles to include in
                     the result.
        :return: Dictionary with keys set according to `keys` param and values
                 set to union of all components defined in all installation
                 profiles matching the key using the buildrequires.

        If there are some modules loaded by utils.load_local_builds(...), these
        local modules will be considered when returning the profiles.

        https://pagure.io/fm-orchestrator/issue/181
        """

        results = {}
        for key in keys:
            results[key] = set()
        for module_name, module_info in mmd.get_xmd()["mbs"]["buildrequires"].items():
            local_modules = models.ModuleBuild.local_modules(
                db.session, module_name, module_info["stream"])
            if local_modules:
                local_module = local_modules[0]
                log.info("Using local module %r to resolve profiles.", local_module)
                dep_mmd = local_module.mmd()
                for key in keys:
                    profile = dep_mmd.get_profile(key)
                    if profile:
                        results[key] |= set(profile.get_rpms())
                continue

            # Find the dep in the built modules in MBS
            modules = self._get_modules(
                module_name,
                module_info["stream"],
                module_info["version"],
                module_info["context"],
                strict=True,
            )

            for module in modules:
                yaml = module["modulemd"]
                dep_mmd = load_mmd(yaml)
                # Take note of what rpms are in this dep's profile.
                for key in keys:
                    profile = dep_mmd.get_profile(key)
                    if profile:
                        results[key] |= set(profile.get_rpms())

        # Return the union of all rpms in all profiles of the given keys.
        return results

    def get_module_build_dependencies(
        self, name=None, stream=None, version=None, context=None, mmd=None, strict=False
    ):
        """
        Returns a dictionary of koji_tag:[mmd, ...] of all the dependencies of input module.

        Although it is expected that single Koji tag always contain just single module build,
        it does not have to be a true for Offline local builds which use the local repository
        identifier as `koji_tag`.

        :param name: a module's name (required if mmd is not set)
        :param stream: a module's stream (required if mmd is not set)
        :param version: a module's version (required if mmd is not set)
        :param context: a module's context (required if mmd is not set)
        :param mmd: uses the mmd instead of the name, stream, version
        :param strict: Normally this function returns None if no module can be
            found.  If strict=True, then an UnprocessableEntity is raised.
        :return: a mapping containing buildrequire modules info in key/value pairs,
            where key is koji_tag and value is list of Modulemd.ModuleStream objects.
        :rtype: dict(str, :class:`Modulemd.Module`)
        """

        if mmd:
            log.debug("get_module_build_dependencies(mmd=%r strict=%r)" % (mmd, strict))
        elif any(x is None for x in [name, stream, version, context]):
            raise RuntimeError("The name, stream, version, and/or context weren't specified")
        else:
            version = str(version)
            log.debug(
                "get_module_build_dependencies(%s, strict=%r)"
                % (", ".join([name, stream, str(version), context]), strict)
            )

        # This is the set we're going to build up and return.
        module_tags = {}

        if mmd:
            queried_mmd = mmd
        else:
            queried_module = self._get_module(name, stream, version, context, strict=strict)
            yaml = queried_module["modulemd"]
            queried_mmd = load_mmd(yaml)

        if not queried_mmd or "buildrequires" not in queried_mmd.get_xmd().get("mbs", {}):
            raise RuntimeError(
                'The module "{0!r}" did not contain its modulemd or did not have '
                "its xmd attribute filled out in MBS".format(queried_mmd)
            )

        buildrequires = queried_mmd.get_xmd()["mbs"]["buildrequires"]
        # Queue up the next tier of deps that we should look at..
        for name, details in buildrequires.items():
            local_modules = models.ModuleBuild.local_modules(db.session, name, details["stream"])
            if local_modules:
                for m in local_modules:
                    # If the buildrequire is a meta-data only module with no Koji tag set, then just
                    # skip it
                    if m.koji_tag is None:
                        continue
                    module_tags[m.koji_tag] = m.mmd()
                continue

            if "context" not in details:
                details["context"] = models.DEFAULT_MODULE_CONTEXT
            modules = self._get_modules(
                name, details["stream"], details["version"], details["context"], strict=True)
            for m in modules:
                if m["koji_tag"] in module_tags:
                    continue
                # If the buildrequire is a meta-data only module with no Koji tag set, then just
                # skip it
                if m["koji_tag"] is None:
                    continue
                module_tags.setdefault(m["koji_tag"], [])
                module_tags[m["koji_tag"]].append(load_mmd(m["modulemd"]))

        return module_tags

    def resolve_requires(self, requires):
        """
        Resolves the requires list of N:S or N:S:V:C to a dictionary with keys as
        the module name and the values as a dictionary with keys of ref,
        stream, version.
        If there are some modules loaded by utils.load_local_builds(...), these
        local modules will be considered when resolving the requires. A RuntimeError
        is raised on MBS lookup errors.
        :param requires: a list of N:S or N:S:V:C strings
        :return: a dictionary
        """
        new_requires = {}
        for nsvc in requires:
            nsvc_splitted = nsvc.split(":")
            if len(nsvc_splitted) == 2:
                module_name, module_stream = nsvc_splitted
                module_version = None
                module_context = None
            elif len(nsvc_splitted) == 4:
                module_name, module_stream, module_version, module_context = nsvc_splitted
            else:
                raise ValueError(
                    "Only N:S or N:S:V:C is accepted by resolve_requires, got %s" % nsvc)
            # Try to find out module dependency in the local module builds
            # added by utils.load_local_builds(...).
            local_modules = models.ModuleBuild.local_modules(db.session, module_name, module_stream)
            if local_modules:
                local_build = local_modules[0]
                new_requires[module_name] = {
                    # The commit ID isn't currently saved in modules.yaml
                    "ref": None,
                    "stream": local_build.stream,
                    "version": local_build.version,
                    "context": local_build.context,
                    "koji_tag": local_build.koji_tag,
                    # No need to set filtered_rpms for local builds, because MBS
                    # filters the RPMs automatically when the module build is
                    # done.
                    "filtered_rpms": [],
                }
                continue

            commit_hash = None
            version = None
            filtered_rpms = []
            module = self._get_module(
                module_name, module_stream, module_version, module_context, strict=True
            )
            if module.get("modulemd"):
                mmd = load_mmd(module["modulemd"])
                if mmd.get_xmd().get("mbs", {}).get("commit"):
                    commit_hash = mmd.get_xmd()["mbs"]["commit"]

                # Find out the particular NVR of filtered packages
                if "rpms" in module and mmd.get_rpm_filters():
                    for rpm in module["rpms"]:
                        nvr = kobo.rpmlib.parse_nvra(rpm)
                        # If the package is not filtered, continue
                        if not nvr["name"] in mmd.get_rpm_filters():
                            continue

                        # If the nvr is already in filtered_rpms, continue
                        nvr = kobo.rpmlib.make_nvr(nvr, force_epoch=True)
                        if nvr in filtered_rpms:
                            continue
                        filtered_rpms.append(nvr)

            if module.get("version"):
                version = module["version"]

            if version and commit_hash:
                new_requires[module_name] = {
                    "ref": commit_hash,
                    "stream": module_stream,
                    "version": str(version),
                    "context": module["context"],
                    "koji_tag": module["koji_tag"],
                    "filtered_rpms": filtered_rpms,
                }
            else:
                raise RuntimeError(
                    'The module "{0}" didn\'t contain either a commit hash or a'
                    " version in MBS".format(module_name)
                )
            # If the module is a base module, then import it in the database so that entries in
            # the module_builds_to_module_buildrequires table can be created later on
            if module_name in conf.base_module_names:
                import_mmd(db.session, mmd)

        return new_requires

    def get_modulemd_by_koji_tag(self, tag):
        resp = self.session.get(self.mbs_prod_url, params={"koji_tag": tag, "verbose": True})
        data = resp.json()
        if data["items"]:
            modulemd = data["items"][0]["modulemd"]
            return load_mmd(modulemd)
        else:
            return None

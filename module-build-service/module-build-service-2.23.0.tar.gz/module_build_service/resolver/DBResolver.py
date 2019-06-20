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
# Written by Matt Prahl <mprahl@redhat.com>
#            Jan Kaluza <jkaluza@redhat.com>

from sqlalchemy.orm import aliased

from module_build_service import log, db
from module_build_service.resolver.base import GenericResolver
from module_build_service import models
from module_build_service.errors import UnprocessableEntity
from module_build_service.utils.general import load_mmd
import sqlalchemy


class DBResolver(GenericResolver):
    """
    Resolver using the MBS database
    """

    backend = "db"

    def __init__(self, config):
        self.config = config

    def _get_module(
        self, name, stream, version, context, state=models.BUILD_STATES["ready"], strict=False
    ):
        with models.make_session(self.config) as session:
            mb = models.ModuleBuild.get_build_from_nsvc(
                session, name, stream, version, context, state=state)
            if mb:
                return mb.extended_json()

            if strict:
                raise UnprocessableEntity(
                    "Cannot find any module builds for %s:%s" % (name, stream))

    def get_module_count(self, **kwargs):
        """
        Determine the number of modules that match the provided filter.

        :return: the number of modules that match the provided filter
        :rtype: int
        """
        with models.make_session(self.config) as session:
            return models.ModuleBuild.get_module_count(session, **kwargs)

    def get_latest_with_virtual_stream(self, name, virtual_stream):
        """
        Get the latest module with the input virtual stream based on the stream version and version.

        :param str name: the module name to search for
        :param str virtual_stream: the module virtual stream to search for
        :return: the module's modulemd or None
        :rtype: Modulemd.ModuleStream or None
        """
        with models.make_session(self.config) as session:
            query = session.query(models.ModuleBuild).filter_by(name=name)
            query = models.ModuleBuild._add_virtual_streams_filter(session, query, [virtual_stream])
            # Cast the version as an integer so that we get proper ordering
            module = query.order_by(
                models.ModuleBuild.stream_version.desc(),
                sqlalchemy.cast(models.ModuleBuild.version, db.BigInteger).desc(),
            ).first()

            if module:
                return load_mmd(module.modulemd)

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
        if version and context:
            mmd = self._get_module(name, stream, version, context, strict=strict)
            if mmd is None:
                return
            return [load_mmd(mmd["modulemd"])]

        with models.make_session(self.config) as session:
            if not version and not context:
                if stream_version_lte and (
                    len(str(models.ModuleBuild.get_stream_version(stream, right_pad=False))) >= 5
                ):
                    stream_version = models.ModuleBuild.get_stream_version(stream)
                    builds = models.ModuleBuild.get_last_builds_in_stream_version_lte(
                        session, name, stream_version, virtual_streams)
                elif not stream_version_lte and virtual_streams:
                    builds = models.ModuleBuild.get_last_builds_in_stream_version_lte(
                        session, name, None, virtual_streams)
                else:
                    builds = models.ModuleBuild.get_last_builds_in_stream(session, name, stream)
            else:
                raise NotImplementedError(
                    "This combination of name/stream/version/context is not implemented")

            if not builds and strict:
                raise UnprocessableEntity(
                    "Cannot find any module builds for %s:%s" % (name, stream))
            return [build.mmd() for build in builds]

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
        log.debug("Looking for %s:%s buildrequiring %s", name, stream, base_module_nsvc)
        with models.make_session(self.config) as session:
            query = session.query(models.ModuleBuild)
            query = query.filter_by(name=name, stream=stream, state=models.BUILD_STATES["ready"])

            module_br_alias = aliased(models.ModuleBuild, name="module_br")
            # Shorten this table name for clarity in the query below
            mb_to_br = models.module_builds_to_module_buildrequires
            # The following joins get added:
            # JOIN module_builds_to_module_buildrequires
            #     ON module_builds_to_module_buildrequires.module_id = module_builds.id
            # JOIN module_builds AS module_br
            #     ON module_builds_to_module_buildrequires.module_buildrequire_id = module_br.id
            query = query.join(mb_to_br, mb_to_br.c.module_id == models.ModuleBuild.id).join(
                module_br_alias, mb_to_br.c.module_buildrequire_id == module_br_alias.id)

            # Get only modules buildrequiring particular base_module_nsvc
            n, s, v, c = base_module_nsvc.split(":")
            query = query.filter(
                module_br_alias.name == n,
                module_br_alias.stream == s,
                module_br_alias.version == v,
                module_br_alias.context == c,
            )
            query = query.order_by(
                sqlalchemy.cast(models.ModuleBuild.version, db.BigInteger).desc())
            all_builds = query.all()

            # The `all_builds` list contains builds sorted by "build.version". We need only
            # the builds with latest version, but in all contexts.
            builds = []
            latest_version = None
            for build in all_builds:
                if latest_version is None:
                    latest_version = build.version
                if latest_version != build.version:
                    break
                builds.append(build)

            mmds = [build.mmd() for build in builds]
            nsvcs = [
                mmd.get_nsvc()
                for mmd in mmds
            ]
            log.debug("Found: %r", nsvcs)
            return mmds

    def resolve_profiles(self, mmd, keys):
        """
        Returns a dictionary with keys set according the `keys` parameters and values
        set to the union of all components defined in all installation profiles matching
        the key in all buildrequires. If there are some modules loaded by
        utils.load_local_builds(...), these local modules will be considered when returning
        the profiles.
        :param mmd: Modulemd.ModuleStream instance representing the module
        :param keys: list of modulemd installation profiles to include in the result
        :return: a dictionary
        """
        results = {}
        for key in keys:
            results[key] = set()
        with models.make_session(self.config) as session:
            for module_name, module_info in mmd.get_xmd()["mbs"]["buildrequires"].items():
                local_modules = models.ModuleBuild.local_modules(
                    session, module_name, module_info["stream"])
                if local_modules:
                    local_module = local_modules[0]
                    log.info("Using local module {0!r} to resolve profiles.".format(local_module))
                    dep_mmd = local_module.mmd()
                    for key in keys:
                        profile = dep_mmd.get_profile(key)
                        if profile:
                            results[key] |= set(profile.get_rpms())
                    continue

                build = models.ModuleBuild.get_build_from_nsvc(
                    session,
                    module_name,
                    module_info["stream"],
                    module_info["version"],
                    module_info["context"],
                    state=models.BUILD_STATES["ready"],
                )
                if not build:
                    raise UnprocessableEntity(
                        "The module {}:{}:{}:{} was not found".format(
                            module_name,
                            module_info["stream"],
                            module_info["version"],
                            module_info["context"],
                        )
                    )
                dep_mmd = build.mmd()

                # Take note of what rpms are in this dep's profile
                for key in keys:
                    profile = dep_mmd.get_profile(key)
                    if profile:
                        results[key] |= set(profile.get_rpms())

        # Return the union of all rpms in all profiles of the given keys
        return results

    def get_module_build_dependencies(
        self, name=None, stream=None, version=None, context=None, mmd=None, strict=False
    ):
        """
        Returns a dictionary of koji_tag:[mmd, ...] of all the dependencies of input module.

        Although it is expected that single Koji tag always contain just single module build,
        it does not have to be a true for Offline local builds which use the local repository
        identifier as `koji_tag`.

        :kwarg name: a string of a module's name (required if mmd is not set)
        :kwarg stream: a string of a module's stream (required if mmd is not set)
        :kwarg version: a string of a module's version (required if mmd is not set)
        :kwarg context: a string of a module's context (required if mmd is not set)
        :kwarg mmd: Modulemd.ModuleStream object. If this is set, the mmd will be used instead of
            querying the DB with the name, stream, version, and context.
        :kwarg strict: Normally this function returns None if no module can be
            found.  If strict=True, then an UnprocessableEntity is raised.
        :return: a dictionary
        """
        if mmd:
            log.debug("get_module_build_dependencies(mmd={0!r} strict={1!r})".format(mmd, strict))
        elif any(x is None for x in [name, stream, version, context]):
            raise RuntimeError("The name, stream, version, and/or context weren't specified")
        else:
            version = str(version)
            log.debug(
                "get_module_build_dependencies({0}, strict={1!r})".format(
                    ", ".join([name, stream, str(version), context]), strict)
            )

        module_tags = {}
        with models.make_session(self.config) as session:
            if mmd:
                queried_mmd = mmd
                nsvc = ":".join([
                    mmd.get_module_name(),
                    mmd.get_stream_name(),
                    str(mmd.get_version()),
                    mmd.get_context() or models.DEFAULT_MODULE_CONTEXT,
                ])
            else:
                build = models.ModuleBuild.get_build_from_nsvc(
                    session, name, stream, version, context)
                if not build:
                    raise UnprocessableEntity(
                        "The module {} was not found".format(
                            ":".join([name, stream, version, context]))
                    )
                queried_mmd = build.mmd()
                nsvc = ":".join([name, stream, version, context])

            xmd_mbs = queried_mmd.get_xmd().get("mbs", {})
            if "buildrequires" not in xmd_mbs:
                raise RuntimeError(
                    "The module {} did not contain its modulemd or did not have "
                    "its xmd attribute filled out in MBS".format(nsvc)
                )

            buildrequires = xmd_mbs["buildrequires"]
            for br_name, details in buildrequires.items():
                build = models.ModuleBuild.get_build_from_nsvc(
                    session,
                    br_name,
                    details["stream"],
                    details["version"],
                    details["context"],
                    state=models.BUILD_STATES["ready"],
                )
                if not build:
                    raise RuntimeError(
                        "Buildrequired module %s %r does not exist in MBS db" % (br_name, details))

                # If the buildrequire is a meta-data only module with no Koji tag set, then just
                # skip it
                if build.koji_tag is None:
                    continue
                module_tags.setdefault(build.koji_tag, [])
                module_tags[build.koji_tag].append(build.mmd())

        return module_tags

    def resolve_requires(self, requires):
        """
        Resolves the requires list of N:S or N:S:V:C to a dictionary with keys as
        the module name and the values as a dictionary with keys of ref,
        stream, version.
        If there are some modules loaded by utils.load_local_builds(...), these
        local modules will be considered when resolving the requires. A RuntimeError
        is raised on DB lookup errors.
        :param requires: a list of N:S or N:S:V:C strings
        :return: a dictionary
        """
        new_requires = {}
        with models.make_session(self.config) as session:
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

                local_modules = models.ModuleBuild.local_modules(
                    session, module_name, module_stream)
                if local_modules:
                    local_build = local_modules[0]
                    new_requires[module_name] = {
                        "ref": None,
                        "stream": local_build.stream,
                        "version": local_build.version,
                        "context": local_build.context,
                        "koji_tag": local_build.koji_tag,
                    }
                    continue

                if module_version is None or module_context is None:
                    build = models.ModuleBuild.get_last_build_in_stream(
                        session, module_name, module_stream)
                else:
                    build = models.ModuleBuild.get_build_from_nsvc(
                        session, module_name, module_stream, module_version, module_context)

                if not build:
                    raise UnprocessableEntity("The module {} was not found".format(nsvc))

                commit_hash = None
                mmd = build.mmd()
                mbs_xmd = mmd.get_xmd().get("mbs", {})
                if mbs_xmd.get("commit"):
                    commit_hash = mbs_xmd["commit"]
                else:
                    raise RuntimeError(
                        'The module "{0}" didn\'t contain a commit hash in its xmd'.format(
                            module_name)
                    )

                if not mbs_xmd.get("mse"):
                    raise RuntimeError(
                        'The module "{}" is not built using Module Stream Expansion. '
                        "Please rebuild this module first".format(nsvc)
                    )

                new_requires[module_name] = {
                    "ref": commit_hash,
                    "stream": module_stream,
                    "version": build.version,
                    "context": build.context,
                    "koji_tag": build.koji_tag,
                }

        return new_requires

    def get_modulemd_by_koji_tag(self, tag):
        with models.make_session(self.config) as session:
            module = models.ModuleBuild.get_build_by_koji_tag(session, tag)
            return module.mmd() if module else None

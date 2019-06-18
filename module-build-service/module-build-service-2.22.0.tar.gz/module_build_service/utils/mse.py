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
# Written by Ralph Bean <rbean@redhat.com>
#            Matt Prahl <mprahl@redhat.com>
#            Jan Kaluza <jkaluza@redhat.com>
from module_build_service import log, models, Modulemd, db, conf
from module_build_service.errors import StreamAmbigous
from module_build_service.errors import UnprocessableEntity
from module_build_service.mmd_resolver import MMDResolver
from module_build_service.utils.general import deps_to_dict, mmd_to_str
import module_build_service.resolver


def _expand_mse_streams(session, name, streams, default_streams, raise_if_stream_ambigous):
    """
    Helper method for `expand_mse_stream()` expanding single name:[streams].
    Returns list of expanded streams.

    :param session: SQLAlchemy DB session.
    :param str name: Name of the module which will be expanded.
    :param streams: List of streams to expand.
    :type streams: list[str]
    :param dict default_streams: Dict in {module_name: module_stream, ...} format defining
        the default stream to choose for module in case when there are multiple streams to
        choose from.
    :param bool raise_if_stream_ambigous: When True, raises a StreamAmbigous exception in case
        there are multiple streams for some dependency of module and the module name is not
        defined in `default_streams`, so it is not clear which stream should be used.
    """
    default_streams = default_streams or {}
    # Stream can be prefixed with '-' sign to define that this stream should
    # not appear in a resulting list of streams. There can be two situations:
    # a) all streams have '-' prefix. In this case, we treat list of streams
    #    as blacklist and we find all the valid streams and just remove those with
    #    '-' prefix.
    # b) there is at least one stream without '-' prefix. In this case, we can
    #    ignore all the streams with '-' prefix and just add those without
    #    '-' prefix to the list of valid streams.
    streams_is_blacklist = all(stream.startswith("-") for stream in streams)
    if streams_is_blacklist or len(streams) == 0:
        if name in default_streams:
            expanded_streams = [default_streams[name]]
        elif raise_if_stream_ambigous:
            raise StreamAmbigous("There are multiple streams to choose from for module %s." % name)
        else:
            builds = models.ModuleBuild.get_last_build_in_all_streams(session, name)
            expanded_streams = [build.stream for build in builds]
    else:
        expanded_streams = []
    for stream in streams:
        if stream.startswith("-"):
            if streams_is_blacklist and stream[1:] in expanded_streams:
                expanded_streams.remove(stream[1:])
        else:
            expanded_streams.append(stream)

    if len(expanded_streams) > 1:
        if name in default_streams:
            expanded_streams = [default_streams[name]]
        elif raise_if_stream_ambigous:
            raise StreamAmbigous(
                "There are multiple streams %r to choose from for module %s."
                % (expanded_streams, name)
            )

    return expanded_streams


def expand_mse_streams(session, mmd, default_streams=None, raise_if_stream_ambigous=False):
    """
    Expands streams in both buildrequires/requires sections of MMD.

    :param session: SQLAlchemy DB session.
    :param Modulemd.ModuleStream mmd: Modulemd metadata with original unexpanded module.
    :param dict default_streams: Dict in {module_name: module_stream, ...} format defining
        the default stream to choose for module in case when there are multiple streams to
        choose from.
    :param bool raise_if_stream_ambigous: When True, raises a StreamAmbigous exception in case
        there are multiple streams for some dependency of module and the module name is not
        defined in `default_streams`, so it is not clear which stream should be used.
    """
    for deps in mmd.get_dependencies():
        new_deps = Modulemd.Dependencies()
        for name in deps.get_runtime_modules():
            streams = deps.get_runtime_streams(name)
            new_streams = _expand_mse_streams(
                session, name, streams, default_streams, raise_if_stream_ambigous)

            if new_streams == []:
                new_deps.set_empty_runtime_dependencies_for_module(name)
            else:
                for stream in new_streams:
                    new_deps.add_runtime_stream(name, stream)

        for name in deps.get_buildtime_modules():
            streams = deps.get_buildtime_streams(name)
            new_streams = _expand_mse_streams(
                session, name, streams, default_streams, raise_if_stream_ambigous)

            if new_streams == []:
                new_deps.set_empty_buildtime_dependencies_for_module(name)
            else:
                for stream in new_streams:
                    new_deps.add_buildtime_stream(name, stream)

        # Replace the Dependencies object
        mmd.remove_dependencies(deps)
        mmd.add_dependencies(new_deps)


def _get_mmds_from_requires(
    requires,
    mmds,
    recursive=False,
    default_streams=None,
    raise_if_stream_ambigous=False,
    base_module_mmds=None,
):
    """
    Helper method for get_mmds_required_by_module_recursively returning
    the list of module metadata objects defined by `requires` dict.

    :param dict requires: requires or buildrequires in the form {module: [streams]}
    :param mmds: Dictionary with already handled name:streams as a keys and lists
        of resulting mmds as values.
    :param recursive: If True, the requires are checked recursively.
    :param dict default_streams: Dict in {module_name: module_stream, ...} format defining
        the default stream to choose for module in case when there are multiple streams to
        choose from.
    :param bool raise_if_stream_ambigous: When True, raises a StreamAmbigous exception in case
        there are multiple streams for some dependency of module and the module name is not
        defined in `default_streams`, so it is not clear which stream should be used.
    :param list base_module_mmds: List of modulemd metadata instances. When set, the
        returned list contains MMDs build against each base module defined in
        `base_module_mmds` list.
    :return: Dict with name:stream as a key and list with mmds as value.
    """
    default_streams = default_streams or {}
    # To be able to call itself recursively, we need to store list of mmds
    # we have added to global mmds list in this particular call.
    added_mmds = {}
    resolver = module_build_service.resolver.system_resolver

    for name, streams in requires.items():
        # Base modules are already added to `mmds`.
        if name in conf.base_module_names:
            continue

        streams_to_try = streams
        if name in default_streams:
            streams_to_try = [default_streams[name]]
        elif len(streams_to_try) > 1 and raise_if_stream_ambigous:
            raise StreamAmbigous(
                "There are multiple streams %r to choose from for module %s."
                % (streams_to_try, name)
            )

        # For each valid stream, find the last build in a stream and also all
        # its contexts and add mmds of these builds to `mmds` and `added_mmds`.
        # Of course only do that if we have not done that already in some
        # previous call of this method.
        for stream in streams:
            ns = "%s:%s" % (name, stream)
            if ns not in mmds:
                mmds[ns] = []
            if ns not in added_mmds:
                added_mmds[ns] = []

            if base_module_mmds:
                for base_module_mmd in base_module_mmds:
                    base_module_nsvc = base_module_mmd.get_nsvc()
                    mmds[ns] += resolver.get_buildrequired_modulemds(name, stream, base_module_nsvc)
            else:
                mmds[ns] = resolver.get_module_modulemds(name, stream, strict=True)
            added_mmds[ns] += mmds[ns]

    # Get the requires recursively.
    if recursive:
        for mmd_list in added_mmds.values():
            for mmd in mmd_list:
                for deps in mmd.get_dependencies():
                    deps_dict = deps_to_dict(deps, 'runtime')
                    mmds = _get_mmds_from_requires(
                        deps_dict, mmds, True, base_module_mmds=base_module_mmds)

    return mmds


def _get_base_module_mmds(mmd):
    """
    Returns list of MMDs of base modules buildrequired by `mmd` including the compatible
    old versions of the base module based on the stream version.

    :param Modulemd mmd: Input modulemd metadata.
    :rtype: list of Modulemd
    :return: List of MMDs of base modules buildrequired by `mmd`.
    """
    seen = set()
    ret = []

    resolver = module_build_service.resolver.system_resolver
    for deps in mmd.get_dependencies():
        buildrequires = {
            module: deps.get_buildtime_streams(module)
            for module in deps.get_buildtime_modules()
        }
        for name in conf.base_module_names:
            if name not in buildrequires.keys():
                continue

            # Since the query below uses stream_version_lte, we can sort the streams by stream
            # version in descending order to not perform unnecessary queries. Otherwise, if the
            # streams are f29.1.0 and f29.2.0, then two queries will occur, causing f29.1.0 to be
            # returned twice. Only one query for that scenario is necessary.
            sorted_desc_streams = sorted(
                buildrequires[name], reverse=True, key=models.ModuleBuild.get_stream_version)
            for stream in sorted_desc_streams:
                ns = ":".join([name, stream])
                if ns in seen:
                    continue

                # Get the MMD for particular buildrequired name:stream to find out the virtual
                # streams according to which we can find the compatible streams later.
                # The returned MMDs are all the module builds for name:stream in the highest
                # version. Given the base module does not depend on other modules, it can appear
                # only in single context and therefore the `mmds` should always contain just
                # zero or one module build.
                mmds = resolver.get_module_modulemds(name, stream)
                if not mmds:
                    continue
                stream_mmd = mmds[0]

                # Get the list of compatible virtual streams.
                xmd = stream_mmd.get_xmd()
                virtual_streams = xmd.get("mbs", {}).get("virtual_streams")

                # In case there are no virtual_streams in the buildrequired name:stream,
                # it is clear that there are no compatible streams, so return just this
                # `stream_mmd`.
                if not virtual_streams:
                    seen.add(ns)
                    ret.append(stream_mmd)
                    continue

                virtual_streams = xmd["mbs"]["virtual_streams"]

                if conf.allow_only_compatible_base_modules:
                    stream_version_lte = True
                else:
                    stream_version_lte = False

                mmds = resolver.get_module_modulemds(
                    name, stream, stream_version_lte=stream_version_lte,
                    virtual_streams=virtual_streams)
                ret_chunk = []
                # Add the returned mmds to the `seen` set to avoid querying those individually if
                # they are part of the buildrequire streams for this base module
                for mmd_ in mmds:
                    mmd_ns = ":".join([mmd_.get_module_name(), mmd_.get_stream_name()])
                    # An extra precaution to ensure there are no duplicates in the event the sorting
                    # above wasn't flawless
                    if mmd_ns not in seen:
                        ret_chunk.append(mmd_)
                        seen.add(mmd_ns)
                ret += ret_chunk
                # Just in case it was queried for but MBS didn't find it
                seen.add(ns)
            break
    return ret


def get_mmds_required_by_module_recursively(
    mmd, default_streams=None, raise_if_stream_ambigous=False
):
    """
    Returns the list of Module metadata objects of all modules required while
    building the module defined by `mmd` module metadata. This presumes the
    module metadata streams are expanded using `expand_mse_streams(...)`
    method.

    This method finds out latest versions of all the build-requires of
    the `mmd` module and then also all contexts of these latest versions.

    For each build-required name:stream:version:context module, it checks
    recursively all the "requires" and finds the latest version of each
    required module and also all contexts of these latest versions.

    :param dict default_streams: Dict in {module_name: module_stream, ...} format defining
        the default stream to choose for module in case when there are multiple streams to
        choose from.
    :param bool raise_if_stream_ambigous: When True, raises a StreamAmbigous exception in case
        there are multiple streams for some dependency of module and the module name is not
        defined in `default_streams`, so it is not clear which stream should be used.
    :rtype: list of Modulemd metadata
    :return: List of all modulemd metadata of all modules required to build
        the module `mmd`.
    """
    # We use dict with name:stream as a key and list with mmds as value.
    # That way, we can ensure we won't have any duplicate mmds in a resulting
    # list and we also don't waste resources on getting the modules we already
    # handled from DB.
    mmds = {}

    # Get the MMDs of all compatible base modules based on the buildrequires.
    base_module_mmds = _get_base_module_mmds(mmd)
    if not base_module_mmds:
        base_module_choices = " or ".join(conf.base_module_names)
        raise UnprocessableEntity(
            "None of the base module ({}) streams in the buildrequires section could be found"
            .format(base_module_choices)
        )

    # Add base modules to `mmds`.
    for base_module in base_module_mmds:
        ns = ":".join([base_module.get_module_name(), base_module.get_stream_name()])
        mmds.setdefault(ns, [])
        mmds[ns].append(base_module)

    # Get all the buildrequires of the module of interest.
    for deps in mmd.get_dependencies():
        deps_dict = deps_to_dict(deps, 'buildtime')
        mmds = _get_mmds_from_requires(
            deps_dict, mmds, False, default_streams, raise_if_stream_ambigous, base_module_mmds)

    # Now get the requires of buildrequires recursively.
    for mmd_key in list(mmds.keys()):
        for mmd in mmds[mmd_key]:
            for deps in mmd.get_dependencies():
                deps_dict = deps_to_dict(deps, 'runtime')
                mmds = _get_mmds_from_requires(
                    deps_dict,
                    mmds,
                    True,
                    default_streams,
                    raise_if_stream_ambigous,
                    base_module_mmds,
                )

    # Make single list from dict of lists.
    res = []
    for ns, mmds_list in mmds.items():
        if len(mmds_list) == 0:
            raise UnprocessableEntity("Cannot find any module builds for %s" % (ns))
        res += mmds_list
    return res


def generate_expanded_mmds(session, mmd, raise_if_stream_ambigous=False, default_streams=None):
    """
    Returns list with MMDs with buildrequires and requires set according
    to module stream expansion rules. These module metadata can be directly
    built using MBS.

    :param session: SQLAlchemy DB session.
    :param Modulemd.ModuleStream mmd: Modulemd metadata with original unexpanded module.
    :param bool raise_if_stream_ambigous: When True, raises a StreamAmbigous exception in case
        there are multiple streams for some dependency of module and the module name is not
        defined in `default_streams`, so it is not clear which stream should be used.
    :param dict default_streams: Dict in {module_name: module_stream, ...} format defining
        the default stream to choose for module in case when there are multiple streams to
        choose from.
    """
    if not session:
        session = db.session

    if not default_streams:
        default_streams = {}

    # Create local copy of mmd, because we will expand its dependencies,
    # which would change the module.
    current_mmd = mmd.copy()

    # MMDResolver expects the input MMD to have no context.
    current_mmd.set_context(None)

    # Expands the MSE streams. This mainly handles '-' prefix in MSE streams.
    expand_mse_streams(session, current_mmd, default_streams, raise_if_stream_ambigous)

    # Get the list of all MMDs which this module can be possibly built against
    # and add them to MMDResolver.
    mmd_resolver = MMDResolver()
    mmds_for_resolving = get_mmds_required_by_module_recursively(
        current_mmd, default_streams, raise_if_stream_ambigous)
    for m in mmds_for_resolving:
        mmd_resolver.add_modules(m)

    # Show log.info message with the NSVCs we have added to mmd_resolver.
    nsvcs_to_solve = [m.get_nsvc() for m in mmds_for_resolving]
    log.info("Starting resolving with following input modules: %r", nsvcs_to_solve)

    # Resolve the dependencies between modules and get the list of all valid
    # combinations in which we can build this module.
    requires_combinations = mmd_resolver.solve(current_mmd)
    log.info("Resolving done, possible requires: %r", requires_combinations)

    # This is where we are going to store the generated MMDs.
    mmds = []
    for requires in requires_combinations:
        # Each generated MMD must be new Module object...
        mmd_copy = mmd.copy()
        xmd = mmd_copy.get_xmd()

        # Requires contain the NSVC representing the input mmd.
        # The 'context' of this NSVC defines the id of buildrequires/requires
        # pair in the mmd.get_dependencies().
        dependencies_id = None

        # We don't want to depend on ourselves, so store the NSVC of the current_mmd
        # to be able to ignore it later.
        self_nsvca = None

        # Dict to store name:stream pairs from nsvca, so we are able to access it
        # easily later.
        req_name_stream = {}

        # Get the values for dependencies_id, self_nsvca and req_name_stream variables.
        for nsvca in requires:
            req_name, req_stream, _, req_context, req_arch = nsvca.split(":")
            if req_arch == "src":
                assert req_name == current_mmd.get_module_name()
                assert req_stream == current_mmd.get_stream_name()
                assert dependencies_id is None
                assert self_nsvca is None
                dependencies_id = int(req_context)
                self_nsvca = nsvca
                continue
            req_name_stream[req_name] = req_stream
        if dependencies_id is None or self_nsvca is None:
            raise RuntimeError(
                "%s:%s not found in requires %r"
                % (current_mmd.get_module_name(), current_mmd.get_stream_name(), requires)
            )

        # The name:[streams, ...] pairs do not have to be the same in both
        # buildrequires/requires. In case they are the same, we replace the streams
        # in requires section with a single stream against which we will build this MMD.
        # In case they are not the same, we have to keep the streams as they are in requires
        # section.  We always replace stream(s) for build-requirement with the one we
        # will build this MMD against.
        new_deps = Modulemd.Dependencies()
        deps = mmd_copy.get_dependencies()[dependencies_id]
        deps_requires = deps_to_dict(deps, 'runtime')
        deps_buildrequires = deps_to_dict(deps, 'buildtime')
        for req_name, req_streams in deps_requires.items():
            if req_name not in deps_buildrequires:
                # This require is not a buildrequire so just copy this runtime requirement to
                # new_dep and don't touch buildrequires
                if req_streams == []:
                    new_deps.set_empty_runtime_dependencies_for_module(req_name)
                else:
                    for req_stream in req_streams:
                        new_deps.add_runtime_stream(req_name, req_stream)
            elif set(req_streams) != set(deps_buildrequires[req_name]):
                # Streams in runtime section are not the same as in buildtime section,
                # so just copy this runtime requirement to new_dep.
                if req_streams == []:
                    new_deps.set_empty_runtime_dependencies_for_module(req_name)
                else:
                    for req_stream in req_streams:
                        new_deps.add_runtime_stream(req_name, req_stream)

                new_deps.add_buildtime_stream(req_name, req_name_stream[req_name])
            else:
                # This runtime requirement has the same streams in both runtime/buildtime
                # requires sections, so replace streams in both sections by the one we
                # really used in this resolved variant.
                new_deps.add_runtime_stream(req_name, req_name_stream[req_name])
                new_deps.add_buildtime_stream(req_name, req_name_stream[req_name])

        # There might be buildrequires which are not in runtime requires list.
        # Such buildrequires must be copied to expanded MMD.
        for req_name, req_streams in deps_buildrequires.items():
            if req_name not in deps_requires:
                new_deps.add_buildtime_stream(req_name, req_name_stream[req_name])

        # Set the new dependencies.
        mmd_copy.remove_dependencies(deps)
        mmd_copy.add_dependencies(new_deps)

        # The Modulemd.Dependencies() stores only streams, but to really build this
        # module, we need NSVC of buildrequires, so we have to store this data in XMD.
        # We also need additional data like for example list of filtered_rpms. We will
        # get them using module_build_service.resolver.GenericResolver.resolve_requires,
        # so prepare list with NSVCs of buildrequires as an input for this method.
        br_list = []
        for nsvca in requires:
            if nsvca == self_nsvca:
                continue
            # Remove the arch from nsvca
            nsvc = ":".join(nsvca.split(":")[:-1])
            br_list.append(nsvc)

        # Resolve the buildrequires and store the result in XMD.
        if "mbs" not in xmd:
            xmd["mbs"] = {}
        resolver = module_build_service.resolver.system_resolver
        xmd["mbs"]["buildrequires"] = resolver.resolve_requires(br_list)
        xmd["mbs"]["mse"] = True

        mmd_copy.set_xmd(xmd)

        # Now we have all the info to actually compute context of this module.
        _, _, _, context = models.ModuleBuild.contexts_from_mmd(mmd_to_str(mmd_copy))
        mmd_copy.set_context(context)

        mmds.append(mmd_copy)

    return mmds

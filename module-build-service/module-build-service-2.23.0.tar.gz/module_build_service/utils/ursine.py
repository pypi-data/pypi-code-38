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
# Written by Chenxiong Qi <cqi@redhat.com>

import re

from module_build_service import conf, log
from module_build_service.resolver import system_resolver


"""
This module handles module stream collision with ursine content before a module
is built.

This kind of collision would happen when packages, which are managed by
Ursa-Major, are used to build a module. Let's see an example, when a module foo
buildrequires bar with stream A, however module bar with another stream B was
already added to ursine content by Ursa-Major when it has been built and moved
to ready state. Hence, MBS has to ensure any packages from module bar:B are not
present in the buildroot.

A technical background:

Generally, each module buildrequires a platform module, which is associated
with ursine content by adding an external repository to the platform module's
tag. That repository is generated from a build tag that inherits from a set
modules' koji tag through its tag inheritance hierarchy. Ursa-Major manages
the inheritance relationship.

Stream collision modules are just those modules added to tag inheritance by
Ursa-Major.
"""


def find_build_tags_from_external_repos(koji_session, repo_infos):
    """Find build tags from external repos

    An external repo added to a tag could be an arbitrary external repository.
    Hence, this method tries best to guess the tags from each external repo's
    URL by a regular expression.

    :param repo_infos: list of mappings represeting external repos information.
    :type repo_infos: list[dict]
    :return: a list of tag names.
    :rtype: list[str]
    """
    re_external_repo_url = r"^{}/repos/(.+-build)/latest/\$arch/?$".format(
        conf.koji_external_repo_url_prefix.rstrip("/"))
    tag_names = []
    for info in repo_infos:
        match = re.match(re_external_repo_url, info["url"])
        if match:
            name = match.groups()[0]
            if koji_session.getTag(name) is None:
                log.warning(
                    "Ignoring the found tag %s because no tag info was found with this name.",
                    name,
                )
            else:
                tag_names.append(name)
        else:
            log.warning(
                "The build tag could not be parsed from external repo %s whose url is %s.",
                info["external_repo_name"], info["url"],
            )
    return tag_names


def find_module_koji_tags(koji_session, build_tag):
    """
    Find module koji tags from parents of build tag through the tag inheritance

    MBS supports a few prefixes which are configured in
    ``conf.koij_tag_prefixes``. Tags with a configured prefix will be
    considered as a module's koji tag.

    :param koji_session: instance of Koji client session.
    :type koji_session: ClientSession
    :param str build_tag: tag name, which is the build tag inheriting from
        parent tags where module koji tags are contained.
    :return: list of module koji tags.
    :rtype: list[str]
    """
    return [
        data["name"]
        for data in koji_session.getFullInheritance(build_tag)
        if any(data["name"].startswith(prefix) for prefix in conf.koji_tag_prefixes)
    ]


def get_modulemds_from_ursine_content(tag):
    """Get all modules metadata which were added to ursine content

    Ursine content is the tag inheritance managed by Ursa-Major by adding
    specific modules' koji_tag.

    Background of module build based on ursine content:

    Each module build buildrequires a platform module, which is a presudo-module
    used to connect to an external repository whose packages will be present
    in the buildroot. In practice, the external repo is generated from a build
    tag which could inherit from a few module koji_tags so that those module's
    RPMs could be build dependencies for some specific packages.

    So, this function is to find out all module koji_tags from the build tag
    and return corresponding module metadata.

    :param str tag: a base module's koji_tag.
    :return: list of module metadata. Empty list will be returned if no ursine
        modules metadata is found.
    :rtype: list[Modulemd.Module]
    """
    from module_build_service.builder.KojiModuleBuilder import KojiModuleBuilder

    koji_session = KojiModuleBuilder.get_session(conf, login=False)
    repos = koji_session.getExternalRepoList(tag)
    build_tags = find_build_tags_from_external_repos(koji_session, repos)
    if not build_tags:
        log.debug("No external repo containing ursine content is found.")
        return []
    modulemds = []
    for tag in build_tags:
        koji_tags = find_module_koji_tags(koji_session, tag)
        for koji_tag in koji_tags:
            md = system_resolver.get_modulemd_by_koji_tag(koji_tag)
            if md:
                modulemds.append(md)
            else:
                log.warning("No module is found by koji_tag '%s'", koji_tag)
    return modulemds


def find_stream_collision_modules(buildrequired_modules, koji_tag):
    """
    Find buildrequired modules that are part of the ursine content represented
    by the koji_tag but with a different stream.

    :param dict buildrequired_modules: a mapping of buildrequires, which is just
        the ``xmd/mbs/buildrequires``. This mapping is used to determine if a module
        found from ursine content is a buildrequire with different stream.
    :param str koji_tag: a base module's koji_tag. Modules will be retrieved from
        ursine content associated with this koji_tag and check if there are
        modules that collide.
    :return: a list of NSVC of collision modules. If no collision module is
        found, an empty list is returned.
    :rtype: list[str]
    """
    ursine_modulemds = get_modulemds_from_ursine_content(koji_tag)
    if not ursine_modulemds:
        log.debug("No module metadata is found from ursine content.")
        return []

    collision_modules = [
        item.get_nsvc()
        for item in ursine_modulemds
        # If some module in the ursine content is one of the buildrequires but has
        # different stream, that is what we want to record here, whose RPMs will be
        # excluded from buildroot by adding them into SRPM module-build-macros as
        # Conflicts.
        if (
            item.get_module_name() in buildrequired_modules
            and item.get_stream_name() != buildrequired_modules[item.get_module_name()]["stream"]
        )
    ]

    for item in collision_modules:
        name, stream, _ = item.split(":", 2)
        log.info(
            "Buildrequired module %s exists in ursine content with "
            "different stream %s, whose RPMs will be excluded.",
            name, stream,
        )

    return collision_modules


def handle_stream_collision_modules(mmd):
    """
    Find out modules from ursine content and record those that are buildrequire
    module but have different stream. And finally, record built RPMs of these
    found modules for later use to exclude them from buildroot.

    Note that this depends on the result of module stream expansion.

    MBS supports multiple base modules via option conf.base_module_names. A base
    module name could be platform in most cases, but there could be others for
    particular cases in practice. So, each expanded base module stored in
    ``xmd/mbs/buildrequires`` will be handled and will have a new
    key/value pair ``stream_collision_modules: [N-S-V-C, ...]``. This key/value
    will then be handled by the module event handler.

    As a result, a new item is added xmd/mbs/buildrequires/platform/stream_collision_modules,
    which is a list of NSVC strings. Each of them is the module added to ursine
    content by Ursa-Major.

    :param mmd: a module's metadata which will be built.
    :type mmd: Modulemd.Module
    """
    log.info("Start to find out stream collision modules.")
    xmd = mmd.get_xmd()
    buildrequires = xmd["mbs"]["buildrequires"]

    for module_name in conf.base_module_names:
        base_module_info = buildrequires.get(module_name)
        if base_module_info is None:
            log.info(
                "Base module %s is not a buildrequire of module %s. "
                "Skip handling module stream collision for this base module.",
                module_name, mmd.get_module_name(),
            )
            continue

        # Module stream collision is handled only for newly created module
        # build. However, if a build is resumed and restarted from init
        # state, we have to ensure stream collision is not handled twice for a
        # base module.
        # Just check the existence, and following code ensures this key exists
        # even if no stream collision module is found.
        if "stream_collision_modules" in base_module_info and "ursine_rpms" in base_module_info:
            log.debug(
                "Base module %s has stream collision modules and ursine "
                "rpms. Skip to handle stream collision again for it.",
                module_name,
            )
            continue

        modules_nsvc = find_stream_collision_modules(buildrequires, base_module_info["koji_tag"])

        if modules_nsvc:
            # Save modules NSVC for later use in subsequent event handlers to
            # log readable messages.
            base_module_info["stream_collision_modules"] = modules_nsvc
            base_module_info["ursine_rpms"] = find_module_built_rpms(modules_nsvc)
        else:
            log.info("No stream collision module is found against base module %s.", module_name)
            # Always set in order to mark it as handled already.
            base_module_info["stream_collision_modules"] = None
            base_module_info["ursine_rpms"] = None

    mmd.set_xmd(xmd)


def find_module_built_rpms(modules_nsvc):
    """Find out built RPMs of given modules

    :param modules_nsvc: a list of modules' NSVC to find out built RPMs for
        each of them.
    :type modules_nsvc: list[str]
    :return: a sorted list of RPMs, each of them is represented as NEVR.
    :rtype: list[str]
    """
    import kobo.rpmlib
    from module_build_service.resolver import GenericResolver
    from module_build_service.builder.KojiModuleBuilder import KojiModuleBuilder

    resolver = GenericResolver.create(conf)

    built_rpms = []
    koji_session = KojiModuleBuilder.get_session(conf, login=False)

    for nsvc in modules_nsvc:
        name, stream, version, context = nsvc.split(":")
        module = resolver._get_module(name, stream, version, context, strict=True)
        rpms = koji_session.listTaggedRPMS(module["koji_tag"], latest=True)[0]
        built_rpms.extend(kobo.rpmlib.make_nvr(rpm, force_epoch=True) for rpm in rpms)

    # In case there is duplicate NEVRs, ensure every NEVR is unique in the final list.
    # And, sometimes, sorted list of RPMs would be easier to read.
    return sorted(set(built_rpms))

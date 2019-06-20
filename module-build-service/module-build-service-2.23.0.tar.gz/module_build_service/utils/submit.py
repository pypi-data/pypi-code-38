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
import json
import math
import re
import time
import shutil
import tempfile
import os
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import copy

import kobo.rpmlib
import requests
from gi.repository import GLib

import module_build_service.scm
from module_build_service import conf, db, log, models, Modulemd
from module_build_service.errors import ValidationError, UnprocessableEntity, Forbidden, Conflict
from module_build_service.utils import (
    to_text_type, deps_to_dict, mmd_to_str, load_mmd, load_mmd_file,
    get_build_arches
)


def record_module_build_arches(mmd, build, session):
    """
    Finds out the list of build arches against which the ModuleBuld `build` should be built
    and records them to `build.arches`.

    :param Modulemd mmd: The MMD file associated with a ModuleBuild.
    :param ModuleBuild build: The ModuleBuild.
    :param session: Database session.
    """
    arches = get_build_arches(mmd, conf)
    for arch in arches:
        arch_obj = session.query(models.ModuleArch).filter_by(name=arch).first()
        if not arch_obj:
            arch_obj = models.ModuleArch(name=arch)
            session.add(arch_obj)
            session.commit()

        if arch_obj not in build.arches:
            build.arches.append(arch_obj)
            session.add(build)


def record_filtered_rpms(mmd):
    """Record filtered RPMs that should not be installed into buildroot

    These RPMs are filtered:

    * Reads the mmd["xmd"]["buildrequires"] and extends it with "filtered_rpms"
      list containing the NVRs of filtered RPMs in a buildrequired module.

    :param Modulemd mmd: Modulemd that will be built next.
    :rtype: Modulemd.Module
    :return: Modulemd extended with the "filtered_rpms" in XMD section.
    """
    # Imported here to allow import of utils in GenericBuilder.
    from module_build_service.builder import GenericBuilder
    from module_build_service.resolver import GenericResolver

    resolver = GenericResolver.create(conf)
    builder = GenericBuilder.backends[conf.system]

    new_buildrequires = {}
    for req_name, req_data in mmd.get_xmd()["mbs"]["buildrequires"].items():
        # In case this is module resubmit or local build, the filtered_rpms
        # will already be there, so there is no point in generating them again.
        if "filtered_rpms" in req_data:
            new_buildrequires[req_name] = req_data
            continue

        # We can just get the first modulemd data from result right here thanks to
        # strict=True, so in case the module cannot be found, get_module_modulemds
        # raises an exception.
        req_mmd = resolver.get_module_modulemds(
            req_name, req_data["stream"], req_data["version"], req_data["context"], True)[0]

        # Find out the particular NVR of filtered packages
        filtered_rpms = []
        rpm_filter = req_mmd.get_rpm_filters()
        if rpm_filter:
            built_nvrs = builder.get_built_rpms_in_module_build(req_mmd)
            for nvr in built_nvrs:
                parsed_nvr = kobo.rpmlib.parse_nvr(nvr)
                if parsed_nvr["name"] in rpm_filter:
                    filtered_rpms.append(nvr)
        req_data["filtered_rpms"] = filtered_rpms

        new_buildrequires[req_name] = req_data

    # Replace the old buildrequires with new ones.
    xmd = mmd.get_xmd()
    xmd["mbs"]["buildrequires"] = new_buildrequires
    mmd.set_xmd(xmd)
    return mmd


def _scm_get_latest(pkg):
    try:
        # If the modulemd specifies that the 'f25' branch is what
        # we want to pull from, we need to resolve that f25 branch
        # to the specific commit available at the time of
        # submission (now).
        repo = pkg.get_repository()
        ref = pkg.get_ref()
        log.debug("Getting the commit hash for the ref %s on the repo %s", ref, repo)
        pkgref = module_build_service.scm.SCM(repo).get_latest(ref)
    except Exception as e:
        log.exception(e)
        return {
            "error": "Failed to get the latest commit for %s#%s"
            % (pkg.get_repository(), pkg.get_ref())
        }

    return {"pkg_name": pkg.get_name(), "pkg_ref": pkgref, "error": None}


def format_mmd(mmd, scmurl, module=None, session=None):
    """
    Prepares the modulemd for the MBS. This does things such as replacing the
    branches of components with commit hashes and adding metadata in the xmd
    dictionary.
    :param mmd: the Modulemd.ModuleStream object to format
    :param scmurl: the url to the modulemd
    :param module: When specified together with `session`, the time_modified
        of a module is updated regularly in case this method takes lot of time.
    :param session: Database session to update the `module`.
    """
    # Import it here, because SCM uses utils methods and fails to import
    # them because of dep-chain.
    from module_build_service.scm import SCM

    xmd = mmd.get_xmd()
    if "mbs" not in xmd:
        xmd["mbs"] = {}
    if "scmurl" not in xmd["mbs"]:
        xmd["mbs"]["scmurl"] = scmurl or ""
    if "commit" not in xmd["mbs"]:
        xmd["mbs"]["commit"] = ""

    # If module build was submitted via yaml file, there is no scmurl
    if scmurl:
        scm = SCM(scmurl)
        # We want to make sure we have the full commit hash for consistency
        if SCM.is_full_commit_hash(scm.scheme, scm.commit):
            full_scm_hash = scm.commit
        else:
            full_scm_hash = scm.get_full_commit_hash()

        xmd["mbs"]["commit"] = full_scm_hash

    if mmd.get_rpm_component_names() or mmd.get_module_component_names():
        if "rpms" not in xmd["mbs"]:
            xmd["mbs"]["rpms"] = {}
        # Add missing data in RPM components
        for pkgname in mmd.get_rpm_component_names():
            pkg = mmd.get_rpm_component(pkgname)
            # In case of resubmit of existing module which have been
            # cancelled/failed during the init state, the package
            # was maybe already handled by MBS, so skip it in this case.
            if pkgname in xmd["mbs"]["rpms"]:
                continue
            if pkg.get_repository() and not conf.rpms_allow_repository:
                raise Forbidden(
                    "Custom component repositories aren't allowed.  "
                    "%r bears repository %r" % (pkgname, pkg.get_repository())
                )
            if pkg.get_cache() and not conf.rpms_allow_cache:
                raise Forbidden(
                    "Custom component caches aren't allowed.  "
                    "%r bears cache %r" % (pkgname, pkg.get_cache())
                )
            if pkg.get_buildonly() is True:
                raise ValidationError('The usage of "buildonly" is not yet supported')
            if pkg.get_buildafter():
                raise ValidationError('The usage of "buildafter" is not yet supported')
            if not pkg.get_repository():
                pkg.set_repository(conf.rpms_default_repository + pkgname)
            if not pkg.get_cache():
                pkg.set_cache(conf.rpms_default_cache + pkgname)
            if not pkg.get_ref():
                pkg.set_ref("master")
            if not pkg.get_arches():
                for arch in conf.arches:
                    pkg.add_restricted_arch(arch)

        # Add missing data in included modules components
        for modname in mmd.get_module_component_names():
            mod = mmd.get_module_component(modname)
            if mod.get_repository() and not conf.modules_allow_repository:
                raise Forbidden(
                    "Custom module repositories aren't allowed.  "
                    "%r bears repository %r" % (modname, mod.get_repository())
                )
            if not mod.get_repository():
                mod.set_repository(conf.modules_default_repository + modname)
            if not mod.get_ref():
                mod.set_ref("master")

        # Check that SCM URL is valid and replace potential branches in pkg refs
        # by real SCM hash and store the result to our private xmd place in modulemd.
        pool = ThreadPool(20)
        try:
            # Filter out the packages which we have already resolved in possible
            # previous runs of this method (can be caused by module build resubmition).
            pkgs_to_resolve = [
                mmd.get_rpm_component(name)
                for name in mmd.get_rpm_component_names()
                if name not in xmd["mbs"]["rpms"]
            ]
            async_result = pool.map_async(_scm_get_latest, pkgs_to_resolve)

            # For modules with lot of components, the _scm_get_latest can take a lot of time.
            # We need to bump time_modified from time to time, otherwise poller could think
            # that module is stuck in "init" state and it would send fake "init" message.
            while not async_result.ready():
                async_result.wait(60)
                if module and session:
                    module.time_modified = datetime.utcnow()
                    session.commit()
            pkg_dicts = async_result.get()
        finally:
            pool.close()

        err_msg = ""
        for pkg_dict in pkg_dicts:
            if pkg_dict["error"]:
                err_msg += pkg_dict["error"] + "\n"
            else:
                pkg_name = pkg_dict["pkg_name"]
                pkg_ref = pkg_dict["pkg_ref"]
                xmd["mbs"]["rpms"][pkg_name] = {"ref": pkg_ref}
        if err_msg:
            raise UnprocessableEntity(err_msg)

    # Set the modified xmd back to the modulemd
    mmd.set_xmd(xmd)


def get_prefixed_version(mmd):
    """
    Return the prefixed version of the module based on the buildrequired base module stream.

    :param mmd: the Modulemd.ModuleStream object to format
    :return: the prefixed version
    :rtype: int
    """
    xmd = mmd.get_xmd()
    version = mmd.get_version()

    base_module_stream = None
    for base_module in conf.base_module_names:
        try:
            base_module_stream = xmd["mbs"]["buildrequires"].get(base_module, {}).get("stream")
            if base_module_stream:
                # Break after finding the first base module that is buildrequired
                break
        except KeyError:
            log.warning("The module's mmd is missing information in the xmd section")
            return version
    else:
        log.warning(
            "This module does not buildrequire a base module ({0})".format(
                " or ".join(conf.base_module_names)
            )
        )
        return version

    # The platform version (e.g. prefix1.2.0 => 010200)
    version_prefix = models.ModuleBuild.get_stream_version(base_module_stream, right_pad=False)

    if version_prefix is None:
        log.warning(
            'The "{0}" stream "{1}" couldn\'t be used to prefix the module\'s '
            "version".format(base_module, base_module_stream)
        )
        return version

    # Strip the stream suffix because Modulemd requires version to be an integer
    new_version = int(str(int(math.floor(version_prefix))) + str(version))
    if new_version > GLib.MAXUINT64:
        log.warning(
            'The "{0}" stream "{1}" caused the module\'s version prefix to be '
            "too long".format(base_module, base_module_stream)
        )
        return version
    return new_version


def validate_mmd(mmd):
    """Validate module metadata

    If everything is ok, just keep quiet, otherwise error is raised for
    specific problem.

    :param mmd: modulemd object representing module metadata.
    :type mmd: Modulemd.Module
    :raises Forbidden: if metadata contains module repository but it is not
        allowed.
    :raise ValidationError: if the xmd has the "mbs" key set.
    """
    for modname in mmd.get_module_component_names():
        mod = mmd.get_module_component(modname)
        if mod.get_repository() and not conf.modules_allow_repository:
            raise Forbidden(
                "Custom module repositories aren't allowed.  "
                "%r bears repository %r" % (modname, mod.get_repository())
            )

    name = mmd.get_module_name()
    xmd = mmd.get_xmd()
    if "mbs" in xmd:
        if name not in conf.allowed_privileged_module_names:
            raise ValidationError('The "mbs" xmd field is reserved for MBS')

        allowed_keys = ["disttag_marking", "koji_tag_arches"]
        for key in xmd["mbs"].keys():
            if key not in allowed_keys:
                raise ValidationError('The "mbs" xmd field is reserved for MBS')

    if name in conf.base_module_names:
        raise ValidationError(
            'You cannot build a module named "{}" since it is a base module'.format(name))


def merge_included_mmd(mmd, included_mmd):
    """
    Merges two modulemds. This merges only metadata which are needed in
    the `main` when it includes another module defined by `included_mmd`
    """
    included_xmd = included_mmd.get_xmd()
    if "rpms" in included_xmd["mbs"]:
        xmd = mmd.get_xmd()
        if "rpms" not in xmd["mbs"]:
            xmd["mbs"]["rpms"] = included_xmd["mbs"]["rpms"]
        else:
            xmd["mbs"]["rpms"].update(included_xmd["mbs"]["rpms"])
    # Set the modified xmd back to the modulemd
    mmd.set_xmd(xmd)


def get_module_srpm_overrides(module):
    """
    Make necessary preparations to use any provided custom SRPMs.

    :param module: ModuleBuild object representing the module being submitted.
    :type module: :class:`models.ModuleBuild`
    :return: mapping of package names to SRPM links for all packages which
             have custom SRPM overrides specified
    :rtype: dict[str, str]

    """
    overrides = {}

    if not module.srpms:
        return overrides

    try:
        # Make sure we can decode the custom SRPM list
        srpms = json.loads(module.srpms)
        assert isinstance(srpms, list)
    except Exception:
        raise ValueError("Invalid srpms list encountered: {}".format(module.srpms))

    for source in srpms:
        if source.startswith("cli-build/") and source.endswith(".src.rpm"):
            # This is a custom srpm that has been uploaded to koji by rpkg
            # using the package name as the basename suffixed with .src.rpm
            rpm_name = os.path.basename(source)[: -len(".src.rpm")]
        else:
            # This should be a local custom srpm path
            if not os.path.exists(source):
                raise IOError("Provided srpm is missing: {}".format(source))
            # Get package name from rpm headers
            try:
                rpm_hdr = kobo.rpmlib.get_rpm_header(source)
                rpm_name = kobo.rpmlib.get_header_field(rpm_hdr, "name").decode("utf-8")
            except Exception:
                raise ValueError("Provided srpm is invalid: {}".format(source))

        if rpm_name in overrides:
            log.warning(
                'Encountered duplicate custom SRPM "{0}" for package {1}'
                .format(source, rpm_name)
            )
            continue

        log.debug('Using custom SRPM "{0}" for package {1}'.format(source, rpm_name))
        overrides[rpm_name] = source

    return overrides


def record_component_builds(
    mmd, module, initial_batch=1, previous_buildorder=None, main_mmd=None, session=None
):
    # Imported here to allow import of utils in GenericBuilder.
    import module_build_service.builder

    if not session:
        session = db.session

    # Format the modulemd by putting in defaults and replacing streams that
    # are branches with commit hashes
    format_mmd(mmd, module.scmurl, module, session)

    # When main_mmd is set, merge the metadata from this mmd to main_mmd,
    # otherwise our current mmd is main_mmd.
    if main_mmd:
        # Check for components that are in both MMDs before merging since MBS
        # currently can't handle that situation.
        main_mmd_rpms = main_mmd.get_rpm_component_names()
        mmd_rpms = mmd.get_rpm_component_names()
        duplicate_components = [
            rpm for rpm in main_mmd_rpms
            if rpm in mmd_rpms
        ]
        if duplicate_components:
            error_msg = (
                'The included module "{0}" in "{1}" have the following '
                "conflicting components: {2}".format(
                    mmd.get_module_name(), main_mmd.get_module_name(),
                    ", ".join(duplicate_components)
                )
            )
            raise UnprocessableEntity(error_msg)
        merge_included_mmd(main_mmd, mmd)
    else:
        main_mmd = mmd

    # If the modulemd yaml specifies components, then submit them for build
    rpm_components = [
        mmd.get_rpm_component(name)
        for name in mmd.get_rpm_component_names()
    ]
    module_components = [
        mmd.get_module_component(name)
        for name in mmd.get_module_component_names()
    ]
    all_components = list(rpm_components) + list(module_components)
    if not all_components:
        return

    # Get map of packages that have SRPM overrides
    srpm_overrides = get_module_srpm_overrides(module)

    rpm_weights = module_build_service.builder.GenericBuilder.get_build_weights(
        [c.get_name() for c in rpm_components]
    )
    all_components.sort(key=lambda x: x.get_buildorder())
    # We do not start with batch = 0 here, because the first batch is
    # reserved for module-build-macros. First real components must be
    # planned for batch 2 and following.
    batch = initial_batch

    for component in all_components:
        # Increment the batch number when buildorder increases.
        if previous_buildorder != component.get_buildorder():
            previous_buildorder = component.get_buildorder()
            batch += 1

        # If the component is another module, we fetch its modulemd file
        # and record its components recursively with the initial_batch
        # set to our current batch, so the components of this module
        # are built in the right global order.
        if isinstance(component, Modulemd.ComponentModule):
            full_url = component.get_repository() + "?#" + component.get_ref()
            # It is OK to whitelist all URLs here, because the validity
            # of every URL have been already checked in format_mmd(...).
            included_mmd = _fetch_mmd(full_url, whitelist_url=True)[0]
            batch = record_component_builds(
                included_mmd, module, batch, previous_buildorder, main_mmd, session=session)
            continue

        package = component.get_name()
        if package in srpm_overrides:
            component_ref = None
            full_url = srpm_overrides[package]
            log.info('Building custom SRPM "{0}"' " for package {1}".format(full_url, package))
        else:
            component_ref = mmd.get_xmd()["mbs"]["rpms"][package]["ref"]
            full_url = component.get_repository() + "?#" + component_ref

        # Skip the ComponentBuild if it already exists in database. This can happen
        # in case of module build resubmition.
        existing_build = models.ComponentBuild.from_component_name(db.session, package, module.id)
        if existing_build:
            # Check that the existing build has the same most important attributes.
            # This should never be a problem, but it's good to be defensive here so
            # we do not mess things during resubmition.
            if (
                existing_build.batch != batch
                or existing_build.scmurl != full_url
                or existing_build.ref != component_ref
            ):
                raise ValidationError(
                    "Module build %s already exists in database, but its attributes "
                    " are different from resubmitted one." % component.get_module_name()
                )
            continue

        build = models.ComponentBuild(
            module_id=module.id,
            package=package,
            format="rpms",
            scmurl=full_url,
            batch=batch,
            ref=component_ref,
            weight=rpm_weights[package],
        )
        session.add(build)

    return batch


def submit_module_build_from_yaml(username, handle, params, stream=None, skiptests=False):
    yaml_file = to_text_type(handle.read())
    mmd = load_mmd(yaml_file)
    dt = datetime.utcfromtimestamp(int(time.time()))
    if hasattr(handle, "filename"):
        def_name = str(os.path.splitext(os.path.basename(handle.filename))[0])
    elif not mmd.get_module_name():
        raise ValidationError(
            "The module's name was not present in the modulemd file. Please use the "
            '"module_name" parameter'
        )
    def_version = int(dt.strftime("%Y%m%d%H%M%S"))
    module_name = mmd.get_module_name() or def_name
    module_stream = stream or mmd.get_stream_name() or "master"
    if module_name != mmd.get_module_name() or module_stream != mmd.get_stream_name():
        # This is how you set the name and stream in the modulemd
        mmd = mmd.copy(module_name, module_stream)
    mmd.set_version(mmd.get_version() or def_version)
    if skiptests:
        buildopts = mmd.get_buildopts() or Modulemd.Buildopts()
        macros = buildopts.get_rpm_macros() or ""
        buildopts.set_rpm_macros(macros + "\n\n%__spec_check_pre exit 0\n")
        mmd.set_buildopts(buildopts)
    return submit_module_build(username, mmd, params)


_url_check_re = re.compile(r"^[^:/]+:.*$")


def submit_module_build_from_scm(username, params, allow_local_url=False):
    url = params["scmurl"]
    branch = params["branch"]
    # Translate local paths into file:// URL
    if allow_local_url and not _url_check_re.match(url):
        log.info("'{}' is not a valid URL, assuming local path".format(url))
        url = os.path.abspath(url)
        url = "file://" + url
    mmd, scm = _fetch_mmd(url, branch, allow_local_url)

    return submit_module_build(username, mmd, params)


def _apply_dep_overrides(mmd, params):
    """
    Apply the dependency override parameters (if specified) on the input modulemd.

    :param Modulemd.ModuleStream mmd: the modulemd to apply the overrides on
    :param dict params: the API parameters passed in by the user
    :raises ValidationError: if one of the overrides doesn't apply
    """
    dep_overrides = {
        "buildrequires": copy.copy(params.get("buildrequire_overrides", {})),
        "requires": copy.copy(params.get("require_overrides", {})),
    }

    # Parse the module's branch to determine if it should override the stream of the buildrequired
    # module defined in conf.br_stream_override_module
    branch_search = None
    if params.get("branch") and conf.br_stream_override_module and conf.br_stream_override_regexes:
        # Only parse the branch for a buildrequire override if the user didn't manually specify an
        # override for the module specified in conf.br_stream_override_module
        if not dep_overrides["buildrequires"].get(conf.br_stream_override_module):
            branch_search = None
            for regex in conf.br_stream_override_regexes:
                branch_search = re.search(regex, params["branch"])
                if branch_search:
                    log.debug(
                        "The stream override regex `%s` matched the branch %s",
                        regex,
                        params["branch"],
                    )
                    break
            else:
                log.debug('No stream override regexes matched the branch "%s"', params["branch"])

    # If a stream was parsed from the branch, then add it as a stream override for the module
    # specified in conf.br_stream_override_module
    if branch_search:
        # Concatenate all the groups that are not None together to get the desired stream.
        # This approach is taken in case there are sections to ignore.
        # For instance, if we need to parse `el8.0.0` from `rhel-8.0.0`.
        parsed_stream = "".join(group for group in branch_search.groups() if group)
        if parsed_stream:
            dep_overrides["buildrequires"][conf.br_stream_override_module] = [parsed_stream]
            log.info(
                'The buildrequired stream of "%s" was overriden with "%s" based on the branch "%s"',
                conf.br_stream_override_module, parsed_stream, params["branch"],
            )
        else:
            log.warning(
                'The regex `%s` only matched empty capture groups on the branch "%s". The regex is '
                " invalid and should be rewritten.",
                regex, params["branch"],
            )

    unused_dep_overrides = {
        "buildrequires": set(dep_overrides["buildrequires"].keys()),
        "requires": set(dep_overrides["requires"].keys()),
    }

    deps = mmd.get_dependencies()
    for dep in deps:
        overridden = False
        new_dep = Modulemd.Dependencies()
        for dep_type, overrides in dep_overrides.items():
            if dep_type == "buildrequires":
                mmd_dep_type = "buildtime"
            else:
                mmd_dep_type = "runtime"
            # Get the existing streams
            reqs = deps_to_dict(dep, mmd_dep_type)
            # Get the method to add a new stream for this dependency type
            # (e.g. add_buildtime_stream)
            add_func = getattr(new_dep, "add_{}_stream".format(mmd_dep_type))
            add_empty_func = getattr(
                new_dep, "set_empty_{}_dependencies_for_module".format(mmd_dep_type))
            for name, streams in reqs.items():
                if name in dep_overrides[dep_type]:
                    streams_to_add = dep_overrides[dep_type][name]
                    unused_dep_overrides[dep_type].remove(name)
                    overridden = True
                else:
                    streams_to_add = reqs[name]

                if streams_to_add == []:
                    add_empty_func(name)
                else:
                    for stream in streams_to_add:
                        add_func(name, stream)
        if overridden:
            # Set the overridden streams
            mmd.remove_dependencies(dep)
            mmd.add_dependencies(new_dep)

    for dep_type in unused_dep_overrides.keys():
        # If a stream override was applied from parsing the branch and it wasn't applicable,
        # just ignore it
        if branch_search and conf.br_stream_override_module in unused_dep_overrides[dep_type]:
            unused_dep_overrides[dep_type].remove(conf.br_stream_override_module)
        if unused_dep_overrides[dep_type]:
            raise ValidationError(
                "The {} overrides for the following modules aren't applicable: {}".format(
                    dep_type[:-1], ", ".join(sorted(unused_dep_overrides[dep_type])))
            )


def _modify_buildtime_streams(mmd, new_streams_func):
    """
    Modify buildtime streams using the input new_streams_func.

    :param Modulemd.ModuleStream mmd: the modulemd to apply the overrides on
    :param function new_streams: a function that takes the parameters (module_name, module_streams),
        and returns the streams that should be set on the buildtime dependency.
    """
    deps = mmd.get_dependencies()
    for dep in deps:
        overridden = False
        brs = deps_to_dict(dep, "buildtime")
        # There is no way to replace streams, so create a new Dependencies object that will end up
        # being a copy, but with the streams replaced if a virtual stream is detected
        new_dep = Modulemd.Dependencies()

        for name, streams in brs.items():
            new_streams = new_streams_func(name, streams)
            if streams != new_streams:
                overridden = True

            if new_streams == []:
                new_dep.set_empty_buildtime_dependencies_for_module(name)
            else:
                for stream in new_streams:
                    new_dep.add_buildtime_stream(name, stream)

        if overridden:
            # Copy the runtime streams as is
            reqs = deps_to_dict(dep, "runtime")
            for name, streams in reqs.items():
                if streams == []:
                    new_dep.set_empty_runtime_dependencies_for_module(name)
                else:
                    for stream in streams:
                        new_dep.add_runtime_stream(name, stream)
            # Replace the old Dependencies object with the new one with the overrides
            mmd.remove_dependencies(dep)
            mmd.add_dependencies(new_dep)


def resolve_base_module_virtual_streams(name, streams):
    """
    Resolve any base module virtual streams and return a copy of `streams` with the resolved values.

    :param str name: the module name
    :param str streams: the streams to resolve
    :return: the resolved streams
    :rtype: list
    """
    from module_build_service.resolver import system_resolver

    if name not in conf.base_module_names:
        return streams

    new_streams = copy.deepcopy(streams)
    for i, stream in enumerate(streams):
        # Ignore streams that start with a minus sign, since those are handled in the
        # MSE code
        if stream.startswith("-"):
            continue

        # Check if the base module stream is available
        log.debug('Checking to see if the base module "%s:%s" is available', name, stream)
        if system_resolver.get_module_count(name=name, stream=stream) > 0:
            continue

        # If the base module stream is not available, check if there's a virtual stream
        log.debug(
            'Checking to see if there is a base module "%s" with the virtual stream "%s"',
            name, stream,
        )
        base_module_mmd = system_resolver.get_latest_with_virtual_stream(
            name=name, virtual_stream=stream
        )
        if not base_module_mmd:
            # If there isn't this base module stream or virtual stream available, skip it,
            # and let the dep solving code deal with it like it normally would
            log.warning(
                'There is no base module "%s" with stream/virtual stream "%s"',
                name, stream,
            )
            continue

        latest_stream = base_module_mmd.get_stream_name()
        log.info(
            'Replacing the buildrequire "%s:%s" with "%s:%s", since "%s" is a virtual '
            "stream",
            name, stream, name, latest_stream, stream
        )
        new_streams[i] = latest_stream

    return new_streams


def _process_support_streams(mmd, params):
    """
    Check if any buildrequired base modules require a support stream suffix.

    This checks the Red Hat Product Pages to see if the buildrequired base module stream has been
    released, if yes, then add the appropriate stream suffix.

    :param Modulemd.ModuleStream mmd: the modulemd to apply the overrides on
    :param dict params: the API parameters passed in by the user
    """
    config_msg = (
        'Skipping the release date checks for adding a stream suffix since "%s" '
        "is not configured"
    )
    if not conf.product_pages_url:
        log.debug(config_msg, "product_pages_url")
        return
    elif not conf.product_pages_module_streams:
        log.debug(config_msg, "product_pages_module_streams")
        return

    buildrequire_overrides = params.get("buildrequire_overrides", {})

    def new_streams_func(name, streams):
        if name not in conf.base_module_names:
            log.debug("The module %s is not a base module. Skipping the release date check.", name)
            return streams
        elif name in buildrequire_overrides:
            log.debug(
                "The module %s is a buildrequire override. Skipping the release date check.", name)
            return streams

        new_streams = copy.deepcopy(streams)
        for i, stream in enumerate(streams):
            for regex, values in conf.product_pages_module_streams.items():
                if re.match(regex, stream):
                    log.debug(
                        'The regex `%s` from the configuration "product_pages_module_streams" '
                        "matched the stream %s",
                        regex, stream,
                    )
                    stream_suffix, pp_release_template, pp_major_release_template = values
                    break
            else:
                log.debug(
                    'No regexes in the configuration "product_pages_module_streams" matched the '
                    "stream %s. Skipping the release date check for this stream.",
                    stream,
                )
                continue

            if stream.endswith(stream_suffix):
                log.debug(
                    'The stream %s already contains the stream suffix of "%s". Skipping the '
                    "release date check.",
                    stream, stream_suffix
                )
                continue

            stream_version = models.ModuleBuild.get_stream_version(stream)
            if not stream_version:
                log.debug("A stream version couldn't be parsed from %s", stream)
                continue

            # Convert the stream_version float to an int to make the math below deal with only
            # integers
            stream_version_int = int(stream_version)
            # For example 80000 => 8
            x = stream_version_int // 10000
            # For example 80100 => 1
            y = (stream_version_int - x * 10000) // 100
            # For example 80104 => 4
            z = stream_version_int - x * 10000 - y * 100
            # Check if the stream version is x.0.0
            if stream_version_int % 10000 == 0 and pp_major_release_template:
                # For example, el8.0.0 => rhel-8-0
                pp_release = pp_major_release_template.format(x=x, y=y, z=z)
            else:
                # For example el8.0.1 => rhel-8-0.1
                pp_release = pp_release_template.format(x=x, y=y, z=z)

            url = "{}/api/v7/releases/{}/?fields=ga_date".format(
                conf.product_pages_url.rstrip("/"), pp_release)

            try:
                pp_rv = requests.get(url, timeout=15)
                pp_json = pp_rv.json()
            # Catch requests failures and JSON parsing errors
            except (requests.exceptions.RequestException, ValueError):
                log.exception(
                    "The query to the Product Pages at %s failed. Assuming it is not yet released.",
                    url,
                )
                continue

            ga_date = pp_json.get("ga_date")
            if not ga_date:
                log.debug("A release date for the release %s could not be determined", pp_release)
                continue

            if datetime.strptime(ga_date, '%Y-%m-%d') > datetime.utcnow():
                log.debug(
                    "The release %s hasn't been released yet. Not adding a stream suffix.",
                    ga_date
                )
                continue

            new_stream = stream + stream_suffix
            log.info(
                'Replacing the buildrequire "%s:%s" with "%s:%s", since the stream is released',
                name, stream, name, new_stream
            )
            new_streams[i] = new_stream

        return new_streams

    _modify_buildtime_streams(mmd, new_streams_func)


def submit_module_build(username, mmd, params):
    """
    Submits new module build.

    :param str username: Username of the build's owner.
    :param Modulemd.ModuleStream mmd: Modulemd defining the build.
    :param dict params: the API parameters passed in by the user
    :rtype: list with ModuleBuild
    :return: List with submitted module builds.
    """
    import koji  # Placed here to avoid py2/py3 conflicts...
    from .mse import generate_expanded_mmds

    log.debug(
        "Submitted %s module build for %s:%s:%s",
        ("scratch" if params.get("scratch", False) else "normal"),
        mmd.get_module_name(),
        mmd.get_stream_name(),
        mmd.get_version(),
    )
    validate_mmd(mmd)

    raise_if_stream_ambigous = False
    default_streams = {}
    # For local builds, we want the user to choose the exact stream using the default_streams
    # in case there are multiple streams to choose from and raise an exception otherwise.
    if "local_build" in params:
        raise_if_stream_ambigous = True
    # Get the default_streams if set.
    if "default_streams" in params:
        default_streams = params["default_streams"]
    _apply_dep_overrides(mmd, params)
    _modify_buildtime_streams(mmd, resolve_base_module_virtual_streams)
    _process_support_streams(mmd, params)

    mmds = generate_expanded_mmds(db.session, mmd, raise_if_stream_ambigous, default_streams)
    if not mmds:
        raise ValidationError(
            "No dependency combination was satisfied. Please verify the "
            "buildrequires in your modulemd have previously been built."
        )
    modules = []

    # True if all module builds are skipped so MBS will actually not rebuild
    # anything. To keep the backward compatibility, we need to raise an exception
    # later in the end of this method.
    all_modules_skipped = True

    for mmd in mmds:
        # Prefix the version of the modulemd based on the base module it buildrequires
        version = get_prefixed_version(mmd)
        mmd.set_version(version)
        nsvc = mmd.get_nsvc()

        log.debug("Checking whether module build already exists: %s.", nsvc)
        module = models.ModuleBuild.get_build_from_nsvc(db.session, *nsvc.split(":"))
        if module and not params.get("scratch", False):
            if module.state != models.BUILD_STATES["failed"]:
                log.info(
                    "Skipping rebuild of %s, only rebuild of modules in failed state is allowed.",
                    nsvc,
                )
                modules.append(module)
                continue

            rebuild_strategy = params.get("rebuild_strategy")
            if rebuild_strategy and module.rebuild_strategy != rebuild_strategy:
                raise ValidationError(
                    'You cannot change the module\'s "rebuild_strategy" when '
                    "resuming a module build"
                )

            log.debug("Resuming existing module build %r" % module)
            # Reset all component builds that didn't complete
            for component in module.component_builds:
                if component.state and component.state != koji.BUILD_STATES["COMPLETE"]:
                    component.state = None
                    component.state_reason = None
                    db.session.add(component)
            module.username = username
            prev_state = module.previous_non_failed_state
            if prev_state == models.BUILD_STATES["init"]:
                transition_to = models.BUILD_STATES["init"]
            else:
                transition_to = models.BUILD_STATES["wait"]
                module.batch = 0
            module.transition(conf, transition_to, "Resubmitted by %s" % username)
            log.info("Resumed existing module build in previous state %s" % module.state)
        else:
            # make NSVC unique for every scratch build
            context_suffix = ""
            if params.get("scratch", False):
                log.debug("Checking for existing scratch module builds by NSVC")
                scrmods = models.ModuleBuild.get_scratch_builds_from_nsvc(
                    db.session, *nsvc.split(":"))
                scrmod_contexts = [scrmod.context for scrmod in scrmods]
                log.debug(
                    "Found %d previous scratch module build context(s): %s",
                    len(scrmods), ",".join(scrmod_contexts),
                )
                # append incrementing counter to context
                context_suffix = "_" + str(len(scrmods) + 1)
                mmd.set_context(mmd.get_context() + context_suffix)

            log.debug("Creating new module build")
            module = models.ModuleBuild.create(
                db.session,
                conf,
                name=mmd.get_module_name(),
                stream=mmd.get_stream_name(),
                version=str(mmd.get_version()),
                modulemd=mmd_to_str(mmd),
                scmurl=params.get("scmurl"),
                username=username,
                rebuild_strategy=params.get("rebuild_strategy"),
                scratch=params.get("scratch"),
                srpms=params.get("srpms"),
            )
            (
                module.ref_build_context,
                module.build_context,
                module.runtime_context,
                module.context,
            ) = module.contexts_from_mmd(module.modulemd)
            module.context += context_suffix

        all_modules_skipped = False
        db.session.add(module)
        db.session.commit()
        modules.append(module)
        log.info('The user "%s" submitted the build "%s"', username, nsvc)

    if all_modules_skipped:
        err_msg = (
            "Module (state=%s) already exists. Only a new build, resubmission of "
            "a failed build or build against new buildrequirements is "
            "allowed." % module.state
        )
        log.error(err_msg)
        raise Conflict(err_msg)

    return modules


def _is_eol_in_pdc(name, stream):
    """ Check PDC if the module name:stream is no longer active. """

    params = {"type": "module", "global_component": name, "name": stream}
    url = conf.pdc_url + "/component-branches/"

    response = requests.get(url, params=params)
    if not response:
        raise ValidationError("Failed to talk to PDC {}{}".format(response, response.text))

    data = response.json()
    results = data["results"]
    if not results:
        raise ValidationError(
            "No such module {}:{} found at {}".format(name, stream, response.request.url))

    # If the module is active, then it is not EOL and vice versa.
    return not results[0]["active"]


def _fetch_mmd(url, branch=None, allow_local_url=False, whitelist_url=False, mandatory_checks=True):
    # Import it here, because SCM uses utils methods
    # and fails to import them because of dep-chain.
    import module_build_service.scm

    td = None
    scm = None
    try:
        log.debug("Verifying modulemd")
        td = tempfile.mkdtemp()
        if whitelist_url:
            scm = module_build_service.scm.SCM(url, branch, [url], allow_local_url)
        else:
            scm = module_build_service.scm.SCM(url, branch, conf.scmurls, allow_local_url)
        scm.checkout(td)
        if not whitelist_url and mandatory_checks:
            scm.verify()
        cofn = scm.get_module_yaml()
        mmd = load_mmd_file(cofn)
    finally:
        try:
            if td is not None:
                shutil.rmtree(td)
        except Exception as e:
            log.warning("Failed to remove temporary directory {!r}: {}".format(td, str(e)))

    if conf.check_for_eol:
        if _is_eol_in_pdc(scm.name, scm.branch):
            raise ValidationError(
                "Module {}:{} is marked as EOL in PDC.".format(scm.name, scm.branch))

    if not mandatory_checks:
        return mmd, scm

    # If the name was set in the modulemd, make sure it matches what the scmurl
    # says it should be
    if mmd.get_module_name() and mmd.get_module_name() != scm.name:
        if not conf.allow_name_override_from_scm:
            raise ValidationError(
                'The name "{0}" that is stored in the modulemd is not valid'
                .format(mmd.get_module_name())
            )
    else:
        # Set the module name
        mmd = mmd.copy(scm.name)

    # If the stream was set in the modulemd, make sure it matches what the repo
    # branch is
    if mmd.get_stream_name() and mmd.get_stream_name() != scm.branch:
        if not conf.allow_stream_override_from_scm:
            raise ValidationError(
                'The stream "{0}" that is stored in the modulemd does not match the branch "{1}"'
                .format(mmd.get_stream_name(), scm.branch)
            )
    else:
        # Set the module stream
        mmd = mmd.copy(mmd.get_module_name(), scm.branch)

    # If the version is in the modulemd, throw an exception since the version
    # since the version is generated by MBS
    if mmd.get_version():
        raise ValidationError(
            'The version "{0}" is already defined in the modulemd but it shouldn\'t be since the '
            "version is generated based on the commit time".format(mmd.get_version())
        )
    else:
        mmd.set_version(int(scm.version))

    return mmd, scm


def load_local_builds(local_build_nsvs, session=None):
    """
    Loads previously finished local module builds from conf.mock_resultsdir
    and imports them to database.

    :param local_build_nsvs: List of NSV separated by ':' defining the modules
        to load from the mock_resultsdir.
    """
    if not local_build_nsvs:
        return

    if not session:
        session = db.session

    if type(local_build_nsvs) != list:
        local_build_nsvs = [local_build_nsvs]

    # Get the list of all available local module builds.
    builds = []
    try:
        for d in os.listdir(conf.mock_resultsdir):
            m = re.match("^module-(.*)-([^-]*)-([0-9]+)$", d)
            if m:
                builds.append((m.group(1), m.group(2), int(m.group(3)), d))
    except OSError:
        pass

    # Sort with the biggest version first
    try:
        # py27
        builds.sort(lambda a, b: -cmp(a[2], b[2]))  # noqa: F821
    except TypeError:
        # py3
        builds.sort(key=lambda a: a[2], reverse=True)

    for nsv in local_build_nsvs:
        parts = nsv.split(":")
        if len(parts) < 1 or len(parts) > 3:
            raise RuntimeError(
                'The local build "{0}" couldn\'t be be parsed into NAME[:STREAM[:VERSION]]'
                .format(nsv)
            )

        name = parts[0]
        stream = parts[1] if len(parts) > 1 else None
        version = int(parts[2]) if len(parts) > 2 else None

        found_build = None
        for build in builds:
            if name != build[0]:
                continue
            if stream is not None and stream != build[1]:
                continue
            if version is not None and version != build[2]:
                continue

            found_build = build
            break

        if not found_build:
            raise RuntimeError(
                'The local build "{0}" couldn\'t be found in "{1}"'.format(
                    nsv, conf.mock_resultsdir)
            )

        # Load the modulemd metadata.
        path = os.path.join(conf.mock_resultsdir, found_build[3], "results")
        mmd = load_mmd_file(os.path.join(path, "modules.yaml"))

        # Create ModuleBuild in database.
        module = models.ModuleBuild.create(
            session,
            conf,
            name=mmd.get_module_name(),
            stream=mmd.get_stream_name(),
            version=str(mmd.get_version()),
            context=mmd.get_context(),
            modulemd=mmd_to_str(mmd),
            scmurl="",
            username="mbs",
            publish_msg=False,
        )
        module.koji_tag = path
        module.state = models.BUILD_STATES["ready"]
        session.commit()

        if (
            found_build[0] != module.name
            or found_build[1] != module.stream
            or str(found_build[2]) != module.version
        ):
            raise RuntimeError(
                'Parsed metadata results for "{0}" don\'t match the directory name'.format(
                    found_build[3])
            )
        log.info("Loaded local module build %r", module)

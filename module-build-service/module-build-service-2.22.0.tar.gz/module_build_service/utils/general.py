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
import os
import functools
import inspect
import hashlib
import time
from datetime import datetime
from functools import partial

from six import text_type, string_types
from gi.repository.GLib import Error as ModuleMDError

from module_build_service import conf, log, models, Modulemd
from module_build_service.errors import ValidationError, ProgrammingError, UnprocessableEntity


def to_text_type(s):
    """
    Converts `s` to `text_type`. In case it fails, returns `s`.
    """
    try:
        return text_type(s, "utf-8")
    except TypeError:
        return s


def load_mmd(yaml, is_file=False):
    if not yaml:
        raise UnprocessableEntity('The input modulemd was empty')

    target_mmd_version = Modulemd.ModuleStreamVersionEnum.TWO
    try:
        if is_file:
            mmd = Modulemd.ModuleStream.read_file(yaml, True)
        else:
            mmd = Modulemd.ModuleStream.read_string(to_text_type(yaml), True)
        mmd.validate()
        if mmd.get_mdversion() < target_mmd_version:
            mmd = mmd.upgrade(target_mmd_version)
        elif mmd.get_mdversion() > target_mmd_version:
            log.error("Encountered a modulemd file with the version %d", mmd.get_mdversion())
            raise UnprocessableEntity(
                "The modulemd version cannot be greater than {}".format(target_mmd_version))
    except ModuleMDError as e:
        not_found = False
        if is_file:
            error = "The modulemd {} is invalid.".format(os.path.basename(yaml))
            if os.path.exists(yaml):
                with open(yaml, "rt") as yaml_hdl:
                    log.debug("Modulemd that failed to load:\n%s", yaml_hdl.read())
            else:
                not_found = True
                error = "The modulemd file {} was not found.".format(os.path.basename(yaml))
                log.error("The modulemd file %s was not found.", yaml)
        else:
            error = "The modulemd is invalid."
            log.debug("Modulemd that failed to load:\n%s", yaml)

        if "modulemd-error-quark: " in str(e):
            error = "{} The error was '{}'.".format(
                error, str(e).split("modulemd-error-quark: ")[-1])
        elif "Unknown ModuleStream version" in str(e):
            error = (
                "{}. The modulemd version can't be greater than {}."
                .format(error, target_mmd_version)
            )
        elif not_found is False:
            error = "{} Please verify the syntax is correct.".format(error)

        log.exception(error)
        raise UnprocessableEntity(error)

    return mmd


load_mmd_file = partial(load_mmd, is_file=True)


def scm_url_schemes(terse=False):
    """
    Definition of URL schemes supported by both frontend and scheduler.

    NOTE: only git URLs in the following formats are supported atm:
        git://
        git+http://
        git+https://
        git+rsync://
        http://
        https://
        file://

    :param terse=False: Whether to return terse list of unique URL schemes
                        even without the "://".
    """

    scm_types = {
        "git": (
            "git://",
            "git+http://",
            "git+https://",
            "git+rsync://",
            "http://",
            "https://",
            "file://",
        )
    }

    if not terse:
        return scm_types
    else:
        scheme_list = []
        for scm_type, scm_schemes in scm_types.items():
            scheme_list.extend([scheme[:-3] for scheme in scm_schemes])
        return list(set(scheme_list))


def retry(timeout=conf.net_timeout, interval=conf.net_retry_interval, wait_on=Exception):
    """ A decorator that allows to retry a section of code...
    ...until success or timeout.
    """

    def wrapper(function):
        @functools.wraps(function)
        def inner(*args, **kwargs):
            start = time.time()
            while True:
                try:
                    return function(*args, **kwargs)
                except wait_on as e:
                    log.warning(
                        "Exception %r raised from %r.  Retry in %rs" % (e, function, interval)
                    )
                    time.sleep(interval)
                    if (time.time() - start) >= timeout:
                        raise  # This re-raises the last exception.

        return inner

    return wrapper


def module_build_state_from_msg(msg):
    state = int(msg.module_build_state)
    # TODO better handling
    assert state in models.BUILD_STATES.values(), "state=%s(%s) is not in %s" % (
        state,
        type(state),
        list(models.BUILD_STATES.values()),
    )
    return state


def generate_koji_tag(name, stream, version, context, max_length=256, scratch=False, scratch_id=0):
    """Generate a koji tag for a module

    Generally, a module's koji tag is in format ``module-N-S-V-C``. However, if
    it is longer than maximum length, old format ``module-hash`` is used.

    :param str name: a module's name
    :param str stream: a module's stream
    :param str version: a module's version
    :param str context: a module's context
    :param int max_length: the maximum length the Koji tag can be before
        falling back to the old format of "module-<hash>". Default is 256
        characters, which is the maximum length of a tag Koji accepts.
    :param bool scratch: a flag indicating if the generated tag will be for
        a scratch module build
    :param int scratch_id: for scratch module builds, a unique build identifier
    :return: a Koji tag
    :rtype: str
    """
    if scratch:
        prefix = "scrmod-"
        # use unique suffix so same commit can be resubmitted
        suffix = "+" + str(scratch_id)
    else:
        prefix = "module-"
        suffix = ""
    nsvc_list = [name, stream, str(version), context]
    nsvc_tag = prefix + "-".join(nsvc_list) + suffix
    if len(nsvc_tag) + len("-build") > max_length:
        # Fallback to the old format of 'module-<hash>' if the generated koji tag
        # name is longer than max_length
        nsvc_hash = hashlib.sha1(".".join(nsvc_list).encode("utf-8")).hexdigest()[:16]
        return prefix + nsvc_hash + suffix
    return nsvc_tag


def validate_koji_tag(tag_arg_names, pre="", post="-", dict_key="name"):
    """
    Used as a decorator validates koji tag arg(s)' value(s)
    against configurable list of koji tag prefixes.
    Supported arg value types are: dict, list, str

    :param tag_arg_names: Str or list of parameters to validate.
    :param pre: Prepend this optional string (e.g. '.' in case of disttag
    validation) to each koji tag prefix.
    :param post: Append this string/delimiter ('-' by default) to each koji
    tag prefix.
    :param dict_key: In case of a dict arg, inspect this key ('name' by default).
    """

    if not isinstance(tag_arg_names, list):
        tag_arg_names = [tag_arg_names]

    def validation_decorator(function):
        def wrapper(*args, **kwargs):
            call_args = inspect.getcallargs(function, *args, **kwargs)

            for tag_arg_name in tag_arg_names:
                err_subject = "Koji tag validation:"

                # If any of them don't appear in the function, then fail.
                if tag_arg_name not in call_args:
                    raise ProgrammingError(
                        "{} Inspected argument {} is not within function args."
                        " The function was: {}.".format(
                            err_subject, tag_arg_name, function.__name__
                        )
                    )

                tag_arg_val = call_args[tag_arg_name]

                # First, check that we have some value
                if not tag_arg_val:
                    raise ValidationError(
                        "{} Can not validate {}. No value provided.".format(
                            err_subject, tag_arg_name)
                    )

                # If any of them are a dict, then use the provided dict_key
                if isinstance(tag_arg_val, dict):
                    if dict_key not in tag_arg_val:
                        raise ProgrammingError(
                            "{} Inspected dict arg {} does not contain {} key."
                            " The function was: {}.".format(
                                err_subject, tag_arg_name, dict_key, function.__name__)
                        )
                    tag_list = [tag_arg_val[dict_key]]
                elif isinstance(tag_arg_val, list):
                    tag_list = tag_arg_val
                else:
                    tag_list = [tag_arg_val]

                # Check to make sure the provided values match our whitelist.
                for allowed_prefix in conf.koji_tag_prefixes:
                    if all([t.startswith(pre + allowed_prefix + post) for t in tag_list]):
                        break
                else:
                    # Only raise this error if the given tags don't start with
                    # *any* of our allowed prefixes.
                    raise ValidationError(
                        "Koji tag validation: {} does not satisfy any of allowed prefixes: {}"
                        .format(tag_list, [pre + p + post for p in conf.koji_tag_prefixes])
                    )

            # Finally.. after all that validation, call the original function
            # and return its value.
            return function(*args, **kwargs)

        # We're replacing the original function with our synthetic wrapper,
        # but dress it up to make it look more like the original function.
        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        return wrapper

    return validation_decorator


def get_rpm_release(module_build):
    """
    Generates the dist tag for the specified module
    :param module_build: a models.ModuleBuild object
    :return: a string of the module's dist tag
    """
    dist_str = ".".join([
        module_build.name,
        module_build.stream,
        str(module_build.version),
        str(module_build.context),
    ]).encode("utf-8")
    dist_hash = hashlib.sha1(dist_str).hexdigest()[:8]

    # We need to share the same auto-incrementing index in dist tag between all MSE builds.
    # We can achieve that by using the lowest build ID of all the MSE siblings including
    # this module build.
    mse_build_ids = module_build.siblings + [module_build.id or 0]
    mse_build_ids.sort()
    index = mse_build_ids[0]
    try:
        buildrequires = module_build.mmd().get_xmd()["mbs"]["buildrequires"]
    except (ValueError, KeyError):
        log.warning(
            "Module build {0} does not have buildrequires in its xmd".format(module_build.id))
        buildrequires = None

    # Determine which buildrequired module will influence the disttag
    br_module_marking = ""
    # If the buildrequires are recorded in the xmd then we can try to find the base module that
    # is buildrequired
    if buildrequires:
        # Looping through all the non-base modules that are allowed to set the disttag_marking
        # and the base modules to see what the disttag marking should be. Doing it this way
        # preserves the order in the configurations.
        for module in conf.allowed_privileged_module_names + conf.base_module_names:
            module_in_xmd = buildrequires.get(module)

            if not module_in_xmd:
                continue

            with models.make_session(conf) as session:
                module_obj = models.ModuleBuild.get_build_from_nsvc(
                    session,
                    module,
                    module_in_xmd["stream"],
                    module_in_xmd["version"],
                    module_in_xmd["context"],
                )
                if not module_obj:
                    continue

                try:
                    marking = module_obj.mmd().get_xmd()["mbs"]["disttag_marking"]
                # We must check for a KeyError because a Variant object doesn't support the `get`
                # method
                except KeyError:
                    if module not in conf.base_module_names:
                        continue
                    # If we've made it past all the modules in
                    # conf.allowed_privileged_module_names, and the base module doesn't have
                    # the disttag_marking set, then default to the stream of the first base module
                    marking = module_obj.stream
                br_module_marking = marking + "+"
                break
        else:
            log.warning(
                "Module build {0} does not buildrequire a base module ({1})".format(
                    module_build.id, " or ".join(conf.base_module_names))
            )

    # use alternate prefix for scratch module build components so they can be identified
    prefix = "scrmod+" if module_build.scratch else conf.default_dist_tag_prefix

    return "{prefix}{base_module_marking}{index}+{dist_hash}".format(
        prefix=prefix, base_module_marking=br_module_marking, index=index, dist_hash=dist_hash
    )


def create_dogpile_key_generator_func(skip_first_n_args=0):
    """
    Creates dogpile key_generator function with additional features:

    - when models.ModuleBuild is an argument of method cached by dogpile-cache,
      the ModuleBuild.id is used as a key. Therefore it is possible to cache
      data per particular module build, while normally, it would be per
      ModuleBuild.__str__() output, which contains also batch and other data
      which changes during the build of a module.
    - it is able to skip first N arguments of a cached method. This is useful
      when the db.session is part of cached method call, and the caching should
      work no matter what session instance is passed to cached method argument.
    """

    def key_generator(namespace, fn):
        fname = fn.__name__

        def generate_key(*arg, **kwarg):
            key_template = fname + "_"
            for s in arg[skip_first_n_args:]:
                if type(s) == models.ModuleBuild:
                    key_template += str(s.id)
                else:
                    key_template += str(s) + "_"
            return key_template

        return generate_key

    return key_generator


def import_mmd(session, mmd, check_buildrequires=True):
    """
    Imports new module build defined by `mmd` to MBS database using `session`.
    If it already exists, it is updated.

    The ModuleBuild.koji_tag is set according to xmd['mbs]['koji_tag'].
    The ModuleBuild.state is set to "ready".
    The ModuleBuild.rebuild_strategy is set to "all".
    The ModuleBuild.owner is set to "mbs_import".

    :param bool check_buildrequires: When True, checks that the buildrequires defined in the MMD
        have matching records in the `mmd["xmd"]["mbs"]["buildrequires"]` and also fills in
        the `ModuleBuild.buildrequires` according to this data.
    :return: module build (ModuleBuild),
             log messages collected during import (list)
    :rtype: tuple
    """
    if not mmd.get_context():
        mmd.set_context(models.DEFAULT_MODULE_CONTEXT)
    name = mmd.get_module_name()
    stream = mmd.get_stream_name()
    version = str(mmd.get_version())
    context = mmd.get_context()

    try:
        disttag_marking = mmd.get_xmd()["mbs"]["disttag_marking"]
    except (ValueError, KeyError):
        disttag_marking = None

    try:
        virtual_streams = mmd.get_xmd()["mbs"]["virtual_streams"]
    except (ValueError, KeyError):
        virtual_streams = []

    # Verify that the virtual streams are the correct type
    if virtual_streams and (
        not isinstance(virtual_streams, list)
        or any(not isinstance(vs, string_types) for vs in virtual_streams)
    ):
        msg = "The virtual streams must be a list of strings"
        log.error(msg)
        raise UnprocessableEntity(msg)

    # If it is a base module, then make sure the value that will be used in the RPM disttags
    # doesn't contain a dash since a dash isn't allowed in the release field of the NVR
    if name in conf.base_module_names:
        if disttag_marking and "-" in disttag_marking:
            msg = "The disttag_marking cannot contain a dash"
            log.error(msg)
            raise UnprocessableEntity(msg)
        elif not disttag_marking and "-" in stream:
            msg = "The stream cannot contain a dash unless disttag_marking is set"
            log.error(msg)
            raise UnprocessableEntity(msg)

    # Log messages collected during import
    msgs = []

    # NSVC is used for logging purpose later.
    try:
        nsvc = ":".join([name, stream, version, context])
    except TypeError:
        msg = "Incomplete NSVC: {}:{}:{}:{}".format(name, stream, version, context)
        log.error(msg)
        raise UnprocessableEntity(msg)

    if len(mmd.get_dependencies()) > 1:
        raise UnprocessableEntity(
            "The imported module's dependencies list should contain just one element")

    xmd = mmd.get_xmd()
    # Set some defaults in xmd["mbs"] if they're not provided by the user
    if "mbs" not in xmd:
        xmd["mbs"] = {"mse": True}

    if check_buildrequires and mmd.get_dependencies():
        brs = set(mmd.get_dependencies()[0].get_buildtime_modules())
        xmd_brs = set(xmd["mbs"].get("buildrequires", {}).keys())
        if brs - xmd_brs:
            raise UnprocessableEntity(
                "The imported module buildrequires other modules, but the metadata in the "
                'xmd["mbs"]["buildrequires"] dictionary is missing entries'
            )
    elif "buildrequires" not in xmd["mbs"]:
        xmd["mbs"]["buildrequires"] = {}
        mmd.set_xmd(xmd)

    koji_tag = xmd["mbs"].get("koji_tag")
    if koji_tag is None:
        log.warning("'koji_tag' is not set in xmd['mbs'] for module {}".format(nsvc))

    # Get the ModuleBuild from DB.
    build = models.ModuleBuild.get_build_from_nsvc(session, name, stream, version, context)
    if build:
        msg = "Updating existing module build {}.".format(nsvc)
        log.info(msg)
        msgs.append(msg)
    else:
        build = models.ModuleBuild()

    build.name = name
    build.stream = stream
    build.version = version
    build.koji_tag = koji_tag
    build.state = models.BUILD_STATES["ready"]
    build.modulemd = mmd_to_str(mmd)
    build.context = context
    build.owner = "mbs_import"
    build.rebuild_strategy = "all"
    build.time_submitted = datetime.utcnow()
    build.time_modified = datetime.utcnow()
    build.time_completed = datetime.utcnow()
    if build.name in conf.base_module_names:
        build.stream_version = models.ModuleBuild.get_stream_version(stream)

    # Record the base modules this module buildrequires
    if check_buildrequires:
        for base_module in build.get_buildrequired_base_modules(session):
            if base_module not in build.buildrequires:
                build.buildrequires.append(base_module)

    session.add(build)
    session.commit()

    for virtual_stream in virtual_streams:
        vs_obj = session.query(models.VirtualStream).filter_by(name=virtual_stream).first()
        if not vs_obj:
            vs_obj = models.VirtualStream(name=virtual_stream)
            session.add(vs_obj)
            session.commit()

        if vs_obj not in build.virtual_streams:
            build.virtual_streams.append(vs_obj)
            session.add(build)

    session.commit()

    msg = "Module {} imported".format(nsvc)
    log.info(msg)
    msgs.append(msg)

    return build, msgs


def import_fake_base_module(nsvc):
    """
    Creates and imports new fake base module to be used with offline local builds.

    :param str nsvc: name:stream:version:context of a module.
    """
    name, stream, version, context = nsvc.split(":")
    mmd = Modulemd.ModuleStreamV2.new(name, stream)
    mmd.set_version(int(version))
    mmd.set_context(context)
    mmd.set_summary("fake base module")
    mmd.set_description("fake base module")
    mmd.add_module_license("GPL")

    buildroot = Modulemd.Profile.new("buildroot")
    for rpm in conf.default_buildroot_packages:
        buildroot.add_rpm(rpm)
    mmd.add_profile(buildroot)

    srpm_buildroot = Modulemd.Profile.new("srpm-buildroot")
    for rpm in conf.default_srpm_buildroot_packages:
        srpm_buildroot.add_rpm(rpm)
    mmd.add_profile(srpm_buildroot)

    xmd = {"mbs": {}}
    xmd_mbs = xmd["mbs"]
    xmd_mbs["buildrequires"] = {}
    xmd_mbs["requires"] = {}
    xmd_mbs["commit"] = "ref_%s" % context
    xmd_mbs["mse"] = "true"
    # Use empty "repofile://" URI for base module. The base module will use the
    # `conf.base_module_names` list as list of default repositories.
    xmd_mbs["koji_tag"] = "repofile://"
    mmd.set_xmd(xmd)

    with models.make_session(conf) as session:
        import_mmd(session, mmd, False)


def get_local_releasever():
    """
    Returns the $releasever variable used in the system when expanding .repo files.
    """
    # Import DNF here to not force it as a hard MBS dependency.
    import dnf

    dnf_base = dnf.Base()
    return dnf_base.conf.releasever


def import_builds_from_local_dnf_repos(platform_id=None):
    """
    Imports the module builds from all available local repositories to MBS DB.

    This is used when building modules locally without any access to MBS infra.
    This method also generates and imports the base module according to /etc/os-release.

    :param str platform_id: The `name:stream` of a fake platform module to generate in this
        method. When not set, the /etc/os-release is parsed to get the PLATFORM_ID.
    """
    # Import DNF here to not force it as a hard MBS dependency.
    import dnf

    log.info("Loading available RPM repositories.")
    dnf_base = dnf.Base()
    dnf_base.read_all_repos()

    log.info("Importing available modules to MBS local database.")
    with models.make_session(conf) as session:
        for repo in dnf_base.repos.values():
            try:
                repo.load()
            except Exception as e:
                log.warning(str(e))
                continue
            mmd_data = repo.get_metadata_content("modules")
            mmd_index = Modulemd.ModuleIndex.new()
            ret, _ = mmd_index.update_from_string(mmd_data, True)
            if not ret:
                log.warning("Loading the repo '%s' failed", repo.name)
                continue

            for module_name in mmd_index.get_module_names():
                for mmd in mmd_index.get_module(module_name).get_all_streams():
                    xmd = mmd.get_xmd()
                    xmd["mbs"] = {}
                    xmd["mbs"]["koji_tag"] = "repofile://" + repo.repofile
                    xmd["mbs"]["mse"] = True
                    xmd["mbs"]["commit"] = "unknown"
                    mmd.set_xmd(xmd)

                    import_mmd(session, mmd, False)

    if not platform_id:
        # Parse the /etc/os-release to find out the local platform:stream.
        with open("/etc/os-release", "r") as fd:
            for l in fd.readlines():
                if not l.startswith("PLATFORM_ID"):
                    continue
                platform_id = l.split("=")[1].strip("\"' \n")
    if not platform_id:
        raise ValueError("Cannot get PLATFORM_ID from /etc/os-release.")

    # Create the fake platform:stream:1:000000 module to fulfill the
    # dependencies for local offline build and also to define the
    # srpm-buildroot and buildroot.
    import_fake_base_module("%s:1:000000" % platform_id)


def get_mmd_from_scm(url):
    """
    Provided an SCM URL, fetch mmd from the corresponding module YAML
    file. If ref is specified within the URL, the mmd will be returned
    as of the ref.
    """
    from module_build_service.utils.submit import _fetch_mmd

    mmd, _ = _fetch_mmd(
        url, branch=None, allow_local_url=False, whitelist_url=False, mandatory_checks=False)

    return mmd


def get_build_arches(mmd, config):
    """
    Returns the list of architectures for which the module `mmd` should be built.

    :param mmd: Module MetaData
    :param config: config (module_build_service.config.Config instance)
    :return list of architectures
    """
    # Imported here to allow import of utils in GenericBuilder.
    import module_build_service.builder
    nsvc = mmd.get_nsvc()

    # At first, handle BASE_MODULE_ARCHES - this overrides any other option.
    # Find out the base modules in buildrequires section of XMD and
    # set the Koji tag arches according to it.
    if "mbs" in mmd.get_xmd():
        for req_name, req_data in mmd.get_xmd()["mbs"]["buildrequires"].items():
            ns = ":".join([req_name, req_data["stream"]])
            if ns in config.base_module_arches:
                arches = config.base_module_arches[ns]
                log.info("Setting build arches of %s to %r based on the BASE_MODULE_ARCHES." % (
                    nsvc, arches))
                return arches

    # Check whether the module contains the `koji_tag_arches`. This is used only
    # by special modules defining the layered products.
    try:
        arches = mmd.get_xmd()["mbs"]["koji_tag_arches"]
        log.info("Setting build arches of %s to %r based on the koji_tag_arches." % (
            nsvc, arches))
        return arches
    except KeyError:
        pass

    # Check the base/layered-product module this module buildrequires and try to get the
    # list of arches from there.
    try:
        buildrequires = mmd.get_xmd()["mbs"]["buildrequires"]
    except (ValueError, KeyError):
        log.warning(
            "Module {0} does not have buildrequires in its xmd".format(mmd.get_nsvc()))
        buildrequires = None
    if buildrequires:
        # Looping through all the privileged modules that are allowed to set koji tag arches
        # and the base modules to see what the koji tag arches should be. Doing it this way
        # preserves the order in the configurations.
        with models.make_session(conf) as session:
            for module in conf.allowed_privileged_module_names + conf.base_module_names:
                module_in_xmd = buildrequires.get(module)

                if not module_in_xmd:
                    continue

                module_obj = models.ModuleBuild.get_build_from_nsvc(
                    session,
                    module,
                    module_in_xmd["stream"],
                    module_in_xmd["version"],
                    module_in_xmd["context"],
                )
                if not module_obj:
                    continue
                arches = module_build_service.builder.GenericBuilder.get_module_build_arches(
                    module_obj)
                if arches:
                    log.info("Setting build arches of %s to %r based on the buildrequired "
                             "module %r." % (nsvc, arches, module_obj))
                    return arches

    # As a last resort, return just the preconfigured list of arches.
    arches = config.arches
    log.info("Setting build arches of %s to %r based on default ARCHES." % (nsvc, arches))
    return arches


def deps_to_dict(deps, deps_type):
    """
    Helper method to convert a Modulemd.Dependencies object to a dictionary.

    :param Modulemd.Dependencies deps: the Modulemd.Dependencies object to convert
    :param str deps_type: the type of dependency (buildtime or runtime)
    :return: a dictionary with the keys as module names and values as a list of strings
    :rtype dict
    """
    names_func = getattr(deps, 'get_{}_modules'.format(deps_type))
    streams_func = getattr(deps, 'get_{}_streams'.format(deps_type))
    return {
        module: streams_func(module)
        for module in names_func()
    }


def mmd_to_str(mmd):
    """
    Helper method to convert a Modulemd.ModuleStream object to a YAML string.

    :param Modulemd.ModuleStream mmd: the modulemd to convert
    :return: the YAML string of the modulemd
    :rtype: str
    """
    index = Modulemd.ModuleIndex()
    index.add_module_stream(mmd)
    return to_text_type(index.dump_to_string())

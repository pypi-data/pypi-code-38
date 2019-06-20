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
#            Luboš Kocman <lkocman@redhat.com>

"""Generic component build functions."""

# TODO: Query the MBS to find what modules satisfy the build dependencies and
#       their tag names.
# TODO: Ensure the RPM %dist tag is set according to the policy.

import six
import dogpile.cache
from abc import ABCMeta, abstractmethod
from requests.exceptions import ConnectionError

from module_build_service import conf, log, db
from module_build_service import models
import module_build_service.resolver
import module_build_service.scm
import module_build_service.utils
from module_build_service.utils import create_dogpile_key_generator_func


"""
Example workflows - helps to see the difference in implementations
Koji workflow

1) create tag, and build-tag
2) create target out of ^tag and ^build-tag
3) run regen-repo to have initial repodata (happens automatically)
4) build module-build-macros which provides "dist" macro
5) tag module-build-macro into buildroot
6) wait for module-build-macro to be available in buildroot
7) build all components from scmurl
8) (optional) wait for selected builds to be available in buildroot

"""


class GenericBuilder(six.with_metaclass(ABCMeta)):
    """
    External Api for builders

    Example usage:
        config = module_build_service.config.Config()
        builder = Builder(module="testmodule-1.2-3", backend="koji", config)
        builder.buildroot_connect()
        builder.build(artifact_name="bash",
                      source="https://src.stg.fedoraproject.org/rpms/bash"
                             "?#70fa7516b83768595a4f3280ae890a7ac957e0c7")

        ...
        # E.g. on some other worker ... just resume buildroot that was initially created
        builder = Builder(module="testmodule-1.2-3", backend="koji", config)
        builder.buildroot_connect()
        builder.build(artifact_name="not-bash",
                      source="https://src.stg.fedoraproject.org/rpms/not-bash"
                             "?#70fa7516b83768595a4f3280ae890a7ac957e0c7")
        # wait until this particular bash is available in the buildroot
        builder.buildroot_ready(artifacts=["bash-1.23-el6"])
        builder.build(artifact_name="not-not-bash",
                      source="https://src.stg.fedoraproject.org/rpms/not-not-bash"
                             "?#70fa7516b83768595a4f3280ae890a7ac957e0c7")

    """

    backend = "generic"
    backends = {}

    # Create region to cache the default_buildroot_groups results.
    # We are skipping the caching based on the first two arguments of
    # default_buildroot_groups, because they are "self" and db.session
    # instance which are different each call we call that method.
    default_buildroot_groups_cache = (
        dogpile.cache.make_region(function_key_generator=create_dogpile_key_generator_func(2))
        .configure("dogpile.cache.memory")
    )

    @classmethod
    def register_backend_class(cls, backend_class):
        GenericBuilder.backends[backend_class.backend] = backend_class

    @classmethod
    def create(cls, owner, module, backend, config, **extra):
        """
        :param owner: a string representing who kicked off the builds
        :param module: module_build_service.models.ModuleBuild instance.
        :param backend: a string representing backend e.g. 'koji'
        :param config: instance of module_build_service.config.Config

        Any additional arguments are optional extras which can be passed along
        and are implementation-dependent.
        """
        # check if the backend is within allowed backends for the used resolver
        resolver = module_build_service.resolver.system_resolver
        if not resolver.is_builder_compatible(backend):
            raise ValueError(
                "Builder backend '{}' is not compatible with resolver backend '{}'. Check your "
                "configuration.".format(backend, resolver.backend)
            )

        if backend in GenericBuilder.backends:
            return GenericBuilder.backends[backend](
                owner=owner, module=module, config=config, **extra)
        else:
            raise ValueError("Builder backend='%s' not recognized" % backend)

    @classmethod
    def create_from_module(cls, session, module, config, buildroot_connect=True):
        """
        Creates new GenericBuilder instance based on the data from module
        and config and connects it to buildroot.

        :param session: SQLAlchemy databa session.
        :param module: module_build_service.models.ModuleBuild instance.
        :param config: module_build_service.config.Config instance.
        :kwarg buildroot_connect: a boolean that determines if the builder should run
        buildroot_connect on instantiation.
        """
        components = [c.package for c in module.component_builds]
        builder = GenericBuilder.create(
            module.owner,
            module,
            config.system,
            config,
            tag_name=module.koji_tag,
            components=components,
        )
        if buildroot_connect is True:
            groups = GenericBuilder.default_buildroot_groups(session, module)
            builder.buildroot_connect(groups)
        return builder

    @classmethod
    def tag_to_repo(cls, backend, config, tag_name, arch):
        """
        :param backend: a string representing the backend e.g. 'koji'.
        :param config: instance of module_build_service.config.Config
        :param tag_name: Tag for which the repository is returned
        :param arch: Architecture for which the repository is returned

        Returns URL of repository containing the built artifacts for
        the tag with particular name and architecture.
        """
        if backend in GenericBuilder.backends:
            return GenericBuilder.backends[backend].repo_from_tag(config, tag_name, arch)
        else:
            raise ValueError("Builder backend='%s' not recognized" % backend)

    @abstractmethod
    def buildroot_connect(self, groups):
        """
        This is an idempotent call to create or resume and validate the build
        environment.  .build() should immediately fail if .buildroot_connect()
        wasn't called.

        Koji Example: create tag, targets, set build tag inheritance...
        """
        raise NotImplementedError()

    @abstractmethod
    def buildroot_ready(self, artifacts=None):
        """
        :param artifacts=None : a list of artifacts supposed to be in the buildroot
                                (['bash-123-0.el6'])

        returns when the buildroot is ready (or contains the specified artifact)

        This function is here to ensure that the buildroot (repo) is ready and
        contains the listed artifacts if specified.
        """
        raise NotImplementedError()

    @abstractmethod
    def buildroot_add_repos(self, dependencies):
        """
        :param dependencies: a list of modules represented as a list of dicts,
                             like:
                             [{'name': ..., 'version': ..., 'release': ...}, ...]

        Make an additional repository available in the buildroot. This does not
        necessarily have to directly install artifacts (e.g. koji), just make
        them available.

        E.g. the koji implementation of the call uses MBS to get koji_tag
        associated with each module dep and adds the tag to $module-build tag
        inheritance.
        """
        raise NotImplementedError()

    @abstractmethod
    def buildroot_add_artifacts(self, artifacts, install=False):
        """
        :param artifacts: list of artifacts to be available or installed
                          (install=False) in the buildroot (e.g  list of $NEVRAS)
        :param install=False: pre-install artifact in the buildroot (otherwise
                              "just make it available for install")

        Example:

        koji tag-build $module-build-tag bash-1.234-1.el6
        if install:
            koji add-group-pkg $module-build-tag build bash
            # This forces install of bash into buildroot and srpm-buildroot
            koji add-group-pkg $module-build-tag srpm-build bash
        """
        raise NotImplementedError()

    @abstractmethod
    def tag_artifacts(self, artifacts):
        """
        :param artifacts: list of artifacts (NVRs) to be tagged

        Adds the artifacts to tag associated with this module build.
        """
        raise NotImplementedError()

    @abstractmethod
    def build(self, artifact_name, source):
        """
        :param artifact_name : A package name. We can't guess it since macros
                               in the buildroot could affect it, (e.g. software
                               collections).
        :param source : an SCM URL, clearly identifying the build artifact in a
                        repository
        :return 4-tuple of the form (build task id, state, reason, nvr)

        The artifact_name parameter is used in koji add-pkg (and it's actually
        the only reason why we need to pass it). We don't really limit source
        types. The actual source is usually delivered as an SCM URL from
        fedmsg.

        Warning: This function must be thread-safe.

        Example
        .build("bash", "git://someurl/bash#damn") #build from SCM URL
        .build("bash", "/path/to/srpm.src.rpm") #build from source RPM
        """
        raise NotImplementedError()

    @abstractmethod
    def cancel_build(self, task_id):
        """
        :param task_id: Task ID returned by the build method.

        Cancels the build.
        """
        raise NotImplementedError()

    @abstractmethod
    def finalize(self, succeeded=True):
        """
        :param succeeded: True if all module builds were successful
        :return: None

        This method is supposed to be called after all module builds are
        finished.

        It could be utilized for various purposes such as cleaning or
        running additional build-system based operations on top of
        finished builds
        """
        pass

    @classmethod
    @abstractmethod
    def repo_from_tag(self, config, tag_name, arch):
        """
        :param config: instance of module_build_service.config.Config
        :param tag_name: Tag for which the repository is returned
        :param arch: Architecture for which the repository is returned

        Returns URL of repository containing the built artifacts for
        the tag with particular name and architecture.
        """
        raise NotImplementedError()

    @classmethod
    def clear_cache(cls, module_build):
        """
        Clears the per module build default_buildroot_groups cache.
        """
        cls.default_buildroot_groups_cache.delete(
            "default_buildroot_groups_" + str(module_build.id))

    @classmethod
    @module_build_service.utils.retry(wait_on=(ConnectionError))
    @default_buildroot_groups_cache.cache_on_arguments()
    def default_buildroot_groups(cls, session, module):
        local_modules = models.ModuleBuild.local_modules(db.session)
        local_modules = {m.name + "-" + m.stream: m for m in local_modules}

        try:
            mmd = module.mmd()
            resolver = module_build_service.resolver.system_resolver

            # Resolve default buildroot groups using the MBS, but only for
            # non-local modules.
            groups = resolver.resolve_profiles(mmd, ("buildroot", "srpm-buildroot"))
            groups = {"build": groups["buildroot"], "srpm-build": groups["srpm-buildroot"]}
        except ValueError:
            reason = "Failed to gather buildroot groups from SCM."
            log.exception(reason)
            module.transition(conf, state="failed", state_reason=reason, failure_type="user")
            session.commit()
            raise
        return groups

    @abstractmethod
    def list_tasks_for_components(self, component_builds=None, state="active"):
        """
        :param component_builds: list of component builds which we want to check
        :param state: limit the check only for tasks in the given state
        :return: list of tasks

        This method is supposed to list tasks ('active' by default)
        for component builds.
        """
        raise NotImplementedError()

    @classmethod
    def get_built_rpms_in_module_build(cls, mmd):
        """
        :param Modulemd mmd: Modulemd to get the built RPMs from.
        :return: list of NVRs
        """
        raise NotImplementedError()

    @classmethod
    def get_module_build_arches(cls, module):
        """
        :param ModuleBuild module: Get the list of architectures associated with
            the module build in the build system.
        :return: list of architectures
        """
        return GenericBuilder.backends[conf.system].get_module_build_arches(module)

    @classmethod
    def recover_orphaned_artifact(cls, component_build):
        """
        Searches for a complete build of an artifact belonging to the module and sets the
        component_build in the MBS database to the found build. This usually returns nothing since
        these builds should *not* exist.
        :param artifact_name: a ComponentBuild object
        :return: a list of msgs that MBS needs to process
        """
        return []

    @classmethod
    def get_average_build_time(self, component):
        """
        Placeholder function for the builders to report the average time it takes to build the
        specified component. If this function is not overridden, then 0.0 is returned.
        :param component: a ComponentBuild object
        :return: a float of 0.0
        """
        return 0.0

    @classmethod
    def get_build_weights(cls, components):
        """
        Returns a dict with component name as a key and float number
        representing the overall Koji weight of a component build.

        :param list components: List of component names.
        :rtype: dict
        :return: {component_name: weight_as_float, ...}
        """
        return cls.compute_weights_from_build_time(components)

    @classmethod
    def compute_weights_from_build_time(cls, components, arches=None):
        """
        Computes the weights of ComponentBuilds based on average time to build
        and list of arches for which the component is going to be built.

        This method should be used as a fallback only when KojiModuleBuilder
        cannot be used, because the weight this method produces is not 100% accurate.

        :param components: List of comopnent names to compute the weight for.
        :param arches: List of arches to build for or None. If the value is None,
            conf.arches will be used instead.
        :rtype: dict
        :return: {component_name: weight_as_float, ...}
        """
        if not arches:
            arches = conf.arches

        weights = {}

        for component in components:
            average_time_to_build = cls.get_average_build_time(component)

            # The way how `weight` is computed is based on hardcoded weight values
            # in kojid.py.
            # The weight computed here is not 100% accurate, because there are
            # multiple smaller tasks in koji like waitrepo or createrepo and we
            # cannot say if they will be executed as part of this component build.
            # The weight computed here is used only to limit the number of builds
            # and we generally do not care about waitrepo/createrepo weights in MBS.

            # 1.5 is what Koji hardcodes as a default weight for BuildArchTask.
            weight = 1.5
            if not average_time_to_build:
                weights[component] = weight
                continue

            if average_time_to_build < 0:
                log.warning(
                    "Negative average build duration for component %s: %s",
                    component, str(average_time_to_build),
                )
                weights[component] = weight
                continue

            # Increase the task weight by 0.75 for every hour of build duration.
            adj = average_time_to_build / ((60 * 60) / 0.75)
            # cap the adjustment at +4.5
            weight += min(4.5, adj)

            # We build for all arches, so multiply the weight by number of arches.
            weight = weight * len(arches)

            # 1.5 here is hardcoded Koji weight of single BuildSRPMFromSCMTask
            weight += 1.5
            weights[component] = weight

        return weights

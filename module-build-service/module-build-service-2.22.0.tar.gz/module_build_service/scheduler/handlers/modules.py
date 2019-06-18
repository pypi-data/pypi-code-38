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
# Written by Ralph Bean <rbean@redhat.com>

""" Handlers for module change events on the message bus. """

from module_build_service import conf, models, log, build_logs
import module_build_service.builder
import module_build_service.resolver
import module_build_service.utils
import module_build_service.messaging
from module_build_service.utils import (
    attempt_to_reuse_all_components,
    record_component_builds,
    get_rpm_release,
    generate_koji_tag,
    record_filtered_rpms,
    record_module_build_arches,
)
from module_build_service.errors import UnprocessableEntity, Forbidden, ValidationError
from module_build_service.utils.ursine import handle_stream_collision_modules
from module_build_service.utils.greenwave import greenwave

from requests.exceptions import ConnectionError
from module_build_service.utils import mmd_to_str

import koji
import six.moves.xmlrpc_client as xmlrpclib
import logging
import os
import time

logging.basicConfig(level=logging.DEBUG)


def get_artifact_from_srpm(srpm_path):
    return os.path.basename(srpm_path).replace(".src.rpm", "")


def failed(config, session, msg):
    """
    Called whenever a module enters the 'failed' state.

    We cancel all the remaining component builds of a module
    and stop the building.
    """

    build = models.ModuleBuild.from_module_event(session, msg)

    module_info = build.json()
    if module_info["state"] != msg.module_build_state:
        log.warning(
            "Note that retrieved module state %r doesn't match message module state %r",
            module_info["state"], msg.module_build_state,
        )
        # This is ok.. it's a race condition we can ignore.
        pass

    unbuilt_components = [
        c for c in build.component_builds
        if (c.state != koji.BUILD_STATES["COMPLETE"] and c.state != koji.BUILD_STATES["FAILED"])
    ]

    if build.koji_tag:
        builder = module_build_service.builder.GenericBuilder.create_from_module(
            session, build, config)

        if build.new_repo_task_id:
            builder.cancel_build(build.new_repo_task_id)

        for component in unbuilt_components:
            if component.task_id:
                builder.cancel_build(component.task_id)
            component.state = koji.BUILD_STATES["FAILED"]
            component.state_reason = build.state_reason
            session.add(component)

        # Tell the external buildsystem to wrap up
        builder.finalize(succeeded=False)
    else:
        # Do not overwrite state_reason set by Frontend if any.
        if not build.state_reason:
            reason = "Missing koji tag. Assuming previously failed module lookup."
            log.error(reason)
            build.transition(config, state="failed", state_reason=reason, failure_type="infra")
            session.commit()
            return

    # Don't transition it again if it's already been transitioned
    if build.state != models.BUILD_STATES["failed"]:
        build.transition(config, state="failed", failure_type="user")

    session.commit()

    build_logs.stop(build)
    module_build_service.builder.GenericBuilder.clear_cache(build)


def done(config, session, msg):
    """Called whenever a module enters the 'done' state.

    We currently don't do anything useful, so moving to ready.
    Except for scratch module builds, which remain in the done state.
    Otherwise the done -> ready state should happen when all
    dependent modules were re-built, at least that's the current plan.
    """
    build = models.ModuleBuild.from_module_event(session, msg)
    module_info = build.json()
    if module_info["state"] != msg.module_build_state:
        log.warning(
            "Note that retrieved module state %r doesn't match message module state %r",
            module_info["state"], msg.module_build_state,
        )
        # This is ok.. it's a race condition we can ignore.
        pass

    # Scratch builds stay in 'done' state
    if not build.scratch:
        if greenwave is None or greenwave.check_gating(build):
            build.transition(config, state="ready")
            session.commit()

    build_logs.stop(build)
    module_build_service.builder.GenericBuilder.clear_cache(build)


def init(config, session, msg):
    """ Called whenever a module enters the 'init' state."""
    # Sleep for a few seconds to make sure the module in the database is committed
    # TODO: Remove this once messaging is implemented in SQLAlchemy hooks
    for i in range(3):
        build = models.ModuleBuild.from_module_event(session, msg)
        if build:
            break
        time.sleep(1)

    error_msg = ""
    failure_reason = "unspec"
    try:
        mmd = build.mmd()
        record_module_build_arches(mmd, build, session)
        record_component_builds(mmd, build, session=session)
        # The ursine.handle_stream_collision_modules is Koji specific.
        if conf.system in ["koji", "test"]:
            handle_stream_collision_modules(mmd)
        mmd = record_filtered_rpms(mmd)
        build.modulemd = mmd_to_str(mmd)
        build.transition(conf, models.BUILD_STATES["wait"])
    # Catch custom exceptions that we can expose to the user
    except (UnprocessableEntity, Forbidden, ValidationError, RuntimeError) as e:
        log.exception(str(e))
        error_msg = str(e)
        failure_reason = "user"
    except (xmlrpclib.ProtocolError, koji.GenericError) as e:
        log.exception(str(e))
        error_msg = 'Koji communication error: "{0}"'.format(str(e))
        failure_reason = "infra"
    except Exception as e:
        log.exception(str(e))
        error_msg = "An unknown error occurred while validating the modulemd"
        failure_reason = "user"
    else:
        session.add(build)
        session.commit()
    finally:
        if error_msg:
            # Rollback changes underway
            session.rollback()
            build.transition(
                conf,
                models.BUILD_STATES["failed"],
                state_reason=error_msg,
                failure_type=failure_reason,
            )


def generate_module_build_koji_tag(build):
    """Used by wait handler to get module build koji tag

    :param build: a module build.
    :type build: :class:`ModuleBuild`
    :return: generated koji tag.
    :rtype: str
    """
    log.info("Getting tag for %s:%s:%s", build.name, build.stream, build.version)
    if conf.system in ["koji", "test"]:
        return generate_koji_tag(
            build.name,
            build.stream,
            build.version,
            build.context,
            scratch=build.scratch,
            scratch_id=build.id,
        )
    else:
        return "-".join(["module", build.name, build.stream, build.version])


@module_build_service.utils.retry(
    interval=10, timeout=120, wait_on=(ValueError, RuntimeError, ConnectionError)
)
def get_module_build_dependencies(build):
    """Used by wait handler to get module's build dependencies

    :param build: a module build.
    :type build: :class:`ModuleBuild`
    :return: the value returned from :meth:`get_module_build_dependencies`
        according to the configured resolver.
    :rtype: dict[str, Modulemd.Module]
    """
    resolver = module_build_service.resolver.system_resolver
    if conf.system in ["koji", "test"]:
        # For Koji backend, query for the module we are going to
        # build to get the koji_tag and deps from it.
        log.info("Getting tag for %s:%s:%s", build.name, build.stream, build.version)
        return resolver.get_module_build_dependencies(
            build.name, build.stream, build.version, build.context, strict=True)
    else:
        # In case of non-koji backend, we want to get the dependencies
        # of the local module build based on Modulemd.Module, because the
        # local build is not stored in the external MBS and therefore we
        # cannot query it using the `query` as for Koji below.
        return resolver.get_module_build_dependencies(mmd=build.mmd(), strict=True)


def get_content_generator_build_koji_tag(module_deps):
    """Used by wait handler to get koji tag for import by content generator

    :param module_deps: a mapping from module's koji tag to its module
        metadata.
    :type: dict[str, Modulemd.Module]
    :return: the koji tag.
    :rtype: str
    """
    if conf.system in ["koji", "test"]:
        # Find out the name of Koji tag to which the module's Content
        # Generator build should be tagged once the build finishes.
        module_names_streams = {
            mmd.get_module_name(): mmd.get_stream_name()
            for mmds in module_deps.values()
            for mmd in mmds
        }
        for base_module_name in conf.base_module_names:
            if base_module_name in module_names_streams:
                return conf.koji_cg_build_tag_template.format(
                    module_names_streams[base_module_name])

        log.debug(
            "No configured base module is a buildrequire. Hence use"
            " default content generator build koji tag %s",
            conf.koji_cg_default_build_tag,
        )
        return conf.koji_cg_default_build_tag
    else:
        return conf.koji_cg_default_build_tag


def wait(config, session, msg):
    """ Called whenever a module enters the 'wait' state.

    We transition to this state shortly after a modulebuild is first requested.

    All we do here is request preparation of the buildroot.
    The kicking off of individual component builds is handled elsewhere,
    in module_build_service.schedulers.handlers.repos.
    """

    # Wait for the db on the frontend to catch up to the message, otherwise the
    # xmd information won't be present when we need it.
    # See https://pagure.io/fm-orchestrator/issue/386
    @module_build_service.utils.retry(interval=10, timeout=120, wait_on=RuntimeError)
    def _get_build_containing_xmd_for_mbs():
        build = models.ModuleBuild.from_module_event(session, msg)
        if "mbs" in build.mmd().get_xmd():
            return build
        session.expire(build)
        raise RuntimeError("{!r} doesn't contain xmd information for MBS.".format(build))

    build = _get_build_containing_xmd_for_mbs()
    build_logs.start(build)

    log.info("Found build=%r from message" % build)
    log.info("%r", build.modulemd)

    if build.state != msg.module_build_state:
        log.warning(
            "Note that retrieved module state %r doesn't match message module state %r",
            build.state, msg.module_build_state,
        )
        # This is ok.. it's a race condition we can ignore.
        pass

    try:
        build_deps = get_module_build_dependencies(build)
    except ValueError:
        reason = "Failed to get module info from MBS. Max retries reached."
        log.exception(reason)
        build.transition(config, state="failed", state_reason=reason, failure_type="infra")
        session.commit()
        raise

    tag = generate_module_build_koji_tag(build)
    log.debug("Found tag=%s for module %r" % (tag, build))
    # Hang on to this information for later.  We need to know which build is
    # associated with which koji tag, so that when their repos are regenerated
    # in koji we can figure out which for which module build that event is
    # relevant.
    log.debug("Assigning koji tag=%s to module build" % tag)
    build.koji_tag = tag

    if build.scratch:
        log.debug(
            "Assigning Content Generator build koji tag is skipped for scratch module build.")
    elif conf.koji_cg_tag_build:
        cg_build_koji_tag = get_content_generator_build_koji_tag(build_deps)
        log.debug(
            "Assigning Content Generator build koji tag=%s to module build", cg_build_koji_tag)
        build.cg_build_koji_tag = cg_build_koji_tag
    else:
        log.debug(
            "It is disabled to tag module build during importing into Koji by Content Generator.")
        log.debug("Skip to assign Content Generator build koji tag to module build.")

    builder = module_build_service.builder.GenericBuilder.create_from_module(session, build, config)

    log.debug(
        "Adding dependencies %s into buildroot for module %s:%s:%s",
        build_deps.keys(), build.name, build.stream, build.version,
    )
    builder.buildroot_add_repos(build_deps)

    if not build.component_builds:
        log.info("There are no components in module %r, skipping build" % build)
        build.transition(config, state="build")
        session.add(build)
        session.commit()
        # Return a KojiRepoChange message so that the build can be transitioned to done
        # in the repos handler
        return [
            module_build_service.messaging.KojiRepoChange(
                "handlers.modules.wait: fake msg", builder.module_build_tag["name"])
        ]

    # If all components in module build will be reused, we don't have to build
    # module-build-macros, because there won't be any build done.
    if attempt_to_reuse_all_components(builder, session, build):
        log.info("All components have been reused for module %r, skipping build" % build)
        build.transition(config, state="build")
        session.add(build)
        session.commit()
        return []

    log.debug("Starting build batch 1")
    build.batch = 1
    session.commit()

    artifact_name = "module-build-macros"

    component_build = models.ComponentBuild.from_component_name(session, artifact_name, build.id)
    further_work = []
    srpm = builder.get_disttag_srpm(disttag=".%s" % get_rpm_release(build), module_build=build)
    if not component_build:
        component_build = models.ComponentBuild(
            module_id=build.id,
            package=artifact_name,
            format="rpms",
            scmurl=srpm,
            batch=1,
            build_time_only=True,
        )
        session.add(component_build)
        # Commit and refresh so that the SQLAlchemy relationships are available
        session.commit()
        session.refresh(component_build)
        msgs = builder.recover_orphaned_artifact(component_build)
        if msgs:
            log.info("Found an existing module-build-macros build")
            further_work += msgs
        # There was no existing artifact found, so lets submit the build instead
        else:
            task_id, state, reason, nvr = builder.build(artifact_name=artifact_name, source=srpm)
            component_build.task_id = task_id
            component_build.state = state
            component_build.reason = reason
            component_build.nvr = nvr
    elif component_build.state != koji.BUILD_STATES["COMPLETE"]:
        # It's possible that the build succeeded in the builder but some other step failed which
        # caused module-build-macros to be marked as failed in MBS, so check to see if it exists
        # first
        msgs = builder.recover_orphaned_artifact(component_build)
        if msgs:
            log.info("Found an existing module-build-macros build")
            further_work += msgs
        else:
            task_id, state, reason, nvr = builder.build(artifact_name=artifact_name, source=srpm)
            component_build.task_id = task_id
            component_build.state = state
            component_build.reason = reason
            component_build.nvr = nvr

    session.add(component_build)
    build.transition(config, state="build")
    session.add(build)
    session.commit()

    # We always have to regenerate the repository.
    if config.system == "koji":
        log.info("Regenerating the repository")
        task_id = builder.koji_session.newRepo(builder.module_build_tag["name"])
        build.new_repo_task_id = task_id
        session.commit()
    else:
        further_work.append(
            module_build_service.messaging.KojiRepoChange(
                "fake msg", builder.module_build_tag["name"])
        )
    return further_work

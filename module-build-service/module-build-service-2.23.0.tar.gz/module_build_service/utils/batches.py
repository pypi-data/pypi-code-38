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
import concurrent.futures

from module_build_service import conf, log, models
import module_build_service.messaging
from .reuse import get_reusable_components, reuse_component


def at_concurrent_component_threshold(config, session):
    """
    Determines if the number of concurrent component builds has reached
    the configured threshold
    :param config: Module Build Service configuration object
    :param session: SQLAlchemy database session
    :return: boolean representing if there are too many concurrent builds at
    this time
    """

    # We must not check it for "mock" backend.
    # It would lead to multiple calls of continue_batch_build method and
    # creation of multiple worker threads there. Mock backend uses thread-id
    # to create and identify mock buildroot and for mock backend, we must
    # build whole module in this single continue_batch_build call to keep
    # the number of created buildroots low. The concurrent build limit
    # for mock backend is secured by setting max_workers in
    # ThreadPoolExecutor to num_concurrent_builds.
    if conf.system == "mock":
        return False

    import koji  # Placed here to avoid py2/py3 conflicts...

    # Components which are reused should not be counted in, because
    # we do not submit new build for them. They are in BUILDING state
    # just internally in MBS to be handled by
    # scheduler.handlers.components.complete.
    if config.num_concurrent_builds:
        count = session.query(models.ComponentBuild).filter_by(
            state=koji.BUILD_STATES["BUILDING"], reused_component_id=None).count()
        if config.num_concurrent_builds <= count:
            return True

    return False


def start_build_component(builder, c):
    """
    Submits single component build to builder. Called in thread
    by QueueBasedThreadPool in continue_batch_build.
    """
    import koji

    try:
        c.task_id, c.state, c.state_reason, c.nvr = builder.build(
            artifact_name=c.package, source=c.scmurl)
    except Exception as e:
        c.state = koji.BUILD_STATES["FAILED"]
        c.state_reason = "Failed to build artifact %s: %s" % (c.package, str(e))
        log.exception(e)
        c.module_build.transition(conf, models.BUILD_STATES["failed"], failure_type="infra")
        return

    if not c.task_id and c.state == koji.BUILD_STATES["BUILDING"]:
        c.state = koji.BUILD_STATES["FAILED"]
        c.state_reason = "Failed to build artifact %s: Builder did not return task ID" % (c.package)
        c.module_build.transition(conf, models.BUILD_STATES["failed"], failure_type="infra")
        return


def continue_batch_build(config, module, session, builder, components=None):
    """
    Continues building current batch. Submits next components in the batch
    until it hits concurrent builds limit.

    Returns list of BaseMessage instances which should be scheduled by the
    scheduler.
    """
    import koji  # Placed here to avoid py2/py3 conflicts...

    # The user can either pass in a list of components to 'seed' the batch, or
    # if none are provided then we just select everything that hasn't
    # successfully built yet or isn't currently being built.
    unbuilt_components = components or [
        c for c in module.component_builds
        if (
            c.state != koji.BUILD_STATES["COMPLETE"]
            and c.state != koji.BUILD_STATES["BUILDING"]
            and c.state != koji.BUILD_STATES["FAILED"]
            and c.batch == module.batch
        )
    ]

    if not unbuilt_components:
        log.debug("Cannot continue building module %s. No component to build." % module)
        return []

    # Get the list of components to be built in this batch. We are not building
    # all `unbuilt_components`, because we can meet the num_concurrent_builds
    # threshold
    further_work = []
    components_to_build = []
    # Sort the unbuilt_components so that the components that take the longest to build are
    # first
    unbuilt_components.sort(key=lambda c: c.weight, reverse=True)

    # Check for builds that exist in the build system but MBS doesn't know about
    for component in unbuilt_components:
        # Only evaluate new components
        if component.state is not None:
            continue
        msgs = builder.recover_orphaned_artifact(component)
        further_work += msgs

    for c in unbuilt_components:
        # If a previous build of the component was found, then the state will be marked as
        # COMPLETE so we should skip this
        if c.state == koji.BUILD_STATES["COMPLETE"]:
            continue
        # Check the concurrent build threshold.
        if at_concurrent_component_threshold(config, session):
            log.info("Concurrent build threshold met")
            break

        # We set state to "BUILDING" here because at this point we are committed
        # to build the component and at_concurrent_component_threshold() works by
        # counting the number of components in the "BUILDING" state.
        c.state = koji.BUILD_STATES["BUILDING"]
        components_to_build.append(c)

    # Start build of components in this batch.
    max_workers = 1
    if config.num_concurrent_builds > 0:
        max_workers = config.num_concurrent_builds
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(start_build_component, builder, c): c for c in components_to_build
        }
        concurrent.futures.wait(futures)
        # In case there has been an excepion generated directly in the
        # start_build_component, the future.result() will re-raise it in the
        # main thread so it is not lost.
        for future in futures:
            future.result()

    session.commit()
    return further_work


def start_next_batch_build(config, module, session, builder, components=None):
    """
    Tries to start the build of next batch. In case there are still unbuilt
    components in a batch, tries to submit more components until it hits
    concurrent builds limit. Otherwise Increments module.batch and submits component
    builds from the next batch.

    :return: a list of BaseMessage instances to be handled by the MBSConsumer.
    """
    import koji  # Placed here to avoid py2/py3 conflicts...

    # Check the status of the module build and current batch so we can
    # later decide if we can start new batch or not.
    has_unbuilt_components = False
    has_unbuilt_components_in_batch = False
    has_building_components_in_batch = False
    has_failed_components = False
    # This is used to determine if it's worth checking if a component can be reused
    # later on in the code
    all_reused_in_prev_batch = True
    for c in module.component_builds:
        if c.state in [None, koji.BUILD_STATES["BUILDING"]]:
            has_unbuilt_components = True

            if c.batch == module.batch:
                if not c.state:
                    has_unbuilt_components_in_batch = True
                elif c.state == koji.BUILD_STATES["BUILDING"]:
                    has_building_components_in_batch = True
        elif c.state in [koji.BUILD_STATES["FAILED"], koji.BUILD_STATES["CANCELED"]]:
            has_failed_components = True

        if c.batch == module.batch and not c.reused_component_id:
            all_reused_in_prev_batch = False

    # Do not start new batch if there are no components to build.
    if not has_unbuilt_components:
        log.debug(
            "Not starting new batch, there is no component to build for module %s" % module)
        return []

    # Check that there is something to build in current batch before starting
    # the new one. If there is, continue building current batch.
    if has_unbuilt_components_in_batch:
        log.info("Continuing building batch %d", module.batch)
        return continue_batch_build(config, module, session, builder, components)

    # Check that there are no components in BUILDING state in current batch.
    # If there are, wait until they are built.
    if has_building_components_in_batch:
        log.debug(
            "Not starting new batch, there are still components in "
            "BUILDING state in current batch for module %s",
            module,
        )
        return []

    # Check that there are no failed components in this batch. If there are,
    # do not start the new batch.
    if has_failed_components:
        log.info("Not starting new batch, there are failed components for module %s", module)
        return []

    # Identify active tasks which might contain relicts of previous builds
    # and fail the module build if this^ happens.
    active_tasks = builder.list_tasks_for_components(module.component_builds, state="active")
    if isinstance(active_tasks, list) and active_tasks:
        state_reason = \
            "Cannot start a batch, because some components are already in 'building' state."
        state_reason += " See tasks (ID): {}".format(
            ", ".join([str(t["id"]) for t in active_tasks])
        )
        module.transition(
            config,
            state=models.BUILD_STATES["failed"],
            state_reason=state_reason,
            failure_type="infra",
        )
        session.commit()
        return []

    else:
        log.debug("Builder {} doesn't provide information about active tasks.".format(builder))

    # Find out if there is repo regeneration in progress for this module.
    # If there is, wait until the repo is regenerated before starting a new
    # batch.
    artifacts = [c.nvr for c in module.current_batch()]
    if not builder.buildroot_ready(artifacts):
        log.info(
            "Not starting new batch, not all of %r are in the buildroot. Waiting." % artifacts)
        return []

    # Although this variable isn't necessary, it is easier to read code later on with it
    prev_batch = module.batch
    module.batch += 1

    # The user can either pass in a list of components to 'seed' the batch, or
    # if none are provided then we just select everything that hasn't
    # successfully built yet or isn't currently being built.
    unbuilt_components = components or [
        c for c in module.component_builds
        if (
            c.state != koji.BUILD_STATES["COMPLETE"]
            and c.state != koji.BUILD_STATES["BUILDING"]
            and c.state != koji.BUILD_STATES["FAILED"]
            and c.batch == module.batch
        )
    ]

    # If there are no components to build, skip the batch and start building
    # the new one. This can happen when resubmitting the failed module build.
    if not unbuilt_components and not components:
        log.info("Skipping build of batch %d, no component to build.", module.batch)
        return start_next_batch_build(config, module, session, builder)

    log.info("Starting build of next batch %d, %s" % (module.batch, unbuilt_components))

    # Attempt to reuse any components possible in the batch before attempting to build any
    further_work = []
    unbuilt_components_after_reuse = []
    components_reused = False
    should_try_reuse = True
    # If the rebuild strategy is "changed-and-after", try to figure out if it's worth checking if
    # the components can be reused to save on resources
    if module.rebuild_strategy == "changed-and-after":
        # Check to see if the previous batch had all their builds reused except for when the
        # previous batch was 1 because that always has the module-build-macros component built
        should_try_reuse = all_reused_in_prev_batch or prev_batch == 1
    if should_try_reuse:
        component_names = [c.package for c in unbuilt_components]
        reusable_components = get_reusable_components(session, module, component_names)
        for c, reusable_c in zip(unbuilt_components, reusable_components):
            if reusable_c:
                components_reused = True
                further_work += reuse_component(c, reusable_c)
            else:
                unbuilt_components_after_reuse.append(c)
        # Commit the changes done by reuse_component
        if components_reused:
            session.commit()

    # If all the components were reused in the batch then make a KojiRepoChange
    # message and return
    if components_reused and not unbuilt_components_after_reuse:
        further_work.append(
            module_build_service.messaging.KojiRepoChange(
                "start_build_batch: fake msg", builder.module_build_tag["name"])
        )
        return further_work

    return further_work + continue_batch_build(
        config, module, session, builder, unbuilt_components_after_reuse)

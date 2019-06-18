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

""" Handlers for repo change events on the message bus. """

import module_build_service.builder
import logging
import koji
from datetime import datetime
from module_build_service import models, log
from module_build_service.utils import start_next_batch_build

logging.basicConfig(level=logging.DEBUG)


def done(config, session, msg):
    """ Called whenever koji rebuilds a repo, any repo. """

    # First, find our ModuleBuild associated with this repo, if any.
    tag = msg.repo_tag
    if config.system in ("koji", "test") and not tag.endswith("-build"):
        log.debug("Tag %r does not end with '-build' suffix, ignoring" % tag)
        return
    tag = tag[:-6] if tag.endswith("-build") else tag
    module_build = models.ModuleBuild.from_repo_done_event(session, msg)
    if not module_build:
        log.debug("No module build found associated with koji tag %r" % tag)
        return

    # It is possible that we have already failed.. but our repo is just being
    # routinely regenerated.  Just ignore that.  If module_build_service says the module is
    # dead, then the module is dead.
    if module_build.state == models.BUILD_STATES["failed"]:
        log.info("Ignoring repo regen for already failed %r" % module_build)
        return

    # Get the list of untagged components in current/previous batches which
    # have been built successfully
    if config.system in ("koji", "test") and module_build.component_builds:
        untagged_components = [
            c for c in module_build.up_to_current_batch()
            if (not c.tagged or (not c.tagged_in_final and not c.build_time_only))
            and c.state == koji.BUILD_STATES["COMPLETE"]
        ]
        if untagged_components:
            log.info("Ignoring repo regen, because not all components are tagged.")
            return
        if all([c.state is None for c in module_build.current_batch()]):
            log.info("Ignoring repo regen because no components have started in the batch.")
            return

    # If there are no components in this module build, then current_batch will be empty
    if not module_build.component_builds:
        current_batch = []
    else:
        current_batch = module_build.current_batch()

    # If any in the current batch are still running.. just wait.
    running = [c.state == koji.BUILD_STATES["BUILDING"] for c in current_batch]
    if any(running):
        log.info(
            "%r has %r of %r components still "
            "building in this batch (%r total)"
            % (module_build, len(running), len(current_batch), len(module_build.component_builds))
        )
        return

    # Assemble the list of all successful components in the batch.
    good = [c for c in current_batch if c.state == koji.BUILD_STATES["COMPLETE"]]

    failed_states = (koji.BUILD_STATES["FAILED"], koji.BUILD_STATES["CANCELED"])

    # If *none* of the components completed for this batch, then obviously the
    # module fails.  However!  We shouldn't reach this scenario.  There is
    # logic over in the component handler which should fail the module build
    # first before we ever get here.  This is here as a race condition safety
    # valve.
    if module_build.component_builds and not good:
        state_reason = "Component(s) {} failed to build.".format(
            ", ".join(c.package for c in current_batch if c.state in failed_states))
        module_build.transition(
            config, models.BUILD_STATES["failed"], state_reason, failure_type="infra")
        session.commit()
        log.warning("Odd!  All components in batch failed for %r." % module_build)
        return

    groups = module_build_service.builder.GenericBuilder.default_buildroot_groups(
        session, module_build)

    builder = module_build_service.builder.GenericBuilder.create(
        module_build.owner,
        module_build,
        config.system,
        config,
        tag_name=tag,
        components=[c.package for c in module_build.component_builds],
    )
    builder.buildroot_connect(groups)

    # If we have reached here then we know the following things:
    #
    # - All components in this batch have finished (failed or succeeded)
    # - One or more succeeded.
    # - They have been regenerated back into the buildroot.
    #
    # So now we can either start a new batch if there are still some to build
    # or, if everything is built successfully, then we can bless the module as
    # complete.
    has_unbuilt_components = any(
        c.state in [None, koji.BUILD_STATES["BUILDING"]] for c in module_build.component_builds)
    has_failed_components = any(c.state in failed_states for c in module_build.component_builds)

    further_work = []
    if has_unbuilt_components and not has_failed_components:
        # Ok, for the subset of builds that did complete successfully, check to
        # see if they are in the buildroot before starting new batch.
        artifacts = [component_build.nvr for component_build in good]
        if not builder.buildroot_ready(artifacts):
            log.info("Not all of %r are in the buildroot.  Waiting." % artifacts)
            return

        # Try to start next batch build, because there are still unbuilt
        # components in a module.
        further_work += start_next_batch_build(config, module_build, session, builder)

    else:
        if has_failed_components:
            state_reason = "Component(s) {} failed to build.".format(
                ", ".join(
                    c.package for c in module_build.component_builds if c.state in failed_states
                )
            )
            module_build.transition(
                config,
                state=models.BUILD_STATES["failed"],
                state_reason=state_reason,
                failure_type="user",
            )
        else:
            # Tell the external buildsystem to wrap up (CG import, createrepo, etc.)
            module_build.time_completed = datetime.utcnow()
            builder.finalize(succeeded=True)

            module_build.transition(config, state=models.BUILD_STATES["done"])
        session.commit()

    return further_work

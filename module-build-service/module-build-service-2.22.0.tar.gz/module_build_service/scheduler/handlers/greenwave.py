# -*- coding: utf-8 -*-
# Copyright (c) 2019  Red Hat, Inc.
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

from module_build_service import conf, log
from module_build_service.builder.KojiModuleBuilder import KojiModuleBuilder
from module_build_service.models import ModuleBuild, BUILD_STATES


def get_corresponding_module_build(session, nvr):
    """Find corresponding module build from database and return

    :param session: the SQLAlchemy database session object.
    :param str nvr: module build NVR. This is the subject_identifier included
        inside ``greenwave.decision.update`` message.
    :return: the corresponding module build object. For whatever the reason,
        if the original module build id cannot be found from the Koji build of
        ``nvr``, None will be returned.
    :rtype: :class:`ModuleBuild` or None
    """
    koji_session = KojiModuleBuilder.get_session(conf, login=False)
    build_info = koji_session.getBuild(nvr)
    if build_info is None:
        return None

    try:
        module_build_id = build_info["extra"]["typeinfo"]["module"]["module_build_service_id"]
    except KeyError:
        # If any of the keys is not present, the NVR is not the one for
        # handling Greenwave event.
        return None

    return ModuleBuild.get_by_id(session, module_build_id)


def decision_update(config, session, msg):
    """Move module build to ready or failed according to Greenwave result

    :param config: the config object returned from function :func:`init_config`,
        which is loaded from configuration file.
    :type config: :class:`Config`
    :param session: the SQLAlchemy database session object.
    :param msg: the message object representing a message received from topic
        ``greenwave.decision.update``.
    :type msg: :class:`GreenwaveDecisionUpdate`
    """
    if not config.greenwave_decision_context:
        log.debug(
            "Skip Greenwave message %s as MBS does not have GREENWAVE_DECISION_CONTEXT "
            "configured",
            msg.msg_id,
        )
        return

    if msg.decision_context != config.greenwave_decision_context:
        log.debug(
            "Skip Greenwave message %s as MBS only handles messages with the "
            'decision context "%s"',
            msg.msg_id,
            config.greenwave_decision_context,
        )
        return

    module_build_nvr = msg.subject_identifier

    if not msg.policies_satisfied:
        log.debug(
            "Skip to handle module build %s because it has not satisfied Greenwave policies.",
            module_build_nvr,
        )
        return

    build = get_corresponding_module_build(session, module_build_nvr)

    if build is None:
        log.debug(
            "No corresponding module build of subject_identifier %s is found.", module_build_nvr)
        return

    if build.state == BUILD_STATES["done"]:
        build.transition(
            conf,
            BUILD_STATES["ready"],
            state_reason="Module build {} has satisfied Greenwave policies.".format(
                module_build_nvr
            ),
        )
    else:
        log.warning(
            "Module build %s is not in done state but Greenwave tells "
            "it passes tests in decision context %s",
            module_build_nvr,
            msg.decision_context,
        )

    session.commit()

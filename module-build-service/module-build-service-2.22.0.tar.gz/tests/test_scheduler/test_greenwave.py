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

import pytest

from mock import call, patch, Mock
from sqlalchemy import func

from module_build_service import conf, db
from module_build_service.models import BUILD_STATES, ModuleBuild
from module_build_service.scheduler.consumer import MBSConsumer
from module_build_service.scheduler.handlers.greenwave import get_corresponding_module_build
from module_build_service.scheduler.handlers.greenwave import decision_update
from tests import clean_database, make_module


class TestGetCorrespondingModuleBuild:
    """Test get_corresponding_module_build"""

    def setup_method(self, method):
        clean_database()

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_module_build_nvr_does_not_exist_in_koji(self, ClientSession):
        ClientSession.return_value.getBuild.return_value = None

        assert get_corresponding_module_build(db.session, "n-v-r") is None

    @pytest.mark.parametrize(
        "build_info",
        [
            # Build info does not have key extra
            {"id": 1000, "name": "ed"},
            # Build info contains key extra, but it is not for the module build
            {"extra": {"submitter": "osbs", "image": {}}},
            # Key module_build_service_id is missing
            {"extra": {"typeinfo": {"module": {}}}},
        ],
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_cannot_find_module_build_id_from_build_info(self, ClientSession, build_info):
        ClientSession.return_value.getBuild.return_value = build_info

        assert get_corresponding_module_build(db.session, "n-v-r") is None

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_corresponding_module_build_id_does_not_exist_in_db(self, ClientSession):
        fake_module_build_id, = db.session.query(func.max(ModuleBuild.id)).first()

        ClientSession.return_value.getBuild.return_value = {
            "extra": {"typeinfo": {"module": {"module_build_service_id": fake_module_build_id + 1}}}
        }

        assert get_corresponding_module_build(db.session, "n-v-r") is None

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_find_the_module_build(self, ClientSession):
        expected_module_build = (
            db.session.query(ModuleBuild).filter(ModuleBuild.name == "platform").first()
        )

        ClientSession.return_value.getBuild.return_value = {
            "extra": {"typeinfo": {"module": {"module_build_service_id": expected_module_build.id}}}
        }

        build = get_corresponding_module_build(db.session, "n-v-r")

        assert expected_module_build.id == build.id
        assert expected_module_build.name == build.name


class TestDecisionUpdateHandler:
    """Test handler decision_update"""

    @patch("module_build_service.scheduler.handlers.greenwave.log")
    def test_decision_context_is_not_match(self, log):
        msg = Mock(msg_id="msg-id-1", decision_context="bodhi_update_push_testing")
        decision_update(conf, db.session, msg)
        log.debug.assert_called_once_with(
            'Skip Greenwave message %s as MBS only handles messages with the decision context "%s"',
            "msg-id-1",
            "test_dec_context"
        )

    @patch("module_build_service.scheduler.handlers.greenwave.log")
    def test_not_satisfy_policies(self, log):
        msg = Mock(
            msg_id="msg-id-1",
            decision_context="test_dec_context",
            policies_satisfied=False,
            subject_identifier="pkg-0.1-1.c1",
        )
        decision_update(conf, db.session, msg)
        log.debug.assert_called_once_with(
            "Skip to handle module build %s because it has not satisfied Greenwave policies.",
            msg.subject_identifier,
        )

    @patch("module_build_service.messaging.publish")
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_transform_from_done_to_ready(self, ClientSession, publish):
        clean_database()

        # This build should be queried and transformed to ready state
        module_build = make_module("pkg:0.1:1:c1", requires_list={"platform": "el8"})
        module_build.transition(
            conf, BUILD_STATES["done"], "Move to done directly for running test."
        )

        # Assert this call below
        first_publish_call = call(
            service="mbs",
            topic="module.state.change",
            msg=module_build.json(show_tasks=False),
            conf=conf,
        )

        db.session.refresh(module_build)

        ClientSession.return_value.getBuild.return_value = {
            "extra": {"typeinfo": {"module": {"module_build_service_id": module_build.id}}}
        }

        msg = {
            "msg_id": "msg-id-1",
            "topic": "org.fedoraproject.prod.greenwave.decision.update",
            "msg": {
                "decision_context": "test_dec_context",
                "policies_satisfied": True,
                "subject_identifier": "pkg-0.1-1.c1",
            },
        }
        hub = Mock(config={"validate_signatures": False})
        consumer = MBSConsumer(hub)
        consumer.consume(msg)

        # Load module build again to check its state is moved correctly
        module_build = (
            db.session.query(ModuleBuild).filter(ModuleBuild.id == module_build.id).first())

        assert BUILD_STATES["ready"] == module_build.state

        publish.assert_has_calls([
            first_publish_call,
            call(
                service="mbs",
                topic="module.state.change",
                msg=module_build.json(show_tasks=False),
                conf=conf,
            ),
        ])

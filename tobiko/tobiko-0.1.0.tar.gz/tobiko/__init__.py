# Copyright 2018 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

from tobiko.common import _asserts
from tobiko.common import _exception
from tobiko.common import _fixture
from tobiko.common.managers import testcase as testcase_manager
from tobiko.common.managers import loader as loader_manager
from tobiko.common import _skip


FailureException = _asserts.FailureException
fail = _asserts.fail

TobikoException = _exception.TobikoException

is_fixture = _fixture.is_fixture
get_fixture = _fixture.get_fixture
fixture_property = _fixture.fixture_property
required_fixture = _fixture.required_fixture
required_setup_fixture = _fixture.required_setup_fixture
get_fixture_name = _fixture.get_fixture_name
get_fixture_class = _fixture.get_fixture_class
get_fixture_dir = _fixture.get_fixture_dir
remove_fixture = _fixture.remove_fixture
setup_fixture = _fixture.setup_fixture
cleanup_fixture = _fixture.cleanup_fixture
list_required_fixtures = _fixture.list_required_fixtures
SharedFixture = _fixture.SharedFixture

load_object = loader_manager.load_object
load_module = loader_manager.load_module

discover_testcases = testcase_manager.discover_testcases

SkipException = _skip.SkipException
skip = _skip.skip
skip_if = _skip.skip_if
skip_until = _skip.skip_until

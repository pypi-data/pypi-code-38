# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

import pytest

import fastr
from fastr.core.tool import Tool
from fastr.core.version import Version


@pytest.fixture(scope="module")
def tool_addint():
    return fastr.tools['fastr/math/Add:1.0', '1.0']


@pytest.fixture(scope="module")
def tool_sum():
    return fastr.tools['fastr/math/Sum:1.0', '1.0']


def test_tool_eq_operator(tool_addint, tool_sum):
    # Create copies for testing equal operator
    tool_addint_copy = copy.deepcopy(tool_addint)
    tool_sum_copy = copy.deepcopy(tool_sum)

    assert tool_addint == tool_addint
    assert tool_addint == tool_addint_copy
    assert tool_sum == tool_sum_copy
    assert tool_addint != tool_sum
    assert tool_addint_copy != tool_sum


def test_tool_getstate_setstate(tool_addint, tool_sum):
    #  Dump state and rebuild in a clean object
    addint_state = tool_addint.__getstate__()
    addint_rebuilt = Tool.__new__(Tool)
    addint_rebuilt.__setstate__(addint_state)
    assert tool_addint == addint_rebuilt

    #  Dump state and rebuild in a clean object
    sum_state = tool_sum.__getstate__()
    sum_rebuilt = Tool.__new__(Tool)
    sum_rebuilt.__setstate__(sum_state)
    assert tool_sum == sum_rebuilt


def test_tool_serializing(tool_addint, tool_sum):
    addint_json = tool_addint.dumps()
    addint_rebuilt = Tool.loads(addint_json)
    assert tool_addint == addint_rebuilt

    sum_json = tool_sum.dumps()
    sum_rebuilt = Tool.loads(sum_json)
    assert tool_sum == sum_rebuilt


def test_toolversions():
    toolname = 'fastr/Source:1.0'
    version = Version("1.0")
    tool = fastr.tools[toolname, version]
    assert fastr.tools.toolversions(tool)[0] == version
    assert fastr.tools.toolversions(toolname)[0] == version
    assert len(fastr.tools.toolversions(toolname)) == 1  # "Excpected number of versions for tool is 1

    # Maybe a unique id should be used here, but I think it very unlikely that this toolname will be encountered.
    assert fastr.tools.toolversions('097G)(A&*BD)(A7vA)(F67vAD)F967vAF-67vAD)F(86vAFD096vAF)97v') == []
    assert isinstance(fastr.tools.toolversions(tool), list)

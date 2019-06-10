"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import unittest

from cortex import Cortex
from .fixtures import john_doe_token, mock_api_endpoint


class TestSkill(unittest.TestCase):

    def setUp(self):
        self.cortex = Cortex.client(api_endpoint=mock_api_endpoint(), api_version=3, token=john_doe_token())

    def test_skill_to_camel(self):
        builder = self.cortex.builder()
        skill_test = builder.skill('unittest/skill1').title('Skill Unit Test').description('Skill that Uses a Dataset Reference')
        skill_test = skill_test.input('input1').title('input').parameter(name='text', type='string').all_routing("action", 'output1').build()
        skill_test = skill_test.output('output1').title('output').parameter(name='text', type='object').build()
        skill_test = skill_test.dataset('dataset_ref').parameter(ref='cortex/dataset').build()
        skill_test_camel = skill_test.to_camel()
        skill_camel = {
            'camel': '1.0.0',
            'name': 'unittest/skill1',
            'title': 'Skill Unit Test',
            'inputs': [{'name': 'input1',
                        'title': 'input',
                        'parameters': [{'name': 'text', 'type': 'string', 'required': True}],
                        'routing': {'all': {'action': 'action', 'output': 'output1'}}}],
            'outputs': [{'name': 'output1',
                         'title': 'output',
                         'parameters': [{'name': 'text', 'type': 'object', 'required': True}]}],
            'datasets': [{'name': 'dataset_ref', 'parameters': [{'$ref': 'cortex/dataset'}]}],
            'description': 'Skill that Uses a Dataset Reference'
        }
        self.assertEqual(skill_test_camel, skill_camel)

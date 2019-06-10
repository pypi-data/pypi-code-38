# Copyright 2016 Commerce Technologies, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from kerb_sts.awsrole import AWSRole


class TestAWSRoleCreation(unittest.TestCase):
    def test_with_role_as_none(self):
        is_valid = AWSRole.is_valid(None)
        self.assertFalse(is_valid)

    def test_with_empty_string(self):
        is_valid = AWSRole.is_valid('')
        self.assertFalse(is_valid)

    def test_with_malformed_role_string(self):
        is_valid = AWSRole.is_valid('arn_noseparator_provider')
        self.assertFalse(is_valid)

    def test_with_missing_arn_string(self):
        is_valid = AWSRole.is_valid(',provider')
        self.assertFalse(is_valid)

    def test_with_missing_provider_string(self):
        is_valid = AWSRole.is_valid('arn/role,')
        self.assertFalse(is_valid)

    def test_with_valid_strings(self):
        is_valid = AWSRole.is_valid('arn/role,provider')
        self.assertTrue(is_valid)

    def test_parsed_role(self):
        role = AWSRole('arn/role,provider')
        self.assertEqual(role.arn, 'arn/role')
        self.assertEqual(role.provider, 'provider')

    def test_with_valid_strings(self):
        role = AWSRole('arn/role,provider')
        self.assertEqual(role.name, 'role')


if __name__ == '__main__':
    unittest.main()

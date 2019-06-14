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

class AWSRole:
    """
    The AWSRole is parsed from the Active Directory login page. It contains
    the ARN of the IAM Role and the name of the SAML Provider. This class allows
    the code to manage that parsing and access.
    """

    ARN_PART_INDEX = 0
    PROVIDER_PART_INDEX = 1
    ROLE_PART_INDEX = 1

    def __init__(self, aws_role):
        """
        Create a new Role object and parse the specified role into is parts.
        :param aws_role: the text from the IdP login page
        """
        if AWSRole.is_valid(aws_role):
            self._parse(aws_role)
        else:
            msg = "The 'aws_role' is not valid: {0}".format(aws_role)
            raise ValueError(msg)

    @staticmethod
    def is_valid(aws_role):
        """
        Determine if the role string will be valid when parsed.
        :param aws_role: the Role ARN from AWS
        :return: **True** if the role string can be parsed, otherwise **False**
        """
        if not aws_role:
            return False

        parts = aws_role.split(',')

        if len(parts) != 2:
            return False

        arn = parts[AWSRole.ARN_PART_INDEX]
        provider = parts[AWSRole.PROVIDER_PART_INDEX]

        if len(arn) <= 0:
            return False

        if len(provider) <= 0:
            return False

        # all ARNs are in the form of 'arn:aws:iam::account-id:role/role-name'
        slash_index = arn.find('/')
        if slash_index == -1:
            return False

        return True

    # Parse the role string.
    def _parse(self, aws_role):
        parts = aws_role.split(',')

        arn = parts[AWSRole.ARN_PART_INDEX]
        provider = parts[AWSRole.PROVIDER_PART_INDEX]

        role_parts = arn.split('/')
        name = role_parts[AWSRole.ROLE_PART_INDEX]

        self.arn = arn
        self.name = name
        self.provider = provider

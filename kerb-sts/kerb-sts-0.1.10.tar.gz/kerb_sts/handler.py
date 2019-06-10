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

import base64
import boto.sts
import configparser
import logging
import os
import requests
import xml.etree.ElementTree as ET
import sys
import traceback

from bs4 import BeautifulSoup
from kerb_sts.awsrole import AWSRole

class DefaultRoleCredsGenerationError(Exception):
    pass

class KerberosHandler:
    """
    The KerberosHandler sends a request to an IdP endpoint. The handler can either use Kerberos auth
    or can also be configured with a username and password and use NTLM auth. This handler takes
    the SAML response from the IdP and parses out the available AWS IAM roles that the
    user can assume. The handler then reaches out to AWS and generates temporary tokens for each of
    the roles that the user can assume.
    """

    def __init__(self):
        """
        Creates a new KerberosHandler object
        """
        self.output_format = 'json'
        self.ssl_verification = True

    def handle_sts_by_kerberos(self, region, url, credentials_filename, config_filename,
                               only_role, default_role, list_only, authenticator):
        """
        Entry point for generating a set of temporary tokens from AWS.
        :param region: The AWS region tokens are being requested for
        :param url: The URL of the IdP endpoint to auth against
        :param credentials_filename: Where should the tokens be written to
        :param config_filename: Where should the region/format be written to
        :param default_role: Which IAM role should be set as the default in the config file
        :param list_only: If set, the IAM roles available will just be printed instead of assumed
        :param authenticator: the Authenticator
        """

        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}

        response = session.get(
            url,
            verify=self.ssl_verification,
            headers=headers,
            auth=authenticator.get_auth_handler(session)
        )
        logging.debug("received {} IdP response".format(response.status_code))

        if response.status_code != requests.codes.ok:
            raise Exception(
                "did not get a valid reply. response was: {} {}".format(response.status_code, response.text)
            )

        # We got a successful response from the IdP. Parse the assertion and pass it to AWS
        self._handle_sts_from_response(response, region, credentials_filename, config_filename, only_role, default_role, list_only)

    def _handle_sts_from_response(self, response, region, credentials_filename, config_filename, only_role, default_role, list_only):
        """
        Takes a successful SAML response, parses it for valid AWS IAM roles, and then reaches out to
        AWS and requests temporary tokens for each of the IAM roles.
        :param response: The SAML response from a previous request to IdP endpoint
        :param region: The AWS region tokens are being requested for
        :param credentials_filename: Where should the region/format be written to
        :param config_filename: Where should the tokens be written to
        :param default_role: Which IAM role should be as as the default in the config file
        :param list_only: If set, the IAM roles available will just be printed instead of assumed
        """

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the SAMLResponse attribute of the input tag (determined by
        # analyzing the debug print lines above)
        assertion = None
        for inputtag in soup.find_all('input'):
            if inputtag.get('name') == 'SAMLResponse':
                assertion = inputtag.get('value')

        if not assertion:
            raise Exception("did not get a valid SAML response. response was:\n%s" % response.text)

        # Parse the returned assertion and extract the authorized roles
        aws_roles = []
        root = ET.fromstring(base64.b64decode(assertion))
        for saml2attribute in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
            if saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role':
                for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                    aws_roles.append(saml2attributevalue.text)

        if not aws_roles:
            raise Exception("user does not have any valid aws roles.")

        # Note the format of the attribute value should be role_arn,principal_arn
        # but lots of blogs list it as principal_arn,role_arn so let's reverse
        # them if needed
        for aws_role in aws_roles:
            chunks = aws_role.split(',')
            if 'saml-provider' in chunks[0]:
                new_aws_role = chunks[1] + ',' + chunks[0]
                index = aws_roles.index(aws_role)
                aws_roles.insert(index, new_aws_role)
                aws_roles.remove(aws_role)

        # If the user supplied to a default role make sure
        # that role is available to them.
        if default_role is not None:
            found_default_role = False
            for aws_role in aws_roles:
                name = AWSRole(aws_role).name
                if name == default_role:
                    found_default_role = True
                    break
            if not found_default_role:
                raise Exception("provided default role not found in list of available roles")

        # Go through each of the available roles and
        # attempt to get temporary tokens for each
        try:
            for aws_role in aws_roles:
                profile = AWSRole(aws_role).name

                if list_only:
                    logging.info("role: {}".format(profile))
                elif only_role is not None:
                    if only_role == profile:
                        self._generate_credentials_for_role(region, credentials_filename, config_filename, default_role, assertion, aws_role, profile)
                    else:
                        logging.debug("skipping role {}; --only_role specified".format(profile))
                else:
                    self._generate_credentials_for_role(region, credentials_filename, config_filename, default_role, assertion, aws_role, profile)
        except DefaultRoleCredsGenerationError:
            sys.exit(1)

    def _generate_credentials_for_role(self, region, credentials_filename, config_filename, default_role, assertion, aws_role, profile):
        try:
            token = self._bind_assertion_to_role(assertion, aws_role, profile,
                                                 region, credentials_filename, config_filename, default_role)

            if not token:
                raise Exception('did not receive a valid token from aws')

            expires_utc = token.credentials.expiration

            if default_role == profile:
                logging.info("default role: {} until {}".format(profile, expires_utc))
            else:
                logging.info("role: {} until {}".format(profile, expires_utc))
        except Exception as ex:
            if default_role == profile:
                logging.error(
                    'failed to save temporary credentials for default role {}: {}'.format(profile, ex)
                )
                raise DefaultRoleCredsGenerationError('failed to save temporary credentials for default role {}: {}'.format(profile, ex))
            else:
                logging.warning('failed to save temporary credentials for role {}'.format(profile))
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])

    def _bind_assertion_to_role(self, assertion, role, profile, region,
                                credentials_filename, config_filename, default_role):
        """
        Attempts to assume an IAM role using a given SAML assertion.
        :param assertion: A SAML assertion authenticating the user
        :param role: The IAM role being assumed
        :param profile: The name of the role
        :param region: The region the role is being assumed in
        :param credentials_filename: Output file for the regions/formats for each profile
        :param config_filename: Output file for the generated tokens
        :param default_role: Which role should be set as default in the config
        :return token: A valid token with temporary IAM credentials
        """

        # Attempt to assume the IAM role
        conn = boto.sts.connect_to_region(region, aws_secret_access_key='', aws_access_key_id='')
        role_arn = role.split(',')[0]
        principal_arn = role.split(',')[1]
        token = conn.assume_role_with_saml(role_arn, principal_arn, assertion)
        if not token:
            raise Exception("failed to receive a valid token when assuming a role.")

        # Write the AWS STS token into the AWS credential file
        # Read in the existing config file
        default_section = 'default'

        credentials_config = configparser.RawConfigParser(default_section=default_section)
        credentials_config.read(credentials_filename)

        config = configparser.RawConfigParser(default_section=default_section)
        config.read(config_filename)

        # If the default_role was passed in on the command line we will overwrite
        # the [default] section of the credentials file
        sections = []
        if default_role == profile:
            sections.append(default_section)

        # Make sure the section exists
        if not credentials_config.has_section(profile):
            credentials_config.add_section(profile)
        if not config.has_section(profile):
            config.add_section(profile)

        sections.append(profile)

        for section in sections:
            self._set_config_section(credentials_config,
                                     section,
                                     output=self.output_format,
                                     region=region,
                                     aws_role_arn=role_arn,
                                     aws_access_key_id=token.credentials.access_key,
                                     aws_secret_access_key=token.credentials.secret_key,
                                     aws_session_token=token.credentials.session_token,
                                     aws_security_token=token.credentials.session_token,
                                     aws_session_expires_utc=token.credentials.expiration)
            self._set_config_section(config, section, output=self.output_format, region=region)

        # Write the updated config file
        if not os.path.exists(os.path.dirname(credentials_filename)):
            try:
                os.makedirs(os.path.dirname(credentials_filename))
            except OSError as ex:
                raise Exception("could not create credential file directory")

        if not os.path.exists(os.path.dirname(config_filename)):
            try:
                os.makedirs(os.path.dirname(config_filename))
            except OSError as ex:
                raise Exception("could not create config file directory")

        with open(credentials_filename, 'w+') as fp:
            credentials_config.write(fp)

        with open(config_filename, 'w+') as fp:
            config.write(fp)

        return token

    @staticmethod
    def _set_config_section(config, section, **kwargs):
        """
        Set the configuration section in the file with the properties given. The section
        must exist before calling this method.

        :param config: the configuration object
        :param section: the name of the section
        :param kwargs: the key value pairs to put into the section
        :return: Nothing
        """
        for name, value in kwargs.items():
            config.set(section, name, value)

# Copyright (c) 2018-2019. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import requests
import shlex
import subprocess
import json
import time
import os
import stat
import re
import time
import urllib.request
import shutil
import tarfile
import zipfile
import glob
import socket
import datetime
import dateutil.parser
from Crypto.PublicKey import RSA # pycrypto
import uniquid.core.constants as cons
import uniquid.core.constants_aws as awscons
import uniquid.core.remote as remote

# constants
_TAB = cons.TXT_TAB
_OUTPUT_DIR = 'uniquid_aws'
_KEYPAIR_FILE_PREFIX = 'aws_ec2_keypair_'
_KEYPAIR_FILE_SUFFIX = '.pem'
_KEYPAIR_FILE_PERMS = stat.S_IRUSR
_KEYPAIR_NAME = 'uniquid-agent-key-'
# filename of downloaded AWS agent tarball
_AWS_AGENT_FILE = 'aws-agent-latest.tar.gz'
# filename of downloaded AWS MQTT Proxy tarball
_AWS_PROXY_FILE = 'aws-proxy-latest.tar.gz'
# MQTT Broker Root CA certificate filename
_AWS_BROKER_CA_FILE = 'mqtt-broker-root-ca.crt'
# Verisign Root CA certificate file
_AWS_VERISIGN_FILE = 'iotRootCA.pem'
# ec2 instance name prefix
_AWS_EC2_NAME_PREFIX = 'uniquid-agent-'
# agent name prefix
_AWS_AGENT_PREFIX = 'AWS-IOT-UNIQUID-AUTHORIZER-'
# lambda function name prefix
_AWS_LAMBDA_FUNC_PREFIX = 'UniquidLambda-'
# lambda role prefix
_AWS_IAM_ROLE_PREFIX = 'UniquidLambdaRole-'
# iot authorizer name prefix
_AWS_AUTH_PREFIX = 'UniquIDCustomAuth-'
# agent tarfile sub-directory
_AGENT_TAR_SUBDIR = 'aws-agent'
# name of AWS security group for new EC2 instance running Agent
_SEC_GROUP_NAME = 'uniquid-agent-sg'
# proxy keys and certs
_AWS_PROXY_KEY_PREFIX = 'mqtt-proxy-'
# proxy root cert
_AWS_PROXY_ROOT_PREFIX = 'mqtt-proxy-root-ca-'
# name of aws device configuration file
_AWS_DEV_CFG_FILE = 'aws_device_cfg.json'
# name of basic/common device configuration file
_BASIC_DEV_CFG_FILE = 'device_cfg.json'
# number of aws retries (logins etc.)
_NUM_RETRIES = 10
# delay between retries in seconds
_RETRY_DELAY = 30
# grab the current time
_timenow = datetime.datetime.now()
# timestamp used to individualise the names of components in AWS
_TIMESTAMP = _timenow.strftime('%Y%m%d%H%M%S')


# device config. for common devices exported as a JSON file
_basic_device_config = {
    'orgId': '',
    'mqttUrl': '',
    'mqttsUrl': '',
    'mqttTopic' : '',
    'registryUrl': '',
    'checkpointUrl': '',
    'network' : 'ltc-regtest'
}

# AWS IoT device configuration exported as a JSON file
_aws_device_config = {
    'orgId': '',
    'mqttUrl': '',
    'mqttsUrl': '',
    'mqttTopic' : '',
    'registryUrl': '',
    'checkpointUrl': '',
    'awsAuthorizerName': '',
    'awsPrivateKey': [],
    'awsTokenKey': 'UniquIDToken',
    'awsAgentName': '',
    'awsEndpointAddress': '',
    'network' : 'ltc-regtest'
}

# network map - maps network type from orchestrator value to enum
_LTC_REGTEST = 'ltc-regtest'
_LTC_TESTNET = 'ltc-testnet'
_LTC_MAINNET = 'ltc-mainnet'
_blockchain_map = {
    _LTC_REGTEST: 'litecoinregtest'.casefold(),
    _LTC_TESTNET: 'litecointest'.casefold(),
    _LTC_MAINNET: 'litecoin.main'.casefold()
}

class Deploy:
    """Implements all commands related to AWS deployment of the Uniquid Agent.
    """

    def __init__(self, in_console, in_login_mgr):
        """Initialise an instance of the class.

            in_console -- CliConsole object.
            in_login_mgr -- LoginManager object.
        """
        assert in_console is not None
        assert in_login_mgr is not None
        self._console = in_console
        self._login_mgr = in_login_mgr
        self._aws_account_id = None
        self._sec_group_id = None
        self._subnet_id = None
        self._keypair_name = None
        self._keypair_path = None
        self._ec2_public_ip = None
        self._aws_function_arn = None
        self._orch_props = None
        self._rsa_private_key = None
        self._authorizer_name = None
        self._role_name = None
        self._lambda_name = None
        self._agent_node_name = None
        self._yes_mode = False
        self._cert_chain_file = None

    def deploy(self, in_platform, in_yesmode=False):
        """Deploy Uniquid node and custom authorizer lambda function to
            customer's platform.

            Args:
            in_platform -- Customer platform identifier.
            in_yesmode -- True indicates the command is run in 'yes mode', which
            means that the answer to all questions to the user is yes.
        """
        self._yes_mode = in_yesmode
        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(cons.ERR_LOGGED_OUT)
        # verify that the user supplied a supported platform
        if in_platform not in cons.PLATFORMS:
            self._console.exception(cons.ERR_BAD_PLATFORM + str(in_platform))
        # check platform is supported
        if in_platform == cons.PLATFORM_BASIC:
            self._basic_deploy()
        elif in_platform == cons.PLATFORM_AWS:
            self._aws_deploy()
        else:
            self._console.exception(cons.ERR_BAD_PLATFORM + str(in_platform))

    def undeploy(self, in_platform, in_timestamps, in_yesmode=False):
        """Undeploy mutiple Uniquid nodes and custom authorizer lambda functions
            to the customer's platform.

            Args:
            in_platform -- Customer platform identifier.
            in_timestamps -- Timestamps of components to delete.
            in_yesmode -- True indicates the command is run in 'yes mode', which
            means that the answer to all questions to the user is yes.
        """
        self._yes_mode = in_yesmode
        # undeploy only interacts with aws - the user does not need to be
        # logged into the UniquID backend.
        # verify that the user supplied a supported platform
        if in_platform not in cons.PLATFORMS:
            self._console.exception(cons.ERR_BAD_PLATFORM + str(in_platform))
        # check platform is supported
        if in_platform == cons.PLATFORM_BASIC:
            self._console.error(cons.ERR_UNDEPLOY_NOT_REQUIRED)
        elif in_platform == cons.PLATFORM_AWS:
            self._aws_undeploy(in_timestamps)
        else:
            self._console.exception(cons.ERR_BAD_PLATFORM + str(in_platform))

    def _basic_deploy(self):
        """Generate a device configuration file for when no IoT platform
            is being integrated.
        """
        self._console.ok('Starting the generation of a device configuration file.\n')
        self._yes_mode = True
        step = 1
        step = self._basic_deploy_init(step)
        step = self._basic_deploy_dev_cfg(step)
        self._basic_print_summary(step)
        self._console.ok('')
        self._console.ok(_TAB + 'File generation is now complete.')

    def _aws_deploy(self):
        """Deploy the Agent, Lambda function and MQTT Proxy to AWS EC2.
        """
        # query user to proceed
        self._console.ok('Starting deployment of Uniquid AWS Agent and MQTT Proxy to your Amazon AWS cloud.\n')
        if not self._yes_mode:
            if self._console.confirm("Do you want to proceed in automatic mode (answer yes to all dialogs)?",
                                     in_default=False):
                self._yes_mode = True
        self._console.ok(_TAB + 'The following tools must be installed and configured: awscli, Node.js (>= v8.0), npm, ssh, scp.')
        if (not self._yes_mode and
            not self._console.confirm("Do you want to start the deployment?",
                                     in_default=False)):
            self._console.ok(awscons.TXT_AWS_EXIT_EARLY)
            return
        step = 1
        step = self._aws_deploy_init(step)
        step = self._aws_deploy_secgroup(step)
        step = self._aws_deploy_choose_subnet(step)
        step = self._aws_deploy_keypair(step)
        step = self._aws_deploy_instance(step)
        step = self._aws_deploy_agent(step)
        step = self._aws_deploy_lambda(step)
        step = self._aws_deploy_authorizer(step)
        step = self._aws_deploy_dev_cfg(step)
        step = self._aws_deploy_mqtt_proxy(step)
        self._aws_print_summary(step)
        self._console.ok('')
        self._console.ok(_TAB + 'Deployment is now complete.')

    def _aws_undeploy(self, in_timestamps):
        """Undeploy multiple Agents and Lambdas function from AWS EC2.
            Args:
            in_timestamps -- List of timestamps of components to be removed.
        """
        # query user to proceed
        self._console.ok('Starting removal of Uniquid components from your Amazon AWS cloud.\n')
        if (not self._yes_mode and
            self._console.confirm("Do you want to proceed in automatic mode (answer yes to all dialogs)?",
                                     in_default=False)):
            self._yes_mode = True
        self._console.ok(_TAB + 'The following tool(s) must be installed and configured: awscli.')
        if (not self._yes_mode and
            not self._console.confirm("Do you want to start the removal?",
                                     in_default=False)):
            self._console.ok(awscons.TXT_AWS_EXIT_EARLY)
            return
        step = 1
        step = self._aws_undeploy_init(step)
        self._aws_undeploy_all(step, in_timestamps)

    def _basic_deploy_init(self, in_step):
        """Check dependencies and initialise.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # read properties from orchestrator
        self._orch_props = self._get_orch_properties()
        if self._orch_props is None:
            self._console.exception(cons.ERR_ORCH_REQ_FAIL)
        return step

    def _aws_deploy_init(self, in_step):
        """Check dependencies and initialise.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # data retrieved
        aws_access_key = None
        aws_secret_key = None
        self._aws_region = None
        # check awscli is installed
        step = self._print_step(step, 'Check awscli is installed.')
        version_cmd = 'aws --version'
        arg_list = shlex.split(version_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            self._console.error('awscli must be installed.')
            self._console.exception(cons.ERR_MISSING_DEPENDENCY)
        self._console.ok(_TAB + cons.TXT_PASS)
        # check aws client configured - access_key
        step = self._print_step(step, 'Check AWS CLI tool is configured.')
        aws_access_key = self._aws_configure_get('aws_access_key_id')
        aws_secret_key = self._aws_configure_get('aws_secret_access_key')
        self._aws_region = self._aws_configure_get('region')
        self._console.ok(_TAB + cons.TXT_PASS)
        # check aws credentials are valid
        step = self._print_step(step, 'Check AWS credentials.')
        cmd = 'aws iam get-user'
        arg_list = shlex.split(cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            self._console.exception(awscons.ERR_AWS_CLI_PERMISSIONS)
        self._console.ok(_TAB + cons.TXT_PASS)
        # check node.js is installed
        step = self._print_step(step, 'Check node.js is installed.')
        version_cmd = 'node --version'
        arg_list = shlex.split(version_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            self._console.error('node.js must be installed.')
            self._console.exception(cons.ERR_MISSING_DEPENDENCY)
        self._console.ok(_TAB + 'node.js version: ' + result.stdout.decode('utf-8'))
        self._console.ok(_TAB + 'node.js version must be >= 8.0')
        # TODO check version of npm meets criteria
        self._console.ok(_TAB + cons.TXT_PASS)
        # check npm is installed
        step = self._print_step(step, 'Check npm is installed.')
        version_cmd = 'npm --version'
        arg_list = shlex.split(version_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            self._console.error('npm must be installed.')
            self._console.exception(cons.ERR_MISSING_DEPENDENCY)
        self._console.ok(_TAB + 'npm version: ' + result.stdout.decode('utf-8'))
        self._console.ok(_TAB + 'npm version must be >= 6.4')
        # TODO check version of npm meets criteria
        self._console.ok(_TAB + cons.TXT_PASS)
        # check openssl is installed
        step = self._print_step(step, 'Check openssl is installed.')
        # error code 127 would be returned if openssl not on path
        openssl_cmd = 'openssl no-blahblahblah'
        arg_list = shlex.split(openssl_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            self._console.error('openssl must be installed.')
            self._console.exception(cons.ERR_MISSING_DEPENDENCY)
        self._console.ok(_TAB + 'openssl is correctly installed')
        self._console.ok(_TAB + cons.TXT_PASS)
        # read properties from orchestrator
        self._orch_props = self._get_orch_properties()
        if self._orch_props is None:
            self._console.exception(cons.ERR_ORCH_REQ_FAIL)
        return step

    def _aws_undeploy_init(self, in_step):
        """Check dependencies and initialise before undeployment.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # data retrieved
        aws_access_key = None
        aws_secret_key = None
        self._aws_region = None
        # check awscli is installed
        step = self._print_step(step, 'Check awscli is installed.')
        version_cmd = 'aws --version'
        arg_list = shlex.split(version_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            self._console.error('awscli must be installed.')
            self._console.exception(cons.ERR_MISSING_DEPENDENCY)
        self._console.ok(_TAB + cons.TXT_PASS)
        # check aws client configured - access_key
        step = self._print_step(step, 'Check AWS CLI tool is configured.')
        aws_access_key = self._aws_configure_get('aws_access_key_id')
        aws_secret_key = self._aws_configure_get('aws_secret_access_key')
        self._aws_region = self._aws_configure_get('region')
        self._console.ok(_TAB + cons.TXT_PASS)
        # check aws credentials are valid
        step = self._print_step(step, 'Check AWS credentials.')
        cmd = 'aws iam get-user'
        arg_list = shlex.split(cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            self._console.exception(awscons.ERR_AWS_CLI_PERMISSIONS)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_secgroup(self, in_step):
        """Create/configure the AWS Security Group.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # get the aws account id
        step = self._print_step(step, 'Retrieve AWS Account Id.')
        self._aws_account_id = self._aws_get_caller_identity('Account')
        self._console.ok(_TAB + cons.TXT_PASS)
        # create or select a security group
        step = self._print_step(step, 'Configure an AWS Security Group.')
        sec_group_name = None
        sec_groups = self._aws_list_security_groups()
        self._console.ok(_TAB + 'Existing Security Groups:')
        agent_sec_group_found = False
        if len(sec_groups) > 0:
            for group in sec_groups:
                suffix = ''
                # highlight exist group which may be an agent sg.
                if _SEC_GROUP_NAME in group['Name']:
                    suffix = '  <<<<'
                    agent_sec_group_found = True
                self._console.ok(_TAB + '* ' + group['Name'] + suffix)
        else:
            self._console.ok(_TAB + 'None')
        # give the user the option to create a new security group
        is_new_group = False
        self._console.ok(_TAB + awscons.TXT_AWS_SEC_GROUP_MATCH_FOUND)
        if (self._yes_mode or
            self._console.confirm("Do you want to create another AWS Security Group?",
                                 in_default=False)):
            if self._yes_mode:
                sec_group_name = _SEC_GROUP_NAME + '-' + _TIMESTAMP
            while sec_group_name is None:
                sec_group_name = self._console.prompt('Enter the name of the new AWS security group name',
                                                 in_type=str,
                                                 in_default=(_SEC_GROUP_NAME + '-' + _TIMESTAMP),
                                                 in_show_default=True)
                for group in sec_groups:
                    if sec_group_name in group['Name']:
                        self._console.error('Security Group name already exists. Please try again.')
                        sec_group_name = None
            # security group created for default aws vpc
            version_cmd = ('aws ec2 create-security-group --group-name ' +
                           sec_group_name +
                           ' --description ' +
                           '\"Uniquid Agent Security Group (' + _TIMESTAMP + ')\"')
            result = self._run_command(version_cmd)
            sec_group_dict = json.loads(result.stdout.decode('utf-8').strip())
            if 'GroupId' in sec_group_dict:
                self._sec_group_id = sec_group_dict.get('GroupId')
                self._console.ok(_TAB + awscons.TXT_AWS_SEC_GROUP_CREATED +
                                 self._sec_group_id)
                is_new_group = True
            else:
                self._console.exception(awscons.ERR_AWS_REPLY_MISSING_DATA + 'GroupId')
            # tag the new security group
            tag_cmd = ('aws ec2 create-tags --resources ' + self._sec_group_id +
                       ' --tags Key=Name,Value=\"' + sec_group_name + '\"' +
                       ' Key=' + awscons.AWS_RES_TAG_NAME +',Value=\"' + self._get_org_tag() + '\"')
            result = self._run_command(tag_cmd)
        # user choose to use an existing security group
        else:
            sec_group_name = self._console.prompt('Enter the name of the existing AWS security group to use',
                                             in_default=_SEC_GROUP_NAME,
                                             in_type=str,
                                             in_show_default=True)
            # verify user entered name of an existing security group
            isMatch = False
            for group in sec_groups:
                if sec_group_name == group['Name']:
                    self._sec_group_id = group['Id']
                    isMatch = True
            if not isMatch:
                self._console.exception(awscons.ERR_AWS_SEC_GROUP_NOT_EXISTS)
        # open ports for security group if required
        self._console.ok(_TAB + 'Checking TCP ports are open for the security group. Port numbers: ' + ', '.join(awscons.AWS_SEC_GROUP_PORTS))
        query_cmd = 'aws ec2 describe-security-groups --filters Name=group-name,Values=\"' + sec_group_name + '\"'
        result = self._run_command(query_cmd)
        sec_group_dict = json.loads(result.stdout.decode('utf-8').strip())
        # list of ports which have valid existing rules
        existing_rule_ports = []
        # check existing rules for the security group
        if ('SecurityGroups' in sec_group_dict and
                len(sec_group_dict.get('SecurityGroups',[])) == 1):
            permissions = sec_group_dict.get('SecurityGroups',[])[0].get('IpPermissions',[])
            for rule in permissions:
                port_num = rule.get('FromPort',0)
                if (str(port_num) in awscons.AWS_SEC_GROUP_PORTS and
                        rule.get('IpProtocol') == 'tcp' and
                        {'CidrIp': '0.0.0.0/0'} in rule.get('IpRanges',[])):
                    existing_rule_ports.append(str(port_num))
        elif ('SecurityGroups' in sec_group_dict and
                len(sec_group_dict.get('SecurityGroups')) > 1):
            self._console.exception(awscons.ERR_AWS_SEC_GROUP_TOO_MANY)
        else:
            self._console.exception(awscons.ERR_AWS_SEC_GROUP_NOT_EXISTS)
        # fix ports which are not opened
        for portnum in awscons.AWS_SEC_GROUP_PORTS:
            if portnum not in existing_rule_ports:
                self._console.ok(_TAB + awscons.TXT_AWS_PORT_NOT_OPEN)
                if (is_new_group or
                        self._yes_mode or
                        self._console.confirm('Do you want to open inbound TCP port ' + portnum + ' of '
                                              'the Security Group ' + sec_group_name + '?',
                                              in_default=False)):
                    portnum_cmd = ('aws ec2 authorize-security-group-ingress ' +
                                   '--group-name ' + sec_group_name +
                                   ' --protocol tcp --port ' + portnum +
                                   ' --cidr 0.0.0.0/0')
                    result = self._run_command(portnum_cmd)
                    self._console.ok(_TAB + awscons.TXT_AWS_PORT_OPENED + portnum)
                else:
                    self._console.error(_TAB + awscons.TXT_AWS_PORT_REFUSED_OPEN_PORT)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_choose_subnet(self, in_step):
        """Select an AWS EC2 VPC and subnet.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        default_vpc_id = None
        default_subnet_id = None
        existing_subnets = []
        # query the aws account type
        step = self._print_step(step, 'Check AWS account type.')
        if not self._aws_is_ec2_vpc_account():
            self._console.exception(_TAB + awscons.ERR_AWS_NOT_VPC_ACCOUNT)
        self._console.ok(_TAB + awscons.TXT_AWS_EC2_VPC_ACCOUNT_AVAILABLE)
        self._console.ok(_TAB + cons.TXT_PASS)
        # select a VPC and subnet
        step = self._print_step(step, 'Select the VPC Subnet to use.')
        default_vpc_id = self._aws_get_ec2_default_vpc_id()
        if (self._yes_mode and
            default_vpc_id == None):
            self._console.exception(_TAB + awscons.ERR_AWS_NO_DEFAULT_VPC)
        elif (self._yes_mode and
                default_vpc_id != None):
            self._console.ok(_TAB + awscons.TXT_AWS_USING_DEFAULT_VPC)
        else:
            # choose from existing subnets
            self._console.ok(_TAB + 'A Subnet Id is required for EC2 instance creation.')
            self._console.ok(_TAB + 'Existing VPCs and Subnets:')
            subnets = self._aws_list_subnets()
            if len(subnets) > 0:
                for subnet in subnets:
                    suffix = ''
                    # highlight the default vpc/subnet
                    if subnet[0] == default_vpc_id:
                        suffix = '  <<<< (default vpc)'
                        default_subnet_id = subnet[1]
                    self._console.ok(_TAB + '* [vpc id: ' + subnet[0] + '] ' + subnet[1] + suffix)
                    existing_subnets.append(subnet[1])
            else:
                self._console.ok(_TAB + 'None')
            # user must choose the subnet to use
            subnet_id = self._console.prompt('Enter the Subnet ID to use: ',
                                             in_default=default_subnet_id,
                                             in_type=str,
                                             in_show_default=True)
            # verify user entered the id of an existing subnet
            if subnet_id in existing_subnets:
                self._console.ok(_TAB + 'User selected Subnet ID: ' + subnet_id)
                # save the ID of the Subnet for future use when creating EC2 instances.
                self._subnet_id = subnet_id
            else:
                self._console.exception(awscons.ERR_AWS_SUBNET_NOT_EXISTS)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_keypair(self, in_step):
        """Create/configure the AWS EC2 Key Pair.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # keypair selection/creation
        step = self._print_step(step, 'AWS Key Pair selection/creation.')
        self._console.ok(_TAB + 'A Key Pair is required to secure access to the EC2 instance.')
        key_pairs = self._aws_list_key_pairs()
        self._console.ok(_TAB + 'Existing Key Pairs:')
        if len(key_pairs) > 0:
            for keypair in key_pairs:
                self._console.ok(_TAB + '* ' + keypair)
        else:
            self._console.ok(_TAB + 'None')
        if (self._yes_mode or
            self._console.confirm('Do you want to create a key-pair '
                                 'for the instance?')):
            self._keypair_name = _KEYPAIR_NAME + _TIMESTAMP
            keypair_cmd = ('aws ec2 create-key-pair --key-name ' +
                           self._keypair_name +
                           ' --query \"KeyMaterial\" --output text')
            result = self._run_command(keypair_cmd)
            self._keypair_path = self._write_keypair_file(
                                    result.stdout.decode('utf-8').strip())
        else:
            self._keypair_path = self._console.prompt('Enter the path of an existing'
                                                ' key-pair file to use for the'
                                                ' new EC2 instance',
                                                in_default='',
                                                in_type=str,
                                                in_show_default=False)
            if (not os.path.exists(self._keypair_path) or
                    not os.path.isfile(self._keypair_path) or
                    not os.access(self._keypair_path, os.R_OK)):
                self._console.exception(awscons.ERR_AWS_KEYPAIR_FILE_READ)
            self._keypair_name = self._console.prompt('Enter the name of this key '
                                                'pair',
                                                in_default='uniquid-agent-key',
                                                in_type=str,
                                                in_show_default=True)
        if (self._keypair_name is None or
                len(self._keypair_name) == 0):
            self._console.exception(awscons.ERR_AWS_INVALID_KEYPAIR_NAME)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_instance(self, in_step):
        """Create/configure the AWS EC2 instance.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # aws ec2 instance creation
        ec2_id = None
        step = self._print_step(step, 'AWS EC2 instance creation.')
        if (self._yes_mode or
            self._console.confirm('Do you want to create a new AWS EC2 Instance'
                                 ' for the Uniquid Agent?',
                                 in_default=False)):
            # find a suitable ec2 image to use
            ami_id = None
            ami_datetime = None
            self._console.ok(_TAB + 'Retrieving list of EC2 image types from Amazon ' +
                             'AWS. Please wait....')
            # TODO hardcoded Canonical owner id
            aws_cmd = ('aws ec2 describe-images --filters '
                       '\"Name=architecture,Values=x86_64\" '
                       '\"Name=state,Values=available\" '
                       '\"Name=root-device-type,Values=ebs\" '
                       '\"Name=virtualization-type,Values=hvm\" '
                       '\"Name=owner-id,Values=' + awscons.AWS_ID_CANONICAL + '\"')
            result = self._run_command(aws_cmd)
            result_str = result.stdout.decode('utf-8').strip()
            result_json = json.loads(result_str)
            for image in result_json.get('Images'):
                image_datetime = dateutil.parser.parse(image.get('CreationDate'))
                if (image.get('Name').startswith('ubuntu/images') and
                       'Description' in image and
                       'Canonical' in image.get('Description','') and
                       'Ubuntu' in image.get('Description','') and
                       '18.04 LTS' in image.get('Description','') and
                       'UNSUPPORTED' not in image.get('Description','UNSUPPORTED') and
                       'Desktop' not in image.get('Description','Desktop') and
                       'based on' not in image.get('Description','based on') and
                       'minimal' not in image.get('Description','minimal') and
                       'Deep Learning' not in image.get('Description','Deep Learning')):
                    # newer images can overwrite older ami images
                    if(ami_datetime == None or
                            (ami_datetime < image_datetime)):
                        ami_id = image.get('ImageId', '')
                        ami_datetime = image_datetime
            if ami_id is None:
                self._console.exception(cons.ERR_NO_AWS_IMAGE)
            self._console.ok(_TAB + 'AWS EC2 image choosen: ' + ami_id)
            # create the instance using choosen image type
            subnet_option = ''
            # only pass the subnet option if creating the instance with a subnet
            # which is not associated with the default VPC.
            if self._subnet_id != None:
                subnet_option = ' --subnet-id ' + self._subnet_id + ' '
            aws_cmd = ('aws ec2 run-instances --image-id ' + ami_id +
                       ' --security-group-ids ' + self._sec_group_id +
                       ' --count 1 --instance-type t2.micro --key-name ' +
                       self._keypair_name + ' --tag-specifications \"ResourceType=' +
                       'instance,Tags=[{Key=Name,Value=' + _AWS_EC2_NAME_PREFIX + _TIMESTAMP+ '},' +
                       '{Key=Description,Value=Uniquid_CLI_created_' + _TIMESTAMP + '},' +
                       '{Key=' + awscons.AWS_RES_TAG_NAME + ',Value=' + self._get_org_tag() + '}]\"' +
                       ' --query \"Instances[0].InstanceId\"' + subnet_option)
            result = self._run_command(aws_cmd)
            ec2_id = result.stdout.decode('utf-8').strip()
        else:
            ec2_id = self._console.prompt('Enter the ID of the AWS EC2 '
                                                'instance to be used',
                                                in_default='',
                                                in_type=str,
                                                in_show_default=False)
        self._console.ok(_TAB + cons.TXT_PASS)
        # retrieve the public ip of the ec2 instance
        step = self._print_step(step, 'Query IP address of EC2 instance.')
        num_ip_tries = 0
        is_ip_valid = False
        # aws can reply with 'null' as the ip address. see DEV-221.
        while(num_ip_tries < _NUM_RETRIES and
                not is_ip_valid):
            if num_ip_tries > 0:
                self._console.ok(_TAB + awscons.TXT_AWS_IP_ADDRESS_RETRY)
                time.sleep(_RETRY_DELAY)
            aws_cmd = ('aws ec2 describe-instances --instance-ids ' +
                        ec2_id +
                        ' --query \"Reservations[0].Instances[0].PublicIpAddress\"')
            result = self._run_command(aws_cmd)
            self._ec2_public_ip = result.stdout.decode('utf-8').strip().replace('\"','')
            # check that the ip is correct
            if (self._ec2_public_ip is None or
                len(self._ec2_public_ip) == 0):
                is_ip_valid = False
            else:
                try:
                    socket.inet_aton(self._ec2_public_ip)
                    self._console.ok(_TAB + 'EC2 Instance IP Address: ' + str(self._ec2_public_ip))
                    is_ip_valid = True
                except socket.error:
                    is_ip_valid = False
            num_ip_tries = num_ip_tries + 1
        # check that the ip was correctly retrieved or abort
        if not is_ip_valid:
            self._console.exception(awscons.ERR_AWS_CANNOT_GET_IP_ADDRESS + ec2_id)
        self._console.ok(_TAB + cons.TXT_PASS)
        # wait for instance to run
        step = self._print_step(step, 'Wait for EC2 Instance to Initialize.')
        # failure seen. give time for new instance to propagate in aws infrastructure.
        time.sleep(_RETRY_DELAY)
        status = self._aws_get_instance_status(ec2_id)
        while status != 'running':
            self._console.ok(_TAB + awscons.TXT_AWS_WAIT_INSTANCE_RUNNING)
            time.sleep(_RETRY_DELAY)
            status = self._aws_get_instance_status(ec2_id)
        # connect to ec2 instance
        time.sleep(_RETRY_DELAY) # TODO hardcoded delay so login doesn't fail
        step = self._print_step(step, 'Verify login to AWS EC2 instance.')
        linux_cmd = 'uname -a && exit 0'
        result = self._run_remote_command(in_ip=self._ec2_public_ip,
                                            in_pem=self._keypair_path,
                                            in_command=linux_cmd,
                                            in_retries=_NUM_RETRIES,
                                            in_sleep=_RETRY_DELAY)
        self._console.ok(_TAB + cons.TXT_PASS)
        # install java in ec2 instance
        step = self._print_step(step, 'Provision the AWS EC2 instance.')
        linux_cmd = ('sudo apt-get -y update &&' +
                     ' sudo apt-get -y install default-jdk &&' +
                     ' java -version && exit 0')
        result = self._run_remote_command(in_ip=self._ec2_public_ip,
                                            in_pem=self._keypair_path,
                                            in_command=linux_cmd,
                                            in_retries=_NUM_RETRIES,
                                            in_sleep=_RETRY_DELAY)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_agent(self, in_step):
        """Create/configure the Uniquid Agent.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # download the jar file
        step = self._print_step(step, 'Download the Uniquid Agent.')
        package_url = ('http://' + self._login_mgr.get_login_ip() + ':' +
                       cons.UNIQUID_STATIC_PORT +
                       awscons.AWS_AGENT_URL)
        # create the output directory
        if not os.path.isdir(_OUTPUT_DIR):
            os.makedirs(_OUTPUT_DIR)
        target_path = os.path.join(_OUTPUT_DIR, _AWS_AGENT_FILE)
        with urllib.request.urlopen(package_url) as response, \
                open(target_path, 'wb') as outfile:
            shutil.copyfileobj(response, outfile)
        with tarfile.open(target_path, 'r') as tf:
            tf.extractall(_OUTPUT_DIR)
        self._console.ok(_TAB + cons.TXT_PASS)
        # customize the agent configuration
        step = self._print_step(step, 'Customize the Uniquid AWS Agent.')
        config_path = os.path.join(_OUTPUT_DIR, _AGENT_TAR_SUBDIR,
                                   'appconfig.properties')
        appconfig = ''
        with open(config_path, 'r') as cf:
            appconfig = cf.read()
        appconfig = appconfig.replace('NETWORK_PARAMS', self._orch_props.get('network', '[Error]'))
        appconfig = appconfig.replace('MQTT_BROKER', self._orch_props.get('mqttBroker', '[Error]'))
        appconfig = appconfig.replace('CHECKPOINT_URL', self._orch_props.get('checkpointUrl', '[Error]'))
        # TODO topic.announce will change to org.id - depends on agent version
        appconfig = appconfig.replace('TOPIC', self._login_mgr.get_org_id() + '/announce')
        # string name of agent node - passed later to device
        self._agent_node_name = _AWS_AGENT_PREFIX + self._aws_account_id + '-' + _TIMESTAMP
        appconfig = appconfig.replace('NODE_NAME', self._agent_node_name)
        with open(config_path, 'w') as cf:
            cf.write(appconfig)
        self._console.ok(_TAB + cons.TXT_PASS)
        # upload jar to instance and start
        step = self._print_step(step, 'Upload Uniquid Agent to AWS EC2 instance.')
        result = self._upload_file(in_ip=self._ec2_public_ip,
                                    in_pem=self._keypair_path,
                                    in_local_path=config_path,
                                    in_remote_path='appconfig.properties',
                                    in_retries=_NUM_RETRIES,
                                    in_sleep=_RETRY_DELAY)
        # find untarred jar file
        for f in glob.glob(_OUTPUT_DIR + '/**/aws*.jar', recursive=True):
            jar_path = f
        if jar_path is None:
            self._console.exception(ERR_AWS_CANNOT_FIND_JAR_FILE)
        result = self._upload_file(in_ip=self._ec2_public_ip,
                                    in_pem=self._keypair_path,
                                    in_local_path=jar_path,
                                    in_remote_path='awsagent.jar',
                                    in_retries=_NUM_RETRIES,
                                    in_sleep=_RETRY_DELAY)
        upload_cmd = 'nohup java -jar awsagent.jar appconfig.properties < /dev/null > /dev/null 2>&1 &'
        result = self._run_remote_command(in_ip=self._ec2_public_ip,
                                            in_pem=self._keypair_path,
                                            in_command=upload_cmd,
                                            in_retries=_NUM_RETRIES,
                                            in_sleep=_RETRY_DELAY)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_mqtt_proxy(self, in_step):
        """Deploy MQTT Proxy on an EC2 instance.

            Args:
            in_step: Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # create uniquid filenames
        proxy_root_key_file = _AWS_PROXY_ROOT_PREFIX + _TIMESTAMP + '.key'
        proxy_root_cert_file =  _AWS_PROXY_ROOT_PREFIX + _TIMESTAMP + '.crt'
        proxy_chain_cert_file = 'caChain-' + _TIMESTAMP + '.crt'
        proxy_sign_req_file = _AWS_PROXY_KEY_PREFIX + _TIMESTAMP + '.csr'
        proxy_key_file = _AWS_PROXY_KEY_PREFIX + _TIMESTAMP + '.key'
        proxy_cert_file = _AWS_PROXY_KEY_PREFIX + _TIMESTAMP + '.crt'
        step = self._print_step(step, 'Upload MQTT Proxy tarball to EC2 instance.')
        package_url = ('http://' + self._login_mgr.get_login_ip() + ':' +
                       cons.UNIQUID_STATIC_PORT +
                       awscons.AWS_PROXY_URL)
        with urllib.request.urlopen(package_url) as response, \
                open(_AWS_PROXY_FILE, 'wb') as outfile:
            shutil.copyfileobj(response, outfile)
        result = self._upload_file(in_ip=self._ec2_public_ip,
                                    in_pem=self._keypair_path,
                                    in_local_path=_AWS_PROXY_FILE,
                                    in_remote_path=_AWS_PROXY_FILE,
                                    in_retries=_NUM_RETRIES,
                                    in_sleep=_RETRY_DELAY)
        untar_cmd = ('tar xvz -f  ' + _AWS_PROXY_FILE)
        result = self._run_remote_command(in_ip=self._ec2_public_ip,
                                            in_pem=self._keypair_path,
                                            in_command=untar_cmd,
                                            in_retries=0,
                                            in_sleep=0)
        self._console.ok(_TAB + cons.TXT_PASS)
        step = self._print_step(step, 'Build MQTT Proxy on EC2 instance.')
        apt_cmd = ('sudo apt-get -y update &&'
                   ' sudo apt-get -y install make &&'
                   ' sudo apt-get -y install gcc &&'
                   ' sudo apt-get -y install libssl-dev')
        result = self._run_remote_command(in_ip=self._ec2_public_ip,
                                            in_pem=self._keypair_path,
                                            in_command=apt_cmd,
                                            in_retries=_NUM_RETRIES,
                                            in_sleep=_RETRY_DELAY)
        make_cmd = 'cd ' + awscons.AWS_PROXY_REPO + ' && make'
        result = self._run_remote_command(in_ip=self._ec2_public_ip,
                                            in_pem=self._keypair_path,
                                            in_command=make_cmd,
                                            in_retries=_NUM_RETRIES,
                                            in_sleep=_RETRY_DELAY)
        self._console.ok(_TAB + cons.TXT_PASS)
        step = self._print_step(step, 'Create certificates for proxy.')
        cert_cmd = 'openssl genrsa -out ' + proxy_root_key_file + ' 4096'
        result = self._run_command(cert_cmd)
        cert_cmd = ('openssl req -x509 -new -nodes -key ' + proxy_root_key_file + ' -sha256'
                    ' -days 3650 -out ' + proxy_root_cert_file + ' -subj \"/CN=UniquidAwsMqttProxyOrg\"')
        result = self._run_command(cert_cmd)
        cert_cmd = 'openssl genrsa -out ' + proxy_key_file + ' 2048'
        result = self._run_command(cert_cmd)
        cert_cmd = ('openssl req -new -sha256 -key ' + proxy_key_file +
                    ' -subj \"/CN=' + self._ec2_public_ip + '\" -out ' + proxy_sign_req_file)
        result = self._run_command(cert_cmd)
        cert_cmd = ('openssl x509 -req -in ' + proxy_sign_req_file + ' -CA ' + proxy_root_cert_file +
                    ' -CAkey ' + proxy_root_key_file + ' -CAcreateserial -out ' + proxy_cert_file + ' -days 3650 -sha256')
        result = self._run_command(cert_cmd)
        self._console.ok(_TAB + cons.TXT_PASS)
        step = self._print_step(step, 'Create the Certificate chain file for devices.')
        cert_url = ('http://' + self._login_mgr.get_login_ip() + ':' +
                    cons.UNIQUID_STATIC_PORT +
                    awscons.AWS_ROOT_CERT_URL)
        with urllib.request.urlopen(cert_url) as response, \
                open(_AWS_BROKER_CA_FILE, 'wb') as outfile:
            shutil.copyfileobj(response, outfile)
        # concatenate two cert files before upload
        broker_cert = None
        proxy_cert = None
        with open(_AWS_BROKER_CA_FILE, 'r') as f:
            broker_cert = f.read()
        with open('' + proxy_root_cert_file + '', 'r') as f:
            proxy_cert = f.read()
        with open(proxy_chain_cert_file, 'w') as f:
            f.write(broker_cert)
            f.write(proxy_cert)
        self._cert_chain_file = os.path.abspath(proxy_chain_cert_file)
        self._console.ok(_TAB + cons.TXT_PASS)
        step = self._print_step(step, 'Download the Verisign Root Certificate.')
        cert_url = ('https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem')
        with urllib.request.urlopen(cert_url) as response, \
                open(_AWS_VERISIGN_FILE, 'wb') as outfile:
            shutil.copyfileobj(response, outfile)
        self._console.ok(_TAB + cons.TXT_PASS)
        step = self._print_step(step, 'Upload keys and certificates.')
        upload_path = os.path.join(awscons.AWS_PROXY_REPO, 'mqtt-proxy.crt')
        result = self._upload_file(in_ip=self._ec2_public_ip,
                                    in_pem=self._keypair_path,
                                    in_local_path=proxy_cert_file,
                                    in_remote_path=upload_path,
                                    in_retries=_NUM_RETRIES,
                                    in_sleep=_RETRY_DELAY)
        upload_path = os.path.join(awscons.AWS_PROXY_REPO, 'mqtt-proxy.key')
        result = self._upload_file(in_ip=self._ec2_public_ip,
                                    in_pem=self._keypair_path,
                                    in_local_path=proxy_key_file,
                                    in_remote_path=upload_path,
                                    in_retries=_NUM_RETRIES,
                                    in_sleep=_RETRY_DELAY)
        upload_path = os.path.join(awscons.AWS_PROXY_REPO, _AWS_VERISIGN_FILE)
        result = self._upload_file(in_ip=self._ec2_public_ip,
                                    in_pem=self._keypair_path,
                                    in_local_path=_AWS_VERISIGN_FILE,
                                    in_remote_path=upload_path,
                                    in_retries=_NUM_RETRIES,
                                    in_sleep=_RETRY_DELAY)
        self._console.ok(_TAB + cons.TXT_PASS)
        step = self._print_step(step, 'Upload the device configuration file.')
        upload_path = os.path.join(awscons.AWS_PROXY_REPO, _AWS_DEV_CFG_FILE)
        result = self._upload_file(in_ip=self._ec2_public_ip,
                                    in_pem=self._keypair_path,
                                    in_local_path=_AWS_DEV_CFG_FILE,
                                    in_remote_path=upload_path,
                                    in_retries=_NUM_RETRIES,
                                    in_sleep=_RETRY_DELAY)
        self._console.ok(_TAB + cons.TXT_PASS)
        step = self._print_step(step, 'Start the MQTT Proxy process.')
        start_cmd = ('cd ' + os.path.join('.', awscons.AWS_PROXY_REPO) +
                      '; nohup ' + os.path.join('.', 'mqtt-proxy') +
                      ' < /dev/null > /dev/null 2>&1 &')
        result = self._run_remote_command(in_ip=self._ec2_public_ip,
                                            in_pem=self._keypair_path,
                                            in_command=start_cmd,
                                            in_retries=1,
                                            in_sleep=_RETRY_DELAY)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_lambda(self, in_step):
        """Create/configure the AWS Lambda function.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # update values in javascript
        step = self._print_step(step, 'Customize the AWS Lambda function.')
        lambda_code = ''
        line_a = 'var aws_account = \'' + self._aws_account_id + '\';\n'
        line_b = 'var aws_region = \'' + self._aws_region + '\';\n'
        line_c = 'var uniquid_aws_agent = \'http://' + self._ec2_public_ip + ':8070/api/v1/checkawscontract\';\n'
        lambda_path = os.path.join(_OUTPUT_DIR, _AGENT_TAR_SUBDIR, 'lambda', 'UniquidLambda.js')
        with open(lambda_path, 'r') as f:
            lambda_code = f.read()
        with open(lambda_path, 'w') as f:
            f.write(line_a)
            f.write(line_b)
            f.write(line_c)
            f.write('\n')
            f.write(lambda_code)
        self._console.ok(_TAB + cons.TXT_PASS)
        # install dependencies
        step = self._print_step(step, 'Install Javascript dependencies.')
        original_dir = os.getcwd()
        node_dir = os.path.join(_OUTPUT_DIR, _AGENT_TAR_SUBDIR)
        os.chdir(node_dir)
        result = self._run_command('npm install request')
        self._console.ok(_TAB + cons.TXT_PASS)
        # zip package
        step = self._print_step(step, 'Zip the Lambda function package.')
        modules_path = 'node_modules'
        # TODO add compression
        with zipfile.ZipFile('UniquidLambda.zip', 'w') as zf:
            zf.write(os.path.join('lambda', 'UniquidLambda.js'), arcname='UniquidLambda.js') # FIXME hardcoded
            zf.write(modules_path)
            for f in glob.glob(modules_path + '/**/*', recursive=True):
                zf.write(f)
        os.chdir(original_dir)
        self._console.ok(_TAB + cons.TXT_PASS)
        # create the AWS IAM Execution Role
        step = self._print_step(step, 'Create an AWS IAM Execution Role.')
        self._role_name = _AWS_IAM_ROLE_PREFIX + _TIMESTAMP
        cmd = 'aws iam get-role --role-name ' + self._role_name
        arg_list = shlex.split(cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode == 0:
            self._console.ok(_TAB + 'AWS IAM role ' + self._role_name + ' already exists. Skipping Role creation.')
        else:
            cmd = 'aws iam create-role --role-name ' + self._role_name + ' --assume-role-policy-document \'{\"Version\": \"2012-10-17\", \"Statement\": [ { \"Action\": \"sts:AssumeRole\", \"Effect\": \"Allow\", \"Principal\": { \"Service\": \"lambda.amazonaws.com\" } } ] }\' --description \"Allows Lambda functions to call AWS services on your behalf.\"'
            result = self._run_command(cmd)
        # TODO check output from command
        result_string = result.stdout.decode('utf-8').strip()
        result_json = json.loads(result_string)
        aws_role_arn = result_json.get('Role').get('Arn')
        self._console.ok(_TAB + cons.TXT_PASS)
        # attach AWS IAM policy
        step = self._print_step(step, 'Attach the AWS IAM policy.')
        cmd = 'aws iam attach-role-policy --role-name ' + self._role_name + ' --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        result = self._run_command(cmd)
        self._console.ok(_TAB + cons.TXT_PASS)
        # upload the lambda function
        step = self._print_step(step, 'Upload the Lambda function package.')
        # give time for new role to propagate through AWS
        time.sleep(_RETRY_DELAY)
        self._lambda_name = _AWS_LAMBDA_FUNC_PREFIX + _TIMESTAMP
        cmd = 'aws lambda create-function --function-name ' + self._lambda_name + ' --runtime nodejs8.10 --role ' + aws_role_arn + ' --handler UniquidLambda.handler --zip-file fileb://' + node_dir + '/UniquidLambda.zip --region ' + self._aws_region
        result = self._run_command(cmd)
        result_string = result.stdout.decode('utf-8').strip()
        result_json = json.loads(result_string)
        self._aws_function_arn = result_json.get('FunctionArn')
        self._console.ok(_TAB + cons.TXT_PASS)
        # test lambda invocation
        step = self._print_step(step, 'Test the Lambda function invocation.')
        time.sleep(_RETRY_DELAY)
        cmd = 'aws lambda invoke --invocation-type RequestResponse --function-name ' + self._lambda_name + ' --region ' +self._aws_region + ' --log-type Tail --payload \'{\"key1\":\"value1\", \"key2\":\"value2\", \"key3\":\"value3\"}\' ' + node_dir + '/lambda-out.txt'
        result = self._run_command(cmd)
        result_string = result.stdout.decode('utf-8').strip()
        result_json = json.loads(result_string)
        if result_json.get('StatusCode') != 200:
            self._console.exception(awscons.ERR_AWS_LAMBDA_INVOKE_FAILED)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_authorizer(self, in_step):
        """Create/configure the AWS IoT Authorizer.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # generate key pair
        step = self._print_step(step, 'Generate Key pair for IoT Authorizer.')
        rsa_keys = RSA.generate(2048)
        self._rsa_private_key = rsa_keys.exportKey('PEM').decode('utf-8')
        rsa_public_key = rsa_keys.publickey().exportKey('PEM').decode('utf-8')
        virt_kp_name = 'aws_device_key_pair_' + _TIMESTAMP + '.pem'
        with open(virt_kp_name, 'w') as f:
            f.write(self._rsa_private_key + '\n')
            f.write(rsa_public_key)
            self._console.ok(_TAB + 'Key pair file written: ' + virt_kp_name)
        self._console.ok(_TAB + cons.TXT_PASS)
        # create authorizer
        step = self._print_step(step, 'Create the IoT Authorizer.')
        # check if authorizer exists already
        self._authorizer_name = _AWS_AUTH_PREFIX + _TIMESTAMP
        cmd = 'aws iot describe-authorizer --authorizer-name ' + self._authorizer_name
        arg_list = shlex.split(cmd)
        is_authorizer_exists = True
        while is_authorizer_exists:
            result = subprocess.run(arg_list,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            if result.returncode == 0:
                self._console.ok('Warning: AWS IoT Authorizer ' + self._authorizer_name + ' already exists!')
                self._console.ok('Please delete before proceeding....')
                if self._console.confirm('Is it OK to proceed?'):
                    pass
            else:
                is_authorizer_exists = False
                # no authorizer therefore ok to proceed
        cmd = 'aws iot create-authorizer --authorizer-name ' + self._authorizer_name + ' --authorizer-function-arn ' + self._aws_function_arn + ' --token-key-name UniquIDToken --token-signing-public-keys FIRST_KEY=\"' + rsa_public_key + '\" --status ACTIVE --region ' +self._aws_region
        result = self._run_command(cmd)
        result_string = result.stdout.decode('utf-8').strip()
        result_json = json.loads(result_string)
        aws_authorizer_arn = result_json.get('authorizerArn')
        self._console.ok(_TAB + cons.TXT_PASS)
        # update permissions
        step = self._print_step(step, 'Update permissions for IoT Authorizer.')
        cmd = 'aws lambda add-permission --function-name ' + self._lambda_name + ' --principal iot.amazonaws.com --source-arn ' + aws_authorizer_arn + ' --statement-id UniquID-Id-123 --action \"lambda:InvokeFunction\"'
        result = self._run_command(cmd)
        self._console.ok(_TAB + cons.TXT_PASS)
        # TODO test the authorizer
        return step

    def _init_device_cfg(self, in_dev_cfg:dict = None):
        """Initialise a device configuration dictionary with values which are
            common to all deployments.

            Args:
              in_dev_cfg: Device configuration dictionary.
        """
        assert in_dev_cfg is not None
        in_dev_cfg['orgId'] = self._login_mgr.get_org_id()
        in_dev_cfg['mqttUrl'] = self._orch_props.get('mqttBroker', '[Error]')
        mqtt_url = self._orch_props.get('mqttBroker', '[Error]')
        in_dev_cfg['mqttsUrl'] = mqtt_url.replace('1883','8883') # FIXME work-around for lack of field in reply from orchestrator (DEV-75)
        in_dev_cfg['mqttTopic'] = self._login_mgr.get_org_id() + '/announce' # FIXME work-around # self._orch_props.get('mqttTopic', '[Error]')
        in_dev_cfg['registryUrl'] = 'http://' + self._login_mgr.get_api_ip() + ':8060' # FIXME work-around # self._orch_props.get('registryUrl', '[Error]')
        in_dev_cfg['checkpointUrl'] = self._orch_props.get('checkpointUrl', '[Error]')
        # map from orchestrator network type to an agreed identifier
        network_type = self._orch_props.get('network', '').casefold()
        if _blockchain_map.get(_LTC_REGTEST,'[Error]') in network_type:
            in_dev_cfg['network'] = _LTC_REGTEST
        elif _blockchain_map.get(_LTC_TESTNET,'[Error]') in network_type:
            in_dev_cfg['network'] = _LTC_TESTNET
        else:
            in_dev_cfg['network'] = _LTC_MAINNET

    def _save_device_cfg(self, in_dev_cfg:dict = None, in_filename:str=None):
        """Save the device configuration dictionary to a local file.

            Args:
              in_dev_cfg: Device configuration dictionary.
              in_filename: Name of the configuration file. Not the full path.
        """
        assert in_dev_cfg is not None
        assert in_filename is not None
        with open(in_filename, 'w') as f:
            f.write(json.dumps(in_dev_cfg, indent=2))
            self._console.ok(_TAB + 'Configuration file written: '+ in_filename)

    def _basic_deploy_dev_cfg(self, in_step):
        """Create/configure the configuration file for the non-AWS integrated devices.

            Args:
              in_step: Current step number.
            Returns:
              Incremented step number.
        """
        step = in_step
        # generate config file for UniquID devices
        step = self._print_step(step, 'Generate device configuration file.')
        self._init_device_cfg(_basic_device_config)
        # save device configuration to file
        self._save_device_cfg(_basic_device_config, _BASIC_DEV_CFG_FILE)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _aws_deploy_dev_cfg(self, in_step):
        """Create/configure the configuration file for the AWS-integrated devices.

            Args:
              in_step: Current step number.
            Returns:
              Incremented step number.
        """
        step = in_step
        # retrieve the public endpoint of the ec2 instance
        step = self._print_step(step, 'Query AWS IoT Endpoint.')
        iot_endpoint = None
        aws_cmd = ('aws iot describe-endpoint')
        result = self._run_command(aws_cmd)
        iot_string = result.stdout.decode('utf-8').strip()
        iot_json = json.loads(iot_string)
        iot_endpoint = iot_json.get('endpointAddress')
        if (iot_endpoint is None or
            len(iot_endpoint) == 0):
            self._console.exception(awscons.ERR_AWS_CANNOT_FIND_IOT_ENDPOINT)
        self._console.ok(_TAB + cons.TXT_PASS)
        # generate config file for Onboarding server
        step = self._print_step(step, 'Generate AWS device configuration file.')
        self._init_device_cfg(_aws_device_config)
        _aws_device_config['proxyUrl'] = 'tcp://' + self._ec2_public_ip + ':8883' # FIXME improve creation of URL
        _aws_device_config['awsPrivateKey'] = self._rsa_private_key.split('\n')
        _aws_device_config['awsAgentName'] = self._agent_node_name
        _aws_device_config['awsAuthorizerName'] = self._authorizer_name
        _aws_device_config['awsEndpointAddress'] = iot_endpoint
        # save device configuration to file
        self._save_device_cfg(_aws_device_config, _AWS_DEV_CFG_FILE)
        self._console.ok(_TAB + cons.TXT_PASS)
        return step

    def _basic_print_summary(self, in_step):
        """Print a summary of the common device configuration file generation.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # retrieve the public endpoint of the ec2 instance
        step = self._print_step(step, 'Summary.\n')
        self._console.ok(_TAB + 'Cloud Resources:')
        self._console.ok(_TAB + 'None')
        self._console.ok(_TAB + 'Generated Files:')
        self._console.ok(_TAB + 'Configuration for devices: ' + str(_BASIC_DEV_CFG_FILE) + '\n')
        return step

    def _aws_print_summary(self, in_step):
        """Print a summary of the deployment.

            Args:
            in_step -- Current step number.
            Returns:
            Incremented step number.
        """
        step = in_step
        # retrieve the public endpoint of the ec2 instance
        step = self._print_step(step, 'Summary.\n')
        self._console.ok(_TAB + 'Timestamp: ' + _TIMESTAMP + '\n')
        self._console.ok(_TAB + 'AWS Resources:')
        self._console.ok(_TAB + 'EC2 Security Group ID: ' + str(self._sec_group_id))
        self._console.ok(_TAB + 'EC2 Key Pair Name: ' + str(self._keypair_name))
        self._console.ok(_TAB + 'EC2 Key Pair File: ' + str(self._keypair_path))
        self._console.ok(_TAB + 'EC2 Instance IP Address: ' + str(self._ec2_public_ip))
        self._console.ok(_TAB + 'IAM Role: '+ str(self._role_name))
        self._console.ok(_TAB + 'Lambda Function Name: ' + str(self._lambda_name))
        self._console.ok(_TAB + 'Lambda Function ARN: ' + str(self._aws_function_arn))
        self._console.ok(_TAB + 'IoT Authorizer Name: ' + str(self._authorizer_name) + '\n')
        self._console.ok(_TAB + 'Generated Files:')
        self._console.ok(_TAB + 'Configuration for devices: ' + str(_AWS_DEV_CFG_FILE))
        self._console.ok(_TAB + 'Certificate Chain for devices: ' + str(self._cert_chain_file) + '\n')
        return step

    def _aws_undeploy_all(self, in_step, in_timestamps):
        """Delete all AWS components identified by each timestamp.

            Args:
            in_step -- Current step number.
            in_timestamps -- Timestamps of components to delete.
            Returns:
            Incremented step number.
        """
        step = in_step
        for timestamp in in_timestamps:
            step = self._print_step(step, 'Delete the AWS EC2, IAM and IoT resources with timestamp: ' + timestamp + '\n')
            # ec2 instances
            delete_ec2_name = None
            delete_ec2_id = None
            aws_cmd = ('aws ec2 describe-instances')
            result = self._run_command(aws_cmd)
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            for obj in json_obj.get('Reservations',[]):
                for inst in obj.get('Instances',[]):
                    for tag in inst.get('Tags',[]):
                        if (_AWS_EC2_NAME_PREFIX in tag.get('Value', '') and
                                timestamp in tag.get('Value','')):
                            delete_ec2_name = tag.get('Value')
                            delete_ec2_id = inst.get('InstanceId')
            if delete_ec2_id:
                self._console.ok(_TAB * 2 + 'EC2 Instance Name: ' + str(delete_ec2_name))
                self._console.ok(_TAB * 2 + 'EC2 Instance Id: ' + str(delete_ec2_id))
            # ec2 security groups
            delete_sg_name = None
            delete_sg_id = None
            aws_cmd = ('aws ec2 describe-security-groups')
            result = self._run_command(aws_cmd)
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            for obj in json_obj.get('SecurityGroups',[]):
                if (_SEC_GROUP_NAME in obj.get('GroupName', '') and
                        timestamp in obj.get('GroupName','')):
                    delete_sg_name = obj.get('GroupName')
                    delete_sg_id = obj.get('GroupId')
            if delete_sg_id:
                self._console.ok(_TAB * 2 + 'EC2 Security Group Name: ' + str(delete_sg_name))
                self._console.ok(_TAB * 2 + 'EC2 Security Group Id: ' + str(delete_sg_id))
            # ec2 key pair
            delete_kp_name = None
            aws_cmd = ('aws ec2 describe-key-pairs')
            result = self._run_command(aws_cmd)
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            for obj in json_obj.get('KeyPairs',[]):
                if (_KEYPAIR_NAME in obj.get('KeyName','') and
                        timestamp in obj.get('KeyName','')):
                    delete_kp_name = obj.get('KeyName')
            if delete_kp_name:
                self._console.ok(_TAB * 2 + 'EC2 Key Pair Name: ' + str(delete_kp_name))
            # lambda function
            delete_lambda_name = None
            delete_lambda_arn = None
            aws_cmd = ('aws lambda list-functions')
            result = self._run_command(aws_cmd)
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            for obj in json_obj.get('Functions',[]):
                if (_AWS_LAMBDA_FUNC_PREFIX in obj.get('FunctionName','') and
                        timestamp in obj.get('FunctionName','')):
                    delete_lambda_name = obj.get('FunctionName')
                    delete_lambda_arn = obj.get('FunctionArn')
            if delete_lambda_arn:
                self._console.ok(_TAB * 2 + 'Lambda Function Name: ' + str(delete_lambda_name))
                self._console.ok(_TAB * 2 + 'Lambda Function ARN: ' + str(delete_lambda_arn))
            # custom authorizer
            delete_authorizer_name = None
            aws_cmd = ('aws iot list-authorizers')
            result = self._run_command(aws_cmd)
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            for obj in json_obj.get('authorizers',[]):
                if (_AWS_AUTH_PREFIX in obj.get('authorizerName','') and
                    timestamp in obj.get('authorizerName','')):
                    delete_authorizer_name = obj.get('authorizerName')
            if delete_authorizer_name:
                self._console.ok(_TAB * 2 + 'IoT Authorizer Name: ' + str(delete_authorizer_name))
            # iam role
            delete_role_name = None
            aws_cmd = ('aws iam list-roles')
            result = self._run_command(aws_cmd)
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            for obj in json_obj.get('Roles',[]):
                if (_AWS_IAM_ROLE_PREFIX in obj.get('RoleName','') and
                    timestamp in obj.get('RoleName','')):
                    delete_role_name = obj.get('RoleName')
            if delete_role_name:
                self._console.ok(_TAB * 2 + 'IAM Role Name: ' + str(delete_role_name))
            # cloudwatch log group
            delete_log_name = None
            aws_cmd = ('aws logs describe-log-groups')
            result = self._run_command(aws_cmd)
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            for obj in json_obj.get('logGroups',[]):
                if (_AWS_LAMBDA_FUNC_PREFIX in obj.get('logGroupName', '') and
                        timestamp in obj.get('logGroupName','')):
                    delete_log_name = obj.get('logGroupName')
            if delete_log_name:
                self._console.ok(_TAB * 2 + 'Cloudwatch Log Group Name: ' + str(delete_log_name))
            # delete all of the identified aws resources
            if (self._yes_mode or
                self._console.confirm("Do you want to delete these AWS resources?",
                                      in_default=False)):
                if delete_ec2_id:
                    aws_cmd = ('aws ec2 terminate-instances --instance-ids ' + delete_ec2_id)
                    result = self._run_command(aws_cmd)
                    aws_cmd = ('aws ec2 describe-instances --instance-ids ' + delete_ec2_id)
                    result = self._run_command(aws_cmd)
                    isTerminated = False
                    json_obj = json.loads(result.stdout.decode('utf-8').strip())
                    while (isTerminated == False):
                        state = None
                        if (json_obj.get('Reservations', None) != None and
                            json_obj.get('Reservations')[0].get('Instances', None) != None and
                            json_obj.get('Reservations')[0].get('Instances')[0].get('State', None) != None and
                            json_obj.get('Reservations')[0].get('Instances')[0].get('State').get('Name') != None):
                            state = json_obj.get('Reservations')[0].get('Instances')[0].get('State').get('Name')
                        if(state is None or
                                state == 'terminated'):
                            isTerminated = True
                        if not isTerminated:
                            self._console.ok(_TAB + awscons.TXT_AWS_WAIT_INSTANCE_TERMINATE)
                            time.sleep(10)
                            result = self._run_command(aws_cmd)
                            json_obj = json.loads(result.stdout.decode('utf-8').strip())
                    self._console.ok(_TAB + awscons.TXT_AWS_INSTANCE_NOW_TERMINATED)
                if delete_sg_name:
                    aws_cmd = ('aws ec2 delete-security-group --group-id ' + delete_sg_id)
                    result = self._run_command(aws_cmd)
                if delete_kp_name:
                    aws_cmd = ('aws ec2 delete-key-pair --key-name ' + delete_kp_name)
                    result = self._run_command(aws_cmd)
                if delete_lambda_arn:
                    aws_cmd = ('aws lambda delete-function --function-name ' + delete_lambda_arn)
                    result = self._run_command(aws_cmd)
                if delete_authorizer_name:
                    aws_cmd = ('aws iot update-authorizer --authorizer-name ' + delete_authorizer_name + ' --status INACTIVE')
                    result = self._run_command(aws_cmd)
                    time.sleep(10)
                    aws_cmd = ('aws iot delete-authorizer --authorizer-name ' + delete_authorizer_name)
                    result = self._run_command(aws_cmd)
                if delete_role_name:
                    aws_cmd = ('aws iam detach-role-policy --role-name ' + delete_role_name + ' --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
                    result = self._run_command(aws_cmd)
                    aws_cmd = ('aws iam delete-role --role-name ' + delete_role_name)
                    result = self._run_command(aws_cmd)
                if delete_log_name:
                    aws_cmd = ('aws logs delete-log-group --log-group-name ' + delete_log_name)
                    result = self._run_command(aws_cmd)
            else:
                self._console.ok(_TAB + 'No AWS resources with timestamp to remove.')
            self._console.ok(_TAB + cons.TXT_PASS)

    def _run_command(self, in_command:str=None, in_retries:int=0, in_sleep:int=0):
        """Run a shell command on the local machine.

            Args:
              in_command -- Full string with command.
              in_retries -- Permitted number of retries before raising an
              exception for an error.
              in_sleep -- Sleep between retries in seconds.
            Returns:
              subprocess.run() return object.
            Throws:
              ClickException if the initial command and all retries failed.
        """
        assert in_command is not None
        assert len(in_command) > 0
        assert in_retries >= 0
        assert in_sleep >= 0
        arg_list = shlex.split(in_command)
        self._console.ok(_TAB + 'Running command: ' + in_command)
        num_tries = 0
        result = None
        while ((result is None or
                    result.returncode != 0) and
                num_tries <= (in_retries + 1)):
            if num_tries > 1:
                self._console.ok(_TAB + 'Command failed. Pausing before retry.....')
                time.sleep(in_sleep)
                self._console.ok(_TAB + 'Retry command: ' + in_command)
            result = subprocess.run(arg_list,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            num_tries = num_tries + 1
        if result.returncode != 0:
            self._console.error(result.stderr.decode('utf-8').strip())
            self._console.exception(awscons.ERR_AWS_SHELL_COMMAND_FAILED)
        return result

    def _run_remote_command(self, in_ip:str=None, in_pem:str=None, in_command:str=None, in_retries:int=0, in_sleep:int=0):
        """Run a shell command on a remote EC2 instance.

            Args:
              in_ip: IP address or hostname.
              in_pem: Full path of the PEM file for the EC2 instance.
              in_command -- Full string with command.
              in_retries -- Permitted number of retries before raising an
              exception for an error.
              in_sleep -- Sleep between retries in seconds.
            Returns:
              A dictionary holding the returncode, stdout and stderr from
              the remote command execution.
            Throws:
              ClickException if the initial command and all retries failed.
        """
        assert in_ip is not None
        assert len(in_ip) > 0
        assert in_pem is not None
        assert in_command is not None
        assert len(in_command) > 0
        assert in_retries >= 0
        assert in_sleep >= 0
        self._console.ok(_TAB + 'Running remote command: ' + in_command)
        num_tries = 0
        result = None
        while ((result is None or
                    result.get('returncode') != 0) and
                num_tries <= (in_retries + 1)):
            if num_tries > 1:
                self._console.ok(_TAB + 'Remote command failed. Pausing before retry.....')
                time.sleep(in_sleep)
                self._console.ok(_TAB + 'Retry remote command: ' + in_command)
            result = remote.ssh_command(in_ip=in_ip,
                                        in_pem_file=in_pem,
                                        in_user='ubuntu',
                                        in_command=in_command)
            num_tries = num_tries + 1
        if result.get('returncode') != 0:
            self._console.error(result.get('stderr'))
            self._console.exception(awscons.ERR_AWS_SHELL_COMMAND_FAILED)
        return result

    def _upload_file(self, in_ip:str=None, in_pem:str=None, in_local_path:str=None, in_remote_path:str=None, in_retries:int=0, in_sleep:int=0):
        """Upload a file to a remote EC2 instance.

            Args:
              in_ip: IP address or hostname.
              in_pem: Full path of the PEM file for the EC2 instance.
              in_local_path: Local file path.
              in_remote_path: Remote file path.
              in_retries: Permitted number of retries before raising an
              exception for an error.
              in_sleep: Sleep between retries in seconds.
            Returns:
              A dictionary holding the returncode, stdout and stderr from
              the remote command execution.
            Throws:
              ClickException if the initial command and all retries failed.
        """
        assert in_ip is not None
        assert len(in_ip) > 0
        assert in_pem is not None
        assert in_local_path is not None
        assert len(in_local_path) > 0
        assert in_remote_path is not None
        assert len(in_remote_path) > 0
        assert in_retries >= 0
        assert in_sleep >= 0
        self._console.ok(_TAB + 'Uploading the file: ' + in_local_path + ' to ' + in_ip)
        num_tries = 0
        result = None
        if not os.path.isfile(in_local_path):
            self._console.exception(cons.ERR_MISSING_LOCAL_FILE + in_local_path)
        while ((result is None or
                    result.get('returncode') != 0) and
                num_tries <= (in_retries + 1)):
            if num_tries > 1:
                self._console.ok(_TAB + 'Remote command failed. Pausing before retry.....')
                time.sleep(in_sleep)
                self._console.ok(_TAB + 'Retry remote command: ' + in_command)
            result = remote.upload_file(in_ip=in_ip,
                                        in_pem_file=in_pem,
                                        in_user='ubuntu',
                                        in_local_path=in_local_path,
                                        in_remote_path=in_remote_path)
            num_tries = num_tries + 1
        if result.get('returncode') != 0:
            self._console.error(result.get('stderr'))
            self._console.exception(awscons.ERR_AWS_SHELL_COMMAND_FAILED)
        return result

    def _aws_configure_get(self, in_param_name):
        """
        Query an aws client configuration parameter.

        Args:
        in_param_name -- Parameter name to be queried.
        Returns:
        String with parameter value.
        Throws:
        Exception thrown if parameter does not exist or is empty.
        """
        query_cmd = 'aws configure get ' + in_param_name
        arg_list = shlex.split(query_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if (result.returncode != 0 or
                result.stdout.decode('utf-8').strip() == 0):
            self._console.error(in_param_name +
                                ' must be configured in awscli.')
            self._console.exception(awscons.ERR_AWS_NOT_CONFIGURED)
        return result.stdout.decode('utf-8').strip()

    def _aws_get_caller_identity(self, in_param_name):
        """
        Query an aws client configuration parameter.

        Args:
        in_param_name -- Parameter name to be queried.
        Returns:
        String with parameter value.
        Throws:
        Exception thrown if parameter does not exist or is empty.
        """
        query_cmd = ('aws sts get-caller-identity --output text --query "' +
                     in_param_name + '"')
        arg_list = shlex.split(query_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if (result.returncode != 0 or
                result.stdout.decode('utf-8').strip() == 0):
            self._console.exception(awscons.ERR_AWS_NOT_CONFIGURED)
        return result.stdout.decode('utf-8').strip()

    def _aws_get_instance_status(self, in_ec2_id:str=None):
        """
        Query the status of an EC2 instance.

        Args:
        in_ec2_id -- Id of the EC2 instance.
        Returns:
        String with status.
        """
        assert in_ec2_id is not None
        retval = None
        query_cmd = ('aws ec2 describe-instance-status --output json --instance-ids ' +
                     in_ec2_id)
        arg_list = shlex.split(query_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if (result.returncode != 0 or
                result.stdout.decode('utf-8').strip() == 0):
            self._console.exception(awscons.ERR_AWS_CANNOT_FIND_INSTANCE +
                                    in_ec2_id)
        json_obj = json.loads(result.stdout.decode('utf-8').strip())
        if ('InstanceStatuses' in json_obj and
            len(json_obj['InstanceStatuses']) == 1):
            retval = json_obj.get('InstanceStatuses')[0].get('InstanceState').get('Name')
        return retval

    def _aws_is_ec2_vpc_account(self):
        """Query if the AWS account supports EC2 VPC or if it is a classic account.
            See https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html

            Returns:
            True if the account does support EC2 VPC or False if it is an EC2 classic
            account.
        """
        retval = False
        query_cmd = ('aws ec2 describe-account-attributes --output json')
        arg_list = shlex.split(query_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if (result.returncode != 0 or
                result.stdout.decode('utf-8').strip() == 0):
            self._console.exception(awscons.ERR_AWS_CANNOT_GET_ACCOUNT_TYPE)
        json_obj = json.loads(result.stdout.decode('utf-8').strip())
        attributes = json_obj.get('AccountAttributes')
        if attributes != None:
            for attribute in attributes:
                if (attribute.get('AttributeName') == 'supported-platforms' and
                        attribute.get('AttributeValues') != None):
                    for value in attribute.get('AttributeValues'):
                        if value.get('AttributeValue') == 'VPC':
                            retval = True
                            break
                if retval:
                    break
        return retval

    def _aws_get_ec2_default_vpc_id(self):
        """
        Get the ID of the EC2 Default VPC for the Region.

        Returns:
        A string containing the Default VPC ID or None if there is no Default
        VPC defined.
        """
        retval = None
        query_cmd = ('aws ec2 describe-vpcs --output json')
        arg_list = shlex.split(query_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if (result.returncode != 0 or
                result.stdout.decode('utf-8').strip() == 0):
            console.ok(_TAB + TXT_AWS_NO_DEFAULT_VPC)
        json_obj = json.loads(result.stdout.decode('utf-8').strip())
        vpcs = json_obj.get('Vpcs', None)
        if vpcs:
            for vpc in vpcs:
                if vpc.get('InstanceTenancy') == 'default':
                    retval = vpc.get('VpcId','')
                    break
        return retval

    def _aws_list_security_groups(self):
        """Return a list with names, ids of all security groups.

            Returns:
            List of dictionary objects."""
        retlist = []
        query_cmd = 'aws ec2 describe-security-groups --output json'
        arg_list = shlex.split(query_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if (result.returncode != 0):
            self._console.error(result.stderr.decode('utf-8').strip())
            self._console.exception(awscons.ERR_AWS_SHELL_COMMAND_FAILED)
        else:
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            if 'SecurityGroups' in json_obj:
                for obj in json_obj.get('SecurityGroups'):
                    sg_obj = {'name': None, 'id': None}
                    sg_obj['Name'] = obj.get('GroupName')
                    sg_obj['Id'] = obj.get('GroupId')
                    retlist.append(sg_obj)
            else:
                self._console.exception(awscons.ERR_AWS_REPLY_MISSING_DATA)
        return retlist

    def _aws_list_subnets(self):
        """Return a list of tuples containing the Subnets and their
            corresponding VPCs.

            Returns:
            List of tuples.  List may be empty."""
        retlist = []
        query_cmd = 'aws ec2 describe-subnets --output json'
        arg_list = shlex.split(query_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if (result.returncode != 0):
            self._console.error(result.stderr.decode('utf-8').strip())
            self._console.exception(awscons.ERR_AWS_SHELL_COMMAND_FAILED)
        else:
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            if 'Subnets' in json_obj:
                for obj in json_obj.get('Subnets'):
                    vpc_id = obj.get('VpcId')
                    subnet_id = obj.get('SubnetId')
                    retlist.append((vpc_id, subnet_id))
            else:
                self._console.exception(awscons.ERR_AWS_REPLY_MISSING_DATA)
        return retlist

    def _aws_list_key_pairs(self):
        """Return a list with names of all key pairs.

            Returns:
            List of strings with key pair names."""
        retlist = []
        query_cmd = 'aws ec2 describe-key-pairs --output json'
        arg_list = shlex.split(query_cmd)
        result = subprocess.run(arg_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if (result.returncode != 0):
            self._console.error(result.stderr.decode('utf-8').strip())
            self._console.exception(awscons.ERR_AWS_SHELL_COMMAND_FAILED)
        else:
            json_obj = json.loads(result.stdout.decode('utf-8').strip())
            if 'KeyPairs' in json_obj:
                for obj in json_obj.get('KeyPairs'):
                    if 'KeyName' in obj:
                        retlist.append(obj.get('KeyName'))
            else:
                self._console.exception(awscons.ERR_AWS_REPLY_MISSING_DATA)
        return retlist

    # TODO Can data be retrieved from login manager?
    def _get_orch_properties(self):
        """Retrieve properties from Orchestrator.

        Returns:
        Dictionary object with properties.
        """
        # request info from server
        url = 'http://{0}:{1}/api/v1/properties'.format(self._login_mgr.get_api_ip(),
                                                        self._login_mgr.get_api_port())
        cookies = dict(JSESSIONID=self._login_mgr.get_session_key())
        response = None
        retval = None
        try:
            response = requests.get(url, cookies=cookies)
        except requests.exceptions.ConnectionError:
            self._console.exception(cons.ERR_NO_RESPONSE)
        if (response.status_code == 200 and
                response.json()):
            retval = response.json()
        elif response.status_code == 401:
            self._console.exception(cons.ERR_LOGIN_REJECTED)
        elif response.status_code == 500:
            self._console.exception(cons.ERR_SERVER_ERROR)
        else:
            self._console.exception(cons.ERR_UNKNOWN_ERROR)
        return retval

    def _get_org_tag(self):
        """Get a unique string which describes the organizaiton. This string
            can be used to tag AWS resources which are created during the
            deployment.
        """
        org_id = self._login_mgr.get_org_id()
        org_ip = self._login_mgr.get_api_ip()
        retval = 'org_{0}_ip_{1}'.format(org_id, org_ip)
        retval = retval.replace('.','_')
        retval = ''.join([x for x in retval if re.match(r'\w', x)])
        return retval

    def _print_step(self, in_step, in_message):
        """Print step number and message. Increment the step number.

        Args:
        in_step -- Step number.
        in_message -- Step description.
        Returns:
        Incremented step number.
        """
        self._console.nolog(_TAB)
        self._console.ok('Step ' + str(in_step) + ': ' + in_message)
        self._console.checkpoint()
        return in_step + 1

    def _write_keypair_file(self, in_keypair):
        """Write the AWS keypair to the keypair file.

            Args:
            in_keypair -- String with key pair from AWS.
            Returns:
            Full path to key pair file on local filesystem.
        """
        fullpath = self._get_keypair_path()
        fd = self._get_file_handle(fullpath, 'w')
        with fd as outfile:
            outfile.write(in_keypair)
            fd.close()
            os.chmod(fullpath, _KEYPAIR_FILE_PERMS)
            self._console.ok(_TAB + awscons.TXT_AWS_KEYPAIR_FILE_WRITTEN +
                             fullpath)
        return fullpath

    def _get_keypair_path(self):
        """Get the full path of the keypair file used to save the keypair.

            Filename includes a timestamp.

            Returns:
            String with the full path to the keypair file."""
        retval = os.path.join(os.getcwd(),
                              _OUTPUT_DIR,
                              (_KEYPAIR_FILE_PREFIX + _TIMESTAMP +
                               _KEYPAIR_FILE_SUFFIX))
        return retval

    def _get_file_handle(self, in_fullpath, in_mode='r'):
        """Get a handle to the temporary file that stores the session key.

            Args:
            in_fullpath -- Full path to file.
            in_mode -- 'r' to open in read mode. 'w' to open in write mode.
            Returns:
            A valid file handle or None.
        """
        retval = None
        if not (in_mode is 'r' or in_mode is 'w'):
            self._console.exception('Internal: Incorrect file mode specified.')
        # create output dir if doesn't exist
        dir_path = os.path.dirname(in_fullpath)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # if keypair file already exists, use it.
        try:
            retval = open(in_fullpath, in_mode)
        except OSError:
            retval = None
        except (IOError, OSError):
            self._console.exception(awscons.ERR_AWS_KEYPAIR_FILE_CREATE +
                                    in_fullpath)
        return retval

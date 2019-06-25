# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

"""Constant definitions."""

# AWS security group ports
AWS_SEC_GROUP_PORTS = ['22', '8070', '8883']
# path to static file containing AWS Agent package
AWS_AGENT_URL = '/static/awsagent/latest.tar.gz'
# path to static file containing AWS MQTT Proxy package
AWS_PROXY_URL = '/static/awsproxy/proxy-latest.tar.gz'
# path to static file containing AWS MQTT Proxy package
AWS_ROOT_CERT_URL = '/static/awsproxy/mqtt-broker-root-ca.crt'
# name of AWS Proxy repo
AWS_PROXY_REPO = 'aws-mqtt-proxy'

# error messages for AWS
ERR_AWS_NOT_CONFIGURED = 'AWS CLI tool is not configured. Halting command.'
ERR_AWS_CLI_PERMISSIONS = 'AWS CLI tool does not have permissions. Please check your AWS credentials.'
ERR_AWS_QUERY_ACCOUNT = 'AWS account identifier not retrieved.'
ERR_AWS_REPLY_MISSING_DATA = 'Missing data from reply to AWS CLI command. Missing: '
ERR_AWS_SEC_GROUP_EXISTS = 'AWS Security Group already exists.'
ERR_AWS_SEC_GROUP_NOT_EXISTS = 'AWS Security Group does not exist.'
ERR_AWS_SEC_GROUP_TOO_MANY = 'Too many Security Groups with the same name found.'
ERR_AWS_KEYPAIR_FILE_CREATE = 'Error creating AWS EC2 key pair file: '
ERR_AWS_KEYPAIR_FILE_READ = 'Error reading AWS EC2 key pair file: '
ERR_AWS_INVALID_KEYPAIR_NAME = 'Invalid name for EC2 key pair.'
ERR_AWS_CANNOT_FIND_INSTANCE = 'Cannot find EC2 instance: '
ERR_AWS_CANNOT_GET_IP_ADDRESS = 'Cannot retrieve the IP address of EC2 instance: '
ERR_AWS_CANNOT_GET_ACCOUNT_TYPE = 'Cannot retrieve the AWS account type.'
ERR_AWS_NOT_VPC_ACCOUNT = 'AWS account must support EC2 VPCs in order to run the required EC2 instance type.'
ERR_AWS_CANNOT_GET_VPC_LIST = 'Cannot retrieve the list of VPCs for AWS Region.'
ERR_AWS_NO_DEFAULT_VPC = 'No default VPC and Subnet defined for the AWS Region. The EC2 instance type requires that these are defined. Please define and retry or do not use the automatic deployment and specify the Subnet Id.'
ERR_AWS_SUBNET_NOT_EXISTS = 'AWS EC2 Subnet does not exist.'
ERR_AWS_NO_EC2_IMAGE = 'Cannot find a suitable EC2 image.'
ERR_AWS_SHELL_COMMAND_FAILED = 'Shell command returned an error.'
ERR_AWS_CANNOT_FIND_IOT_ENDPOINT = 'Cannot find AWS IoT Endpoint'
ERR_AWS_LAMBDA_INVOKE_FAILED = 'Failed to invoke the AWS Lambda function.'
ERR_AWS_CANNOT_FIND_JAR_FILE = 'Cannot find the AWS Agent JAR file within tar file.'

# aws deploy dialogs
TXT_AWS_SEC_GROUP_CREATED = 'AWS Security Group created. Id: '
TXT_AWS_SEC_GROUP_MATCH_FOUND = 'Existing AWS Security Group(s) for the AWS Agent EC2 instance have been found.'
TXT_AWS_PORT_OPENED = 'AWS Security Group inbound TCP port opened: '
TXT_AWS_KEYPAIR_FILE_WRITTEN = 'AWS Key Pair file saved: '
TXT_AWS_EXIT_EARLY = 'User terminated the command early.'
TXT_AWS_IP_ADDRESS_RETRY = 'IP address not available. Must retry....'
TXT_AWS_WAIT_INSTANCE_RUNNING = 'Waiting on EC2 instance to start running.'
TXT_AWS_WAIT_INSTANCE_TERMINATE = 'Waiting on EC2 instance to terminate....'
TXT_AWS_INSTANCE_NOW_TERMINATED = 'EC2 instance now terminated.'
TXT_AWS_PORT_NOT_OPEN = 'Required port not open in AWS Security Group.'
TXT_AWS_PORT_REFUSED_OPEN_PORT = 'User declined to open a required port. AWS Agent may not function correctly.'
TXT_AWS_USING_DEFAULT_VPC = 'Default Subnet and Default VPC will be used for EC2 instance creation.'
TXT_AWS_EC2_VPC_ACCOUNT_AVAILABLE = 'AWS account has VPC enabled and available for AWS Region.'

# amazon aws id of canonical
AWS_ID_CANONICAL = '099720109477'

# aws resource tag name
AWS_RES_TAG_NAME = 'UniquidCliDeployAws'

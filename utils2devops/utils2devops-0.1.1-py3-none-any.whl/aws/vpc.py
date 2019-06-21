import boto3

from utils2devops.aws import Vpc

"""
Aws configuration iiles should be present:
 ~/.aws/credentials
 ~/.aws/config
"""


def list_vpcs(name, state=None):
    """This function does something in aws vpcs. TODO DOC

    :param name: The name to use.
    :type name: str.
    :param state: Current state to be in.
    :type state: bool.
    :returns: int -- the return code.
    :raises: AttributeError, KeyError

    """
    session = boto3.Session(profile_name='terraform')
    client = session.client(service_name='ec2', region_name='us-east-2')
    elements = client.describe_vpcs()

    for element in elements['Vpcs']:
        x = Vpc(element['VpcId'])
        x.cidr_block = element['CidrBlock']
        att = client.describe_vpc_attribute(
            VpcId=element['VpcId'], Attribute='enableDnsHostnames')
        x.enable_dns_hostnames = att['EnableDnsHostnames']['Value']
        att = client.describe_vpc_attribute(
            VpcId=element['VpcId'], Attribute='enableDnsSupport')
        x.enable_dns_support = att['EnableDnsSupport']['Value']
        x.instance_tenancy = element['InstanceTenancy']
        x.tags = element['Tags']
        print(x)

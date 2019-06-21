import boto3

from utils2devops.aws import Subnet

"""
Aws configuration iiles should be present:
 ~/.aws/credentials
 ~/.aws/config
"""


def list_subnets(name, state=None):
    """This function does something in aws subnets. TODO DOC

    :param name: The name to use.
    :type name: str.
    :param state: Current state to be in.
    :type state: bool.
    :returns: int -- the return code.
    :raises: AttributeError, KeyError

    """
    session = boto3.Session(profile_name='terraform')
    client = session.client(service_name='ec2', region_name='us-east-2')
    elements = client.describe_subnets()

    for element in elements['Subnets']:
        x = Subnet(element['SubnetId'])
        x.vpc_id = element['VpcId']
        x.cidr_block = element['CidrBlock']
        x.availability_zone = element['AvailabilityZone']
        x.map_public_ip_on_launch = element['MapPublicIpOnLaunch']
        filters = [{'Name': 'resource-id', 'Values': [element['SubnetId']]}]
        tags = client.describe_tags(Filters=filters)
        x.tags = tags['Tags']
        print(x)

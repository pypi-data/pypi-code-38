import boto3

from utils2devops.aws import NetworkAcl, Gress

"""
Aws configuration iiles should be present:
 ~/.aws/credentials
 ~/.aws/config
"""


def list_network_acls(profile_name: str = 'terraform',
                      region_name: str = 'us-east-2') -> [str]:
    """This function list all AWS API Gateways how can access the profile
    profile_name in the AWS region region_name.

    :param profile_name: The AWS profile name to use.
    :param region_name: The AWS region to use.
    :returns: list of line or empty if nothing.
    :raises: AttributeError, KeyError

    """
    session = boto3.Session(profile_name=profile_name)
    client = session.client(service_name='ec2', region_name=region_name)
    elements = client.describe_network_acls()

    _lines = []
    if 'NetworkAcls' not in elements:
        return _lines
    for element in elements['NetworkAcls']:
        x = NetworkAcl(element['NetworkAclId'])
        x.vpc_id = element['VpcId']
        x.subnet_ids = []
        for p in element['Associations']:
            x.subnet_ids.append(p['SubnetId'])
        for p in element['Entries']:
            if p['RuleNumber'] != 32767:
                gress = Gress()
                gress.rule_no = p['RuleNumber']
                gress.action = p['RuleAction']
                gress.cidr_block = p['CidrBlock']
                gress.protocol = p['Protocol']
                if 'PortRange' in p:
                    gress.from_port = p['PortRange']['From']
                    gress.to_port = p['PortRange']['To']
                else:
                    gress.from_port = 0
                    gress.to_port = 0
                if p['Egress']:
                    x.egress.append(gress)
                else:
                    x.ingress.append(gress)
        x.tags = element['Tags']
        _lines.append(x)

    return _lines


if __name__ == '__main__':
    lines = list_network_acls()
    print(*lines)

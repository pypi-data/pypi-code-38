import boto3

from utils2devops.aws import RouteTable

"""
Aws configuration iiles should be present:
 ~/.aws/credentials
 ~/.aws/config
"""


def list_route_tables(name, state=None):
    """This function does something in aws route_tables. TODO DOC

    :param name: The name to use.
    :type name: str.
    :param state: Current state to be in.
    :type state: bool.
    :returns: int -- the return code.
    :raises: AttributeError, KeyError

    """
    session = boto3.Session(profile_name='terraform')
    client = session.client(service_name='ec2', region_name='us-east-2')
    elements = client.describe_route_tables()

    for element in elements['RouteTables']:
        filters = [{'Name': 'vpc-id', 'Values': [element['VpcId']]}]
        atts = client.describe_route_tables(Filters=filters)
        for att in atts['RouteTables']:
            x = RouteTable(att['RouteTableId'])
            x.vpc_id = element['VpcId']
            for route in att['Routes']:
                if route['GatewayId'] != 'local':
                    x.route['cidr_block'] = route['DestinationCidrBlock']
                    x.route['gateway_id'] = route['GatewayId']
            x.tags = att['Tags']
            print(x)


if __name__ == '__main__':
    list_route_tables('')

import boto3


def lookup_resource(resource_name):
    client = boto3.client('ssm')
    response = client.get_parameter(
        Name=resource_name
    )
    parameter = response['Parameter']
    return parameter['Value']

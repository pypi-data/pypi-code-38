__author__ = 'rcj1492'
__created__ = '2017.06'
__licence__ = 'MIT'

'''
get file from aws instance
TODO: get from other platforms (bluemix, azure, gcp)
'''

_get_details = {
    'title': 'get',
    'description': 'Copies a file or folder on remote host to working directory on localhost. Get is currently only available for the Amazon ec2 platform.\n\nPLEASE NOTE: get uses the service name specified in the docker-compose.yaml configuration file to determine which instance to connect to. The service name will be added as part of ```lab launch ec2```. Otherwise, a tag must be added to the instance with key "Services" and value "<service1>,<service2>".',
    'help': 'copy a file from remote host through scp',
    'benefit': 'Copies remote files to your local machine.'
}

from pocketlab.init import fields_model

def get(file_path, platform_name, service_option, environ_type='', resource_tags='', region_name='', verbose=True, overwrite=False):
    
    title = 'get'

# validate inputs
    if isinstance(service_option, str):
        if service_option:
            service_option = [service_option]
    input_fields = {
        'file_path': file_path,
        'service_option': service_option,
        'verbose': verbose,
        'platform_name': platform_name,
        'environ_type': environ_type,
        'resource_tags': resource_tags
    }
    for key, value in input_fields.items():
        if value:
            object_title = '%s(%s=%s)' % (title, key, str(value))
            fields_model.validate(value, '.%s' % key, object_title)

# determine service name
    service_name = ''
    if service_option:
        service_name = service_option[0]

# construct path to service root
    from pocketlab.methods.service import retrieve_service_root
    if service_name:
        service_insert = '"%s"' % service_name
        service_root = retrieve_service_root(service_name)
    else:
        service_insert = 'in working directory'
        service_root = './'

# retrieve service configurations
    from pocketlab.methods.service import retrieve_service_config
    service_title = '%s %s' % (title, platform_name)
    service_config, service_name = retrieve_service_config(service_root, service_name, service_title)

# handle ec2 platform
    if platform_name == 'ec2':

    # check for dependencies
        from pocketlab.methods.dependencies import import_boto3
        import_boto3('ec2 platform')

    # retrieve aws config
        from pocketlab import __module__
        from jsonmodel.loader import jsonLoader
        from jsonmodel.validators import jsonModel
        from pocketlab.methods.validation import validate_platform
        aws_schema = jsonLoader(__module__, 'models/aws-config.json')
        aws_model = jsonModel(aws_schema)
        aws_config = validate_platform(aws_model, service_root, service_name, '.lab')

    # retrieve instance details from ec2
        from pocketlab.methods.aws import initialize_clients
        ec2_client, ssh_client, instance_details = initialize_clients(
            aws_cred=aws_config,
            service_name=service_name, 
            service_insert=service_insert, 
            service_root=service_root, 
            region_name=region_name, 
            environment_type=environ_type, 
            resource_tags=resource_tags, 
            verbose=verbose
        )

    # get file over scp
        ssh_client.get(file_path, synopsis=False, overwrite=overwrite)

# handle heroku error
    elif platform_name == 'heroku':
        raise Exception('It is not possible to connect to instances on heroku.')

    exit_msg = 'Transfer of %s from %s instance with service %s complete' % (file_path, platform_name, service_insert)

    return exit_msg
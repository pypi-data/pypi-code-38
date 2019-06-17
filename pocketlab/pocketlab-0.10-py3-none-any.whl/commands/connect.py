__author__ = 'rcj1492'
__created__ = '2017.06'
__license__ = 'MIT'

'''
connect to aws instance
TODO: connect to other platforms (bluemix, azure, gcp)
'''

_connect_details = {
    'title': 'connect',
    'description': 'Opens up a direct ssh connection to remote host. Connect is currently only available to the Amazon ec2 platform and only on systems running ssh natively. To connect to a remote host on Windows, try using Putty instead.\n\nPLEASE NOTE: connect uses the service name and other tags associated with remote instances to determine which instance to connect to. The service name will be added as part of ```lab launch ec2```. Otherwise, a tag must be added to the instance with key "Services" and value "<service1>,<service2>".',
    'help': 'connects to remote host through ssh',
    'benefit': 'Edit settings on remote host manually.'
}

from pocketlab.init import fields_model

def connect(platform_name, service_option, environ_type='', resource_tags='', region_name='', verbose=True):

    title = 'connect'

# validate inputs
    if isinstance(service_option, str):
        if service_option:
            service_option = [service_option]
    input_fields = {
        'service_option': service_option,
        'verbose': verbose,
        'platform_name': platform_name,
        'environ_type': environ_type,
        'resource_tags': resource_tags,
        'region_name': region_name
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
#     from pocketlab.methods.service import retrieve_service_name
#     service_name = retrieve_service_name(service_root)
#     if not service_name:
#         try:
#             from pocketlab.methods.service import retrieve_service_config
#             service_title = '%s %s' % (title, platform_name)
#             service_config, service_name = retrieve_service_config(service_root, service_name, service_title)
#         except Exception as err:
#             if str(err).find('docker-compose.yaml does not exist in'):
#                 raise ValueError('Working directory needs a service name or docker-compose.yaml file.\nTry: "lab home <service_name>" or "lab init <service_name" in working directory.')
#             else:
#                 raise

# handle ec2 platform
    if platform_name == 'ec2':

    # check for dependencies
        from pocketlab.methods.dependencies import import_boto3
        import_boto3('ec2 platform')
        from platform import uname
        local_os = uname()
        if local_os.system in ('Windows'):
            raise Exception('%s command is not available for Windows.\nTry using instead: putty.exe' % title)

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
    
    # open terminal
        ssh_client.terminal()

# handle heroku error
    elif platform_name == 'heroku':
        raise Exception('It is not possible to connect to instances on heroku.')

    exit_msg = 'Code is growing like gangbusters.'

    return exit_msg
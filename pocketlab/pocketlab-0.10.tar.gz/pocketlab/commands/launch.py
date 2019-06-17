__author__ = 'rcj1492'
__created__ = '2018.02'
__license__ = 'MIT'

_launch_details = {
    'title': 'Launch',
    'description': 'Launches an instance or an auto-scaling group on a remote platform. Launch is currently only available for the ec2 platform. To create an configuration file to launch an ec2 instance, run ```lab init --ec2``` and adjust the settings appropriately.',
    'help': 'starts instances on remote platform',
    'benefit': 'Launch creates one or more remote instances to host services.'
}

from pocketlab.init import fields_model

def launch(platform_name, service_option, region_name='', verbose=True, overwrite=False):

    title = 'launch'

# ingest service option
    if isinstance(service_option, str):
        if service_option:
            service_option = [service_option]

# validate inputs
    input_fields = {
        'platform_name': platform_name,
        'service_option': service_option,
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
    
# catch heroku error
    exit_msg = ''
    if platform_name == 'heroku':
        raise ValueError('It is not possible to launch an instance on heroku.\nTry: lab deploy heroku')

# TODO deploy to auto-scaling group / elb (requires construction of ec2 image)
    elif platform_name == 'asg':
        pass
    
# process ec2 instance
    elif platform_name == 'ec2':
    
    # # what is the state of the system that is trying to be achieved?
        # single instance vs. load balancer/auto-scaling group
        # create/replace instance vs. update existing instance
        # web routing vs closed ip
        # fresh account vs. account configuration exists
        # add/subtract services vs update services
        # ephemeral vs persistent data (service that backs-up data)
        # single container vs multiple containers

    # check for library dependencies
        from pocketlab.methods.dependencies import import_boto3
        import_boto3('ec2 platform')

    # retrieve aws cred and ec2 config
        from pocketlab import __module__
        from jsonmodel.loader import jsonLoader
        from jsonmodel.validators import jsonModel
        from pocketlab.methods.validation import validate_platform
        from pocketlab.methods.aws import compile_schema, compile_instances
        aws_schema = jsonLoader(__module__, 'models/aws-config.json')
        aws_model = jsonModel(aws_schema)
        aws_cred = validate_platform(aws_model, service_root, service_name, '.lab')
        ec2_schema = compile_schema('models/ec2-config.json')
        ec2_model = jsonModel(ec2_schema)
        ec2_config = validate_platform(ec2_model, service_root, service_name)

    # construct variables
        msg_insert = 'working directory'
        if service_name:
            msg_insert = 'root directory for "%s"' % service_name
        ec2_insert = 'service %s deployed to ec2.' % service_insert

    # construct ec2 client
        ec2_cred = {
            'access_id': aws_cred['aws_access_key_id'],
            'secret_key': aws_cred['aws_secret_access_key'],
            'region_name': aws_cred['aws_default_region'],
            'owner_id': aws_cred['aws_owner_id'],
            'user_name': aws_cred['aws_user_name'],
            'verbose': verbose
        }
        from pocketlab.methods.aws import construct_client_ec2
        if not region_name:
            if 'region_name' in ec2_config.keys():
                region_name = ec2_config['region_name']
        ec2_client = construct_client_ec2(ec2_cred, region_name)

    # verify instance name collision
        old_instance = ''
        tag_list = []
        for tag in ec2_config['tag_list']:
            if tag['key'] == 'Name':
                tag_list.append(tag['value'])
        if tag_list:
            name_tag = tag_list[0]
            instance_list = ec2_client.list_instances(tag_values={ 'Name': name_tag })
            for instance_id in instance_list:
                break_off = False
                ec2_details = ec2_client.read_instance(instance_id)
                if ec2_details['tags']:
                    for tag in ec2_details['tags']:
                        if tag['key'] == 'Name':
                            if tag['value'] == name_tag:
                                if not overwrite:
                                    raise Exception('Instance with name "%s" already exists.\nTo replace, add "-f"' % name_tag)
                                else:
                                    old_instance = instance_id
                                    break_off = True
                                    break
                if break_off:
                    break

    # TODO verify elastic ip and possible assignment collision

    # create new instance
        instance_kwargs = {}
        for key, value in ec2_config.items():
            if key not in ('region_name', 'elastic_ip', 'install_scripts'):
                instance_kwargs[key] = value
        new_instance = ec2_client.create_instance(**instance_kwargs)
        exit_msg = 'Instance %s launched on ec2.' % new_instance
    
    # TODO reassign elastic ip
    # https://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.associate_address
    
    # TODO remove existing image
    
    # run scripts
        install_scripts = []
        if 'install_scripts' in ec2_config.keys():
            install_scripts = ec2_config['install_scripts']
        if install_scripts:

        # wait for instance to be available
            ec2_client.check_instance_status(new_instance)
    
        # initialize ssh client
            from pocketlab.methods.aws import establish_connection
            ssh_client = establish_connection(
                aws_cred=aws_cred,
                instance_id=new_instance,
                pem_file=ec2_config['pem_file'],
                service_insert=service_insert,
                region_name=region_name,
                verbose=verbose
            )

        # install libraries
            ssh_client.script(install_scripts)
            exit_msg = 'Instance %s ready to deploy services on ec2.' % new_instance
    
    return exit_msg
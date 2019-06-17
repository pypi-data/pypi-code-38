__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = 'MIT'

'''
update the .ignore file
update the docker-compose.yaml file
update the setup.py file
TODO: check dependencies and alert new versions
'''

_update_details = {
    'title': 'Update',
    'description': 'Updates the configuration files for a service. When a package and platform are specified, update adds (or updates) the service to the configuration files for the package on the platform. Otherwise, update only updates the local configuration files for a service with the latest pocketlab configurations.',
    'help': 'updates the config files for a service',
    'benefit': 'Keeps your services up-to-date with the latest configurations.'
}

from pocketlab.init import fields_model

def update(package_option, platform_option, service_option, environ_type='', region_name='', resource_tags='', print_terminal='', all_services=False, ssl=True, verbose=True):

    ''' 
        a method to update a software configuration on remote host with service details

    :param package_option: [optional] string with name of software to add to remote platform
    :param platform_option: [optional] string with name of remote platform to host service
    :param service_option: [optional] string with name of service in lab registry
    :param environ_type: [optional] string with environment of instance (dev, test, prod, asg)
    :param region_name: [optional] string with name of remote provider region
    :param resource_tags: [optional] comma separated string with tags on remote platform
    :param print_terminal: [optional] boolean to enable printout of all ssh commands
    :param all_services: [optional] boolean to update all local service repositories
    :param ssl: [optional] boolean to disable ssl routing on reverse proxy
    :param verbose: [optional] boolean to disable process reporting
    :return: string with exit message
    '''

    title = 'update'
    
    # ingest service option
    if isinstance(service_option, str):
        if service_option:
            service_option = [service_option]
    if isinstance(package_option, str):
        if package_option:
            package_option = [package_option]
    if isinstance(platform_option, str):
        if platform_option:
            platform_option = [platform_option]

    # validate inputs
    input_fields = {
        'package_option': package_option,
        'service_option': service_option,
        'platform_option': platform_option,
        'environ_type': environ_type,
        'region_name': region_name,
        'resource_tags': resource_tags
    }
    for key, value in input_fields.items():
        if value:
            object_title = '%s(%s=%s)' % (title, key, str(value))
            fields_model.validate(value, '.%s' % key, object_title)

    # validate package and platform
    local_update = False
    if package_option and not platform_option:
        raise ValueError('Update requires a platform if the package option is specified.')
    elif platform_option and not package_option:
        raise ValueError('Update requires a package if the platform option is specified.')
    elif not platform_option and not package_option:
        local_update = True

    # determine service name
    service_name = ''
    service_list = []
    if service_option:
        service_list = service_option
        service_name = service_option[0]
    platform_name = ''
    if platform_option:
        platform_name = platform_option[0]
    package_name = ''
    if package_option:
        package_name = package_option[0]

    # handle local configuration updates
    if local_update:

        # define test ignore
        def _test_ignore(text):
            import re
            lab_test = re.findall('\\?\.lab', text)
            node_test = re.findall('\nnode_modules/', text)
            if lab_test:
                return 'service'
            elif node_test:
                return 'node'
            return 'python'

        # define update process
        def _apply_update(root_path, service_name=''):
    
        # construct message
            from os import path
            msg_insert = 'local service'
            if service_name:
                msg_insert = 'service "%s"' % service_name
            setup_path = path.join(root_path, 'setup.py')
            if path.exists(setup_path):
                msg_insert = msg_insert.replace('service', 'module')
    
        # update vcs ignore
            import hashlib
            from pocketlab.methods.vcs import load_ignore
            from pocketlab.methods.vcs import merge_ignores
            vcs_files = {
                'git': {
                    'path': path.join(root_path, '.gitignore'),
                    'name': '.gitignore',
                    'vcs': 'git'
                },
                'mercurial': {
                    'path': path.join(root_path, '.hgignore'),
                    'name': '.hgignore',
                    'vcs': 'mercurial'
                },
                'npm': {
                    'path': path.join(root_path, '.npmignore'),
                    'name': '.npmignore',
                    'vcs': 'git'
                },
                'docker': {
                    'path': path.join(root_path, '.dockerignore'),
                    'name': '.dockerignore',
                    'vcs': 'docker'
                }
            }
            for key, value in vcs_files.items():
                if path.exists(value['path']):
                    old_text = open(value['path']).read()
                    old_hash = hashlib.sha1(old_text.encode('utf-8')).hexdigest()
                    ignore_type = _test_ignore(old_text)
                    template_text = load_ignore(vcs=value['vcs'], type=ignore_type)
                    new_text = merge_ignores(old_text, template_text)
                    new_hash = hashlib.sha1(new_text.encode('utf-8')).hexdigest()
                    if old_hash != new_hash:
                        with open(value['path'], 'wt') as f:
                            f.write(new_text)
                            f.close()
                        if verbose:
                            print('%s file for %s updated.' % (value['name'], msg_insert))
    
        # update setup.py
            setup_path = path.join(root_path, 'setup.py')
            if path.exists(setup_path):
                from pocketlab.methods.config import update_setup
                old_text = open(setup_path).read()
                old_hash = hashlib.sha1(old_text.encode('utf-8')).hexdigest()
                new_text = update_setup(old_text, root_path)
                new_hash = hashlib.sha1(new_text.encode('utf-8')).hexdigest()
                if old_hash != new_hash:
                    with open(setup_path, 'wt', encoding='utf-8') as f:
                        f.write(new_text)
                        f.close()
                    if verbose:
                        print('setup.py file for %s updated.' % msg_insert)

        # construct update list
        from pocketlab.methods.service import retrieve_services
        update_list, msg_insert = retrieve_services(service_list, all_services)

        # apply updates
        for service in update_list:
            update_kwargs = {
                'root_path': service['path'],
                'service_name': service['name']
            }
            _apply_update(**update_kwargs)

        # modify service to module
        if msg_insert.find('local service') > -1:
            from os import path
            if path.exists('./setup.py'):
                msg_insert = msg_insert.replace('local service', 'local module')

    # handle remote package configuration update
    else:

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
        service_title = '%s %s %s' % (title, package_name, platform_name)
        service_config, service_name = retrieve_service_config(service_root, service_name, service_title)

        # catch heroku error
        exit_msg = ''
        if platform_name == 'heroku':
            raise ValueError('It is not possible to update packages on a heroku instance.\nTry: lab deploy heroku')
    
        # catch auto-scaling group error
        elif platform_name == 'asg':
            raise ValueError('It is not possible to update packages on a running auto-scaling configuration.\nTry: lab update %s --env asg' % service_title)
    
        # process ec2 instance
        elif platform_name == 'ec2':

            # check for library dependencies
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

            # define ssh script printer
            def print_script(command, message, error=''):
                if verbose:
                    if print_terminal:
                        print(message)
                    else:
                        print(message, end='', flush=True)
                try:
                    response = ssh_client.script(command)
                    if verbose:
                        if not print_terminal:
                            print('done.')
                except:
                    if verbose:
                        print('ERROR.')
                    if error:
                        raise Exception(error)
                    else:
                        raise
                return response

            # disable normal ssh client printing
            if not print_terminal:
                ssh_client.ec2.iam.verbose = False

            # retrieve scripts for image type
            from pocketlab.methods.config import retrieve_scripts
            image_details = ec2_client.read_image(instance_details['image_id'])
            package_details = retrieve_scripts(package_name, image_details['name'])
            package_check = package_details.get('check','')
            package_system = package_details.get('system', {})

            # verify installation
            if package_check:
                sys_message = 'Verifying %s installed on ec2 image ... ' % package_name
                sys_error = 'Package %s is not installed on ec2 instance %s.\nTry: lab install %s ec2' % (package_name, instance_details['instance_id'], package_name)
                print_script(package_check, sys_message, sys_error)

            # verify package in system boot sequence
            if package_system:
                sys_message = 'Verifying %s is enabled ... ' % package_name
                enabled_text = print_script(package_system['enabled'], sys_message)
                if not enabled_text:
                    sys_message = 'Enabling %s on system startup ... ' % package_name
                    print_script(package_system['enable'], sys_message)

            # add reverse proxies
            service_labels = service_config.get('labels',{})
            if service_labels:

                # determine domains port mapping
                domain_map = {}
                import re
                for key, value in service_labels.items():
                    if not re.findall('[^\d]+', value):
                        domain_name = ''
                        cert_name = ''
                        domain_segments = key.split('.')
                        segment_count = 0
                        while domain_segments:
                            if domain_name:
                                domain_name += '.'
                                cert_name += '.'
                            segment_name = domain_segments.pop()
                            domain_name += segment_name
                            if segment_count < 2:
                                cert_name += segment_name
                            segment_count += 1
                        domain_map[domain_name] = {
                            'domain': domain_name,
                            'port': int(value),
                            'cert': cert_name
                        }

                if print_terminal:
                    domain_message = 'Domain map associated with service %s:\n%s' % (service_insert, domain_map)
                    print(domain_message)

                # handle certbot
                if package_name == 'certbot':

                    # check if nginx is running
                    restart_insert = '--debug'
                    sys_command = 'sudo service nginx status'
                    sys_message = 'Verifying reverse proxy is running ... '
                    running_text = print_script(sys_command, sys_message)
                    if running_text.find('active (running)') > -1:
                        restart_insert += ' --pre-hook "service nginx stop" --post-hook "service nginx start"'

                    # retrieve certbot information
                    sys_command = 'certbot-auto certificates --standalone --no-self-upgrade %s' % restart_insert
                    sys_message = 'Retrieving certificate information ... '
                    certbot_text = print_script(sys_command, sys_message)

                    # parse renewal domains in certbot information
                    from time import time
                    from pocketlab.methods.certbot import extract_domains
                    certbot_domains = extract_domains(certbot_text)
                    certbot_map = {}
                    renew_certs = {}
                    renew_time = time() + 29 * 24 * 3600
                    for domain in certbot_domains:
                        if not domain['cert'] in certbot_map.keys():
                            certbot_map[domain['cert']] = []
                        certbot_map[domain['cert']].append(domain['domain'])
                        if domain['expires'] < renew_time:
                            renew_certs[domain['cert']] = True

                    # add new domains to certbot map
                    initial_certs = {}
                    update_certs = []
                    for key, value in domain_map.items():
                        if not key in certbot_map.keys():
                            initial_certs[key] = []
                            initial_certs[key].append(key)
                            initial_certs[key].append('www.%s' % key)
                        elif key in initial_certs.keys():
                            pass
                        elif not value['domain'] in certbot_map[key]:
                            certbot_map[key].append(value['domain'])
                            update_certs.append(key)

                    # register certbot information
                    initial_commands = []
                    for key, value in initial_certs.items():
                        initial_command = 'certbot-auto certonly --standalone --no-self-upgrade -d %s %s' % (','.join(value), restart_insert)
                        initial_commands.append(initial_command)
                    if initial_commands:
                        raise Exception('Registration of a new ssl certificate using CertBot must be done manually.\nTry: lab connect ec2\n%s' % '\n'.join(initial_commands))

                    # update certbot information
                    update_commands = []
                    certbot_current = True
                    for cert in update_certs:
                        certbot_command = 'certbot-auto certonly --standalone --no-self-upgrade -n --cert-name %s -d %s %s' % (cert, ','.join(certbot_map[cert]), restart_insert)
                        update_commands.append(certbot_command)
                    if update_commands:
                        certbot_current = False
                        sys_message = 'Updating ssl certificate information ... '
                        print_script(update_commands, sys_message)

                    # renew certbot information
                    if set(renew_certs) - set(update_certs):
                        certbot_current = False
                        sys_command = 'certbot-auto renew --standalone --no-self-upgrade %s' % restart_insert
                        sys_message = 'Renewing ssl certificates ... '
                        print_script(sys_command, sys_message)

                    # report no changes
                    if certbot_current:
                        print('All ssl certificates are up-to-date.')

                # handle nginx
                elif package_name == 'nginx' and print_terminal:

                    # retrieve nginx information
                    nginx_path = '/etc/nginx/nginx.conf'
                    sys_command = 'sudo cat %s' % nginx_path
                    sys_message = 'Reading existing nginx configuration ... '
                    nginx_text = print_script(sys_command, sys_message)

                    # update nginx information
                    from pocketlab.methods.nginx import compile_nginx, extract_servers
                    nginx_servers = extract_servers(nginx_text)
                    server_map = {}
                    for server in nginx_servers:
                        server_map[server['domain']] = server
                    for key, value in domain_map.items():
                        server_map[key] = value
                    server_list = []
                    for key, value in server_map.items():
                        server_list.append(value)
                    nginx_updated = compile_nginx(server_list)
                    if ssl:
                        nginx_updated = compile_nginx(
                            server_list=server_list, 
                            ssl_port=443,
                            ssl_gateway='certbot'
                        )

                    # replace nginx conf and restart nginx on ec2 image
                    from os import path, remove
                    from time import time
                    nginx_name = 'nginx%s.conf' % int(time())
                    nginx_temp = path.relpath(path.join(service_root, nginx_name))
                    with open(nginx_temp, 'wt') as f:
                        f.write(nginx_updated)
                        f.close()
                    if verbose:
                        print('Updating nginx configurations on ec2 image ... ', end='', flush=True)
                    try:
                        ssh_client.put(nginx_temp, nginx_path, overwrite=True)
                        ssh_client.script('sudo service nginx restart')
                        if verbose:
                            print('done.')
                    except:
                        if verbose:
                            print('ERROR.')
                        remove(nginx_temp)
                        raise

                    # report changes
                    if print_terminal:
                        nginx_comparison = 'Old nginx configuration:\n%s\nNew nginx configuration:\n%s' % (nginx_text, nginx_updated)
                        print(nginx_comparison)

                    # TODO remove port/container from reverse proxy

        msg_insert = '%s on %s for service %s' % (package_name, platform_name, service_insert)

    # construct exit message
    exit_msg = 'Configurations for %s have been updated.' % msg_insert

    return exit_msg

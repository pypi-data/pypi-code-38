__author__ = 'rcj1492'
__created__ = '2016.03'
__license__ = 'MIT'

'''
starts services in docker containers
'''

_start_details = {
    'title': 'Start',
    'description': 'Initiates a container with the Docker image for one or more services. Unless overridden by flags, lab automatically adds the environmental variables SYSTEM_IP, SYSTEM_ENVIRONMENT, SYSTEM_PLATFORM and PUBLIC_IP of the host machine to the container.',
    'help': 'initiates Docker containers for services',
    'benefit': 'Makes services available on localhost'
}

from pocketlab.init import fields_model

def start(service_list, verbose=True, virtualbox='default', environment_type='dev', print_terminal=''):

    title = 'start'

# validate inputs
    if isinstance(service_list, str):
        if service_list:
            service_list = [service_list]
    input_fields = {
        'service_list': service_list,
        'verbose': verbose,
        'virtualbox': virtualbox,
        'environment_type': environment_type,
        'print_terminal': print_terminal
    }
    for key, value in input_fields.items():
        if value:
            object_title = '%s(%s=%s)' % (title, key, str(value))
            fields_model.validate(value, '.%s' % key, object_title)

# validate installation of docker
    from labpack.platforms.docker import dockerClient
    docker_client = dockerClient(virtualbox_name=virtualbox, verbose=verbose)

# verbosity
    if verbose:
        print('Checking service configurations...', end='', flush=True)

# construct list of paths to services
    from pocketlab.methods.service import retrieve_services
    start_list, msg_insert = retrieve_services(service_list)

# retrieve local docker images
    docker_images = docker_client.images()

# construct lab list
    lab_list = []
    port_list = []
    
# validate each service
    for details in start_list:
    
    # validate docker-compose files
        from pocketlab.methods.service import retrieve_service_config
        service_config, service_name = retrieve_service_config(details['path'], details['name'], 'start')
        details['config'] = service_config
        details['name'] = service_name

    # construct message insert
        msg_insert = 'working directory'
        if service_name:
            msg_insert = 'root directory for "%s"' % service_name
        compose_insert = 'docker-compose.yaml file in %s' % msg_insert

    # validate image exists in local docker repository
        from pocketlab.methods.validation import validate_image
        details['repo'], details['tag'] = validate_image(details['config'], docker_images, service_name)

    # retrieve list of docker containers
        docker_containers = docker_client.ps()

    # validate container alias does not already exist
        if 'container_name' in details['config'].keys():
            container_alias = details['config']['container_name']
        else:
            container_alias = details['name']
        container_exists = False
        for alias in docker_containers:
            if container_alias == alias['NAMES'].split()[0]:
                container_exists = True
        if container_exists:
            if not print_terminal:
                raise ValueError('A container already exists for alias "%s".\nTry first: "docker rm -f %s"' % (container_alias, container_alias))
        details['alias'] = container_alias

    # validate ports are available
        from pocketlab.methods.service import compile_ports
        service_ports = compile_ports(details['config'])
        for i in range(len(service_ports)):
            port = service_ports[i]
            if port in port_list:
                raise ValueError('Value "%s" for field ports[%s] in %s is already mapped to another container.' % (str(port), str(i), compose_insert))
            else:
                try:
                    docker_client.command('lsof -Pi :%s -sTCP:LISTEN -t' % port)
                    raise ValueError('Value "%s" for field ports[%s] in %s is already mapped to a local process.' % (str(port), str(i), compose_insert))
                except:
                    pass
                port_list.append(port)

    # print progress for each service
        lab_list.append(details)
        if verbose:
            print('.', end='', flush=True)

# end validations
    if verbose:
        print(' done.')

# construct system environmental variables
    from os import environ
    system_ip = docker_client.ip()
    system_envvar = {
        'SYSTEM_IP': environ.get('SYSTEM_IP', system_ip),
        'SYSTEM_ENVIRONMENT': environ.get('SYSTEM_ENVIRONMENT', environment_type),
        'SYSTEM_PLATFORM': environ.get('SYSTEM_PLATFORM', 'localhost'),
        'PUBLIC_IP': environ.get('PUBLIC_IP', '')
    }
    if system_envvar['SYSTEM_PLATFORM'] == 'localhost':
        if docker_client.vbox_running:
            system_envvar['SYSTEM_PLATFORM'] = 'virtualbox'

# instantiate containers
    exit_msg = ''
    container_list = []
    for service in lab_list:
        container_list.append(service['alias'])

    # compile run command kwargs
        from pocketlab.methods.docker import compile_run_kwargs
        run_kwargs = compile_run_kwargs(
            service_config=service['config'],
            service_repo=service['repo'],
            service_alias=service['alias'],
            service_tag=service['tag'],
            service_path=service['path'],
            system_envvar=system_envvar
        )

    # print run command relative to workdir
        if print_terminal:

        # print run command
            from platform import uname
            local_os = uname()
            from pocketlab.methods.docker import compile_run_command
            run_command = compile_run_command(run_kwargs, os=local_os.system)
            print(run_command)
            return exit_msg

    # run docker run command
        else:
            docker_client.run(**run_kwargs)

    # report outcome
        port_msg = ''
        if 'ports' in service['config'].keys():
            if service['config']['ports']:
                port_string = ''
                for port in service['config']['ports']:
                    if port_string:
                        port_string += ','
                    port_split = port.split(':')
                    sys_port = port_split[0]
                    port_string += sys_port
                port_msg = ' at %s:%s' % (system_ip, port_string)
        service_msg = 'Container "%s" started%s' % (service['alias'], port_msg)
        if len(lab_list) > 1:
            if verbose:
                print(service_msg)
        else:
            exit_msg = service_msg

    # TODO consider ROLLBACK options for failure to start

    if len(lab_list) > 1:
        from labpack.parsing.grammar import join_words
        containers_string = join_words(container_list)
        exit_msg = 'Finished starting containers %s' % containers_string

    return exit_msg
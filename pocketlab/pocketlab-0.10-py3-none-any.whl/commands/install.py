__author__ = 'rcj1492'
__created__ = '2019.06'
__license__ = 'MIT'

_install_details = {
    'title': 'Install',
    'description': 'Installs a software package on a running instance on a remote platform. Install is currently only available for the ec2 platform and supports the following packages:\nnginx\ncertbot',
    'help': 'installs a software package on remote platform',
    'benefit': 'Install adds a fully-configured software package to a remote platform.'
}

from pocketlab.init import fields_model

def install(package_name, platform_name, service_option, environ_type='', region_name='', resource_tags='', print_terminal='', verbose=True):

    title = 'install'

    # ingest service option
    if isinstance(service_option, str):
        if service_option:
            service_option = [service_option]

    # validate inputs
    input_fields = {
        'package_name': package_name,
        'service_option': service_option,
        'platform_name': platform_name,
        'environ_type': environ_type,
        'region_name': region_name,
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

    # catch heroku error
    exit_msg = ''
    if platform_name == 'heroku':
        raise ValueError('It is not possible to install packages on a heroku instance.\nTry: lab deploy heroku')

    # catch auto-scaling group error
    elif platform_name == 'asg':
        raise ValueError('It is not possible to install packages on a running auto-scaling configuration.\nTry: lab install %s ec2 --env asg' % package_name)

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

        # retrieve scripts for image type
        from pocketlab.methods.config import retrieve_scripts
        image_details = ec2_client.read_image(instance_details['image_id'])
        install_details = retrieve_scripts(package_name, image_details['name'])
        install_scripts = install_details.get('scripts',[])
        install_dependencies = install_details.get('dependencies',[])
        install_check = install_details.get('check','')

        # construct dependency text
        dependency_text = ''
        if install_dependencies:
            dependency_text = '%s has the following dependencies:\n%s\n' % (package_name, '\n'.join(install_dependencies))

        # throw error if image is not supported
        package_installed = False
        if not install_scripts:
            raise ValueError('Installation of %s is not supported on ec2 AMI %s.' % (package_name, image_details['name']))

        # handle print to terminal request
        elif print_terminal:
            printout = 'To check for existing installation:\n  %s\n%s' % (install_check, dependency_text)
            if install_scripts:
                printout += 'To install %s run the following commands:\n  %s' % (package_name, '\n  '.join(install_scripts))
            print(printout)
            return exit_msg

        # verify installation
        elif install_check:
            try:
                ssh_client.script(install_check)
                package_installed = True
            except Exception as err:
                pass

        # handle package already installed
        if package_installed:
            exit_msg = 'Package %s is already installed on ec2 instance %s.' % (package_name, instance_details['instance_id'])

        # check for dependency installation
        elif install_dependencies:
            dependency_checks = []
            dependency_names = []
            for dependency in install_dependencies:
                dependency_details = retrieve_scripts(dependency, image_details['name'])
                if dependency_details.get('check',None):
                    dependency_checks.append(dependency_details.get('check'))
                    dependency_names.append(dependency)
            if verbose and dependency_checks:
                print('Checking that dependencies are installed ...')
            for i in range(len(dependency_checks)):
                try:
                    ssh_client.script(dependency_checks[i])
                except:
                    raise ValueError('%s not installed on ec2 instance %s.\n%s' % (dependency_names[i], instance_details['instance_id'], dependency_text))

                # TODO automatically install missing dependencies

            return exit_msg

        # run installation
        ssh_client.script(install_scripts)
        exit_msg = 'Package %s installed on ec2 instance %s.' % (package_name, instance_details['instance_id'])

    return exit_msg


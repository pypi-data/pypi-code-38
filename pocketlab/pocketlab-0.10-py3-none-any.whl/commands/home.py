__author__ = 'rcj1492'
__created__ = '2016.03'

from pocketlab.init import fields_model

_home_details = {
    'title': 'home',
    'description': 'Home adds the service name and working directory to the lab registry. On its first run, it also adds the alias \'home\' to bash config. As a result, on subsequent terminal sessions, typing ```$ home <service>``` will change the working directory to the folder registered under the service name. A quicklink to the workdir is also added by ```lab init <service>```',
    'help': 'creates a quicklink to workdir',
    'benefit': 'Home makes it easy to locate your services.',
    'epilog': ''
}

def home(service_name, print_path=False, service_path='', overwrite=False):

    '''
        a method to manage the local path information for a service

    :param service_name: string with name of service to add to registry
    :param print_path: [optional] boolean to retrieve local path of service from registry
    :param service_path: [optional] string with path to service root
    :param overwrite: [optional] boolean to overwrite existing service registration
    :return: string with local path to service
    '''

    title = 'home'

# validate inputs
    input_map = {
        'service_name': service_name,
        'service_path': service_path
    }
    for key, value in input_map.items():
        if value:
            object_title = '%s(%s=%s)' % (title, key, str(value))
            fields_model.validate(value, '.%s' % key, object_title)

# validate requirements
    # TODO boolean algebra method to check not both inputs

# resolve print path request
    if print_path:

    # retrieve service root
        from pocketlab.methods.service import retrieve_service_root
        command_context = 'Try running "lab home %s" first from its root.' % service_name
        service_root = retrieve_service_root(service_name, command_context)

    # return root path to bash command
        import sys
        exit_msg = 'Transport to "%s" underway.;%s' % (service_name, service_root)
        print(exit_msg)
        sys.exit()

# resolve service request

# validate existence of home alias
    from os import path
    from labpack.platforms.localhost import localhostClient
    localhost_client = localhostClient()
    home_alias = "alias home='function _home(){ lab_output=\"$(lab home --print $1)\"; IFS=\";\" read -ra LINES <<< \"$lab_output\"; echo \"${LINES[0]}\"; cd \"${LINES[1]}\"; };_home'"
    config_list = [localhost_client.bash_config, localhost_client.sh_config]
    for i in range(len(config_list)):
        if config_list[i]:
            if not path.exists(config_list[i]):
                with open(config_list[i], 'wt') as f:
                    f.write('# alias for pocketlab home command\n')
                    f.write(home_alias)
                    f.close()
            else:
                import re
                home_pattern = re.compile('alias home\=')
                lab_pattern = re.compile('alias home\=\'function _home\(\)\{\slab_output')
                home_match = False
                lab_match = False
                with open(config_list[i], 'rt') as f:
                    for line in f:
                        line = line.partition('#')[0]
                        line = line.rstrip()
                        if home_pattern.findall(line):
                            home_match = True
                        if lab_pattern.findall(line):
                            lab_match = True
                if not home_match:
                    with open(config_list[i], 'a') as f:
                        f.write('\n\n# alias for pocketlab home command\n')
                        f.write(home_alias)
                        f.close()
                elif not lab_match:
                    raise ValueError('the "home" alias is being used by another program.')
                else:
                    pass
    # TODO allow declaration of different alias
    # TODO check system path for home command

# construct registry client
    from pocketlab import __module__
    from labpack.storage.appdata import appdataClient
    registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)

# validate service name is not already in registry
    file_name = '%s.yaml' % service_name
    filter_function = registry_client.conditional_filter([{0:{'discrete_values':[file_name]}}])
    service_list = registry_client.list(filter_function=filter_function)
    if file_name in service_list:
        if not overwrite:
            suggest_msg = 'Add -f to overwrite.'
            raise ValueError('"%s" already exists in the registry. %s' % (service_name, suggest_msg))

# add service to registry
    service_root = './'
    if service_path:
        if not path.exists(service_path):
            raise ValueError('"%s" is not a valid path.' % service_path)
        elif not path.isdir(service_path):
            raise ValueError('"%s" is not a valid directory.' % service_path)
        service_root = service_path
    import yaml
    file_details = {
        'service_name': service_name,
        'service_root': path.abspath(service_root)
    }
    file_data = yaml.dump(file_details).encode('utf-8')
    registry_client.save(file_name, file_data)

    exit_msg = '"%s" added to registry. To return to workdir, run "home %s"' % (service_name, service_name)
    return exit_msg

if __name__ == '__main__':

# add dependencies
    try:
        import pytest
    except:
        print('pytest module required to perform unittests.\nTry: pip install pytest')
        exit()
    from time import time
    from pocketlab import __module__
    from labpack.storage.appdata import appdataClient
    registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)
    unittest_service = 'unittest_service_name_%s' % str(time()).replace('.', '')

# test invalid name exception
    from jsonmodel.exceptions import InputValidationError
    with pytest.raises(InputValidationError):
        home('not valid')

# test new service
    assert home(unittest_service).find(unittest_service)

# test existing service exception
    with pytest.raises(ValueError):
        home(unittest_service)

# test existing service overwrite
    assert home(service_name=unittest_service, overwrite=True).find(unittest_service)
    registry_client.delete('%s.yaml' % unittest_service)

# test path option
    assert home(unittest_service, service_path='../').find(unittest_service)

# test invalid path exception
    with pytest.raises(ValueError):
        home(unittest_service, service_path='./home.py')
    registry_client.delete('%s.yaml' % unittest_service)





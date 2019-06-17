__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

def retrieve_service_name(service_root):

    service_name = ''

# construct registry client
    from os import path
    from pocketlab import __module__
    from labpack.storage.appdata import appdataClient
    registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)

# walk registry for
    from labpack.records.settings import load_settings
    for file_path in registry_client.localhost.walk(registry_client.collection_folder):
        try:
            details = load_settings(file_path)
            if details['service_root'] == path.abspath(service_root):
                service_name = details['service_name']
                break
        except:
            pass

    return service_name

def retrieve_service_root(service_name, command_context=''):

# construct registry client
    from os import path
    from pocketlab import __module__
    from labpack.storage.appdata import appdataClient
    registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)

# validate service name exists in registry
    file_name = '%s.yaml' % service_name
    filter_function = registry_client.conditional_filter([{0:{'discrete_values':[file_name]}}])
    service_list = registry_client.list(filter_function=filter_function)
    if not file_name in service_list:
        error_msg = '"%s" not found in the registry.' % service_name
        if command_context:
            error_msg += ' %s' % command_context
        raise ValueError(error_msg)

# retrieve root path to service
    import yaml
    service_data = registry_client.load(file_name)
    service_details = yaml.load(service_data.decode())
    if not 'service_root' in service_details.keys():
        error_msg = 'Record for project "%s" has been corrupted.' % service_name
        if command_context:
            error_msg += ' %s' % command_context
        raise ValueError(error_msg)
    service_root = service_details['service_root']
    if not path.exists(service_root):
        error_msg = 'Path %s to project "%s" no longer exists.' % (service_root, service_name)
        if command_context:
            error_msg += ' %s' % command_context
        raise ValueError(error_msg)

    return service_root

def retrieve_services(service_list=None, all=False):
    
    '''
        a method to generate the root path for one or more services
        
    :param service_list: list of strings with name of services
    :param all: boolean to indicate the retrieve all paths in registry
    :return: list of dictionaries, string with exit message insert
    '''
    
# define default returns
    path_list = []
    msg_insert = 'local service'
    
# add named service to service list
    if service_list:
        from labpack.parsing.grammar import join_words
        word_list = []
        for service in service_list:
            service_root = retrieve_service_root(service)
            service_details = {
                'name': service,
                'path': service_root
            }
            path_list.append(service_details)
            word_list.append('"%s"' % service)
        msg_insert = join_words(word_list)

# add all services in registry to service list
    elif all:
        msg_insert = 'all services'
        from pocketlab import __module__
        from labpack.storage.appdata import appdataClient
        registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)
        from labpack.records.settings import load_settings
        for file_path in registry_client.localhost.walk(registry_client.collection_folder):
            try:
                details = load_settings(file_path)
                service_details = {
                    'name': details['service_name'],
                    'path': details['service_root']
                }
                path_list.append(service_details)
            except:
                pass

# add local path to service list
    else:
        path_list.append({'name': '', 'path': './'})
    
    return path_list, msg_insert

def retrieve_service_config(service_root, service_name, command_title):
    
    from os import path
    from pocketlab.methods.validation import validate_compose
    from pocketlab import __module__
    from jsonmodel.loader import jsonLoader
    from jsonmodel.validators import jsonModel
    compose_schema = jsonLoader(__module__, 'models/compose-config.json')
    service_schema = jsonLoader(__module__, 'models/service-config.json')
    compose_model = jsonModel(compose_schema)
    service_model = jsonModel(service_schema)
    compose_path = path.join(service_root, 'docker-compose.yaml')
    compose_details = validate_compose(compose_model, service_model, compose_path, service_name)
    service_config = {}
    if service_name:
        service_config = compose_details['services'][service_name]
    elif len(compose_details['services'].keys()) > 1:
        raise ValueError('docker-compose.yaml file in working directory contains more than one service.\nTry: lab %s [SERVICE]' % command_title)
    else:
        for key, value in compose_details['services'].items():
            service_config = value
            service_name = key
            break
    
    return service_config, service_name

def compile_services(registry_only=False):

# construct registry client
    from pocketlab import __module__
    from labpack.storage.appdata import appdataClient
    registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)

# walk registry to compile list of services
    service_list = []
    path_list = []
    from labpack.records.settings import load_settings
    for file_path in registry_client.localhost.walk(registry_client.collection_folder):
        try:
            details = load_settings(file_path)
            service_list.append({
                'name': details['service_name'], 
                'path': details['service_root']
            })
            path_list.append(details['service_root'])
        except:
            pass

# add current directory
    if not registry_only:
        from os import path
        current_path = path.abspath('./')
        if current_path not in path_list:
            try:
                file_path = path.join(current_path, 'docker-compose.yaml')
                from pocketlab.methods.validation import validate_compose
                from jsonmodel.loader import jsonLoader
                from jsonmodel.validators import jsonModel
                compose_model = jsonModel(jsonLoader(__module__, 'models/compose-config.json'))
                service_model = jsonModel(jsonLoader(__module__, 'models/service-config.json'))
                compose_details = validate_compose(compose_model, service_model, file_path, '')
                if len(compose_details['services'].keys()) == 1:
                    for key in compose_details['services'].keys():
                        service_list.append({
                            'name': key,
                            'path': current_path
                        })
            except:
                pass

    return service_list

def compile_ports(service_config):

    service_ports = []

# validate ports are available
    if 'ports' in service_config.keys():
        for i in range(len(service_config['ports'])):
            port_string = service_config['ports'][i]
            port_split = port_string.split(':')
            sys_port = port_split[0]
            range_split = sys_port.split('-')
            port_start = range_split[0]
            port_end = ''
            if len(range_split) > 1:
                port_end = range_split[1]
            if not port_end:
                service_ports.append(int(port_start))
            else:
                for j in range(int(port_start),int(port_end) + 1):
                    service_ports.append(j)

    return service_ports

if __name__ == '__main__':

    lab_root = retrieve_service_root('lab')
    lab_name = retrieve_service_name(lab_root)
    assert lab_name == 'lab'
    
    from pprint import pprint
    pprint(compile_services())
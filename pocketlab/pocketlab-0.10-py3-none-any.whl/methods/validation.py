__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = 'MIT'

def validate_platform(platform_model, service_root, service_name='', relative_path=''):
    
    '''
        a method to validate a yaml configuration file in .lab folder
        
    :param platform_model: jsonModel object with config schema
    :param service_root: string with path to root of service
    :param service_name: [optional] string with name of service
    :param relative_path: [optional] string with relative path of folder for file
    :return: dictionary with file configurations
    '''

# construct message insert
    msg_insert = 'working directory'
    if service_name:
        msg_insert = 'root directory for "%s"' % service_name
    msg_insert_2 = msg_insert
    if relative_path:
        msg_insert_2 = '%s sub-folder of %s' % (relative_path, msg_insert)

# validate config file exists
    from os import path
    file_flag = platform_model.metadata['flag']
    file_name = platform_model.title
    if relative_path:
        file_path = path.join(service_root, relative_path, file_name)
    else:
        file_path = path.join(service_root, file_name)
    file_init = 'lab init %s' % file_flag
    if not path.exists(file_path):
        raise ValueError('%s does not exist in %s.\nTry: "%s" in %s.' % (file_name, msg_insert_2, file_init, msg_insert))

# validate yaml file is valid
    from labpack.records.settings import load_settings
    try:
        config_details = load_settings(file_path)
    except:
        raise ValueError('%s file in %s corrupted.\nTry deleting and running again in %s: "%s"' % (file_name, msg_insert_2, msg_insert, file_init))

# validate heroku yaml keys
    from jsonmodel.exceptions import InputValidationError
    for key, value in platform_model.schema.items():
        object_title = 'Field %s in %s in %s' % (key, file_name, msg_insert_2)
        if key in config_details.keys():
            try:
                platform_model.validate(config_details[key], '.%s' % key, object_title)
            except InputValidationError as err:
                error_msg = "Value None for field .%s failed test 'value_datatype': map" % key
                if err.message.find(error_msg) > -1:
                    config_details[key] = {}
                else:
                    raise
            except:
                raise
        elif value:
            missing_msg = '%s is missing' % object_title
            raise ValueError(missing_msg)
    
    return config_details

def validate_compose(compose_model, service_model, file_path, service_name=''):

    '''
        a method to validate docker-compose.yaml configuration for service
        
    :param compose_model: jsonModel object with compose config schema
    :param service_model: jsonModel object with service config schema 
    :param file_path: string with path to docker-compose.yaml file for service
    :param service_name: [optional] string with name of service
    :return: dictionary with lab configurations
    '''

# construct message insert
    msg_insert = 'working directory'
    if service_name:
        msg_insert = 'root directory for "%s"' % service_name
    compose_insert = 'docker-compose.yaml file in %s' % msg_insert

# validate docker compose yaml exists
    from os import path
    if not path.exists(file_path):
        if path.exists(file_path.replace('.yaml','.yml')):
            file_path = file_path.replace('.yaml','.yml')
        else:
            raise ValueError('docker-compose.yaml does not exist in %s.\nTry: "lab init" in %s.' % (msg_insert, msg_insert))
    
# validate docker compose yaml is valid
    from labpack.records.settings import load_settings
    try:
        compose_details = load_settings(file_path)
    except:
        raise ValueError('%s corrupted.\nTry deleting and running again: "lab init"' % (compose_insert))

# validate compose schema structure
    from jsonmodel.exceptions import InputValidationError
    from copy import deepcopy
    test_details = deepcopy(compose_details)
    for key, value in compose_model.schema.items():
        object_title = 'Field %s in %s' % (key, compose_insert)
        if key in test_details.keys():
            try:
                # object_title = 'Field %s in docker-compose.yaml in %s' % (key, msg_insert)
                compose_model.validate(test_details[key], '.%s' % key, object_title)
            except InputValidationError as err:
                map_error = "Value None for field .%s failed test 'value_datatype': map" % key
                list_error = "Value None for field .%s failed test 'value_datatype': list" % key
                if err.message.find(map_error) > -1:
                    test_details[key] = {}
                elif err.message.find(list_error) > -1:
                    test_details[key] = []
                else:
                    raise
            except:
                raise
        elif value:
            missing_msg = '%s is missing' % object_title
            raise ValueError(missing_msg)

# validate services exists
    if not compose_details['services']:
        raise ValueError('%s is missing services.\nTry deleting and running again: "lab init"' % compose_insert)
    elif service_name and not service_name in compose_details['services'].keys():
        raise ValueError('%s is missing settings for "%s" service.' % (service_name, compose_insert))
    elif not service_name and len(compose_details['services'].keys()) > 1:
        raise ValueError('%s contains more than one service option.\nTry specifying service: "lab start [SERVICE]' % compose_insert)

# validate service schema structure
    for key, value in test_details['services'].items():
        for k, v in service_model.schema.items():
            object_title = 'Field services.%s.%s in %s' % (key, k, compose_insert)
            if k in value.keys():
                try:
                    service_model.validate(value[k], '.%s' % k, object_title)
                except InputValidationError as err:
                    map_error = "Value None for field .%s failed test 'value_datatype': map" % key
                    list_error = "Value None for field .%s failed test 'value_datatype': list" % key
                    if err.message.find(map_error) > -1:
                        test_details[key] = {}
                    elif err.message.find(list_error) > -1:
                        test_details[key] = []
                    else:
                        raise
                except:
                    raise

            # validate syntax of ports
                if k == 'ports':
                    port_list = []
                    for i in range(len(value[k])):
                        port_string = value[k][i]
                        port_split = port_string.split(':')
                        sys_port = port_split[0]
                        range_split = sys_port.split('-')
                        port_start = range_split[0]
                        port_end = ''
                        if len(range_split) > 1:
                            port_end = range_split[1]
                        if not port_end:
                            if int(port_start) in port_list:
                                raise ValueError('Value "%s" for field ports[%s] in %s overlaps another port mapping.' % (port_string, str(i), compose_insert))
                            port_list.append(int(port_start))
                        else:
                            if port_end <= port_start:
                                raise ValueError('Value "%s" for field ports[%s] in %s is invalid port mapping.' % (port_string, str(i), compose_insert))
                            else:
                                for j in range(int(port_start),int(port_end) + 1):
                                    if j in port_list:
                                        raise ValueError('Value "%s" for field ports[%s] in %s overlaps another port mapping.' % (port_string, str(i), compose_insert))
                                    port_list.append(j)

            # validate path of volumes
                if k == 'volumes':
                    for i in range(len(value[k])):
                        volume = value[k][i]
                        if volume['type'] == 'bind':
                            service_root, docker_file = path.split(file_path)
                            volume_path = path.join(service_root, volume['source'])
                            if not path.exists(volume_path):
                                raise ValueError('Value "%s" for field volumes[%s].source in %s is not a valid path.' % (volume['source'], str(i), compose_insert))

            elif service_model.components['.%s' % k]['required_field']:
                missing_msg = '%s is missing' % object_title
                raise ValueError(missing_msg)
            
    return compose_details

def validate_image(service_config, docker_images, service_name=''):

# construct message insert
    msg_insert = 'working directory'
    if service_name:
        msg_insert = 'root directory for "%s"' % service_name
    compose_insert = 'docker-compose.yaml file in %s' % msg_insert
    
# validate image exists in local docker repository
    image_tag = ''
    if not 'image' in service_config.keys():
        raise ValueError('%s is missing the image field for services.%s' % (compose_insert, service_name))
    elif not service_config['image']:
        raise ValueError('%s is missing a value for field service.%s.image' % (compose_insert, service_name))
    else:
        image_exists = False
        image_name = service_config['image']
        image_segments = image_name.split(':')
        image_repo = image_segments[0]
        if len(image_segments) > 1:
            image_tag = image_segments[1]
        for image in docker_images:
            if image_repo == image['REPOSITORY']:
                if image_tag:
                    if image_tag == image['TAG']:
                        image_exists = True
                else:
                    image_exists = True
        if not image_exists:
            raise ValueError('Image "%s" listed in %s not found on local device.\nTry either: "docker pull %s" or "docker build -t %s ."' % (image_name, compose_insert, image_name, image_name))
    
    return image_repo, image_tag

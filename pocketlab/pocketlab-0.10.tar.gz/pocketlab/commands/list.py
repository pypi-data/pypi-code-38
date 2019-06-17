__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = 'MIT'

'''
list services
list instances (ec2, heroku)
TODO: list images
TODO: list containers
TODO: list instances on other platforms (gcp, azure, bluemix, rackspace)
'''

_list_details = {
    'title': 'List',
    'description': 'Generates a list of the resources of a specific type. Only the service resource type is supported, but docker oriented and remote host kinds of resources are coming.',
    'help': 'lists the instances of a resource type',
    'benefit': 'Provides a way to find existing resources.'
}

from pocketlab.init import fields_model

def list(resource_type, platform_option, region_name='', paginate=False, all_info=False):

    title = 'list'

# validate inputs
    if isinstance(platform_option, str):
        if platform_option:
            platform_option = [platform_option]
    input_fields = {
        'resource_type': resource_type,
        'platform_option': platform_option,
        'region_name': region_name
    }
    for key, value in input_fields.items():
        if value:
            object_title = '%s(%s=%s)' % (title, key, str(value))
            fields_model.validate(value, '.%s' % key, object_title)

# retrieve window size
    from os import popen
    console_rows, console_columns = popen('stty size', 'r').read().split()
    console_rows = int(console_rows)
    console_columns = int(console_columns)

# construct default print out fields
    exit_msg = ''
    formatted_rows = []
    table_headers = []

# list services
    if resource_type == 'services':

    # construct registry client
        from pocketlab import __module__
        from labpack.storage.appdata import appdataClient
        registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)

    # walk registry to compile list of services
        from tabulate import tabulate
        from labpack.records.settings import load_settings
        service_list = []
        left_width = 0
        table_headers = ['Service', 'Path']
        for file_path in registry_client.localhost.walk(registry_client.collection_folder):
            try:
                details = load_settings(file_path)
                service_name = details['service_name']
                service_root = details['service_root']
                if len(service_name) > left_width:
                    left_width = len(service_name)
                service_list.append([service_name, service_root])
            except:
                pass

    # format list of services
        for row in service_list:
            row_width = left_width + 2 + len(row[1])
            path_text = row[1]
            if row_width > console_columns:
                cut_char = row_width - console_columns
                left_index = (len(row[1]) - cut_char - 12) * -1
                if left_index > -1:
                    path_text = '%s...' % row[1]
                else:
                    path_text = '%s...%s' % (row[1][0:9], row[1][left_index:])
            formatted_rows.append([row[0], path_text])

# list instances
    elif resource_type == 'instances':
    
    # determine platform name
        if not platform_option:
            from copy import deepcopy
            from labpack.parsing.grammar import join_words
            platform_list = deepcopy(fields_model.components['.platform_name']['discrete_values'])
            if len(platform_list) > 2:
                platform_list = platform_list[0:2]
            platform_options = join_words(platform_list, operator='disjunction')
            raise ValueError('list instances requires a platform name (eg. %s)' % platform_options)
        platform_name = platform_option[0]

    # compile service list
        from pocketlab.methods.service import compile_services
        service_list = compile_services()

    # construct empty instance list
        instance_list = []

    # process heroku
        if platform_name == 'heroku':

        # compile instances
            print('Compiling instance list from heroku ... ', end='', flush=True)
            from pocketlab.methods.heroku import compile_instances
            instance_list = compile_instances(service_list)
            print('done.')

    # process ec2
        elif platform_name == 'ec2':

        # TODO compile across accounts and regions

        # compile instances
            print('Compiling instance list from ec2 ... ', end='', flush=True)
            from pocketlab.methods.aws import compile_instances
            instance_list = compile_instances(region_name)
            print('done.')

    # TODO add http code ???
    
    # format list of instances
        table_headers = [ 'Name', 'Machine', 'Services', 'Env', 'IP Address', 'State' ]
        instance_keys = [ 'name', 'machine', 'services', 'environment', 'ip_address', 'state' ]
        if all_info:
            table_headers.pop()
            instance_keys.pop()
            # table_headers.insert(0, 'Name')
            # instance_keys.insert(0, 'name')
            table_headers.extend(['Region', 'Login', 'Instance Id', 'Image Id', 'Tags', 'State'])
            instance_keys.extend(['region', 'login', 'id', 'image', 'tags', 'state'])
        for instance in instance_list:
            instance_row = []
            for key in instance_keys:
                instance_row.append(instance[key])
            formatted_rows.append(instance_row)

# list images
    elif resource_type == 'images':
        pass

# list containers
    elif resource_type == 'containers':

        container_headers = [ 'NAMES', 'STATUS', 'IMAGE', 'PORTS']

# print out list
    if formatted_rows:

        from tabulate import tabulate

    # handle pagination
        if paginate and len(formatted_rows) + 5 > console_rows:
            page_rows = []
            for i in range(len(formatted_rows)):
                page_rows.append(formatted_rows[i])
                if len(page_rows) + 4 == console_rows:
                    table_text = tabulate(page_rows, headers=table_headers)
                    table_text += '\n[press any key for more]'
                    print(table_text)
                    page_rows = []
                    input()
                elif i + 1 == len(formatted_rows):
                    table_text = tabulate(page_rows, headers=table_headers)
                    if len(page_rows) + 5 == console_rows:
                        table_text += '\n[press any key for more]'
                    print(table_text)
                    if len(page_rows) + 5 == console_rows:
                        input()
    # no pagination
        else:
            table_text = tabulate(formatted_rows, headers=table_headers)
            print(table_text)

    return exit_msg

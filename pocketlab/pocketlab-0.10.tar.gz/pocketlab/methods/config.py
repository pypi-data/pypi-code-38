__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = 'MIT'

def retrieve_template(file_path):

    '''
        a method to retrieve text of a template file 
        
    :param file_path: string with relative path of file
    :return: string with text of file
    '''

    from os import path
    from pocketlab import __module__
    from importlib.util import find_spec
    module_path = find_spec(__module__).submodule_search_locations[0]
    absolute_path = path.join(module_path, file_path)
    file_text = open(absolute_path, 'rt').read()

    return file_text

def retrieve_scripts(package_name, os_identifier):

    # retrieve list of scripts for package
    from pocketlab import __module__
    from jsonmodel.loader import jsonLoader
    package_scripts = jsonLoader(__module__, 'models/%s-install.json' % package_name)

    # determine scripts for os
    install_details = {}
    stop = False
    for scripts in package_scripts:
        for identifier in scripts['identifiers']:
            identified = True
            identifiers = identifier.split(' ')
            for s in identifiers:
                if os_identifier.find(s) == -1:
                    identified = False
                    break
            if identified:
                stop = True
                install_details = scripts
                break
        if stop:
            break

    return install_details
    
def replace_text(file_text, substitution_map=None, replacement_map=None):

    '''
        a method to replace values in a file text

    :param substitution_map: [optional] dictionary with regex substitution pattern key pairs
    :param replacement_map: [optional] dictionary with replacement text key pairs
    :return: string with text with replacement fields
    '''

# substitute regex patterns
    import re
    if substitution_map:
        for key, value in substitution_map.items():
            regex_pattern = re.compile(key, re.S)
            file_text = regex_pattern.sub(value, file_text)

# replace text fields
    if replacement_map:
        for key, value in replacement_map.items():
            file_text = file_text.replace(key, value)

    return file_text

def compile_yaml(config_schema, yaml_path='', ingest_kwargs=None):

    '''
        a method to compile a yaml file with top-level comments from a json model
        
    :param config_schema: dictionary with json model schema architecture 
    :param yaml_path: [optional] string with path to user yaml file
    :param ingest_kwargs: [optional] dictionary with additional kwargs to ingest 
    :return: string with yaml formatted text
    '''

# construct config model
    from jsonmodel.validators import jsonModel
    config_model = jsonModel(config_schema)
    
# construct order dict
    config_list = []
    if ingest_kwargs and isinstance(ingest_kwargs, dict):
        config_details = config_model.ingest(**ingest_kwargs)
    else:
        config_details = config_model.ingest()
    for key, value in config_details.items():
        details = {
            'key': key,
            'value': value,
            'position': 0,
            'comments': ''
        }
        comp_key = '.%s' % key
        if comp_key in config_model.keyMap.keys():
            if 'field_metadata' in config_model.keyMap[comp_key].keys():
                metadata = config_model.keyMap[comp_key]['field_metadata']
                if 'position' in metadata.keys():
                    if isinstance(metadata['position'], int):
                        details['position'] = metadata['position']
                if 'comments' in metadata.keys():
                    if isinstance(metadata['comments'], str):
                        details['comments'] = metadata['comments']
        config_list.append(details)
    config_list.sort(key=lambda k: k['position'])
   
# construct config text
    config_text = ''
    if 'comments' in config_model.metadata.keys():
        if isinstance(config_model.metadata['comments'], str):
            comment_lines = config_model.metadata['comments'].splitlines()
            for comment in comment_lines:
                config_text += '# %s\n' % comment
    for item in config_list:
        comment_stub = '\n'
        if item['comments']:
            comment_stub = ' # %s\n' % item['comments']
        try:
            float(item['key'])
            item_key = "'%s'" % item['key']
        except:
            item_key = item['key']
        if isinstance(item['value'], dict):
            line_text = '%s:%s' % (item_key, comment_stub)
            for key, value in item['value'].items():
                try:
                    float(key)
                    key_text = "'%s'" % key
                except:
                    key_text = key
                value_text = value
                if isinstance(value, str):
                    try:
                        float(value)
                        value_text = "'%s'" % value
                    except:
                        pass              
                line_text += '  %s: %s\n' % (key_text, value_text)
        elif isinstance(item['value'], list):
            line_text = '%s:%s' % (item_key, comment_stub)
            for i in range(len(item['value'])):
                value_text = item['value'][i]
                if isinstance(value_text, str):
                    try:
                        float(value_text)
                        value_text = "'%s'" % value_text
                    except:
                        pass
                line_text += '  - %s\n' % value_text
        else:
            line_text = '%s: %s%s' % (item_key, str(item['value']), comment_stub)
        config_text += line_text

# update user config
    if yaml_path:
        from os import path
        if not path.exists(yaml_path):
            raise ValueError('%s is not a valid path.')
        import ruamel.yaml
        user_text = open(yaml_path).read()
        user_code = ruamel.yaml.load(user_text, ruamel.yaml.RoundTripLoader)
        user_len = len(user_code.keys())
        count = 0
        for item in config_list:
            if item['key'] not in user_code.keys():
                insert_row = user_len + count
                insert_kwargs = {
                    'pos': insert_row,
                    'key': item['key'],
                    'value': item['value']
                }
                if item['comments']:
                    insert_kwargs['comment'] = item['comments']
                user_code.insert(**insert_kwargs)
                count += 1
        config_text = ruamel.yaml.dump(user_code, Dumper=ruamel.yaml.RoundTripDumper)

    return config_text
    
def compile_compose(compose_schema, service_schema, service_name):

# add service name to appropriate locations
    service_schema['schema']['image'] = service_name
    compose_schema['schema']['services'][service_name] = { 'key': 'value' }

# compile yaml
    service_text = compile_yaml(service_schema, ingest_kwargs=service_schema['schema'])
    compose_text = compile_yaml(compose_schema, ingest_kwargs=compose_schema['schema'])
    compose_text = compose_text.replace("{'key': 'value'}\n", '# name for container alias and service in lab registry\n    ' + service_text.replace('\n', '\n    '))

# fix version datatype change
    import re
    def replace_version(x):
        return "%s'%s'" % (x.group(1), x.group(2))
    compose_text = re.sub('(\nversion: )(\d\.?\d?)', replace_version, compose_text)

# replace labels
    if service_name != 'server':
        compose_text = compose_text.replace("com.collectiveacuity: '5000'", "com.collectiveacuity.%s: '5000'" % service_name)

    return compose_text

def compile_dockerfile(dockerfile_path, platform_path, compose_path, service_details, msg_insert, platform_name, system_envvar=None, verbose=False):
    
# import dependencies
    from pocketlab import __module__
    from jsonmodel.loader import jsonLoader
    from jsonmodel.validators import jsonModel
    compose_schema = jsonLoader(__module__, 'models/compose-config.json')
    service_schema = jsonLoader(__module__, 'models/service-config.json')
    compose_model = jsonModel(compose_schema)
    service_model = jsonModel(service_schema)

# compose variables
    service_name = service_details['name']
    service_config = service_details['config']
    service_path = service_details['path']
    service_insert = service_details['insert']

# start validation
    dockerfile_text = ''
    if verbose:
        print('Checking Dockerfile settings in %s ... ' % msg_insert, end='', flush=True)

# retrieve dockerfile text from platform specific dockerfile
    from os import path
    if path.exists(platform_path):
        try:
            dockerfile_text = open(platform_path, 'rt').read()
            if verbose:
                print('done.')
        except:
            pass

# fallback to docker compose file
    if not dockerfile_text:
    
    # handle yml and yaml variation
        compose_alt = compose_path.replace('.yaml','.yml')
        if path.exists(compose_path) or path.exists(compose_alt):

            from pocketlab.methods.validation import validate_compose

    # validate docker compose file
            compose_details = validate_compose(compose_model, service_model, compose_path, service_name)
            
            if service_name:
                service_config.update(compose_details['services'][service_name])
            else:
                for key, value in compose_details['services'].items():
                    service_config.update(value)
                    service_name = key
                    break

    # retrieve dockerfile in docker compose
            if 'build' in service_config.keys():
                dockerfile_name = service_config['build'].get('dockerfile', 'Dockerfile')
                relative_path = path.join(service_config['build']['context'], dockerfile_name)
                if not path.isabs(relative_path):
                    relative_path = path.join(service_path, relative_path)
                try:
                    dockerfile_text = open(relative_path, 'rt').read()
                    if verbose:
                        print('done.')
                except:
                    pass

# fallback to Dockerfile in root
    if not dockerfile_text:
        if path.exists(dockerfile_path):
            try:
                dockerfile_text = open(dockerfile_path, 'rt').read()
                if verbose:
                    print('done.')
            except:
                pass

# catch missing Dockerfile error
    if not dockerfile_text:
        raise ValueError('Deploying %s to %s using docker requires Dockerfile instructions.\nTry creating a Dockerfile.' % (service_insert, platform_name))

# define regex patterns
    import re
    command_pattern = re.compile('\nCMD\s')
    entry_pattern = re.compile('\nENTRYPOINT\s')
    dockerfile_text = dockerfile_text.strip() + '\n'

# insert variables into Dockerfile
    if 'environment' in service_config.keys():
        for key, value in service_config['environment'].items():
            if key != 'PORT':
                dockerfile_text += '\nENV %s=%s' % (key.upper(), str(value))

# insert system envvar into Dockerfile
    if system_envvar:
        for key, value in system_envvar.items():
            dockerfile_text = re.sub('\nENV %s=.*?\n' % key.upper(), '\n', dockerfile_text)
            dockerfile_text += '\nENV %s=%s' % (key.upper(), str(value))

# insert volumes into Dockerfile as ADD
    if 'volumes' in service_config.keys():
        for volume in service_config['volumes']:
            if volume['type'] == 'bind':
                volume_line = '\nADD %s %s' % (volume['source'], volume['target'])
                if not re.findall(volume_line, dockerfile_text):
                    dockerfile_text += volume_line

# add command or entrypoint if none existent
    if command_pattern.findall(dockerfile_text) or entry_pattern.findall(dockerfile_text):
        pass
    else:
        if 'entrypoint' in service_config.keys():
            dockerfile_text += '\nENTRYPOINT %s' % str(service_config['entrypoint'])
        elif 'command' in service_config.keys():
            dockerfile_text += '\nCMD %s' % str(service_config['command'])
        else:
            raise ValueError('Deploying %s to %s with docker requires a start command or entrypoint.' % (service_insert, platform_name))
        
    return dockerfile_text
    
def inject_init(init_path, readme_path, setup_kwargs):

    '''
        a method to add arguments to setup.py from module init file
        
    :param init_path: string with path to module __init__ file 
    :param readme_path: string with path to module README.rst file
    :param setup_kwargs: dictionary with existing setup keyword arguments
    :return: dictionary with injected keyword arguments
    '''

    import re
    from os import path
    from copy import deepcopy

# retrieve init text
    init_text = ''
    if not path.exists(init_path):
        raise ValueError('%s is not a valid path' % init_path)
    init_text = open(init_path, encoding='utf-8').read()

# retrieve init settings
    init_kwargs = {
        'version': '',
        'author': '',
        'url': '',
        'description': '',
        'license': '',
    }
    for key in init_kwargs.keys():
        key_regex = re.compile("__%s__\s?\=\s?'(.*?)'" % key)
        key_search = key_regex.findall(init_text)
        if key_search:
            init_kwargs[key] = key_search[0]

# retrieve modifiable settings
    mod_kwargs = {
        'module': '',
        'email': '',
        'entry': '',
        'authors': ''
    }
    for key in mod_kwargs.keys():
        key_regex = re.compile("__%s__\s?\=\s?'(.*?)'" % key)
        key_search = key_regex.findall(init_text)
        if key_search:
            mod_kwargs[key] = key_search[0]
    if mod_kwargs['module']:
        init_kwargs['name'] = mod_kwargs['module']
    if mod_kwargs['entry']:
        init_kwargs['entry_points'] = { "console_scripts": [mod_kwargs['entry']] }
    if mod_kwargs['email']:
        init_kwargs['author_email'] = mod_kwargs['email']
        init_kwargs['maintainer_email'] = mod_kwargs['email']
    if mod_kwargs['authors']:
        del init_kwargs['author']
        init_kwargs['author_list'] = mod_kwargs['authors'].split(' ')

# add readme
    if not path.exists(readme_path):
        raise ValueError('%s is not a valid path' % readme_path)
    try:
        readme_text = open(readme_path).read()
        init_kwargs['long_description'] = str(readme_text)
    except:
        raise ValueError('%s is not a valid text file.' % readme_path)

# merge kwargs
    setup_kwargs.update(**init_kwargs)
    updated_kwargs = deepcopy(setup_kwargs)
    for key, value in updated_kwargs.items():
        if not value:
            del setup_kwargs[key]

    return setup_kwargs

def update_setup(setup_text, root_path='./'):

    '''
        a method to update an existing setup text with latest comments
        
    :param setup_text: string with text from setup.py source code
    :param root_path: string with path to service root
    :return: string with updated comments
    '''

# retrieve setup text comments
    import re
    from os import path
    file_text = retrieve_template('models/python.setup.py.txt')
    comment_regex = re.compile("'''\sDOCUMENTATION.*?'''", re.S)
    comment_text = comment_regex.findall(file_text)[0]

# determine module name and version number
    module_name = 'pocketlab'
    version_number = '0.1'
    init_regex = re.compile("init_path\s\=\s'(.*?)'")
    init_search = init_regex.findall(setup_text)
    if init_search:
        init_path = path.join(root_path, init_search[0])
        if path.exists(init_path):
            init_text = open(init_path).read()
            module_regex = re.compile("__module__\s\=\s'(.*?)'")
            version_regex = re.compile("__version__\s\=\s'(.*?)'")
            module_search = module_regex.findall(init_text)
            version_search = version_regex.findall(init_text)
            if module_search and version_search:
                module_name = module_search[0]
                version_number = version_search[0]

# find vcs URIs
    hg_regex = re.compile('(hgrc\s\[paths\]\sdefault\s\=\s)(.*?)\n')
    hg_search = hg_regex.findall(setup_text)
    github_regex = re.compile('(git\sremote\sadd\sorigin\s)(.*?)\n')
    github_search = github_regex.findall(setup_text)

# find/replace comments in setup text
    setup_text = comment_regex.sub('', setup_text)
    setup_text = setup_text.strip()
    setup_text += '\n\n%s' % comment_text

# replace module and version
    dist_regex = re.compile("pocketlab-0.1")
    new_dist = '%s-%s' % (module_name, version_number)
    setup_text = dist_regex.sub(new_dist, setup_text)

# replace vcs URIs
    if hg_search:
        hg_text = '%s%s\n' % (hg_search[0][0], hg_search[0][1])
        setup_text = hg_regex.sub(hg_text, setup_text)
    if github_search:
        github_text = '%s%s\n' % (github_search[0][0], github_search[0][1])
        setup_text = github_regex.sub(github_text, setup_text)

    return setup_text

def construct_setup(module_name, org_name):

    '''
        a method to create the text for a setup.py file for a module
        
    :param module_name: string with name of module to create
    :param org_name: string with name of repo organization
    :return: string with text for setup.py file
    '''

# retrieve setup text
    file_text = retrieve_template('models/python.setup.py.txt')

# insert module name
    import re
    init_regex = re.compile("init_path\s\=\s''")
    init_text = "init_path = '%s/__init__.py'" % module_name
    file_text = init_regex.sub(init_text, file_text)

# replace module and version
    dist_regex = re.compile("pocketlab-0.1")
    new_dist = '%s-0.1' % module_name
    file_text = dist_regex.sub(new_dist, file_text)
    repo_regex = re.compile('collectiveacuity/pocket[lL]ab')
    new_repo = '%s/%s' % (org_name, module_name)
    file_text = repo_regex.sub(new_repo, file_text)
    
    return file_text

def construct_init(module_type='python'):

    '''
        a method to create the text for a __init__ file for a new module
        
    :param module_type: string with type of init file to create
    :return: string with text for init file
    '''

# retrieve date
    from datetime import datetime
    new_date = datetime.utcnow()
    new_month = str(new_date.month)
    if len(new_month) == 1:
        new_month = '0%s' % new_month
    date_string = '%s.%s' % (str(new_date.year), new_month)

# construct init text
    if module_type == 'node':
        init_text = '/*!\n'
        init_text += '* @name pocketlab\n'
        init_text += '* @description <service-description>\n'
        init_text += '* @author <org-title>\n'
        init_text += '* @contributors <user-name> <<user-email>>\n'
        init_text += '* @license MIT  // MIT, BSD, ALv2, GPLv3+, LGPLv3+, SEE LICENSE IN LICENSE.txt\n'
        init_text += '* @version 0.0.1\n'
        init_text += '* @copyright %s <org-title>\n' % str(new_date.year)
        init_text += '* @email <org-email>\n'
        init_text += '* @url https://github.com/<org-name>/pocketlab\n'
        init_text += '* @preserve\n*/'
    else:
        init_text = "''' <service-description> '''\n"
        init_text += "__author__ = '<user-name>'\n"
        init_text += "__created__ = '%s'\n" % date_string
        init_text += "__module__ = 'pocketlab'\n"
        init_text += "__version__ = '0.1'\n"
        init_text += "__license__ = 'MIT'  # MIT, BSD, ALv2, GPLv3+, LGPLv3+, ©%s <org-title>\n" % str(new_date.year)
        init_text += "__team__ = '<org-title>'\n"
        init_text += "__email__ = '<org-email>'\n"
        init_text += "__url__ = 'https://github.com/<org-name>/pocketlab'\n"
        init_text += "__description__ = '<service-description>'\n"
        
    return init_text

def construct_changes(type='python'):

# retrieve changes text
    if type == 'node':
        file_text = retrieve_template('models/changelog.md.txt')
    else:
        file_text = retrieve_template('models/changes.rst.txt')

# retrieve date
    from datetime import datetime
    new_date = datetime.utcnow()
    new_month = str(new_date.month)
    new_day = str(new_date.day)
    if len(new_month) == 1:
        new_month = '0%s' % new_month
    if len(new_day) == 1:
        new_day = '0%s' % new_day
    date_string = '%s.%s.%s' % (str(new_date.year), new_month, new_day)

# replace date
    file_text = file_text.replace('2001.01.01', date_string)

    return file_text

def construct_license(license_type='mit', replace_map=None):

# retrieve license text
    file_path = 'models/license.%s.txt' % license_type
    file_text = retrieve_template(file_path)

# retrieve date
    from datetime import datetime
    new_date = datetime.utcnow()
    new_year = str(new_date.year)

# replace terms in license
    file_text = file_text.replace('2017', new_year)
    file_text = replace_text(file_text, replacement_map=replace_map)

    return file_text

if __name__ == '__main__':

    standard_path = '../models/heroku-config.json'
    from labpack.records.settings import load_settings
    standard_schema = load_settings(standard_path)
    text = compile_yaml(standard_schema)
    # print(text)

    init_path = '../__init__.py'
    readme_path = '../../README.rst'
    setup_kwargs = inject_init(init_path, readme_path, {})
    # print(setup_kwargs)

    setup_text = open('../../setup.py').read()
    new_text = update_setup(setup_text)
    # print(new_text)

    module_name = 'newmodule'
    setup_text = construct_setup(module_name)
    # print(setup_text)
    init_text = construct_init(module_name)
    # print(init_text)
    readme_text = construct_readme(framework_type='python')
    # print(readme_text)
    service_text = construct_readme(replacement_map={'.gitignore': '.hgignore'})
    # print(service_text)
    manifest_text = construct_manifest(module_name)
    # print(manifest_text)
    changes_text = construct_changes()
    # print(changes_text)
    license_text = construct_license()
    # print(license_text)
    mkdocs_text = construct_mkdocs(module_name)
    # print(mkdocs_text)
    index_text = construct_index(module_name)
    print(index_text)
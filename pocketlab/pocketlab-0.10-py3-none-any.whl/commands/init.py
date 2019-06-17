__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = 'MIT'

'''
add .ignore file
add docker-compose.yaml file
add cred & data folders
copy cred files from notes to cred
add setup.py
add docs folder
add index.md to docs folder
add <module> folder
add __init__ to <module> folder
add .lab folders
add --heroku as a flag to create heroku.yaml .lab
add --aws as a flag to create aws.yaml in .lab
'''

_init_details = {
    'title': 'Init',
    'description': 'Init adds a number of files to the working directory which are required for other lab processes. If not present, it will create a ```docker-compose.yaml``` file and a ```.lab``` folder in the root directory to manage various configuration options. It will also create, if missing, ```cred/``` and ```data/``` folders to store sensitive project information outside version control along with a ```.gitignore``` (or ```.hgignore```) file to escape out standard non-VCS files.\n\nPLEASE NOTE: With the option ```--python``` (or ```--node``` or ```--jquery```), init creates instead a standard framework for publishing a python (or node or jquery) module.',
    'help': 'creates a lab framework in workdir',
    'benefit': 'Init adds the config files for other lab commands.'
}

from pocketlab.init import fields_model

def init(service_option, vcs_service='', license_type='MIT', init_python=False, init_node=False, init_jquery=False, init_heroku=False, init_aws=False, init_ec2=False, init_asg=False, verbose=True, overwrite=False):

    '''
        a method to add lab framework files to the current directory
    
    :param service_option: [optional] string with name of service in lab registry
    :param vcs_service: [optional] string with name of version control service
    :param license_type: [optional] string with name of software license type
    :param init_python: [optional] boolean to initialize a python module framework
    :param init_node: [optional] boolean to initialize a node module framework
    :param init_jquery: [optional] boolean to initialize a jquery based node module framework
    :param init_heroku: [optional] boolean to add heroku.yaml to .lab folder
    :param init_aws: [optional] boolean to add aws.yaml to .lab folder
    :param init_ec2: [optional] boolean to add ec2.yaml to working directory
    :param init_asg: [optional] boolean to add asg.yaml to working directory
    :param verbose: [optional] boolean to toggle process messages
    :param overwrite: [optional] boolean to overwrite existing service registration
    :return: string with success exit message
    '''

    title = 'init'

# ingest service option
    if isinstance(service_option, str):
        if service_option:
            service_option = [service_option]

# validate inputs
    input_fields = {
        'service_option': service_option,
        'vcs_service': vcs_service,
        'license_type': license_type
    }
    for key, value in input_fields.items():
        if value:
            object_title = '%s(%s=%s)' % (title, key, str(value))
            fields_model.validate(value, '.%s' % key, object_title)
    
# determine service name
    service_name = ''
    if service_option:
        service_name = service_option[0]

# import dependencies
    exit_msg = ''
    from os import path, makedirs
    from pocketlab import __module__
    from jsonmodel.loader import jsonLoader

# define printer submethod
    def _printer(file_path, node_type='file'):
        if verbose:
            from os import path
            folder, file = path.split(file_path)
            if not folder:
                folder = 'working directory'
            else:
                folder = '%s folder' % folder
            print('%s %s created in %s.' % (file, node_type, folder))

# handle requirements
    auto_active = False
    auto_files = [ init_aws, init_heroku, init_ec2, init_asg ]
    for toggle in auto_files:
        if toggle:
            auto_active = True
    if not auto_active and not service_name:
        raise ValueError('Lab init requires a name for the service framework.\nTry: lab init <service>')

# handl service init
    if service_name:

    # construct registry client
        from labpack.storage.appdata import appdataClient
        registry_client = appdataClient(collection_name='Registry Data', prod_name=__module__)
    
    # validate service name is not already in registry
        file_name = '%s.yaml' % service_name
        filter_function = registry_client.conditional_filter([{0:{'discrete_values':[file_name]}}])
        service_list = registry_client.list(filter_function=filter_function)
        if not file_name in service_list:
            from pocketlab.commands.home import home
            home(service_name)
        else:
            from labpack.compilers.encoding import decode_data
            service_details = decode_data(file_name, registry_client.load(file_name))
            if service_details['service_root'] != path.abspath('./'):
                from pocketlab.commands.home import home
                home(service_name, overwrite=overwrite)

    # retrieve username
        import os
        from labpack.platforms.localhost import localhostClient
        localhost_client = localhostClient()
        if localhost_client.os.sysname == 'Windows':
            username = os.environ.get('USERNAME')
        else:
            home_path = os.path.abspath(localhost_client.home)
            root_path, username = os.path.split(home_path)
    
    # define replacement map
        replacement_map = {
            '<service-description>': 'A Vital Service for a Brand New Project',
            '<user-name>': username,
            'pocketlab': service_name,
            '<org-name>': username,
            '<org-title>': username,
            '<org-email>': 'user@domain.com',
            '<org-url>': '',
            '<user-email>': 'user@domain.com'
        }
        if username == 'rcj1492':
            replacement_map['<org-name>'] = 'collectiveacuity'
            replacement_map['<org-title>'] = 'Collective Acuity'
            replacement_map['<org-email>'] = 'support@collectiveacuity.com'
            replacement_map['<org-url>'] = 'http://collectiveacuity.com'
            replacement_map['<user-email>'] = ''

    # setup module architecture
        if init_python or init_node or init_jquery:

        # determine module variables
            from pocketlab.methods.vcs import load_ignore
            from pocketlab.methods.config import replace_text, retrieve_template
            module_type = 'python'
            test_folder = 'tests'
            readme_path = 'README.rst'
            if init_node or init_jquery:
                module_type = 'node'
                test_folder = 'test'
                readme_path = 'README.md'

        # customize replacement map
            if init_python:
                replacement_map['<service-description>'] = 'A Brand New Python Module'
            elif init_jquery:
                replacement_map['<service-description>'] = 'A Brilliant Javascript Module For The Browser'
            elif init_node:
                replacement_map['<service-description>'] = 'A Powerful Javascript Tool for NodeJS'

        # define substitution maps
            gitignore_subsitutions = {
                '#+\s+version\scontrol\s+#+': '################  version control  ################\n.hgignore\n.hg/',
                '#+\s+dev\sfiles\s+#+': '#################    dev files    #################\ndev/\n%s_dev/' % test_folder
            }
            hgignore_subsitutions = {
                '#+\s+version\scontrol\s+#+': '################  version control  ################\n\\\.git/'
            }
            npmignore_substitions = {
                '#+\s+version\scontrol\s+#+': '################  version control  ################\n.hgignore\n.hg/\n.gitignore\n.git/',
                '#+\s+dev\sfiles\s+#+': '#################    dev files    #################\ndev/\ntest/\ntest_dev/\ndocs/\ndocs_dev/\n.babelrc\nwebpack.config.js\nkarma.config.js',
                '#+\s+dependencies\s+#+': '#################  dependencies   #################\n*.swp\nnpm-debug.log',
                '#+\s+unit\stesting\s+#+': '#################  unit testing   #################\ncoverage/',
                '#+\s+.gitignore\s+#+': '#################   .npmignore    #################'
            }

        # create .gitignore file
            git_path = '.gitignore'
            if not path.exists(git_path):
                git_text = load_ignore(type=module_type)
                git_text = replace_text(git_text, substitution_map=gitignore_subsitutions)
                with open(git_path, 'wt') as f:
                    f.write(git_text)
                    f.close()
                _printer(git_path)

        # create .hgignore file
            hg_path = '.hgignore'
            if not path.exists(hg_path):
                hg_text = load_ignore(vcs='mercurial', type=module_type)
                hg_text = replace_text(hg_text, substitution_map=hgignore_subsitutions)
                with open(hg_path, 'wt') as f:
                    f.write(hg_text)
                    f.close()
                _printer(hg_path)

        # create .npmignore file
            npm_path = '.npmignore'
            if module_type == 'node' and not path.exists(npm_path):
                npm_text = load_ignore(type=module_type)
                npm_text = replace_text(npm_text, substitution_map=npmignore_substitions)
                with open(npm_path, 'wt') as f:
                    f.write(npm_text)
                    f.close()
                _printer(npm_path)

        # create source folder
            source_path = service_name
            if module_type == 'node':
                source_path = 'src'
            if not path.exists(source_path):
                from os import makedirs
                makedirs(source_path)
                _printer(source_path, 'folder')

        # create init file
            init_path = path.join(source_path, '__init__.py')
            if init_node:
                init_path = path.join(source_path, '__init__.js')
            elif init_jquery:
                init_path = ''
            if init_path and not path.exists(init_path):
                from pocketlab.methods.config import construct_init
                init_text = construct_init(module_type)
                init_text = replace_text(init_text, replacement_map=replacement_map)
                with open(init_path, 'wt', encoding='utf-8') as f:
                    f.write(init_text)
                    f.close()
                _printer(init_path)

        # create source file
            if module_type == 'node':
                source_path = path.join(source_path, '%s.js' % service_name)
                if not path.exists(source_path):
                    if init_jquery:
                        from pocketlab.methods.config import construct_init
                        source_text = retrieve_template('models/jquery.source.js.txt')
                        init_text = construct_init(module_type)
                        init_text = replace_text(init_text, replacement_map=replacement_map)
                        source_text = init_text + '\n' + source_text
                    else:
                        source_text = retrieve_template('models/node.source.js.txt')
                    with open(source_path, 'wt', encoding='utf-8') as f:
                        f.write(source_text)
                        f.close()
                    _printer(source_path)

        # create package json
            if module_type == 'node':
                package_path = 'package.json'
                if not path.exists(package_path):
                    if init_jquery:
                        package_text = retrieve_template('models/jquery.package.json')
                        dependency_text = retrieve_template('models/jquery.global.dependencies.json')
                    else:
                        package_text = retrieve_template('models/node.package.json')
                        dependency_text = retrieve_template('models/node.global.dependencies.json')
                    import json
                    replacement_map['<global-dependencies>'] = ''
                    replacement_map['<local-dependencies>'] = ''
                    package_text = replace_text(package_text, replacement_map=replacement_map)
                    package_json = json.loads(package_text)
                    package_local = package_json['devDependencies']
                    package_global = json.loads(dependency_text)
                    for key in package_local.keys():
                        if replacement_map['<local-dependencies>']:
                            replacement_map['<local-dependencies>'] += ' '
                        replacement_map['<local-dependencies>'] += key
                    for key, value in package_global.items():
                        if replacement_map['<global-dependencies>']:
                            replacement_map['<global-dependencies>'] += ' '
                        replacement_map['<global-dependencies>'] += key
                        package_json['devDependencies'][key] = value
                    package_text = json.dumps(package_json, indent=2)
                    with open(package_path, 'wt', encoding='utf-8') as f:
                        f.write(package_text)
                        f.close()
                    _printer(package_path)

        # create readme file
            readme_text = ''
            if not path.exists(readme_path):
                if module_type == 'node':
                    readme_text = retrieve_template('models/node.readme.md.txt')
                    readme_text = replace_text(readme_text, replacement_map=replacement_map)
                elif init_python:
                    highlight_text = ''
                    for i in range(len(service_name)):
                        highlight_text += '='
                    sub_rst = {
                        '\n=*?\npocketlab.*?=\n': '\n%s\n%s\n%s\n' % (highlight_text, service_name, highlight_text)
                    }
                    readme_text = retrieve_template('models/python.readme.rst.txt')
                    readme_text = replace_text(
                        readme_text, 
                        substitution_map=sub_rst, 
                        replacement_map=replacement_map
                    )
                with open(readme_path, 'wt', encoding='utf-8') as f:
                    f.write(readme_text)
                    f.close()
                _printer(readme_path)

        # create docs folders
            if not path.exists('docs'):
                from os import makedirs
                makedirs('docs')
                _printer('docs', 'folder')

        # create test folder
            if not path.exists(test_folder):
                from os import makedirs
                makedirs(test_folder)
                _printer(test_folder, 'folder')

        # create docsify files
            if module_type == 'node':
                index_path = path.join('docs', 'index.html')
                if not path.exists(index_path):
                    index_text = retrieve_template('models/docsify.index.html.txt')
                    with open(index_path, 'wt') as f:
                        f.write(index_text)
                        f.close()
                    _printer(index_path)
                jekyll_path = path.join('docs', '.nojekyll')
                if not path.exists(jekyll_path):
                    with open(jekyll_path, 'wt') as f:
                        f.write('')
                        f.close()
                    _printer(jekyll_path)
                readme_path = path.join('docs', 'README.md')
                if readme_text and not path.exists(readme_path):
                    with open(readme_path, 'wt') as f:
                        f.write(readme_text)
                        f.close()
                    _printer(readme_path)

        # create mkdocs files
            else:
            # create docs dev folder
                if not path.exists('docs_dev'):
                    from os import makedirs
                    makedirs('docs_dev')
                    _printer('docs_dev', 'folder')

            # create mkdocs markdown file
                mkdocs_path = path.join('docs', 'mkdocs.md')
                if not path.exists(mkdocs_path):
                    mkdocs_text = retrieve_template('models/mkdocs.md.txt')
                    with open(mkdocs_path, 'wt') as f:
                        f.write(mkdocs_text)
                        f.close()
                    _printer(mkdocs_path)
        
            # create roadmap markdown files
                roadmap_docs = path.join('docs', 'roadmap.md')
                roadmap_temp = path.join('docs_dev', 'roadmap.md')
                roadmap_list = [ roadmap_docs, roadmap_temp ]
                for file_path in roadmap_list:
                    if not path.exists(file_path):
                        roadmap_text = retrieve_template('models/mkdocs.roadmap.md.txt')
                        with open(file_path, 'wt') as f:
                            f.write(roadmap_text)
                            f.close()
                        _printer(file_path)
        
            # create components yaml file
                components_path = path.join('docs_dev', 'components.csv')
                if not path.exists(components_path):
                    components_text = retrieve_template('models/mkdocs.components.csv.txt')
                    with open(components_path, 'wt') as f:
                        f.write(components_text)
                        f.close()
                    _printer(components_path)
        
            # create generate script file
                generate_path = path.join('docs_dev', 'generate.py')
                if not path.exists(generate_path):
                    generate_text = retrieve_template('models/mkdocs.generate.py.txt')
                    with open(generate_path, 'wt') as f:
                        f.write(generate_text)
                        f.close()
                    _printer(generate_path)

            # create index markdown file
                index_path = path.join('docs', 'index.md')
                if not path.exists(index_path):
                    index_text = retrieve_template('models/mkdocs.index.md.txt')
                    index_text = replace_text(index_text, replacement_map=replacement_map)
                    with open(index_path, 'wt') as f:
                        f.write(index_text)
                        f.close()
                    _printer(index_path)

        # create test files
            if module_type == 'node':
                test_path = path.join('test', '%s-spec.js' % service_name)
                if not path.exists(test_path):
                    test_text = retrieve_template('models/node.spec.js.txt')
                    test_text= test_text.replace('pocketlab', service_name)
                    with open(test_path, 'wt', encoding='utf-8') as f:
                        f.write(test_text)
                        f.close()
                    _printer(test_path)

        # create other root files
            license_type = license_type.lower()
            from pocketlab.methods.config import construct_changes, construct_license, construct_setup
            if module_type == 'node':
                module_files = {
                    'CHANGELOG.md': construct_changes(module_type),
                    'LICENSE.txt': construct_license(license_type, replacement_map),
                    '.coveralls.yml': retrieve_template('models/coveralls.yml.txt'),
                    '.babelrc': retrieve_template('models/babelrc.txt')
                }
                if init_jquery:
                    webpack_text = retrieve_template('models/webpack.config.js.txt')
                    module_files['karma.config.js'] = retrieve_template('models/karma.config.js.txt')
                    module_files['webpack.config.js'] = replace_text(
                        webpack_text,
                        replacement_map=replacement_map
                    )
            else:
                manifest_text = retrieve_template('models/python.manifest.in.txt')
                mkdocs_text = retrieve_template('models/mkdocs.yaml.txt')
                module_files = {
                    'CHANGES.rst': construct_changes(),
                    'LICENSE.txt': construct_license(license_type, replacement_map),
                    'MANIFEST.in': replace_text(manifest_text, replacement_map=replacement_map),
                    'mkdocs.yml': replace_text(mkdocs_text, replacement_map=replacement_map),
                    'setup.py': construct_setup(service_name, replacement_map['<org-name>'])
                }
            for key, value in module_files.items():
                if not path.exists(key):
                    with open(key, 'wt', encoding='utf-8') as f:
                        f.write(value)
                        f.close()
                    _printer(key)
    
            exit_msg = 'Framework for "%s" module setup in current directory.' % service_name
    
    # setup service architecture
        else:
    
        # determine version control service
            if not vcs_service:
                vcs_service = 'git'
                if path.exists('.git'):
                    if path.isdir('.git'):
                        vcs_service = 'git'
                elif path.exists('.hg'):
                    if path.isdir('.hg'):
                        vcs_service = 'mercurial'
            else:
                vcs_service = vcs_service.lower()
    
        # add a vcs ignore file
            from pocketlab.methods.vcs import load_ignore
            if vcs_service == 'git':
                vcs_path = '.gitignore'
                vcs_type = 'git'
            else:
                vcs_path = '.hgignore'
                vcs_type = 'mercurial'
            if not path.exists(vcs_path):
                file_text = load_ignore(vcs=vcs_type)
                with open(vcs_path, 'wt') as f:
                    f.write(file_text)
                    f.close()
                _printer(vcs_path)

        # add docker ignore file
            docker_path = '.dockerignore'
            if not path.exists(docker_path):
                file_text = load_ignore(vcs='docker')
                with open(docker_path, 'wt') as f:
                    f.write(file_text)
                    f.close()
                _printer(docker_path)

        # add docker compose file
            config_path = 'docker-compose.yaml'
            config_alt = 'docker-compose.yml'
            if not path.exists(config_path) and not path.exists(config_alt):
    
            # retrieve config schemas
                compose_schema = jsonLoader(__module__, 'models/compose-config.json')
                service_schema = jsonLoader(__module__, 'models/service-config.json')
        
            # # add default values to schemas
                default_volume_1 = {'type': 'bind', 'source': './cred', 'target': '/opt/cred'}
                default_volume_2 = {'type': 'bind', 'source': './data', 'target': '/opt/data'}
                service_schema['schema']['volumes'].insert(0, default_volume_2)
                service_schema['schema']['volumes'].insert(0, default_volume_1)
    
            # modify config schema defaults from values in registry
                if service_name:
                    service_schema['schema']['image'] = service_name
                else:
                    from pocketlab.methods.service import retrieve_service_name
                    service_name = retrieve_service_name('./')
                    if service_name:
                        service_schema['schema']['image'] = service_name
                    else:
                        service_name = 'server'

            # compile yaml
                from pocketlab.methods.config import compile_compose
                config_text = compile_compose(compose_schema, service_schema, service_name)
    
            # save config text
                with open(config_path, 'wt') as f:
                    f.write(config_text)
                    f.close()
                _printer(config_path)

        # add a .lab folder
            lab_path = '.lab'
            if not path.exists(lab_path):
                makedirs(lab_path)
                _printer(lab_path, 'folder')

        # add a data folder
            data_path = 'data'
            if not path.exists(data_path):
                makedirs(data_path)
                _printer(data_path, 'folder')
    
        # add a credential folder
            cred_path = 'cred'
            notes_path = 'notes'
            if not path.exists(cred_path):
                makedirs(cred_path)
                _printer(cred_path, 'folder')
                if path.exists(notes_path):
                    if path.isdir(notes_path):
                        src_list = []
                        dst_list = []
                        from os import listdir
                        from shutil import copyfile
                        for file_name in listdir(notes_path):
                            file_path = path.join(notes_path, file_name)
                            if path.isfile(file_path):
                                if file_name.find('.json') > -1 or file_name.find('.yaml') > -1 or file_name.find('.yml') > -1:
                                    src_list.append(file_path)
                                    dst_list.append(path.join(cred_path, file_name))
                        for i in range(len(src_list)):
                            copyfile(src_list[i], dst_list[i])
                            _printer(dst_list[i])

        # add readme file
            readme_path = 'README.md'
            if not path.exists(readme_path):
                from pocketlab.methods.config import retrieve_template, replace_text
                readme_text = retrieve_template('models/service.readme.md.txt')
                if vcs_service == 'mercurial':
                    replacement_map['.gitignore'] = '.hgignore'
                readme_text = replace_text(readme_text, replacement_map=replacement_map)
                with open(readme_path, 'wt', encoding='utf-8') as f:
                    f.write(readme_text)
                    f.close()
                _printer(readme_path)
    
            exit_msg = 'Framework for "%s" service setup in current directory.' % service_name

# handle platform cred files
    platform_names = []
    if init_aws or init_heroku:

    # add lab folder
        lab_path = '.lab'
        if not path.exists(lab_path):
            makedirs(lab_path)
            _printer(lab_path, 'folder')

    # add config files
        config_map = {
            'heroku.yaml': { 
                'toggle': init_heroku,
                'name': 'heroku',
                'schema_path': 'models/heroku-config.json'
            },
            'aws.yaml': {
                'toggle': init_aws,
                'name': 'aws',
                'schema_path': 'models/aws-config.json'
            }
        }
        for key, value in config_map.items():
            if value['toggle']:
                config_path = '.lab/%s' % key
                if not path.exists(config_path):
                    from pocketlab.methods.config import compile_yaml
                    config_schema = jsonLoader(__module__, value['schema_path'])
                    config_text = compile_yaml(config_schema)
                    with open(config_path, 'wt') as f:
                        f.write(config_text)
                        f.close()
                    _printer(config_path)
                    platform_names.append(value['name'])

# define ec2 yaml constructor
    def _generate_ec2(serv_name):
    
    # retrieve service name
        from pocketlab.methods.service import retrieve_service_name
        if not serv_name:
            serv_name = retrieve_service_name('./')
        if not serv_name:
            serv_name = 'server'
        
    # compile schema
        from pocketlab.methods.aws import compile_schema
        config_schema = compile_schema('models/ec2-config.json')
    
    # compile yaml and save
        from pocketlab.methods.config import compile_yaml
        config_text = compile_yaml(config_schema)
        from labpack.records.time import labDT
        new_dt = labDT.new()
        dt_string = str(new_dt.date()).replace('-','')
        config_text = config_text.replace('generate-date', dt_string)
        config_text = config_text.replace('generate-service', serv_name)
        for key_name in ('region_name', 'iam_profile', 'elastic_ip'):
            key_pattern = '\n%s:' % key_name
            if config_text.find(key_pattern) > -1:
                config_text = config_text.replace(key_pattern, "\n# %s:" % key_name)

        return config_text

# handle ec2 config file
    if init_ec2:

        config_path = 'ec2.yaml'
        if not path.exists(config_path):

        # compile ec2 config text and save
            config_text = _generate_ec2(service_name)
            with open(config_path, 'wt') as f:
                f.write(config_text)
                f.close()
            _printer(config_path)
            platform_names.append('ec2')

# handle asg config file
    if init_asg:
        
        config_path = 'asg.yaml'
        if not path.exists(config_path):

        # compile schema
            from pocketlab.methods.aws import compile_schema
            asg_schema = compile_schema('models/asg-config.json')

        # compile asg text
            from pocketlab.methods.config import compile_yaml
            asg_text = compile_yaml(asg_schema)
            from labpack.records.time import labDT
            new_dt = labDT.new()
            dt_string = str(new_dt.date()).replace('-','')
            asg_text = asg_text.replace('generate-date', dt_string)

        # compile ec2 text
            ec2_text = _generate_ec2(service_name)
            ec2_lines = ec2_text.splitlines(keepends=True)
            ec2_splice = []
            for i in range(len(ec2_lines)):
                if i != 1:
                    ec2_splice.append(ec2_lines[i])
            ec2_text = ''.join(ec2_splice)

        # merge yaml
            config_text = asg_text.replace("ec2:\n", 'ec2: ' + ec2_text.replace('\n', '\n  '))
            with open(config_path, 'wt') as f:
                f.write(config_text)
                f.close()
            _printer(config_path)
            platform_names.append('asg')

# generate message for non service creation
    if not exit_msg:
        from labpack.parsing.grammar import join_words
        platform_insert = join_words(platform_names)
        platform_plural = ''
        if len(platform_names) > -1:
            platform_plural = 's'
        exit_msg = 'Configuration file%s for %s added to working directory.' % (platform_plural, platform_insert)
        
    return exit_msg

if __name__ == "__main__":

    from labpack.records.settings import load_settings
    from jsonmodel.validators import jsonModel
    config_path = '../models/service-config.json'
    config_model = jsonModel(load_settings(config_path))
    print(config_model.ingest())

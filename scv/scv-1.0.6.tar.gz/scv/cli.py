# -*- coding: UTF-8 -*-
import os, sys, getpass, argparse, re
import yaml, utils, enum
from . import __version__ as VERSION

# arguments parse, cmd conf
parser = argparse.ArgumentParser(prog='scv', description='Python project manager')
subparsers = parser.add_subparsers(help='sub-command')
# Todo: add `scv -v`

# package.yml file conf & data
package_file = 'package.yml'
project_name = os.path.basename(os.getcwd())

class Manage(enum.Enum):
    ADD = 'add',
    REMOVE = 'remove',
    REMOVEALL = 'remove_all',
    UPDATE = 'update',
    GET = 'get'

def check_argv(func):
    '''
    Check sys.args is exists
    :return: bool
    '''
    def wrapper():
        if not sys.argv[1:]:
            parser.print_help()
            exit(0)
        func()
    return wrapper

def check_file_exists(func):
    '''
    Check package.yml exists
    :param func: function
    :return: dict
    '''
    def wrapper(*args):
        if utils.check_file_exists(package_file):
            return func(*args)
        else:
            print '\'package.yml\' isn\'t exists'
            exit(0)
    return wrapper

def write_conf(package_file, package_file_data):
    '''
    Write file
    :param package_file: string
    :param package_file_data: dict
    :return:
    '''
    try:
        if os.path.dirname(package_file) and not os.path.exists(os.path.dirname(package_file)):
            os.makedirs(os.path.dirname(package_file))
        with open(package_file, 'wb') as yaml_file:
            yaml.dump(package_file_data, yaml_file, default_flow_style=False)
            yaml_file.close()
    except OSError as err:
        print err

@check_file_exists
def read_conf():
    '''
    Read project package.yml
    :return:
    '''
    try:
        with open(package_file) as yaml_file:
            data = yaml.load(yaml_file)
            yaml_file.close()
            return data
    except:
        'Open \'package.yml\' with an error'
        exit(0)

def packages_manage(package_file_data, manage, targets = None, is_dev = False):

    def cover_pkg(pkg):
        '''
        pkg to {pkgName: pkgVersion}
        :param pkgs:
        :return:
        '''
        matchObj = re.match(r'(.*?)==(.*)', pkg, re.M | re.I)
        if (matchObj):
            return {matchObj.group(1): matchObj.group(2)}
        return {pkg: 'latest'}

    dependencies = package_file_data['dependencies'] if 'dependencies' in package_file_data else {}
    dev_dependencies = package_file_data['devDependencies'] if 'devDependencies' in package_file_data else {}
    if manage == Manage.GET:
        all_dependencies = dependencies.copy()
        all_dependencies.update(dev_dependencies)
        result = [key + ('==' +  value if value != 'latest' else '') for key, value in all_dependencies.items()]
        return result
    elif manage == Manage.ADD:
        for target in targets:
            pkg = cover_pkg(target)
            pkg_key = pkg.keys()[0]
            if is_dev:
                dev_dependencies.update(pkg)
                package_file_data['devDependencies'] = dev_dependencies
                if pkg_key in dependencies:
                    del dependencies[pkg_key]
            else:
                dependencies.update(pkg)
                package_file_data['dependencies'] = dependencies
                if pkg_key in dev_dependencies:
                    del dev_dependencies[pkg_key]
        return package_file_data
    elif manage == Manage.REMOVE:
        for target in targets:
            pkg = cover_pkg(target)
            pkg_key = pkg.keys()[0]
            if pkg_key in dependencies:
                del dependencies[pkg_key]
                package_file_data['dependencies'] = dependencies
            if pkg_key in dev_dependencies:
                del dev_dependencies[pkg_key]
                package_file_data['devDependencies'] = dev_dependencies
            if package_file_data.has_key('dependencies') and len(package_file_data['dependencies']) < 1:
                del package_file_data['dependencies']
            if package_file_data.has_key('devDependencies') and len(package_file_data['devDependencies']) < 1:
                del package_file_data['devDependencies']
        return package_file_data
    elif manage == Manage.REMOVEALL:
        if len(dependencies.keys()):
            del package_file_data['dependencies']
        if len(dev_dependencies.keys()):
            del package_file_data['devDependencies']
        return package_file_data
    elif manage == Manage.UPDATE:
        if is_dev:
            for key in dev_dependencies.keys():
                dev_dependencies[key] = 'latest'
        else:
            for key in dependencies.keys():
                dependencies[key] = 'latest'
        return package_file_data

# cmd: init
def init(params):
    '''
    Project initialation

    package.yml base conf
    - name
    - version
    - author
    '''

    if not utils.check_file_exists(os.path.join(params.name, package_file) if params.name else package_file):
        package_file_data = {}
        package_file_data['name'] = params.name if params.name else project_name
        package_file_data['author'] = getpass.getuser()
        package_file_data['version'] = '1.0.0' # version formating: [project version].[feature version].[bug version]
        write_conf(os.path.join(params.name, package_file) if params.name else package_file, package_file_data)

        if params.env:
            virtualenv = {
                'cmd': 'virtualenv',
                'args': [
                    os.path.join(os.getcwd(), os.path.dirname(os.path.join(params.name, package_file) if params.name else package_file), 'venv')
                ]
            }

            if params.sys:
                virtualenv['args'].append('--system-site-packages')
            if params.nosys:
                virtualenv['args'].append('--no-site-packages')

            args = virtualenv['args']

            args.insert(0, virtualenv['cmd'])

            cmd_string = ' '.join(args)

            if not utils.cmd_with_check_os_value(cmd_string):
                cmd = 'source {0}'.format(os.path.join(os.path.dirname(os.path.join(params.name, package_file) if params.name else package_file), 'venv', 'bin', 'activate'))
                print 'Enter command \'{0}\' to start your project.'.format(cmd)
    else:
        print 'package.yml already exists'
        exit(0)

# cmd: install
@check_file_exists
def install(params):
    '''
    Install python package with pip
    '''
    package_file_data = read_conf()

    if params['packages'] == '*' if type(params) == dict else params.packages == '*':
        packages = packages_manage(package_file_data, Manage.GET)
        if len(packages) > 0:
            utils.cmd_with_check_os_value('pip install {0}'.format(' '.join(packages)))
    else:
        package_file_data = packages_manage(package_file_data, Manage.ADD, params.packages, params.dev)
        if not utils.cmd_with_check_os_value('pip install {0}'.format(' '.join(params.packages))):
            write_conf(package_file, package_file_data)

# cmd: uninstall
@check_file_exists
def uninstall(params):
    package_file_data = read_conf()

    if params.packages == '*':
        packages = packages_manage(package_file_data, Manage.GET)
        package_file_data = packages_manage(package_file_data, Manage.REMOVEALL)
        if not utils.cmd_with_check_os_value('pip uninstall {0}'.format(' '.join(packages))):
            write_conf(package_file, package_file_data)
    else:
        package_file_data = packages_manage(package_file_data, Manage.REMOVE, params.packages)
        if not utils.cmd_with_check_os_value('pip uninstall {0}'.format(' '.join(params.packages))):
            write_conf(package_file, package_file_data)

# cmd: udpate
@check_file_exists
def update(params):
    package_file_data = read_conf()
    if params['packages'] == '*' if type(params) == dict else params.packages == '*':
        package_file_data = packages_manage(package_file_data, Manage.UPDATE, None, params.dev)
    else:
        package_file_data = packages_manage(package_file_data, Manage.UPDATE, params.packages, params.dev)

    packages = packages_manage(package_file_data, Manage.GET)
    if len(packages) > 0:
        if not utils.cmd_with_check_os_value('pip install -U {0}'.format(' '.join(packages))):
            write_conf(package_file, package_file_data)

# cmd: version
def version(params):
    print 'version: {0}'.format(VERSION)

# cmd: run
@check_file_exists
def run(params):
    scripts_key = params.cmd
    package_file_data = read_conf()
    if package_file_data.has_key('scripts'):
        scripts = package_file_data['scripts']
        if scripts_key in scripts.keys():
            utils.cmd_with_check_os_value(scripts[scripts_key])
        else:
            print 'missing script: {0}'.format(scripts_key)
    else:
        print 'there\'s no scripts'

# app main
# @check_argv
def main():
    '''
    App entry
    '''

    # cmd: init
    parser_initial = subparsers.add_parser('init', help='project initialization')
    parser_initial.add_argument('name', help='set the initial project name', nargs='?')
    parser_initial.add_argument('--env', '-e', help='need virtual env', action='store_true')
    # Todo: support change python version
    parser_initial.add_argument('--sys', '-s', help='system site package', action='store_true')
    parser_initial.add_argument('--nosys', '-ns', help='system site package', action='store_true')
    parser_initial.set_defaults(func=init)

    # cmd: install
    parser_install = subparsers.add_parser('i', help='install python package with pip')
    parser_install.add_argument('packages', help='install package with pip', nargs='*', default='*')
    parser_install.add_argument('--dev', '-d', help='install package with pip for dev env', action='store_true')
    parser_install.add_argument('--index-url', '-i', help='base url of python package index (default https://pypi.org/simple).')
    parser_install.set_defaults(func=install)

    # cmd: uninstall
    parser_uninitial = subparsers.add_parser('ui', help='uninstall python package with pip')
    parser_uninitial.add_argument('packages', help='uninstall package with pip', nargs='*', default='*')
    parser_uninitial.set_defaults(func=uninstall)

    # cmd: update
    parser_update = subparsers.add_parser('u', help='update package with pip')
    parser_update.add_argument('packages', help='update package with pip', nargs='*', default='*')
    parser_update.add_argument('--dev', '-d', help='install package with pip for dev env', action='store_true')
    parser_update.set_defaults(func=update)

    # cmd: version
    parser_version = subparsers.add_parser('version', help='scv version')
    parser_version.set_defaults(func=version)

    # cmd: run
    parser_run = subparsers.add_parser('run', help='run user script')
    parser_run.add_argument('cmd', help='run user script for current')
    parser_run.set_defaults(func=run)

    if not sys.argv[1:]:
        parser.print_help()
        exit(0)

    # parse
    args = parser.parse_args()
    args.func(args)

# CLI entry
if __name__ == '__main__':
    main()
__version__ = "0.4.6"
import os
import sys
import time
from microlab.io.yaml import create_yaml, read_yaml
from microlab.io.files import delete_file, file_exist
from microlab.io.folders import create_folder, folder_exist
from microlab import hardware, network, software
from microlab.network import Network_manager, lan_ip

class Node:
    debug = False
    is_loaded = False
    workspace = {'name': 'workspace',
                 'version': '0.1',
                 'path': os.getcwd(),
                 'tests': {},
                 'packages': {}
                }
    memory = {'path': '',
              'examples': '',
              'python': '',
              'shutdown': '',
              'reboot': '',
              'cancel': '',
              }
    colors = {'green': "\033[0;32m",
              'blue': "\033[0;34m",
              'default': "\033[0m"}

    def __init__(self):
        if sys.platform == 'linux':
            self.memory['path'] = "/".join(os.path.abspath(__file__).split("/")[:-1])
            self.memory['shutdown'] = 'sudo shutdown -h now'
            self.memory['reboot'] = 'sudo reboot'
            self.memory['python'] = 'python3'
            self.memory['pip'] = 'python3 -m pip'

        else:
            self.memory['path'] = "\\".join(os.path.abspath(__file__).split("\\")[:-1])
            self.memory['shutdown'] = 'shutdown.exe -s -t 10'
            self.memory['reboot'] = 'shutdown.exe -r -t 10'
            self.memory['cancel'] = 'shutdown.exe -a'
            self.memory['python'] = 'python'
            self.memory['pip'] = 'python -m pip'

            # remove colors on terminal
            for color_name, color in self.colors.items():
                self.colors[color_name] = ''

        self.memory['examples'] = os.path.join(self.memory['path'], 'examples')

        self.microlab_tests = {
            'monitoring': os.path.join(self.memory['examples'], 'hardware', 'monitoring.py'),

            'file': os.path.join(self.memory['examples'], 'io', 'file_C.R.U.D.py'),
            'json': os.path.join(self.memory['examples'], 'io', 'json_C.R.U.D.py'),
            'csv': os.path.join(self.memory['examples'], 'io', 'csv_C.R.U.D.py'),
            'yaml': os.path.join(self.memory['examples'], 'io', 'yaml_C.R.U.D.py'),
            'zip': os.path.join(self.memory['examples'], 'io', 'zip_C.R.U.D.py'),

            'signal 1-D': os.path.join(self.memory['examples'], 'signals', '1d.py'),
            'signal 2-D': os.path.join(self.memory['examples'], 'signals', '2d.py'),

            'interpolation': os.path.join(self.memory['examples'], 'methods', 'interpolation.py'),
            'intersection': os.path.join(self.memory['examples'], 'methods', 'Intersection.py'),

            'symetric': os.path.join(self.memory['examples'], 'cryptography', 'symmetric.py'),
            'asymetric': os.path.join(self.memory['examples'], 'cryptography', 'asymmetric.py'),
        }

        self.workspace_load()

    ''' Workspace '''
    def workspace_load(self):
        """
                Load the workspace from yaml file
        :return:
        """
        try:
            # auto fix workspace directory
            workspace_file = read_yaml(path='workspace', verbose=False)
            if workspace_file['workspace']['path'] != os.getcwd():
                print('fixing workspace directory')
                workspace_file['workspace']['path'] = os.getcwd()
                create_yaml(path='workspace', data=workspace_file, verbose=False)
            # reload the warkspace
            workspace_file = read_yaml(path='workspace', verbose=False)
            self.workspace = workspace_file['workspace']
            self.workspace['packages'] = self.load_packages(verbose=False)
            self.is_loaded = True
            if self.debug:
                print('[ {} ]   workspace loaded'.format(self.workspace['name']))
                print('[ {} ]   memory loaded'.format(self.workspace['name']))

        except Exception as e:
            self.is_loaded = False
            if self.debug:
                print('[ {} ]   no workspace found in {}'.format(self.workspace['name'], os.getcwd()))
                print('[ exception] {}'.format(e))

    def workspace_save(self):
        create_yaml(path='workspace',
                    data={'workspace': self.workspace},
                    verbose=False)

    def workspace_clean(self):
        """
                Clean the workspace yaml file
        :return:
        """
        self.workspace['tests'] = {}
        self.workspace['packages'] = {}
        delete_file(path='workspace', verbose=False)

    def workspace_status(self):
        """
                show the status of the workspace
        :return:
        """
        if self.is_loaded:
            print('[ {} ]  workspace    {}'.format(self.workspace['name'], self.workspace['path']))
            print('[ {} ]  version      {}'.format(self.workspace['name'], self.workspace['version']))
            print('[ {} ]  packages     {}'.format(self.workspace['name'], self.workspace['packages'].keys().__len__()))
            print('[ {} ]  tests        {}'.format(self.workspace['name'], self.workspace['tests'].keys().__len__()))
        else:
            print('this directory is not a workspace{}'.format(self.workspace['path']))

    def workspace_rename(self, name, on_memory=False):
        """
                Rename the workspace
        :param name:
        :param on_memory:
        :return:
        """
        self.workspace['name'] = name
        if not on_memory:
            self.workspace_save()
            self.workspace_load()

    def workspace_reversion(self, new_version):
        """
                    change the version of the workspace
        :param version:
        :return:
        """
        self.workspace['version'] = new_version
        self.workspace_save()
        self.workspace_load()

    def workspace_create(self,name):
        """
                Create a workspace folder and sub folders and also the yaml file
        :param name:
        :return:
        """
        if self.is_loaded:
            print('you are already in a workspace')
        else:
            _workspace = os.path.join(os.getcwd(), name)
            _src = os.path.join(_workspace, 'src')
            _scripts = os.path.join(_workspace, 'scripts')
            _tests = os.path.join(_workspace, 'tests')
            _file = os.path.join(_workspace, 'workspace')

            if not folder_exist(path=_workspace, verbose=False):
                create_folder(path=_workspace, verbose=True)
                create_folder(path=_src, verbose=True)
                create_folder(path=_scripts, verbose=True)
                create_folder(path=_tests, verbose=True)
                self.workspace_rename(name=name, on_memory=False)
                create_yaml(path=_file, data={'workspace': self.workspace}, verbose=True)
                print('[ {} ]  created'.format(self.workspace['name']))
            else:
                print('[ {} ]  folder exist'.format(name))

    def workspace_packages(self,):
        """
                Show all packages in workspace
        :return:
        """
        for package_name, package in self.workspace['packages'].items():
            print('[  {}  ]  '.format(package_name))
            for field, value in package.items():
                print('     {} : {}'.format(field, value))

    ''' Tests '''
    def workspace_tests(self):
        for test_name, test_path in self.workspace['tests'].items():
            print('[  {}  ]     {}'.format(test_name, test_path))
        for test_name, test_path in self.microlab_tests.items():
            print('[  {}  ]     {}'.format(test_name, test_path))

    def test_start(self, arg):
        if arg in self.workspace['tests']:
            test_python_scrypt = self.workspace['tests'][arg]
            if sys.platform == 'linux':
                os.system('python3 {} '.format(test_python_scrypt))
            else:
                os.system('python {} '.format(test_python_scrypt))

    def start_microlab_test(self, arg):
        # start a microlab Test
        if arg in self.microlab_tests:
            test_python_scrypt = self.microlab_tests[arg]
            if sys.platform == 'linux':
                os.system('python3 {} '.format(test_python_scrypt))
            else:
                os.system('python {} '.format(test_python_scrypt))

    ''' Packages '''
    def load_packages(self,verbose=False):
        """
                    Load all packages in workspace src folder
        :param verbose:
        :return:
        """
        _src = os.path.join(self.workspace['path'], 'src')
        if verbose:
            print('loading packages in {}'.format(_src))
        pkgs = {}
        if folder_exist(path=_src, verbose=False):
            if verbose:
                print('Packages: {}'.format(_src))
            for package_name in os.listdir(_src):
                _package = os.path.join(_src, package_name)
                _package_file = os.path.join(_package, 'package')

                if verbose:
                    print('[ {} ] package {} found'.format(self.workspace['name'], package_name))
                try:

                    temp = read_yaml(path=_package_file, verbose=False)

                    # auto fix the directory of each package
                    if temp['package']['directory'] != _package:
                        temp['package']['directory'] = _package
                        create_yaml(data=temp, path=_package_file)

                    # load the package
                    pkgs[package_name] = read_yaml(path=_package_file, verbose=False)['package']
                except:
                    print('[ {} ] description damaged on package {}'.format(self.workspace['name'], package_name))
        return pkgs

    def package_create(self, package):
        """
                    Create a package while you are inside of the workspace
        :param package:
        :return:
        """
        if self.is_loaded:
            _workspace = os.path.join(os.getcwd())
            _src = os.path.join(_workspace, 'src')
            _scripts = os.path.join(_workspace, 'scripts')
            _tests = os.path.join(_workspace, 'tests')
            _file = os.path.join(_workspace, 'workspace')

            _package = os.path.join(_src, package['name'])
            _package_src = os.path.join(_package, 'src')
            _package_scripts = os.path.join(_package, 'scripts')
            _package_tests = os.path.join(_package, 'tests')
            _package_file = os.path.join(_package, 'package')

            if not folder_exist(path=_package, verbose=False):
                create_folder(path=_package, verbose=True)
                create_folder(path=_package_src, verbose=True)
                create_folder(path=_package_scripts, verbose=True)
                create_folder(path=_package_tests, verbose=True)
                package['directory'] = _package
                create_yaml(path=_package_file, data={'package': package}, verbose=True)
                print('[ {} ]  package {} created'.format(self.workspace['name'], package['name']))

            else:
                print('[ {} ]  folder exist {}'.format(package['name'], _package))

        else:
            print('you are not in the directory of a workspace')

    def package_install(self, arg):
        if arg in self.workspace['packages']:
            package_name = arg
            package = self.workspace['packages'][package_name]
            print('[  {}  ]     is installing'.format(package_name))
            if sys.platform == 'linux':
                full_path = os.path.join(package['directory'])
                command = '{} install -r {}/requirements.txt'.format(self.memory['pip'], full_path)
            else:
                os.chdir(package['directory'])
                command = '{} {}'.format(self.memory['python'], package['installer'])
            print('[  {}  ]     COMMAND: {}'.format(package_name, command))
            os.system(command)

    def package_uninstall(self, arg):
        if arg in self.workspace['packages']:
            package_name = arg
            package = self.workspace['packages'][package_name]
            print('[  {}  ]     is installing'.format(package_name))
            if sys.platform == 'linux':
                full_path = os.path.join(package['directory'], package['uninstaller'])
                command = 'python3 {}'.format(full_path)
            else:
                os.chdir(package['directory'])
                command = 'python {}'.format(package['uninstaller'])
            print('[  {}  ]     COMMAND: {}'.format(package_name, command))
            os.system(command)

    def package_start(self,arg):
        if arg in self.workspace['packages']:
            package_name = arg
            package = self.workspace['packages'][package_name]
            print('[  {}  ]     is starting'.format(package_name))
            if sys.platform == 'linux':
                full_path = os.path.join(package['directory'], package['executor'])
                command = 'python3 {} {}'.format(full_path, package['arguments'])
            else:
                # os.chdir(package['directory'])
                full_path = os.path.join(package['directory'], package['executor'])
                command = 'python {} {}'.format(full_path, package['arguments'])
            print('[  {}  ]     COMMAND: {}'.format(package_name, command))
            os.system(command)

    def start_microlab_test(self,arg):
        # start a microlab Test
        if arg in self.microlab_tests:
            test_python_scrypt = self.microlab_tests[arg]
            if sys.platform == 'linux':
                os.system('python3 {} '.format(test_python_scrypt))
            else:
                os.system('python {} '.format(test_python_scrypt))

    ''' Plugins '''
    def monitor(self):
        os.system('cls')
        while True:
            time.sleep(1)
            hw = hardware.statistics()
            print('\r CPU:      {}%  RAM:       {}% '.format(hw['cpu']['percent'], hw['ram']['percent']), end=' ')

    def network(self):
        net = network.statistics()
        print(' Hostname  :{} \n Username  :{} \n Localhost :{} \n Lan       :{} \n Wan       :{}'.format(net['hostname'],net['username'],net['localhost'], net['lan'], net['wan']))

    def software(self):
        soft = software.statistics()
        print(' CV2      :{} \n OS       :{} \n Python   :{}'.format(soft['cv'], soft['os'], soft['python']))

    def scan(self):
        nm = Network_manager()
        nm.scan_network(ip=lan_ip(), mask='24')
        nm.online()
        # nm.offline()

    ''' OS '''
    def shutdown(self):
        os.system(self.memory['shutdown'])

    def reboot(self):
        os.system(self.memory['reboot'])

    def cancel(self):
        os.system(self.memory['cancel'])

    ''' Python '''
    def python(self):
        return self.memory['python']


    ''' Pip '''
    def pip(self):
        return self.memory['pip']

    def pip_install(self, module):
        os.system('{} install {}'.format(self.memory['pip'], module))

    def pip_uninstall(self, module):
        os.system('{} uninstall {} -y'.format(self.memory['pip'], module))

    def pip_upgrade(self, module):
        os.system('{} install {} --upgrade'.format(self.memory['pip'], module))

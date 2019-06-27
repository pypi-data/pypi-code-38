from __future__ import print_function

import os
import sys

from fabric.api import env

from burlap.shelf import Shelf
from burlap.context import set_cwd
from burlap.common import set_verbose, get_verbose
from burlap.deploy import deploy as deploy_satchel
from burlap import load_role_handler
from burlap.common import all_satchels
from burlap.tests.functional_tests.base import TestCase

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '../../..'))

class DeployTests(TestCase):

    #TODO:re-enable once deploy rewrite merged
    def _test_deploy(self):
        """
        Creates a multi-site Apache Django powered web server with a MySQL backend.
        """
        try:
            set_verbose(True)
            assert 'apache_specifics' in env

            print('all_satchels:', sorted(all_satchels.keys()))
            assert len(all_satchels.keys()) == 61
            print('env.host_string:', env.host_string)
            print('env.hosts:', env.hosts)
            print('env.user:', env.user)
            assert env.host_string
            assert env.user

            # Delete any old tmp files
            PROJECT_DIR = '/tmp/burlap_test'
            if os.path.exists(PROJECT_DIR):
                #shutil.rmtree(PROJECT_DIR)
                os.system('rm -Rf %s/*' % PROJECT_DIR)
            else:
                os.makedirs(PROJECT_DIR)

            # Create our test virtualenv.
            PYTHON_EXE = os.path.split(sys.executable)[-1]
            VIRTUALENV_DIR = os.path.join(PROJECT_DIR, '.env')
            BURLAP_DIR = os.path.abspath(os.path.join(BASE_DIR, 'burlap'))
            BURLAP_BIN = os.path.abspath(os.path.join(BASE_DIR, 'bin/burlap-admin.py'))
            SITE_PACKAGES = os.path.join(VIRTUALENV_DIR, 'lib/%s/site-packages' % PYTHON_EXE)

            # Initialize project.
            kwargs = dict(
                project_dir=PROJECT_DIR,
                burlap_bin=BURLAP_BIN,
            )
            print('Initializing project skeleton...')
            assert os.path.isdir(PROJECT_DIR)
            with set_cwd(PROJECT_DIR):

                _status, _output = self.bash('{burlap_bin} skel multitenant'.format(**kwargs))
                print('_status, _output:', _status, _output)
                assert not _status

                # Symlink burlap.
                _status, _output = self.bash('ln -s %s %s' % (BURLAP_DIR, SITE_PACKAGES))
                #assert not _status

                # Add production role.
                VIRTUALENV_ACTIVATE = '. %s/bin/activate' % VIRTUALENV_DIR
                kwargs = dict(
                    project_dir=PROJECT_DIR,
                    activate=VIRTUALENV_ACTIVATE,
                    burlap_bin=BURLAP_BIN,
                )
                assert os.path.isdir(PROJECT_DIR)

                _status, _output = self.bash('{burlap_bin} add-role prod'.format(**kwargs))
                assert not _status

                # Test logging in to VM.
                print('env.host_string:', env.host_string)
                print('env.user:', env.user)
                print('env.key_filename:', env.key_filename)
                env.ROLE = 'prod'
                prod_settings = Shelf(filename='%s/roles/{role}/settings.yaml' % PROJECT_DIR)
                prod_settings['hosts'] = [env.host_string]
                assert prod_settings['hosts'][0]
                #prod_settings['host_string']
                prod_settings['user'] = env.user
                prod_settings['key_filename'] = env.key_filename
                prod_settings['is_local'] = False
                prod_settings['app_name'] = 'multitenant'
                kwargs = dict(
                    project_dir=PROJECT_DIR,
                )
                self.bash('ls -lah .')
                assert os.path.isdir(PROJECT_DIR)

                print('Testing hello world...')
                _status, _output = self.bash('.env/bin/fab prod:verbose=1 shell:command="echo hello"'.format(**kwargs))
                print('_status, _output:', _status, _output)
                assert not _status
                _status, _output = self.bash('ls -lah .')
                print('_status, _output:', _status, _output)

                print('Testing ifconfig...')
                _status, _output = self.bash('.env/bin/fab prod:verbose=1 shell:command="ifconfig"'.format(**kwargs))
                print('_status, _output:', _status, _output)
                assert 'inet addr:127.0.0.1' in _output

                # Add services.
                services = prod_settings.get('services', [])
                services.extend([
                    'apache',
                    #'hostname',
                    'mysql',
                    'mysqlclient',
                    'ntpclient',
                    'packager',
                    'pip',
                    'sshnice',
                    'tarball',
                    'timezone',
                    'ubuntumultiverse',
                    'unattendedupgrades',
                    #'user',
                ])
                prod_settings.set('services', services)
                prod_settings.set('sites', {
                    'multitenant': {
                        'apache_domain_template': 'multitenant.test.com',
                        'apache_domain_with_sub_template': 'multitenant.test.com',
                        'apache_domain_without_sub_template': 'multitenant.test.com',
                        'apache_server_aliases_template': 'multitenant.test.com',
                        'apache_ssl': False,
                        'apache_auth_basic': False,
                        'apache_enforce_subdomain': False,
                    },
                })
                prod_settings.set('pip_requirements', 'pip-requirements.txt')
                prod_settings.set('packager_initial_upgrade', False)

                # Confirm deployment changes are detected.
                #from burlap import role_prod as prod
                prod = load_role_handler('prod')
                prod()
                assert 'app_name' in env
                assert 'sites' in env
                env.host_string = env.hosts[0]

                print('-'*80)
                set_verbose(1)
                assert 'apache_specifics' in env
                print('Getting changed_components.verbose:', get_verbose())
                changed_components, deploy_funcs = deploy_satchel.get_component_funcs()
                changed_components = sorted(changed_components)
                expected_components = [
                    'APACHE',
                    'MYSQL',
                    'MYSQLCLIENT',
                    'NTPCLIENT',
                    'PACKAGER',
                    'PIP',
                    'SSHNICE',
                    'TARBALL',
                    'TIMEZONE',
                    'UBUNTUMULTIVERSE',
                    'UNATTENDEDUPGRADES',
                ]
                print('changed_components:', changed_components)
                print('expected_components:', expected_components)
                assert changed_components == expected_components
                deploy_funcs = sorted(deploy_funcs)
                print('deploy_funcs:', deploy_funcs)
                assert deploy_funcs == [
                    ('apache.configure', None),
                    ('mysql.configure', None),
                    ('mysqlclient.configure', None),
                    ('ntpclient.configure', None),
                    ('packager.configure', None),
                    ('pip.configure', None),
                    ('sshnice.configure', None),
                    ('tarball.configure', None),
                    ('timezone.configure', None),
                    ('ubuntumultiverse.configure', None),
                    ('unattendedupgrades.configure', None),
                ]

            # Deploy changes.

            # Confirm changes have been cleared.

            # Add Django site.

        finally:
            # Undo changes to the VM.
            pass

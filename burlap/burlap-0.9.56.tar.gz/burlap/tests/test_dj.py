from __future__ import print_function

import os
#import re
import shutil
import getpass
import traceback

from fabric.contrib.files import append
from fabric.api import settings
from fabric.exceptions import NetworkError

import burlap
from burlap.common import env
from burlap.tests.base import TestCase
from burlap.project import project
from burlap.context import set_cwd
from burlap.deploy import STORAGE_LOCAL

class DjTests(TestCase):

    def test_migrate(self):

        burlap_dir = os.path.abspath(os.path.split(burlap.__file__)[0])

        src_dir = '/tmp/test_dj_migrate/src'

        dj_version = [1, 10, 6]

        d = '/tmp/test_dj_migrate'
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)

        activate_cmd = '. {d}/.env/bin/activate;'.format(d=d)
        with set_cwd(d):
            project.create_skeleton(
                project_name='test_dj_migrate',
                roles='prod',
                components='dj',
                dj_version='.'.join(map(str, dj_version)),
            )

            assert not os.path.isfile('/tmp/test_dj_migrate/plans/prod/000/thumbprints/test-dj-migrate-1')
            assert not os.path.isfile('/tmp/test_dj_migrate/plans/prod/000/thumbprints/test-dj-migrate-2')

            # Simulate multiple remote hosts my creating aliases of localhost.
            # Note, for testing this on your localhost for a user without passwordless sudo,
            # you may have to run: `sudo chmod 777 /etc/hosts`
            # This won't work on Travis, where these will instead be set in .travis.yml.
            print('Modifying /etc/hosts...')
            env.host_string = 'localhost'
            env.hosts = [env.host_string]
            env.user = getpass.getuser()
            with settings(warn_only=True):
                for use_sudo in (False, True):
                    print('Trying with use_sudo:', use_sudo)
                    try:
                        ret = append(filename='/etc/hosts', text='127.0.0.1 test-dj-migrate-1', use_sudo=use_sudo)
                        ret = append(filename='/etc/hosts', text='127.0.0.1 test-dj-migrate-2', use_sudo=use_sudo)
                        if ret is None:
                            break
                    except NetworkError:
                        print('Error modifying /etc/hosts using use_sudo=%s:' % use_sudo)
                        traceback.print_exc()

            os.system('ln -s %s %s/' % (burlap_dir, d))

            project.update_settings({
                    'plan_storage': STORAGE_LOCAL,
                    'plan_data_dir': os.path.join(d, 'plans'),
                    'services': ['dj'],
                    'dj_settings_module': 'test_dj_migrate.settings',
                    'default_site': 'testsite1',
                    'default_role': 'prod',
                    'dj_local_project_dir': 'src',
                    'dj_project_dir': '%s/src' % d,
                    'dj_manage_media': False,
                    'dj_manage_migrations': True,
                    'dj_manage_cmd': '%s/.env/bin/python manage.py' % d,
                    'dj_version': dj_version,
                    # This is necessary to stop get_current_hostname() from attempting to lookup our actual hostname.
                    '_ip_to_hostname': {
                        'test-dj-migrate-1': 'test-dj-migrate-1',
                        'test-dj-migrate-2': 'test-dj-migrate-2',
                    },
                },
                role='all')

            project.update_settings({
                    'hosts': ['test-dj-migrate-1', 'test-dj-migrate-2'],
                    'available_sites_by_host':{
                        'test-dj-migrate-1': [
                            'testsite1',
                        ],
                        'test-dj-migrate-2': [
                            'testsite2',
                        ]
                    },
                    'sites': {
                        'testsite1': {
                            'apache_domain_template': 'testsite1.test-dj-migrate-1.com',
                        },
                        'testsite2': {
                            'apache_domain_template': 'testsite2.test-dj-migrate-2.com',
                        },
                    },
                },
                role='prod')

            # Confirm both hosts are shown.
            kwargs = dict(
                activate_cmd=activate_cmd,
            )
            status, output = self.getstatusoutput('{activate_cmd} fab prod debug.list_hosts'.format(**kwargs))
            print('output:', output)
            assert 'test-dj-migrate-1' in output
            assert 'test-dj-migrate-2' in output

            #TODO:renable once deploy rewrite merged
            # Migrate built-in apps.
            #kwargs = dict(
                #activate_cmd=activate_cmd,
            #)
            #status, output = self.getstatusoutput('{activate_cmd} fab prod deploy.run:yes=1,verbose=0'.format(**kwargs))
            #assert not status
            ## The migrations should have been run on both hosts.
            #assert '[test-dj-migrate-1] run:' in output
            #assert '[test-dj-migrate-2] run:' in output
            #assert os.path.isfile('/tmp/test_dj_migrate/plans/prod/000/thumbprints/test-dj-migrate-1')
            #assert os.path.isfile('/tmp/test_dj_migrate/plans/prod/000/thumbprints/test-dj-migrate-2')

            ## Create custom app.
            #kwargs = dict(
                #src_dir='/tmp/test_dj_migrate/src',
                #activate_cmd=activate_cmd,
            #)
            #status, output = self.getstatusoutput('{activate_cmd} cd {src_dir}; python manage.py startapp myapp'.format(**kwargs))
            #assert os.path.isdir('/tmp/test_dj_migrate/src/myapp')

            ## Add myapp to installed apps list.
            #settings_fn = '/tmp/test_dj_migrate/src/test_dj_migrate/settings.py'
            #with open(settings_fn) as fin:
                #settings_text = fin.read()
            #p = re.compile(r'INSTALLED_APPS = \[([^\]]+)', flags=re.MULTILINE)
            #settings_text = p.sub(r"INSTALLED_APPS = [\1    'myapp',\n", settings_text)
            #with open(settings_fn, 'w') as fout:
                #fout.write(settings_text)
            #status, output = self.getstatusoutput('cd {src_dir}/test_dj_migrate; rm -f *.pyc'.format(**kwargs))
            #assert not status

            ## Confirm the correct version of Django was installed.
            #kwargs = dict(
                #src_dir=src_dir,
                #activate_cmd=activate_cmd,
            #)
            #status, output = self.getstatusoutput('{activate_cmd} cd {src_dir}; pip freeze | grep Django'.format(**kwargs))
            #assert '.'.join(map(str, dj_version)) in output

            ## Populate model.
            #open('/tmp/test_dj_migrate/src/myapp/models.py', 'w').write('''
#from __future__ import unicode_literals

#from django.db import models

#class MyModel(models.Model):
    #pass

#''')
            #kwargs = dict(
                #src_dir='/tmp/test_dj_migrate/src',
                #activate_cmd=activate_cmd,
            #)
            #status, output = self.getstatusoutput('{activate_cmd} cd {src_dir}; python manage.py makemigrations myapp'.format(**kwargs))
            #assert os.path.isfile('/tmp/test_dj_migrate/src/myapp/migrations/0001_initial.py')

            ## Apply migrations.
            #kwargs = dict(
                #activate_cmd=activate_cmd,
            #)
            ##cmd = '{activate_cmd} fab prod deploy.show_diff'.format(activate_cmd=activate_cmd)
            ##cmd = '{activate_cmd} fab prod deploy.run'.format(activate_cmd=activate_cmd)
            ##status, output = self.getstatusoutput('{activate_cmd} fab prod dj.configure:dryrun=1,verbose=1'.format(**kwargs))
            #status, output = self.getstatusoutput('{activate_cmd} fab prod deploy.run:yes=1'.format(**kwargs))
            #print('output:', output)
            #assert not status
            ## The migrations should have been run on both hosts.
            #assert ('test-dj-migrate-1] run: export SITE=testsite1; export ROLE=prod; cd /tmp/test_dj_migrate/src; '
                #'/tmp/test_dj_migrate/.env/bin/python manage.py migrate') in output
            #assert ('test-dj-migrate-2] run: export SITE=testsite2; export ROLE=prod; cd /tmp/test_dj_migrate/src; '
                #'/tmp/test_dj_migrate/.env/bin/python manage.py migrate') in output

            #assert os.path.isfile('/tmp/test_dj_migrate/plans/prod/001/thumbprints/test-dj-migrate-1')
            #assert os.path.isfile('/tmp/test_dj_migrate/plans/prod/001/thumbprints/test-dj-migrate-2')

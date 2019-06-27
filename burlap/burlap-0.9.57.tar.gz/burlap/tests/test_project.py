from __future__ import print_function
import os
import sys
# import tempfile
import shutil # pylint: disable=unused-import
try:
    from commands import getstatusoutput
except ImportError:
    from subprocess import getstatusoutput

import yaml

from burlap.common import set_verbose, find_template, render_to_string
from burlap.tests.base import TestCase
from burlap.context import set_cwd

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

class ProjectTests(TestCase):

    def setUp(self):
        super(ProjectTests, self).setUp()

        set_verbose(True)
        # Ensure we're in burlap's root directory.
        os.chdir(os.path.abspath(os.path.join(CURRENT_DIR, '../..')))

    #TODO:re-enable after deploy merged
    def _test_project(self):
        try:
            project_dir = '/tmp/burlap_test_project'#tempfile.mkdtemp()
            if not os.path.isdir(project_dir):
                os.makedirs(project_dir)
            bin_dir = os.path.split(sys.executable)[0]

            with set_cwd(project_dir):
                cmd = (
                    '. {bin_dir}/activate; '
                    'burlap-admin.py skel myproject'
                ).format(**locals())
                print(cmd)
                ret = os.system(cmd)
                print('ret:', ret)
                assert not ret

                cmd = (
                    '. {bin_dir}/activate; '
                    'burlap-admin.py add-role prod dev'
                ).format(**locals())
                print(cmd)
                ret = os.system(cmd)
                print('ret:', ret)
                assert not ret

                if not os.path.isdir('satchels'):
                    os.makedirs('satchels')
                os.system('touch satchels/__init__.py')
                open('satchels/junk.py', 'w').write("""
from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task

class JunkSatchel(Satchel):

    name = 'junk'

    def set_defaults(self):
        self.env.param = 'default'

    @task
    def show_param(self):
        print('param:%s' % self.env.param)

    @task
    def configure(self):
        self.show_param()

junk = JunkSatchel()
""")

                open('roles/all/settings.yaml', 'w').write(yaml.dump(dict(
                    app_name='myproject_site',
                    default_site='myproject',
                    services=['junk'],
                    sites={},
                    junk_param='allvalue',
                )))

                open('roles/prod/settings.yaml', 'w').write(yaml.dump(dict(
                    inherits='all',
                    hosts=['localhost'],
                    junk_enabled=True,
                    junk_param='prodvalue',
                )))

                open('roles/dev/settings.yaml', 'w').write(yaml.dump(dict(
                    inherits='all',
                    hosts=['localhost'],
                    junk_enabled=True,
                    junk_param='devvalue',
                )))

                ## Check prod role.

                os.system('rm -Rf .burlap')
                cmd = (
                    '. {bin_dir}/activate; '
                    'fab prod junk.show_param'
                ).format(**locals())
                print(cmd)
                status, output = getstatusoutput(cmd)
                print('output:', output)
                assert 'param:prodvalue' in output

                os.system('rm -Rf .burlap')
                cmd = (
                    '. {bin_dir}/activate; '
                    'fab prod deploy.preview:verbose=1'
                ).format(**locals())
                print(cmd)
                status, output = getstatusoutput(cmd)
                print('output:', output)
                assert 'junk.configure' in output

                os.system('rm -Rf .burlap')
                cmd = (
                    '. {bin_dir}/activate; '
                    'fab prod deploy.run:yes=1'
                ).format(**locals())
                print(cmd)
                status, output = getstatusoutput(cmd)
                print('output:', output)
                assert 'param:prodvalue' in output

                ## Check dev role.

                os.system('rm -Rf .burlap')
                cmd = (
                    '. {bin_dir}/activate; '
                    'fab dev junk.show_param'
                ).format(**locals())
                print(cmd)
                status, output = getstatusoutput(cmd)
                print('output:', output)
                assert 'param:devvalue' in output

                os.system('rm -Rf .burlap')
                cmd = (
                    '. {bin_dir}/activate; '
                    'fab dev deploy.preview'
                ).format(**locals())
                print(cmd)
                status, output = getstatusoutput(cmd)
                print('output:', output)
                assert 'junk.configure' in output

                os.system('rm -Rf .burlap')
                cmd = (
                    '. {bin_dir}/activate; '
                    'fab dev deploy.run:yes=1'
                ).format(**locals())
                print(cmd)
                status, output = getstatusoutput(cmd)
                print('output:', output)
                assert 'param:devvalue' in output

        finally:
            #shutil.rmtree(project_dir)
            pass


    def test_find_template(self):
        fn = 'burlap/gitignore.template'
        ret = find_template(fn)
        print('ret:', ret)
        assert ret and ret.endswith(fn)


    def test_render_to_string(self):
        ret = render_to_string(
            'postfix/etc_postfix_sasl_sasl_passwd',
            dict(
                postfix_host='smtp.test.com',
                postfix_port=1234,
                postfix_username='myusername',
                postfix_password='mypassword',
            ))
        print('ret:', ret)
        assert ret == "[smtp.test.com]:1234 myusername:mypassword"

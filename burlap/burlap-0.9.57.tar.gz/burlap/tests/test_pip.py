from __future__ import print_function

import os
import shutil
try:
    from commands import getoutput
except ImportError:
    from subprocess import getoutput

from burlap.constants import *
from burlap.common import get_satchel
from burlap.tests.base import TestCase
from burlap.context import set_cwd


class PipTests(TestCase):

    def test_pip_install(self):
        pip_satchel = get_satchel('pip')
        try:
            # Initialize tmp directory.
            d = '/tmp/test_pip_install'
            if os.path.isdir(d):
                shutil.rmtree(d)
            os.makedirs(d)

            # Install pip requirements.
            with set_cwd(d):

                # Create requirements file.
                os.makedirs('roles/all')
                with open('roles/all/pip-requirements.txt', 'w') as fout:
                    print('PyYAML\n', file=fout)

                # Install without the quiet flag
                pip_satchel.verbose = GLOBAL_VERBOSE
                pip_satchel.env.quiet_flag = ''
                pip_satchel.env.virtualenv_dir = '%s/.env' % d
                pip_satchel.configure()

                self.assertTrue(os.path.isdir(pip_satchel.env.virtualenv_dir))
                ret = getoutput('%s/bin/pip freeze | grep -i yaml' % pip_satchel.env.virtualenv_dir)
                print('pip freeze:\n', ret)
                self.assertTrue('PyYAML' in ret)

                # Delete the virtualenv.
                shutil.rmtree(os.path.join(d, '.env'))

                # Install with the quiet flag
                pip_satchel.verbose = GLOBAL_VERBOSE
                pip_satchel.env.quiet_flag = ' -q '
                pip_satchel.configure()

                self.assertTrue(os.path.isdir('.env'))
                ret = getoutput('.env/bin/pip freeze | grep -i yaml')
                print('pip freeze:\n', ret)
                self.assertTrue('PyYAML' in ret)

        finally:
            shutil.rmtree(d)

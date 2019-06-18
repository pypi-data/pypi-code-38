from __future__ import print_function

import os
import tempfile

from fabric.contrib.files import exists

from burlap.buildbot import buildbot
from burlap.tests.functional_tests.base import TestCase

class BuildbotTests(TestCase):

    def test_cron_check(self):
        try:
            # Create a mock deployment settings directory.
            deploy_from_dir = tempfile.mkdtemp()
            print('deploy_from_dir:', deploy_from_dir)
            os.makedirs(os.path.join(deploy_from_dir, 'roles/all'))
            os.makedirs(os.path.join(deploy_from_dir, 'roles/local'))
            os.makedirs(os.path.join(deploy_from_dir, buildbot.env.src_dir))
            os.chdir(deploy_from_dir)

            buildbot.genv.ROLE = 'local'
            buildbot.genv.services = ['buildbot']
            buildbot.clear_caches()

            #TODO:fix? deprecated?
            #buildbot.env.cron_check_enabled = True
            #buildbot.env.cron_check_worker_pid_path = '/usr/local/myproject/src/buildbot/worker/twistd.pid'
            #buildbot.update_cron_check()

            #assert exists(buildbot.env.cron_check_command_path)
            #assert exists(buildbot.env.cron_check_crontab_path)

            #self.fake(components=buildbot.name)

            #buildbot.env.cron_check_enabled = False
            #buildbot.update_cron_check()

            assert not exists(buildbot.env.cron_check_command_path)
            assert not exists(buildbot.env.cron_check_crontab_path)
        finally:
            buildbot.uninstall_cron_check()

    def test_configure(self):
        try:

            # Create a mock deployment settings directory.
            deploy_from_dir = tempfile.mkdtemp()
            print('deploy_from_dir:', deploy_from_dir)
            os.makedirs(os.path.join(deploy_from_dir, 'all'))
            with open(os.path.join(deploy_from_dir, 'all', 'apt-requirements.txt'), 'w') as fout:
                fout.write('python-dev\npython3-dev\n')
            with open(os.path.join(deploy_from_dir, 'all', 'pip-requirements.txt'), 'w') as fout:
                fout.write('buildbot[bundle]==0.9.5\n')

            # Prevent buildbot from upgrading and rebooting the server.
            packager = buildbot.get_satchel('packager')
            packager.env.initial_upgrade = False
            #packager.env.manage_custom = False

            pip = buildbot.get_satchel('pip')
            pip.env.check_permissions = False

            print('Installing Apache packages...')
            apache = buildbot.get_satchel('apache')
            apache.install_packages()

            buildbot.genv.ROLE = 'local'
            buildbot.genv.ROLES_DIR = deploy_from_dir
            buildbot.env.user = buildbot.genv.user
            buildbot.env.group = buildbot.genv.user
            buildbot.genv.services = ['buildbot']
            buildbot.clear_caches()

            buildbot.env.cron_check_enabled = True
            buildbot.env.cron_check_worker_pid_path = '/usr/local/myproject/src/buildbot/worker/twistd.pid'
            buildbot.verbose = True
#             buildbot.configure()#TODO

#             assert exists(buildbot.env.cron_check_command_path)
#             assert exists(buildbot.env.cron_check_crontab_path)
#
#             self.fake(components=buildbot.name)
#
#             buildbot.env.cron_check_enabled = False
#             buildbot.configure()
#
#             assert not exists(buildbot.env.cron_check_command_path)
#             assert not exists(buildbot.env.cron_check_crontab_path)
        finally:
            buildbot.uninstall()

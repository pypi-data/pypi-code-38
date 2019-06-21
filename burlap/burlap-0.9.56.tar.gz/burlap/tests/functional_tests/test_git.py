from __future__ import print_function

from fabric.contrib.files import exists
from fabric.context_managers import cd
from fabric.api import run

from burlap.common import set_verbose
from burlap.git import git
from burlap.tests.functional_tests.base import TestCase
from burlap.deploy import deploy as deploy_satchel
#from burlap.deploy import thumbprint, clear_fs_cache, delete_plan_data_dir
#from burlap.packager import packager

class GitTests(TestCase):

    def test_hooks(self):

        set_verbose(True)
        git.genv.ROLE = 'prod'
        git.genv.services = ['git']
        git.clear_caches()

        print('Installing git...')
        git.install_packages() # fails on Ubuntu 14 under Travis-CI?

        print('Setting up sample git repo...')
        run('mkdir /tmp/mygithookrepo || true')
        with cd('/tmp/mygithookrepo'):
            run('git init')
        assert not exists('/tmp/mygithookrepo/.git/hooks/post-checkout')

        print('Configuring git...')
        git.env.enabled = True
        git.env.hooks = {'/tmp/mygithookrepo': ['git/post-checkout']}
        git.clear_local_renderer()
        deploy_satchel.purge()
        cm = git.current_manifest
        print('cm1:', cm)
        assert 'hooks' in cm

        added_hooks, removed_hooks = git.get_changed_hooks()
        print('added_hooks:', added_hooks)
        assert added_hooks == {'/tmp/mygithookrepo': ['git/post-checkout']}
        print('removed_hooks:', removed_hooks)
        assert removed_hooks == {}

        print('Installing git hooks...')
        git.clear_local_renderer()
        git.configure()
        deploy_satchel.purge()
        print('-'*80)
        print('Thumbprinting...')
        #thumbprint(components=git.name)
        deploy_satchel.fake(components=git.name)
        print('-'*80)

        assert exists('/tmp/mygithookrepo/.git/hooks/post-checkout')

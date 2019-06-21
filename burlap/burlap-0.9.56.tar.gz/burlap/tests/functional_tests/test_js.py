from __future__ import print_function

#from fabric.contrib.files import exists

from burlap.common import set_verbose
from burlap.js import jshint
from burlap.tests.functional_tests.base import TestCase
from burlap.deploy import deploy as deploy_satchel

class JSTests(TestCase):

    def test_jshint0(self):
        pass

    def test_jshint1(self):

        set_verbose(True)
        jshint.genv.ROLE = 'local'
        jshint.genv.services = ['jshint']
        jshint.clear_caches()

#         packager.update()
#         packager.upgrade(full=1)

        print('Installing jshint...')
        jshint.env.enabled = True
        jshint.clear_local_renderer()
        #jshint.install_packages() # fails on Ubuntu 14 under Travis-CI?
        #jshint.sudo('apt-get purge nodejs-legacy nodejs')
        #jshint.sudo('apt-get update --fix-missing; DEBIAN_FRONTEND=noninteractive apt-get -f -o Dpkg::Options::="--force-overwrite" install --yes npm')
        jshint.configure()
        deploy_satchel.purge()
        print('-'*80)
        print('Thumbprinting...')
        deploy_satchel.fake(components=jshint.name)
        print('-'*80)

        # Confirm jshint was installed.
        #assert exists('/usr/local/bin/jshint')
        output = jshint.run('jshint --version')
        print('output:', output)
        assert 'jshint v' in output

        print('Disabling jshint...')
        jshint.env.enabled = False
        jshint.clear_local_renderer()
        jshint.configure()

        # Confirm jshint was uninstalled.
        #assert not exists('/usr/local/bin/jshint')

    def test_jshint2(self):
        pass

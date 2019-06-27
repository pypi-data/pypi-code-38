"""
Run specific tests like:

    tox -c tox-full.ini -e py27-ubuntu_14_04_64 -- -s burlap/tests/functional_tests/test_selenium.py::SeleniumTests::test_selenium

"""
from fabric.contrib.files import exists

from burlap.common import set_verbose
from burlap.selenium import selenium
from burlap.tests.functional_tests.base import TestCase
from burlap.deploy import deploy as deploy_satchel

class SeleniumTests(TestCase):

    def test_paths(self):
        print('deploy_satchel.env.lockfile_path:', deploy_satchel.env.lockfile_path)
        print('deploy_satchel.env.data_dir:', deploy_satchel.env.data_dir)
        assert deploy_satchel.env.lockfile_path == '/tmp/burlap_unittests/deploy.lock'
        assert deploy_satchel.env.data_dir == '/tmp/burlap_unittests'
        assert deploy_satchel.manifest_filename == '/tmp/burlap_unittests/manifest.yaml'

    def test_selenium(self):
        try:
            print('deploy_satchel.env.lockfile_path:', deploy_satchel.env.lockfile_path)
            print('deploy_satchel.env.data_dir:', deploy_satchel.env.data_dir)
            assert deploy_satchel.env.lockfile_path == '/tmp/burlap_unittests/deploy.lock'
            assert deploy_satchel.env.data_dir == '/tmp/burlap_unittests'
            assert deploy_satchel.manifest_filename == '/tmp/burlap_unittests/manifest.yaml'

            set_verbose(True)
            print('selenium.geckodriver_path:', selenium.geckodriver_path)
            selenium.genv.ROLE = 'local'
            selenium.genv.services = ['selenium']
            selenium.clear_caches()

            print('Enabling selenium/gecko to install and track old version.')
            print('selenium._last_manifest.1:', selenium._last_manifest)
            print('selenium.last_manifest.1:', selenium.last_manifest)
            selenium.env.enabled = True
            selenium.env.geckodriver_version = '0.13.0'
            selenium.clear_local_renderer()
            assert selenium.get_target_geckodriver_version_number() == '0.13.0'
            print('Configuring selenium...')
            selenium.configure()
            print('selenium._last_manifest.2:', selenium._last_manifest)
            print('selenium.last_manifest.2:', selenium.last_manifest)
            print('Writing manifest...')
            deploy_satchel.fake(components=selenium.name)
            deploy_satchel.run('ls -lah %s' % deploy_satchel.manifest_filename)
            deploy_satchel.run('cat %s' % deploy_satchel.manifest_filename)
            print('selenium._last_manifest.3:', selenium._last_manifest)
            print('selenium.last_manifest.3:', selenium.last_manifest)

            print('Confirming install succeeded...')
            assert exists(selenium.geckodriver_path)
            assert not selenium.check_for_change()
            output = selenium.run('geckodriver --version')
            print('Geckodriver version:', output)
            expected_version = selenium.env.geckodriver_version
            assert expected_version in output

            print('Updating configuration to track the most recent version...')
            selenium.env.geckodriver_version = None
            selenium.clear_local_renderer()
            assert selenium.get_target_geckodriver_version_number() != '0.13.0'
            assert selenium.last_manifest.fingerprint == '0.13.0'

            print('Confirm we now see a pending change...')
            assert selenium.check_for_change()

            print('-'*80)
            print('Applying change...')
            selenium.configure()
            deploy_satchel.purge()
            print('-'*80)
            print('Thumbprinting...')
            deploy_satchel.fake(components=selenium.name)
            print('-'*80)

            print('Confirming the most recent version was installed...')
            expected_version = selenium.get_most_recent_version()
            selenium.clear_caches()
            assert selenium.last_manifest.fingerprint == expected_version
            output = selenium.run('geckodriver --version')
            expected_version = selenium.get_latest_geckodriver_version_number()
            assert expected_version in output
            assert not selenium.check_for_change()

            print('Update configuration to not manage gecko and apply...')
            selenium.env.enabled = False
            selenium.clear_local_renderer()
            selenium.configure()

            # Confirm gecko was uninstalled.
            assert not exists(selenium.geckodriver_path)

        finally:
            selenium.uninstall_geckodriver()

    def test_selenium_2(self):
        print('deploy_satchel.env.lockfile_path:', deploy_satchel.env.lockfile_path)
        print('deploy_satchel.env.data_dir:', deploy_satchel.env.data_dir)
        assert deploy_satchel.env.lockfile_path == '/tmp/burlap_unittests/deploy.lock'
        assert deploy_satchel.env.data_dir == '/tmp/burlap_unittests'
        assert deploy_satchel.manifest_filename == '/tmp/burlap_unittests/manifest.yaml'

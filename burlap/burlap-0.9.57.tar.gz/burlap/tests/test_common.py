"""
Tests for the common module.

Run like:

    tox -c tox-full.ini -e py27-ubuntu_16_04_64 -- -s burlap/tests/test_common.py::CommonTests::test_satchel_ordering

"""
from __future__ import print_function

import os
import sys
import tempfile
import unittest
import getpass
from pprint import pprint

import six

from burlap import load_yaml_settings
from burlap.common import CMD_VAR_REGEX, CMD_ESCAPED_VAR_REGEX, shellquote, all_satchels, Satchel, env, get_satchel, clear_state, save_env, env
from burlap.decorators import task
from burlap.tests.base import TestCase

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

class _TestSatchel(Satchel):

    name = 'test'

    def configure(self):
        pass

class CommonTests(TestCase):

    def get_test_satchel(self):
        test = _TestSatchel()
        test.genv.hosts = ['localhost']
        test.genv.host_string = test.genv.hosts[0]
        return test

    def setUp(self):
        super(CommonTests, self).setUp()

        # Importing ourself register us in sys.modules, which burlap uses to track satchels.
        # This is necessary to instantiate this satchel when running this testcase separately.
        import test_common # pylint: disable=import-self

        env.hosts = ['localhost']
        env.host_string = env.hosts[0]
        env.user = getpass.getuser()
        env.always_use_pty = False

    def test_shellquote(self):

        s = """# /etc/cron.d/anacron: crontab entries for the anacron package

    SHELL=/bin/bash
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

    # minute hour day month weekday (0-6, 0 = Sunday) user command

    */5 * * * *   root    {command}
    """

        s = shellquote(s)

    def test_format_regex(self):

        test = self.get_test_satchel()

        assert CMD_VAR_REGEX.findall('{cmd} {host}') == ['cmd', 'host']

        assert CMD_VAR_REGEX.findall("{cmd} {host} | {awk_cmd} '{{ print $1 }}'") == ['cmd', 'host', 'awk_cmd']

        assert CMD_ESCAPED_VAR_REGEX.findall("{cmd}} {{ print hello }}") == ['{{ print hello }}']

        r = test.local_renderer
        r.env.host = 'myhost'
        r.local("getent {host} | awk '{{ print $1 }}'", dryrun=1)

        s = "rsync --recursive --verbose --perms --times --links --compress --copy-links {exclude_str}  ' \
            '--delete --delete-before --force {rsync_auth} {rsync_source_dir} {rsync_target_host}{rsync_target_dir}"
        assert CMD_VAR_REGEX.findall(s) == ['exclude_str', 'rsync_auth', 'rsync_source_dir', 'rsync_target_host', 'rsync_target_dir']

    def test_settings_include(self):
        try:
            os.makedirs('/tmp/burlap_test/roles/all')
        except OSError:
            pass

        try:
            os.makedirs('/tmp/burlap_test/roles/prod')
        except OSError:
            pass

        open('/tmp/burlap_test/roles/all/settings.yaml', 'w').write("""
only_all_param: "just in all"
overridden_by_prod: 123
overridden_by_local: slkdjflsk
    """)
        open('/tmp/burlap_test/roles/prod/settings.yaml', 'w').write("""inherits: all
overridden_by_prod: 'prod'
only_prod_param: 7891
overriden_by_include: 7892
overridden_by_local: oiuweoiruwo
#includes: [settings_include1.yaml]
includes: [settings_include2.yaml]
    """)
        open('/tmp/burlap_test/roles/prod/settings_include2.yaml', 'w').write("""
overriden_by_include: xyz
overridden_by_local: ovmxlkfsweirwio
    """)
        open('/tmp/burlap_test/roles/prod/settings_local.yaml', 'w').write("""
overridden_by_local: 'hello world'
includes: [settings_include3.yaml]
    """)
        open('/tmp/burlap_test/roles/prod/settings_include3.yaml', 'w').write("""
set_by_include3: 'some special setting'
    """)
        os.chdir('/tmp/burlap_test')
        config = load_yaml_settings(name='prod')

        assert config['includes'] == ['settings_include2.yaml', 'settings_include3.yaml']
        assert config['only_all_param'] == 'just in all'
        assert config['overridden_by_prod'] == 'prod'
        assert config['only_prod_param'] == 7891
        assert config['overriden_by_include'] == 'xyz'
        assert config['overridden_by_local'] == 'hello world'
        assert config['set_by_include3'] == 'some special setting'

    def test_renderer(self):

        test = self.get_test_satchel()

        # Confirm renderer is cached.
        r1 = test.local_renderer
        r2 = test.local_renderer
        assert r1 is r2

        # Confirm clear method.
        test.clear_local_renderer()
        r3 = test.local_renderer
        assert r1 is not r3

        r = r3
        env.clear()
        assert r.genv is env

        # Confirm local env var gets renderered.
        r.env.var1 = 'a'
        assert r.format('{var1}') == 'a'

        # Confirm global env var in local namespace gets rendered.
        env.test_var2 = 'b'
        assert r.format('{var2}') == 'b'

        # Confirm global env var in global namespace gets rendered.
        env.test_var2 = 'b2'
        assert r.format('{test_var2}') == 'b2'

        # Confirm global env var overridden in local namespace get rendered.
        env.apache_var3 = '0'
        r.env.apache_var3 = 'c'
        assert r.format('{apache_var3}') == 'c'

        # Confirm recursive template variables get rendered.
        r.env.some_template = '{target_value}'
        r.env.target_value = 'd'
        assert r.format('{some_template}') == 'd'

        class ApacheSatchel(Satchel):

            name = 'apache'

            def configure(self):
                pass

        apache = ApacheSatchel()
        r = apache.local_renderer
        r.env.application_name = 'someappname'
        r.env.site = 'sitename'
        r.env.wsgi_path = '/usr/local/{apache_application_name}/src/wsgi/{apache_site}.wsgi'
        assert r.format(r.env.wsgi_path) == '/usr/local/someappname/src/wsgi/sitename.wsgi'

    def test_iter_sites(self):

        test = self.get_test_satchel()

        env0 = save_env()
        env.sites = {
            'site1': {'apache_ssl': False, 'site': 'mysite'},
            'site2': {'apache_ssl': True},
        }

        lst = list(test.iter_sites())
        print('lst:', lst)
        assert len(lst) == 2

        lst = list(test.iter_sites(site='site2'))
        print('lst:', lst)
        assert len(lst) == 1

        # Confirm all non-default keys were removed.
        assert set(_ for _ in env0 if not _.startswith('_')) == set(_ for _ in env if not _.startswith('_'))

        site_iter = test.iter_sites()
        six.next(site_iter)
        print('env.SITE:', env.SITE)
        assert env.SITE == 'site1'
        six.next(site_iter)
        print('env.SITE:', env.SITE)
        assert env.SITE == 'site2'

    def test_append(self):

        test = self.get_test_satchel()

        test.genv.host_string = 'localhost'

        _, fn = tempfile.mkstemp()
        text = '[{rabbit, [{loopback_users, []}]}].'
        test.append(filename=fn, text=text)
        content = open(fn).read()
        print('content0:', content)
        assert content.count(text) == 1

        # Confirm duplicate lines are appended.
        test.append(filename=fn, text=text)
        content = open(fn).read()
        print('content1:', content)
        assert content.count(text) == 1

    def test_set_verbose(self):
        from burlap.common import set_verbose, get_verbose

        set_verbose(True)
        assert get_verbose()

        set_verbose(False)
        assert not get_verbose()

        set_verbose(1)
        assert get_verbose()

        set_verbose(0)
        assert not get_verbose()

    def test_satchel_ordering(self):
        from burlap.deploy import deploy as deploy_satchel

        # Purge any pre-existing satchels from global registeries so we only get results for our custom satchels.
        clear_state()

        # These test satchels should be dependent in the order c<-a<-b

        class ASatchel(Satchel):
            name = 'a'
            def set_defaults(self):
                self.env.param = 123
            @task(precursors=['c'])
            def configure(self):
                pass

        class BSatchel(Satchel):
            name = 'b'
            def set_defaults(self):
                self.env.param = 123
            @task(precursors=['a', 'c'])
            def configure(self):
                pass

        class CSatchel(Satchel):
            name = 'c'
            def set_defaults(self):
                self.env.param = 123
            @task
            def configure(self):
                pass

        a_satchel = ASatchel()
        b_satchel = BSatchel()
        c_satchel = CSatchel()
        try:

            assert set(all_satchels) == set(['A', 'B', 'C'])
            deploy_satchel.genv.services = ['a', 'b', 'c']

            #assert init_plan_data_dir() == '.burlap/plans'

            env.ROLE = 'local'
            #components, plan_funcs = deploy.preview(components=['A', 'B', 'C'])
            deploy_satchel.verbose = True
            components, plan_funcs = deploy_satchel.get_component_funcs(components=['A', 'B', 'C'])
            expected_components = ['C', 'A', 'B']
            print()
            print('components:', components)
            print('expected_components:', expected_components)
            print('plan_funcs:', plan_funcs)
            task_names = [_0 for _0, _1 in plan_funcs]
            assert components == expected_components
            assert task_names == ['c.configure', 'a.configure', 'b.configure']

        finally:
            a_satchel.unregister()
            del a_satchel
            with self.assertRaises(KeyError):
                get_satchel('a')
#             import gc
#             refs = gc.get_referrers(a_satchel)
#             print('refs:', refs)
            b_satchel.unregister()
            c_satchel.unregister()

    def test_state_clearing(self):
        from burlap.common import get_state, clear_state, set_state, all_satchels

        actual = sorted(all_satchels.keys())
        print('actual satchels:\n', actual)
        expected = [
            'APACHE', 'AVAHI', 'BLUETOOTH', 'BUILDBOT', 'CELERY', 'CLOUDFRONT', 'CRON',
            'DEBUG', 'DEPLOY', 'DEPLOYMENTNOTIFIER', 'DJ', 'DNS', 'EC2MONITOR', 'ELASTICSEARCH', 'FILE',
            'GIT', 'GITCHECKER', 'GITTRACKER', 'GPSD', 'GROUP', 'HOST', 'HOSTNAME', 'HOSTSFILE',
            'INADYN', 'IP', 'JIRAHELPER', 'JSHINT', 'LOCALES', 'LOGINNOTIFIER', 'MANIFEST', 'MONGODB', 'MOTION', 'MYSQL', 'MYSQLCLIENT', 'NM',
            'NTPCLIENT', 'PACKAGER', 'PHANTOMJS', 'PIP', 'POSTFIX', 'POSTGRESQL', 'POSTGRESQLCLIENT', 'PROJECT',
            'RABBITMQ', 'RDS', 'RPI', 'RSYNC', 'S3', 'SELENIUM', 'SERVICE', 'SNORT', 'SOFTWARERAID',
            'SSHNICE', 'SSL', 'SUPERVISOR', 'TARBALL', 'TIMEZONE', 'UBUNTUMULTIVERSE',
            'UNATTENDEDUPGRADES', 'USER', 'VAGRANT', 'VIRTUALBOX',
        ]
        print('expected satchels:\n', expected)
        assert actual == expected

        burlap_state = get_state()
        print('burlap_state:')
        pprint(burlap_state, indent=4)

        clear_state()
        print('all_satchels.b:', sorted(all_satchels.keys()))
        assert not all_satchels

        set_state(burlap_state)
        print('all_satchels.c:', sorted(all_satchels.keys()))
        assert len(all_satchels) == len(expected)

    def test_runs_once_clear(self):
        from fabric.api import runs_once
        from burlap.debug import debug
        from burlap.common import runs_once_methods

        a = ['abc']

        @runs_once
        def test_func():
            return a[0]

        print('a')
        assert test_func() == 'abc'

        a[0] = 'xyz'
        del test_func.return_value

        print('b')
        assert test_func() == 'xyz'

        print('c')
        a[0] = 'hhh'
        assert test_func() == 'xyz'

        print('debug.shell:', debug.shell)
        #assert hasattr(debug.shell, 'wrapped')
        print('runs_once_methods:', runs_once_methods)


if __name__ == '__main__':
    unittest.main()

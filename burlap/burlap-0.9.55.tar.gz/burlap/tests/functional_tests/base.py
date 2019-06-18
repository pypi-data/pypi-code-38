try:
    from commands import getstatusoutput
except ImportError:
    from subprocess import getstatusoutput

from burlap.tests.base import TestCase as _TestCase
from burlap.deploy import deploy as deploy_satchel #thumbprint, clear_fs_cache, delete_plan_data_dir

class TestCase(_TestCase):

    # These are set in conftest.py before the functional tests are run, and aren't set again,
    # so tell the parent TestCase to not clear them between individual tests.
    keep_env_keys = [
        'host_string',
        'hosts',
        'roles',
        'user',
        'key_filename',
        'disable_known_hosts',
        'abort_on_prompts',
        'always_use_pty',
    ]

    def bash(self, cmd):
        cmd = cmd.replace('"', r'\"')
        s = '/bin/bash -c "%s"' % cmd
        print('cmd:', s)
        return getstatusoutput(s)

    def thumbprint(self, components=None):
        deploy_satchel.purge()
        deploy_satchel.fake(components=components)

"""
Groups
======
"""
from __future__ import print_function

from fabric.api import hide#, run, settings
#from burlap.utils import run_as_root

from burlap.constants import *
from burlap import Satchel
from burlap.decorators import task

class GroupSatchel(Satchel):

    name = 'group'

    @task
    def exists(self, name):
        """
        Check if a group exists.
        """
        with self.settings(hide('running', 'stdout', 'warnings'), warn_only=True):
            return self.run('getent group %(name)s' % locals()).succeeded

    @task
    def create(self, name, gid=None):
        """
        Create a new group.

        Example::

            import burlap

            if not burlap.group.exists('admin'):
                burlap.group.create('admin')

        """
        args = []
        if gid:
            args.append('-g %s' % gid)
        args.append(name)
        args = ' '.join(args)
        self.sudo('groupadd --force %s || true' % args)

    @task
    def configure(self):
        pass

group = GroupSatchel()

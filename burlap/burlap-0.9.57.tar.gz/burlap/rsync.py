from __future__ import print_function

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task

class RsyncSatchel(Satchel):

    name = 'rsync'

    def set_defaults(self):
        self.env.clean = 1
        self.env.gzip = 1
        self.env.exclusions = [
            '*_local.py',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '*.svn',
            '*.tar.gz',
            #'static',
        ]
        self.src_dir = '.'
        #self.env.dir = '.burlap/rsync_cache'
        self.env.extra_dirs = []
        self.env.chown_user = 'www-data'
        self.env.chown_group = 'www-data'
        self.env.command = 'rsync --verbose --compress --recursive --delete ' \
            '--rsh "ssh -i {key_filename}" {exclusions_str} {rsync_src_dir} {user}@{host_string}:{rsync_dst_dir}'

    @task
    def deploy_code(self):
        """
        Generates a rsync of all deployable code.
        """

        assert self.genv.SITE, 'Site unspecified.'
        assert self.genv.ROLE, 'Role unspecified.'

        r = self.local_renderer

        if self.env.exclusions:
            r.env.exclusions_str = ' '.join(
                "--exclude='%s'" % _ for _ in self.env.exclusions)

        r.local(r.env.rsync_command)
        r.sudo('chown -R {rsync_chown_user}:{rsync_chown_group} {rsync_dst_dir}')

    @task
    def configure(self):
        pass

rsync_satchel = RsyncSatchel()

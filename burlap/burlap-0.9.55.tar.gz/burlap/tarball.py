from __future__ import print_function

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task
from burlap.common import only_hostname

RSYNC = 'rsync'

#DEPRECATED: TODO: remove tarball functionality, and rename to CodeSatchel
class TarballSatchel(Satchel):

    name = 'tarball'

    def set_defaults(self):

        self.env.clean = 1

        self.env.gzip = 1

        self.env.method = RSYNC

        self.env.rsync_source_dir = 'src'

        self.env.rsync_source_dirs = [] # This overrides rsync_source_dir

        self.env.rsync_target_dir = None

        self.env.rsync_target_host = '{user}@{host_string}:'

        self.env.rsync_auth = '--rsh "ssh -t -o StrictHostKeyChecking=no -i {key_filename}"'

        self.env.rsync_command_template = (
            'rsync '
            '--recursive --verbose --perms --times --links '
            '--compress --copy-links {exclude_str} '
            '--delete --delete-before --force '
            '{rsync_auth} '
            '{rsync_source_dir} '
            '{rsync_target_host}{rsync_target_dir}'
        )

        self.env.exclusions = [
            '*_local.py',
            '*.pyc',
            '*.svn',
            '*.tar.gz',
            '*.log',
            'twistd.pid',
            '*.sqlite',
        ]

        self.env.dir = '.burlap/tarball_cache'

        self.env.extra_dirs = []

        self.env.perm_user = 'www-data'

        self.env.perm_group = 'www-data'

        self.env.perm_chmod = None

        self.env.set_permissions = True

    @property
    def timestamp(self):
        from burlap.common import get_last_modified_timestamp
        r = self.local_renderer
        fn = r.env.rsync_source_dir
        if self.verbose:
            print('tarball.fn:', fn)
        return get_last_modified_timestamp(fn, ignore=[_ for _ in r.env.exclusions if '/' not in _])

    @task
    def changed(self):
        lm = self.last_manifest
        last_timestamp = lm.timestamp
        current_timestamp = self.timestamp
        self.vprint('last_timestamp:', last_timestamp)
        self.vprint('current_timestamp:', current_timestamp)
        ret = last_timestamp == current_timestamp
        print('NO change' if ret else 'CHANGED!')
        return ret

    def record_manifest(self):
        """
        Called after a deployment to record any data necessary to detect changes
        for a future deployment.
        """
        manifest = super(TarballSatchel, self).record_manifest()
        manifest['timestamp'] = self.timestamp
        return manifest

    @task
    def set_permissions(self):
        r = self.local_renderer
        if r.env.rsync_target_dir:
            if r.env.perm_chmod:
                r.sudo('chmod -R {perm_chmod} {rsync_target_dir}')
            r.sudo('chown -R {perm_user}:{perm_group} {rsync_target_dir}')

    def _run_rsync(self, src, dst):
        print('rsync %s -> %s' % (src, dst))
        r = self.local_renderer
        r.env.hostname = only_hostname(r.genv.host_string)
        real_rsync_target_dir = r.env.rsync_target_dir
        try:
            # Rsync to a temporary directory where we'll have full permissions.
            tmp_dir = '/tmp/tmp_%s_%s' % (self.env.rsync_target_dir.replace('/', '_'), src.replace('/', '_'))
            r.env.rsync_target_dir = tmp_dir
            r.env.rsync_source_dir = src
            r.local(self.env.rsync_command_template)

            # Then rsync from the temp directory as sudo to complete the operation.
            r.env.rsync_source_dir = tmp_dir+'/*'
            r.env.rsync_target_dir = real_rsync_target_dir
            r.env.rsync_target_host = ''
            r.env.rsync_auth = ''
            r.sudo(self.env.rsync_command_template)
        finally:
            r.env.rsync_target_dir = real_rsync_target_dir

    @task
    def deploy_rsync(self, *args, **kwargs):
        r = self.local_renderer

        # Confirm source directories.
        src_dirs = list(self.env.rsync_source_dirs)
        if not src_dirs:
            src_dirs.append(self.env.rsync_source_dir)

        # Confirm target directories.
        assert self.env.rsync_target_dir

        r.env.exclude_str = ' '.join('--exclude=%s' % _ for _ in self.env.exclusions)

        for src_dir in src_dirs:
            self._run_rsync(src=src_dir, dst=self.env.rsync_target_dir)

        if self.env.set_permissions:
            self.set_permissions()

    @task(precursors=['gitchecker', 'packager', 'apache2', 'pip', 'user'])
    def configure(self, *args, **kwargs):
        if self.env.method == RSYNC:
            self.deploy_rsync(*args, **kwargs)

tarball_satchel = TarballSatchel()

deploy = tarball_satchel.configure

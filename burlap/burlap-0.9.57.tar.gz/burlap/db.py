from __future__ import print_function

import os
import sys
import subprocess
from pprint import pprint

from fabric.api import env#, runs_once

from burlap.constants import *
from burlap import ServiceSatchel
from burlap.common import LocalRenderer, pretty_bytes
from burlap.decorators import task, runs_once
from burlap.common import str_to_callable

CONNECTION_HANDLER_DJANGO = 'django'
CONNECTION_HANDLER_CUSTOM = 'custom'

class DatabaseSatchel(ServiceSatchel):

    name = 'db'

    _database_renderers = {} # {(name, site): renderer}

    def set_defaults(self):

        # Local cache for renderers.
        self._database_renderers = {} # {(name, site): renderer}

        # If set, allows remote users to connect to the database.
        # This shouldn't be necessary if the webserver and database
        # share the same server.
        self.env.allow_remote_connections = False

        # Directory where database snapshots will be temporarily stored.
        self.env.dump_dest_dir = '/tmp'

        self.env.dump_archive_dir = 'snapshots'

        # Default filename of database snapshots.
        self.env.dump_fn_template = '{dump_dest_dir}/db_{db_type}_{SITE}_{ROLE}_{db_name}_$(date +%Y%m%d).sql.gz'

        # This overrides the built-in dump command.
        self.env.dump_command = None

        # This overrides the built-in load command.
        self.env.load_command = None

        # {hostname: {username: ?, password: ?}}
        self.env.root_logins = {}

        # Settings for specific databases within the server.
        self.env.databases = {} # {name: {}}

        self.env.default_db_name = 'default'

    def clear_caches(self):
        super(DatabaseSatchel, self).clear_caches()
        self._database_renderers.clear()

    def get_database_defaults(self):
        """
        Returns a dictionary of default settings for each database.
        """
        return dict(
            # {name: None=burlap settings, Django=Django Python settings}
            connection_handler=None,
        )

    @task
    def execute(self, sql, name='default', site=None, **kwargs):
        raise NotImplementedError

    @task
    def execute_file(self, filename, name='default', site=None, **kwargs):
        raise NotImplementedError

    @task
    def set_root_login(self, r):
        """
        Looks up the root login for the given database on the given host and sets
        it to environment variables.

        Populates these standard variables:

            db_root_password
            db_root_username

        """

        # Check the legacy password location.
        try:
            r.env.db_root_username = r.env.root_username
        except AttributeError:
            pass
        try:
            r.env.db_root_password = r.env.root_password
        except AttributeError:
            pass

        # Check the new password location.
        key = r.env.get('db_host')
        if self.verbose:
            print('db.set_root_login.key:', key)
            print('db.set_root_logins:', r.env.root_logins)
        if key in r.env.root_logins:
            data = r.env.root_logins[key]
#             print('data:', data)
            if 'username' in data:
                r.env.db_root_username = data['username']
                r.genv.db_root_username = data['username']
            if 'password' in data:
                r.env.db_root_password = data['password']
                r.genv.db_root_password = data['password']
        else:
            msg = 'Warning: No root login entry found for host %s in role %s.' % (r.env.get('db_host'), self.genv.get('ROLE'))
            print(msg, file=sys.stderr)
            #warnings.warn(msg, UserWarning)

    def database_renderer(self, name=None, site=None, role=None):
        """
        Renders local settings for a specific database.
        """

        name = name or self.env.default_db_name

        site = site or self.genv.SITE

        role = role or self.genv.ROLE

        key = (name, site, role)
        self.vprint('checking key:', key)
        if key not in self._database_renderers:
            self.vprint('No cached db renderer, generating...')

            if self.verbose:
                print('db.name:', name)
                print('db.databases:', self.env.databases)
                print('db.databases[%s]:' % name, self.env.databases.get(name))

            d = type(self.genv)(self.lenv)
            d.update(self.get_database_defaults())
            d.update(self.env.databases.get(name, {}))
            d['db_name'] = name
            if self.verbose:
                print('db.d:')
                pprint(d, indent=4)
                print('db.connection_handler:', d.connection_handler)

            if d.connection_handler == CONNECTION_HANDLER_DJANGO:
                self.vprint('Using django handler...')
                dj = self.get_satchel('dj')
                if self.verbose:
                    print('Loading Django DB settings for site {} and role {}.'.format(site, role), file=sys.stderr)
                dj.set_db(name=name, site=site, role=role)
                _d = dj.local_renderer.collect_genv(include_local=True, include_global=False)

                # Copy "dj_db_*" into "db_*".
                _d = type(_d)({k[3:]: v for k, v in _d.items() if k.startswith('dj_db_')})

                if self.verbose:
                    print('Loaded:')
                    pprint(_d)
                d.update(_d)

            elif d.connection_handler and d.connection_handler.startswith(CONNECTION_HANDLER_CUSTOM+':'):

                _callable_str = d.connection_handler[len(CONNECTION_HANDLER_CUSTOM+':'):]
                self.vprint('Using custom handler %s...' % _callable_str)
                _d = str_to_callable(_callable_str)(role=self.genv.ROLE)
                if self.verbose:
                    print('Loaded:')
                    pprint(_d)
                d.update(_d)

            r = LocalRenderer(self, lenv=d)

            # Optionally set any root logins needed for administrative commands.
            self.set_root_login(r)

            self._database_renderers[key] = r
            self._local_renderer = r
        else:
            self.vprint('Cached db renderer found.')

        return self._database_renderers[key]

    @task
    def configure(self, *args, **kwargs):
        super(DatabaseSatchel, self).configure(*args, **kwargs)

    @task
    def get_free_space(self):
        """
        Return free space in bytes.
        """
        cmd = "df -k | grep -vE '^Filesystem|tmpfs|cdrom|none|udev|cgroup' | awk '{ print($1 \" \" $4 }'"
        lines = [_ for _ in self.run(cmd).strip().split('\n') if _.startswith('/')]
        assert len(lines) == 1, 'Ambiguous devices: %s' % str(lines)
        device, kb = lines[0].split(' ')
        free_space = int(kb) * 1024
        self.vprint('free_space (bytes):', free_space)
        return free_space

    @task
    def get_size(self):
        """
        Retrieves the size of the database in bytes.
        """
        #TODO:remove django hardcoding
#         dj = self.get_satchel('dj')
#         dj.set_db(site=env.SITE, role=env.ROLE)
#         r = self.local_renderer
#         if 'postgres' in self.genv.db_engine or 'postgis' in self.genv.db_engine:
#             output = r.run('psql --user=%(db_postgresql_postgres_user)s --tuples-only -c "SELECT pg_database_size(\'%(db_name)s\');"')
#             output = self.run(cmd)
#             output = int(output.strip().split('\n')[-1].strip())
#             self.vprint('database size (bytes):', output)
#             return output
#         else:
        raise NotImplementedError

    @task
    def load_table(self, table_name, src, dst='localhost', name=None, site=None):
        """
        Directly transfers a table between two databases.
        """
        raise NotImplementedError

    @task
    def load_db_set(self, name, r=None):
        """
        Loads database parameters from a specific named set.
        """
        r = r or self
        db_set = r.genv.db_sets.get(name, {})
        r.genv.update(db_set)

    @task
    def loadable(self, src, dst):
        """
        Determines if there's enough space to load the target database.
        """
        from fabric import state
        from fabric.task_utils import crawl

        src_task = crawl(src, state.commands)
        assert src_task, 'Unknown source role: %s' % src

        dst_task = crawl(dst, state.commands)
        assert dst_task, 'Unknown destination role: %s' % src

        # Get source database size.
        src_task()
        env.host_string = env.hosts[0]
        src_size_bytes = self.get_size()

        # Get target database size, if any.
        dst_task()
        env.host_string = env.hosts[0]
        try:
            dst_size_bytes = self.get_size()
        except (ValueError, TypeError):
            dst_size_bytes = 0

        # Get target host disk size.
        free_space_bytes = self.get_free_space()

        # Deduct existing database size, because we'll be deleting it.
        balance_bytes = free_space_bytes + dst_size_bytes - src_size_bytes
        balance_bytes_scaled, units = pretty_bytes(balance_bytes)

        viable = balance_bytes >= 0
        if self.verbose:
            print('src_db_size:', pretty_bytes(src_size_bytes))
            print('dst_db_size:', pretty_bytes(dst_size_bytes))
            print('dst_free_space:', pretty_bytes(free_space_bytes))
            print
            if viable:
                print('Viable! There will be %.02f %s of disk space left.' % (balance_bytes_scaled, units))
            else:
                print('Not viable! We would be %.02f %s short.' % (balance_bytes_scaled, units))

        return viable

    @task
    def dumpload(self, site=None, role=None):
        """
        Dumps and loads a database snapshot simultaneously.
        Requires that the destination server has direct database access
        to the source server.

        This is better than a serial dump+load when:
        1. The network connection is reliable.
        2. You don't need to save the dump file.

        The benefits of this over a dump+load are:
        1. Usually runs faster, since the load and dump happen in parallel.
        2. Usually takes up less disk space since no separate dump file is
            downloaded.
        """
        raise NotImplementedError

    def render_fn(self, fn):
        return subprocess.check_output('echo %s' % fn, shell=True, universal_newlines=True).strip()

    def get_default_db_fn(self, fn_template=None, dest_dir=None, name=None, site=None):
        r = self.database_renderer(name=name, site=site)
        r.dump_dest_dir = dest_dir

        fn = r.format(fn_template or r.env.dump_fn_template)
        return self.render_fn(fn)

    @task
    @runs_once
    def dump(self, dest_dir=None, to_local=1, from_local=0, archive=0, dump_fn=None, name=None, site=None, use_sudo=0, cleanup=1):
        """
        Exports the target database to a single transportable file on the localhost,
        appropriate for loading using load().
        """
        site = site or self.genv.SITE
        r = self.database_renderer(name=name, site=site)

        # Load optional site-specific command, if given.
        try:
            r.env.dump_command = self.genv.sites[site]['postgresql_dump_command']
        except KeyError:
            pass

        use_sudo = int(use_sudo)

        from_local = int(from_local)

        to_local = int(to_local)

        dump_fn = dump_fn or r.env.dump_fn_template

        # Render the snapshot filename.
        r.env.dump_fn = self.get_default_db_fn(
            fn_template=dump_fn,
            dest_dir=dest_dir,
            name=name,
            site=site,
        )

        # Dump the database to a snapshot file.
        #if not os.path.isfile(os.path.abspath(r.env.dump_fn))):
        r.pc('Dumping database snapshot.')
        if from_local:
            r.local(r.env.dump_command)
        elif use_sudo:
            r.sudo(r.env.dump_command)
        else:
            r.run(r.env.dump_command)

        # Download the database dump file on the remote host to localhost.
        if not from_local and to_local:
            r.pc('Downloading database snapshot to localhost.')
            r.local('rsync -rvz --progress --recursive --no-p --no-g '
                '--rsh "ssh -o StrictHostKeyChecking=no -i {key_filename}" {user}@{host_string}:{dump_fn} {dump_fn}')

            # Delete the snapshot file on the remote system.
            if int(cleanup):
                r.pc('Deleting database snapshot on remote host.')
                r.sudo('rm {dump_fn}')

        # Move the database snapshot to an archive directory.
        if to_local and int(archive):
            r.pc('Archiving database snapshot.')
            db_fn = r.render_fn(r.env.dump_fn)
            r.env.archive_fn = '%s/%s' % (env.db_dump_archive_dir, os.path.split(db_fn)[-1])
            r.local('mv %s %s' % (db_fn, env.archive_fn))

        return r.env.dump_fn

    def upload_snapshot(self, name=None, site=None, local_dump_fn=None, remote_dump_fn=None):
        r = self.database_renderer(name=name, site=site)
        print('Uploading database snapshot...')

        if local_dump_fn:
            r.env.local_dump_fn = local_dump_fn
        elif r.env.dump_fn:
            r.env.local_dump_fn = r.env.dump_fn

        if remote_dump_fn:
            r.env.remote_dump_fn = remote_dump_fn

        r.local('rsync -rvz --progress --no-p --no-g '
            '--rsh "ssh -o StrictHostKeyChecking=no -i {key_filename}" '
            '{local_dump_fn} {user}@{host_string}:{remote_dump_fn}')

    @task
    @runs_once
    def load(self, db_dump_fn='', prep_only=0, force_upload=0, from_local=0):
        """
        Restores a database snapshot onto the target database server.

        If prep_only=1, commands for preparing the load will be generated,
        but not the command to finally load the snapshot.
        """
        raise NotImplementedError

    @task
    def shell(self, name='default', user=None, password=None, root=0, verbose=1, write_password=1, no_db=0, no_pw=0):
        """
        Opens a SQL shell to the given database, assuming the configured database
        and user supports this feature.
        """
        raise NotImplementedError

    @task
    def create(self, **kwargs):
        """
        Creates the target database.
        """
        raise NotImplementedError

    @task
    def drop_views(self, name=None, site=None):
        """
        Drops all views.
        """
        raise NotImplementedError

    @task
    def drop_database(self, name):
        raise NotImplementedError

    @task
    def exists(self, name='default', site=None):
        """
        Returns true if a database with the given name exists. False otherwise.
        """
        raise NotImplementedError

#db = DatabaseSatchel()

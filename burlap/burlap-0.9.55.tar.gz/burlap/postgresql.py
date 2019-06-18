"""
PostgreSQL users and databases
==============================

This module provides tools for creating PostgreSQL users and databases.

"""
from __future__ import print_function

import os

import six

from fabric.api import cd, hide, sudo, settings

from burlap import Satchel
from burlap.constants import *
from burlap.db import DatabaseSatchel
from burlap.decorators import task

POSTGIS = 'postgis'
POSTGRESQL = 'postgresql'

def _run_as_pg(command):
    """
    Run command as 'postgres' user
    """
    with cd('~postgres'):
        return sudo(command, user='postgres')


def user_exists(name):
    """
    Check if a PostgreSQL user exists.
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        res = _run_as_pg('''psql -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = '%(name)s';"''' % locals())
    return (res == "1")


def create_user(name, password, superuser=False, createdb=False,
                createrole=False, inherit=True, login=True,
                connection_limit=None, encrypted_password=False):
    """
    Create a PostgreSQL user.

    Example::

        import burlap

        # Create DB user if it does not exist
        if not burlap.postgres.user_exists('dbuser'):
            burlap.postgres.create_user('dbuser', password='somerandomstring')

        # Create DB user with custom options
        burlap.postgres.create_user('dbuser2', password='s3cr3t',
            createdb=True, createrole=True, connection_limit=20)

    """
    options = [
        'SUPERUSER' if superuser else 'NOSUPERUSER',
        'CREATEDB' if createdb else 'NOCREATEDB',
        'CREATEROLE' if createrole else 'NOCREATEROLE',
        'INHERIT' if inherit else 'NOINHERIT',
        'LOGIN' if login else 'NOLOGIN',
    ]
    if connection_limit is not None:
        options.append('CONNECTION LIMIT %d' % connection_limit)
    password_type = 'ENCRYPTED' if encrypted_password else 'UNENCRYPTED'
    options.append("%s PASSWORD '%s'" % (password_type, password))
    options = ' '.join(options)
    _run_as_pg('''psql -c "CREATE USER %(name)s %(options)s;"''' % locals())


def drop_user(name):
    """
    Drop a PostgreSQL user.

    Example::

        import burlap

        # Remove DB user if it exists
        if burlap.postgres.user_exists('dbuser'):
            burlap.postgres.drop_user('dbuser')

    """
    _run_as_pg('''psql -c "DROP USER %(name)s;"''' % locals())


def database_exists(name):
    """
    Check if a PostgreSQL database exists.
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        return _run_as_pg('''psql -d %(name)s -c ""''' % locals()).succeeded


def create_database(name, owner, template='template0', encoding='UTF8',
                    locale='en_US.UTF-8'):
    """
    Create a PostgreSQL database.

    Example::

        import burlap

        # Create DB if it does not exist
        if not burlap.postgres.database_exists('myapp'):
            burlap.postgres.create_database('myapp', owner='dbuser')

    """
    _run_as_pg('''createdb --owner %(owner)s --template %(template)s \
                  --encoding=%(encoding)s --lc-ctype=%(locale)s \
                  --lc-collate=%(locale)s %(name)s''' % locals())


def create_schema(name, database, owner=None):
    """
    Create a schema within a database.
    """
    if owner:
        _run_as_pg('''psql %(database)s -c "CREATE SCHEMA %(name)s AUTHORIZATION %(owner)s"''' % locals())
    else:
        _run_as_pg('''psql %(database)s -c "CREATE SCHEMA %(name)s"''' % locals())


class PostgreSQLSatchel(DatabaseSatchel):
    """
    Represents a PostgreSQL server.
    """

    name = 'postgresql'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['postgresql-11'],
            (UBUNTU, '12.04'): ['postgresql-9.1'],
            (UBUNTU, '14.04'): ['postgresql-9.3'],
            (UBUNTU, '16.04'): ['postgresql-10'],
        }

    def set_defaults(self):
        super(PostgreSQLSatchel, self).set_defaults()

        # Note, if you use gzip, you can't use parallel restore.
        #self.env.dump_command = 'time pg_dump -c -U {db_user} --no-password --blobs --format=c --schema=public --host={db_host} {db_name} > {dump_fn}'
        self.env.dump_command = 'time pg_dump -c -U {db_user} --no-password --blobs --format=c --schema=public --host={db_host} --dbname={db_name} | ' \
            'gzip -c > {dump_fn}'
        self.env.dump_fn_template = '{dump_dest_dir}/db_{db_type}_{SITE}_{ROLE}_{db_name}_$(date +%Y%m%d).sql.gz'

        #self.env.load_command = 'gunzip < {remote_dump_fn} | pg_restore --jobs=8 -U {db_root_username} --format=c --create --dbname={db_name}'
        self.env.load_command = 'gunzip < {remote_dump_fn} | ' \
            'pg_restore -U {db_root_username} --host={db_host} --format=c --clean --if-exists --schema=public --dbname={db_name}'

        self.env.createlangs = ['plpgsql'] # plpythonu
        self.env.postgres_user = 'postgres'
        self.env.encoding = 'UTF8'
        self.env.locale = 'en_US.UTF-8'
        self.env.custom_load_cmd = ''
        self.env.port = 5432
        self.env.pgpass_path = '~/.pgpass'
        self.env.pgpass_chmod = 600
        self.env.force_version = None
        self.env.version_command = r'`psql --version | grep -m 1 -o -E "[0-9]+\.[0-9]+" | head -1`'
        self.env.engine = POSTGRESQL # 'postgresql' | postgis

        # If true, treats the current database as existing as a schema in a multi-tenant environment,
        # so commands to drop/create the entire database will be replaced with commands to drop/create a schema.
        self.env.schema_mt = False

        self.env.db_root_username = 'postgres'
        self.env.db_root_password = 'password'

        self.env.apt_repo_enabled = False

        # https://askubuntu.com/questions/831292/how-to-install-postgresql-9-6-on-any-ubuntu-version
        # Populated from https://www.postgresql.org/download/linux/ubuntu/
        self.env.apt_repo = None

        self.env.apt_key = 'https://www.postgresql.org/media/keys/ACCC4CF8.asc'

        self.env.service_commands = {
            START:{
                UBUNTU: 'service postgresql start',
            },
            STOP:{
                UBUNTU: 'service postgresql stop',
            },
            ENABLE:{
                UBUNTU: 'update-rc.d postgresql defaults',
            },
            DISABLE:{
                UBUNTU: 'update-rc.d -f postgresql remove',
            },
            RESTART:{
                UBUNTU: 'service postgresql restart',
            },
            STATUS:{
                UBUNTU: 'service postgresql status',
            },
        }

    #https://askubuntu.com/questions/831292/how-to-install-postgresql-9-6-on-any-ubuntu-version
    @property
    def packager_repositories(self):
        ver = self.os_version
        if ver.type == LINUX:
            if ver.distro == UBUNTU:
                if ver.release == '16.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
                if ver.release == '18.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
        raise NotImplementedError

    @task
    def write_pgpass(self, name=None, site=None, use_sudo=0, root=0):
        """
        Write the file used to store login credentials for PostgreSQL.
        """

        r = self.database_renderer(name=name, site=site)

        root = int(root)

        use_sudo = int(use_sudo)

        r.run('touch {pgpass_path}')
        if '~' in r.env.pgpass_path:
            r.run('chmod {pgpass_chmod} {pgpass_path}')
        else:
            r.sudo('chmod {pgpass_chmod} {pgpass_path}')

        if root:
            r.env.shell_username = r.env.get('db_root_username', 'postgres')
            r.env.shell_password = r.env.get('db_root_password', 'password')
        else:
            r.env.shell_username = r.env.db_user
            r.env.shell_password = r.env.db_password

        r.append(
            '{db_host}:{port}:*:{shell_username}:{shell_password}',
            r.env.pgpass_path,
            use_sudo=use_sudo)

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
        r = self.database_renderer(site=site, role=role)
        r.run('pg_dump -c --host={host_string} --username={db_user} '
            '--blobs --format=c {db_name} -n public | '
            'pg_restore -U {db_postgresql_postgres_user} --create '
            '--dbname={db_name}')

    @task
    def drop_views(self, name=None, site=None):
        """
        Drops all views.
        """
        raise NotImplementedError
    #        SELECT 'DROP VIEW ' || table_name || ';'
    #        FROM information_schema.views
    #        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    #        AND table_name !~ '^pg_';
            # http://stackoverflow.com/questions/13643831/drop-all-views-postgresql
    #        DO$$
    #        BEGIN
    #
    #        EXECUTE (
    #           SELECT string_agg('DROP VIEW ' || t.oid::regclass || ';', ' ')  -- CASCADE?
    #           FROM   pg_class t
    #           JOIN   pg_namespace n ON n.oid = t.relnamespace
    #           WHERE  t.relkind = 'v'
    #           AND    n.nspname = 'my_messed_up_schema'
    #           );
    #
    #        END
    #        $$

    @task
    def exists(self, name='default', site=None, use_root=False):
        """
        Returns true if a database with the given name exists. False otherwise.
        """

        r = self.database_renderer(name=name, site=site)

        if int(use_root):
            kwargs = dict(
                db_user=r.env.get('db_root_username', 'postgres'),
                db_password=r.env.get('db_root_password', 'password'),
                db_host=r.env.db_host,
                db_name=r.env.db_name,
            )
            r.env.update(kwargs)

        # Set pgpass file.
        if r.env.db_password:
            self.write_pgpass(name=name, root=use_root)

#        cmd = ('psql --username={db_user} --no-password -l '\
#            '--host={db_host} --dbname={db_name}'\
#            '| grep {db_name} | wc -l').format(**env)

        ret = None
        with settings(warn_only=True):
            ret = r.run('psql --username={db_user} --host={db_host} -l '\
            '| grep {db_name} | wc -l')
            if ret is not None:
                if 'password authentication failed' in ret:
                    ret = False
                else:
                    ret = int(ret.split('\n')[-1]) >= 1

        if ret is not None:
            print('%s database on site %s %s exist' % (name, self.genv.SITE, 'DOES' if ret else 'DOES NOT'))
            return ret

    @task
    def execute(self, sql, name='default', site=None, **kwargs):
        r = self.database_renderer(name=name, site=site)
        r.env.sql = sql
        #r.run('psql --user={postgres_user} --no-password --command="{sql}"')
        r.run('psql --user={db_user} --no-password --host={db_host} -d {db_name} --command="{sql}"')

    @task
    def execute_file(self, filename, name='default', site=None, **kwargs):
        r = self.database_renderer(name=name, site=site)
        #r.env.user = kwargs.pop('user', r.env.db_root_username)
        #r.env.password = kwargs.pop('password', r.env.db_root_password)
        r.env.filename = filename
        #r.run('psql --user={postgres_user} --no-password -d {db_name} -a -f {filename}')
        r.run('psql --user={db_user} --no-password --host={db_host} -d {db_name} -a -f {filename}')

    @task
    def create(self, name='default', site=None, **kargs):

        r = self.database_renderer(name=name, site=site)

        # Create role/user.
        with settings(warn_only=True):
            r.pc('Creating user...')
            r.run('psql --user={postgres_user} --no-password --command="CREATE USER {db_user} WITH PASSWORD \'{db_password}\';"')

        r.pc('Creating database...')
        with settings(warn_only=True):
            ret = r.run('psql --user={postgres_user} --no-password --command="'
                'CREATE DATABASE {db_name} WITH OWNER={db_user} ENCODING=\'{encoding}\' LC_CTYPE=\'{locale}\' LC_COLLATE=\'{locale}\''
            '"')
        if isinstance(ret, six.string_types) and 'ERROR:' in ret and 'already exists' not in ret:
            raise Exception('Error creating database: %s' % ret)

        with settings(warn_only=True):
            r.pc('Enabling plpgsql on database...')
            r.run('createlang -U postgres plpgsql {db_name} || true')

    @task
    #@runs_once Interferes with global methods that want to load multiple databases.
    def load(self, dump_fn='', prep_only=0, force_upload=0, from_local=0, name=None, site=None, dest_dir=None, force_host=None):
        """
        Restores a database snapshot onto the target database server.

        If prep_only=1, commands for preparing the load will be generated,
        but not the command to finally load the snapshot.
        """

        site = site or self.genv.SITE

        r = self.database_renderer(name=name, site=site)

        # Load site-specific satchel settings.
        self.set_site_specifics(site)

        # Render the snapshot filename.
        r.env.dump_fn = self.get_default_db_fn(fn_template=dump_fn, dest_dir=dest_dir)

        from_local = int(from_local)

        prep_only = int(prep_only)

        missing_local_dump_error = r.format("Database dump file {dump_fn} does not exist.")

        # Copy snapshot file to target.
        if self.is_local:
            r.env.remote_dump_fn = dump_fn
        else:
            r.env.remote_dump_fn = '/tmp/' + os.path.split(r.env.dump_fn)[-1]

        if not prep_only and not self.is_local:
            if not self.dryrun:
                assert os.path.isfile(r.env.dump_fn), missing_local_dump_error
            self.upload_snapshot(name=name, site=site, local_dump_fn=r.env.dump_fn, remote_dump_fn=r.env.remote_dump_fn)

        if self.is_local and not prep_only and not self.dryrun:
            assert os.path.isfile(r.env.dump_fn), missing_local_dump_error

        if force_host:
            r.env.db_host = force_host

        with settings(warn_only=True):
            if r.env.schema_mt:
                r.sudo('psql --no-password --user={db_root_username} --host={db_host} --dbname={db_name} -c "DROP SCHEMA IF EXISTS {db_schema};"',
                    user=r.env.postgres_user)
            else:
                r.sudo('dropdb --if-exists --no-password --user={db_root_username} --host={db_host} {db_name}', user=r.env.postgres_user)

        if r.env.schema_mt:
            with settings(warn_only=True):
                r.sudo('psql --no-password --user={db_root_username} --host={db_host} -c "CREATE DATABASE {db_name};"', user=r.env.postgres_user)
            # r.sudo('psql --no-password --user={db_root_username} --host={db_host} --dbname={db_name} -c "CREATE SCHEMA {db_schema};"',
                # user=r.env.postgres_user)
        else:
            r.sudo('psql --no-password --user={db_root_username} --host={db_host} -c "CREATE DATABASE {db_name};"', user=r.env.postgres_user)

        if r.env.engine == POSTGIS:
            with settings(warn_only=True):
                r.sudo('psql --user={db_root_username} --no-password --dbname={db_name} --host={db_host} --command="CREATE EXTENSION postgis;"',
                    user=r.env.postgres_user)
                r.sudo('psql --user={db_root_username} --no-password --dbname={db_name} --host={db_host} --command="CREATE EXTENSION postgis_topology;"',
                    user=r.env.postgres_user)

        if not r.env.schema_mt:
            with settings(warn_only=True):
                r.sudo('psql --user={db_root_username} --host={db_host} -c "REASSIGN OWNED BY {db_user} TO {db_root_username};"', user=r.env.postgres_user)
            with settings(warn_only=True):
                r.sudo('psql --user={db_root_username} --host={db_host} -c "DROP OWNED BY {db_user} CASCADE;"', user=r.env.postgres_user)

        if not self.exists():
            r.sudo('psql --user={db_root_username} --host={db_host} -c "DROP USER IF EXISTS {db_user}; '
                'CREATE USER {db_user} WITH PASSWORD \'{db_password}\';"', user=r.env.postgres_user)
            if not r.env.schema_mt:
                r.sudo('psql --user={db_root_username} --host={db_host} -c "GRANT ALL PRIVILEGES ON DATABASE {db_name} to {db_user};"',
                    user=r.env.postgres_user)
                for createlang in r.env.createlangs:
                    r.env.createlang = createlang
                    r.sudo('createlang -U {db_root_username} --host={db_host} {createlang} {db_name} || true', user=r.env.postgres_user)

        if r.env.schema_mt:
            # This assumes each schema is associated with a unique user.
            r.sudo('psql --user={db_root_username} --host={db_host} --dbname={db_name} -c "'
                'CREATE SCHEMA IF NOT EXISTS {db_schema}; '
                'GRANT ALL PRIVILEGES ON SCHEMA {db_schema} to {db_user}; '
                'ALTER ROLE {db_user} SET search_path TO {db_schema};'
                '"', user=r.env.postgres_user)

        if not prep_only:
            # Ignore errors needed to work around bug "ERROR:  schema "public" already exists", which is thrown in 9.6 even if we use --clean and --if-exists?
            with settings(warn_only=True):
                r.sudo(r.env.load_command, user=r.env.postgres_user)

    @task
    def shell(self, name='default', site=None, **kwargs):
        """
        Opens a SQL shell to the given database, assuming the configured database
        and user supports this feature.
        """
        r = self.database_renderer(name=name, site=site)
        self.write_pgpass(name=name, site=site, root=True)

        db_name = kwargs.get('db_name')
        if db_name:
            r.env.db_name = db_name
            r.run('/bin/bash -i -c "psql --username={db_root_username} --host={db_host} --dbname={db_name}"')
        else:
            r.run('/bin/bash -i -c "psql --username={db_root_username} --host={db_host}"')

    @task
    def configure_apt_repository(self):
        r = self.local_renderer
        r.sudo("add-apt-repository '{apt_repo}'")
        r.sudo('wget --quiet -O - {apt_key} | apt-key add -')
        r.sudo('apt-get update')

    @task
    def drop_database(self, name):
        """
        Delete a PostgreSQL database.

        Example::

            import burlap

            # Remove DB if it exists
            if burlap.postgres.database_exists('myapp'):
                burlap.postgres.drop_database('myapp')

        """
        with settings(warn_only=True):
            self.sudo('dropdb %s' % (name,), user='postgres')

    @task
    def version(self):
        r = self.local_renderer
        if self.dryrun:
            v = r.env.version_command
        else:
            v = (r.run('echo {version_command}') or '').strip()
        print('postgresql version:', v)

        # Postgres 10+ doesn't use minor version in /etc/postgresql/ subdirectory names
        if not v.startswith('9'):
            v = v.split('.')[0]

        print('postgresql subdirectory version:', v)
        return v

    @task
    def load_table(self, table_name, src, dst='localhost', name=None, site=None):
        """
        Directly transfers a table between two databases.
        """
        #TODO: incomplete
        r = self.database_renderer(name=name, site=site)
        r.env.table_name = table_name
        r.run('psql --user={dst_db_user} --host={dst_db_host} --command="DROP TABLE IF EXISTS {table_name} CASCADE;"')
        r.run('pg_dump -t {table_name} --user={dst_db_user} --host={dst_db_host} | psql --user={src_db_user} --host={src_db_host}')

    @task
    def write_pg_hba_conf(self):
        r = self.local_renderer
        if 'pg_version' not in r.env:
            r.env.pg_version = self.version()# or r.env.default_version
        r.pc('Writing pg_hba.conf...')
        r.sudo('cp /etc/postgresql/{pg_version}/main/pg_hba.conf /etc/postgresql/{pg_version}/main/pg_hba.conf.$(date +%Y%m%d%H%M).bak')
        fn = self.render_to_file('postgresql/pg_hba.template.conf')
        r.put(
            local_path=fn,
            remote_path='/etc/postgresql/{pg_version}/main/pg_hba.conf',
            use_sudo=True,
        )

    @task(precursors=['packager', 'user', 'locales'])
    def configure(self, *args, **kwargs):
        #TODO:set postgres user password?
        #https://help.ubuntu.com/community/PostgreSQL
        #set postgres ident in pg_hba.conf
        #sudo -u postgres psql postgres
        #sudo service postgresql restart
        #sudo -u postgres psql
        #\password postgres
        r = self.local_renderer

        #self.install_packages()

        if r.env.apt_repo_enabled:
            self.configure_apt_repository()

        r.env.pg_version = self.version()# or r.env.default_version

        self.write_pg_hba_conf()

#         r.pc('Backing up PostgreSQL configuration files...')
        r.sudo('cp /etc/postgresql/{pg_version}/main/postgresql.conf /etc/postgresql/{pg_version}/main/postgresql.conf.$(date +%Y%m%d%H%M).bak')
        r.pc('Enabling auto-vacuuming...')
        r.sed(
            filename='/etc/postgresql/{pg_version}/main/postgresql.conf',
            before='#autovacuum = on',
            after='autovacuum = on',
            backup='',
            use_sudo=True,
        )
        r.sed(
            filename='/etc/postgresql/{pg_version}/main/postgresql.conf',
            before='#track_counts = on',
            after='track_counts = on',
            backup='',
            use_sudo=True,
        )

        # Set UTF-8 as the default database encoding.
        #TODO:fix? throws error code?
#        sudo_or_dryrun('psql --user=postgres --no-password --command="'
#            'UPDATE pg_database SET datistemplate = FALSE WHERE datname = \'template1\';'
#            'DROP DATABASE template1;'
#            'CREATE DATABASE template1 WITH TEMPLATE = template0 ENCODING = \'UNICODE\';'
#            'UPDATE pg_database SET datistemplate = TRUE WHERE datname = \'template1\';'
#            '\c template1\n'
#            'VACUUM FREEZE;'
#            'UPDATE pg_database SET datallowconn = FALSE WHERE datname = \'template1\';"')

        r.sudo('service postgresql restart')


class PostgreSQLClientSatchel(Satchel):

    name = 'postgresqlclient'

    def set_defaults(self):
        self.env.force_version = None

    @property
    def packager_system_packages(self):
        return {
            FEDORA: ['postgresql-client'],
            UBUNTU: ['postgresql-client-11'],
            (UBUNTU, '12.04'): ['postgresql-client-9.1'],
            (UBUNTU, '14.04'): ['postgresql-client-9.3'],
            (UBUNTU, '16.04'): ['postgresql-client-10'],
        }

    #https://askubuntu.com/questions/831292/how-to-install-postgresql-9-6-on-any-ubuntu-version
    @property
    def packager_repositories(self):
        ver = self.os_version
        if ver.type == LINUX:
            if ver.distro == UBUNTU:
                if ver.release == '16.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
                if ver.release == '18.04':
                    return {
                        APT: ['deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main'],
                        APT_KEY: ['https://www.postgresql.org/media/keys/ACCC4CF8.asc',],
                    }
        raise NotImplementedError

    @task(precursors=['packager'])
    def configure(self, *args, **kwargs):
        pass

postgresql = PostgreSQLSatchel()
PostgreSQLClientSatchel()

write_postgres_pgpass = postgresql.write_pgpass

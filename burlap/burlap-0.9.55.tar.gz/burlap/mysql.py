"""
MySQL users and databases
=========================

This module provides tools for creating MySQL users and databases.

"""
from __future__ import print_function

import os
import re
from pipes import quote

from fabric.api import env, hide, puts, run, settings, runs_once
from fabric.colors import red, green

from burlap import Satchel
from burlap.constants import *
from burlap.db import DatabaseSatchel
from burlap.decorators import task
from burlap.utils import run_as_root

MYSQLD_SAFE = 'mysqld_safe'
MYSQLADMIN = 'mysqladmin'
DPKG = 'dpkg'

class MySQLSatchel(DatabaseSatchel):

    name = 'mysql'

    def __init__(self, *args, **kwargs):
        super(MySQLSatchel, self).__init__(*args, **kwargs)
        self._conf_cache = {}

    @property
    def packager_system_packages(self):
        return {
            FEDORA: ['mysql-server'],
            (UBUNTU, '12.04'): ['mysql-server', 'libmysqlclient-dev'],
            (UBUNTU, '14.04'): ['mysql-server-5.6', 'libmysqlclient-dev'],
            (UBUNTU, '16.04'): ['mysql-server', 'libmysqlclient-dev'],
        }

    def set_defaults(self):
        super(MySQLSatchel, self).set_defaults()

        # You want this to be large, and set in both the client and server.
        # Otherwise, MySQL may silently truncate database dumps, leading to much
        # frustration.
        self.env.max_allowed_packet = 524288000 # 500M

        self.env.net_buffer_length = 1000000

        self.env.dump_command = 'mysqldump --opt --compress --max_allowed_packet={max_allowed_packet} ' \
            '--force --single-transaction --quick --user {db_user} ' \
            '--password="{db_password}" -h {db_host} {db_name} | gzip > {dump_fn}'

        self.env.load_command = 'gunzip < {remote_dump_fn} | mysql -u {db_root_username} ' \
            '--password="{db_root_password}" --host={db_host} -D {db_name}'

        self.env.preload_commands = []
        self.env.character_set = 'utf8'
        self.env.collate = 'utf8_general_ci'
        self.env.port = 3306
        self.env.root_username = 'root'
        self.env.root_password = None
        self.env.custom_mycnf = False

        self.env.assumed_version = '5.7'

        self.env.service_commands = {
            START:{
                UBUNTU: 'service mysql start',
            },
            STOP:{
                UBUNTU: 'service mysql stop',
            },
            ENABLE:{
                UBUNTU: 'update-rc.d mysql defaults',
            },
            DISABLE:{
                UBUNTU: 'update-rc.d -f mysql remove',
            },
            RESTART:{
                UBUNTU: 'service mysql restart',
            },
            STATUS:{
                UBUNTU: 'service mysql status',
            },
        }

        self.env.conf_default = '/etc/mysql/my.cnf' # /etc/my.cnf on fedora
        #self.env.conf = '/etc/mysql/my.cnf' # /etc/my.cnf on fedora
        self.env.conf_specifics = {
            (UBUNTU, '14.04'): '/etc/mysql/my.cnf',
            (UBUNTU, '16.04'): '/etc/mysql/mysql.conf.d/mysqld.cnf',
            FEDORA: '/etc/my.cnf',
        }

    @property
    def conf_path(self):
        """
        Retrieves the path to the MySQL configuration file.
        """
        from burlap.system import distrib_id, distrib_release
        hostname = self.current_hostname
        if hostname not in self._conf_cache:
            self.env.conf_specifics[hostname] = self.env.conf_default
            d_id = distrib_id()
            d_release = distrib_release()
            for key in ((d_id, d_release), (d_id,)):
                if key in self.env.conf_specifics:
                    self._conf_cache[hostname] = self.env.conf_specifics[key]
        return self._conf_cache[hostname]

    @task
    def execute(self, sql, name='default', site=None, **kwargs):
        use_sudo = int(kwargs.pop('use_sudo', 0))
        r = self.database_renderer(name=name, site=site)
        r.env.user = kwargs.pop('user', r.env.db_root_username)
        r.env.password = kwargs.pop('password', r.env.db_root_password)
        r.env.sql = sql
        cmd = "mysql --user={user} -p'{db_root_password}' --execute='{sql}'"
        if use_sudo:
            r.sudo(cmd)
        else:
            r.run(cmd)

    @task
    def execute_file(self, filename, name='default', site=None, **kwargs):
        r = self.database_renderer(name=name, site=site)
        r.env.user = kwargs.pop('user', r.env.db_root_username)
        r.env.password = kwargs.pop('password', r.env.db_root_password)
        r.env.filename = filename
        r.run("mysql --user={user} -p'{db_root_password}' {db_name} < {filename}")

    @task
    def set_collation(self, name=None, site=None):
        r = self.database_renderer(name=name, site=site)
        r.run("mysql -v -h {db_host} -u {db_root_username} -p'{db_root_password}' "
            "--execute='ALTER DATABASE {db_name} CHARACTER SET {character_set} COLLATE {collate};'")

    @task
    def set_collation_all(self, name=None, site=None):
        for _site in self.genv.available_sites:
            self.set_collation(name=name, site=_site)

    @task
    def set_max_packet_size(self, name=None, site=None):
        r = self.database_renderer(name=name, site=site)
        r.run(
            ('mysql -v -h {db_host} -D {db_name} -u {db_root_username} '
            '-p"{db_root_password}" --execute="SET global '
            'net_buffer_length={net_buffer_length}; SET global '
            'max_allowed_packet={max_allowed_packet};"') % env)

    def packager_pre_configure(self):
        """
        Called before packager.configure is run.
        """
        self.prep_root_password()

    #DEPRECATED: no longer works with MySQL > 5.6
    @task
    def prep_root_password(self, password=None, **kwargs):
        """
        Enters the root password prompt entries into the debconf cache
        so we can set them without user interaction.

        We keep this process separate from set_root_password() because we also need to do
        this before installing the base MySQL package, because that will also prompt the user
        for a root login.
        """
        r = self.database_renderer(**kwargs)
        r.env.root_password = password or r.genv.get('db_root_password')
        r.sudo("DEBIAN_FRONTEND=noninteractive dpkg --configure -a")
        r.sudo("debconf-set-selections <<< 'mysql-server mysql-server/root_password password {root_password}'")
        r.sudo("debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password {root_password}'")

    @task
    def get_mysql_version(self):
        return (self.run("dpkg --list | grep -oP '(?<=mysql-server-)([0-9.]+)'") or self.env.assumed_version).split('\n')[-1].strip()

    @task
    def assert_mysql_stopped(self):
        with self.settings(warn_only=True):
            ret = (self.run('ps aux |grep -i mysql|grep -v grep|grep -v vagrant|grep -v python') or '').split('\n')[-1].strip().lower()
        assert 'mysql' not in ret, 'Invalid output indicates MySQL is still running: %s' % ret

    @task
    def set_root_password(self, password=None, method=None, **kwargs):
        method = method or MYSQLD_SAFE#|'mysqladmin'#|'mysqld_safe'|'dpkg'
        v = self.get_mysql_version()
        v = tuple(map(int, v.split('.')))
        self.vprint('mysql version:', v)
        self.vprint('mysql password method:', method)
        if method == MYSQLADMIN:
            r = self.database_renderer(**kwargs)
            r.env.root_password = password or r.env.db_root_password
            r.sudo('mysqladmin -u root password {root_password}')
        elif method == DPKG:
            #TODO:fix? This no longer prompts to set root password with >= 5.7.
            self.prep_root_password(**kwargs)
            r = self.database_renderer(**kwargs)
            r.sudo("dpkg-reconfigure -fnoninteractive `dpkg --list | egrep -o 'mysql-server-([0-9.]+)'`")
        elif method == MYSQLD_SAFE:
            #TODO:fix? unreliable?
            #https://dev.mysql.com/doc/refman/5.7/en/resetting-permissions.html
            r = self.database_renderer(**kwargs)
            r.env.root_password = password or r.env.db_root_password

            # Confirm server stopped.
            self.stop()
            self.assert_mysql_stopped()
            #r.sudo('mysqladmin shutdown')

            r.sudo('mkdir -p /var/run/mysqld')
            r.sudo('chown mysql /var/run/mysqld')

            # Note we have to use pty=False here, otherwise, even with nohup, the process gets killed as soon as the sudo call exits.
            # http://stackoverflow.com/a/27600071/247542
            r.sudo('nohup mysqld_safe --skip-grant-tables &> /tmp/mysqld_safe.log < /dev/null &', pty=False)

            running = False
            for _wait in range(10):
                r.run('sleep 1')
                with self.settings(warn_only=True):
                    ret = (r.run('ps aux|grep -i mysql|grep -v grep|grep -v vagrant') or '').split('\n')[-1].strip()
                if ret:
                    running = True
                    break
            if not running and not self.dryrun:
                raise Exception('Could not launch mysqld_safe.')
            r.run('sleep 5')
            # Work in Ubuntu 16/MySQL 5.7 but not Ubuntu 14/MySQL 5.6?
            with settings(warn_only=True):
                r.run("mysql -uroot --execute=\""
                    "use mysql; "
                    "update user set authentication_string=PASSWORD('{root_password}') where User='root'; "
                    "flush privileges;\"")
            # Work in Ubuntu 14/MySQL 5.6 but not Ubuntu 16/MySQL 5.7?
            with settings(warn_only=True):
                r.sudo('mysql --execute="USE mysql; SET PASSWORD FOR \'root\'@\'localhost\' = PASSWORD(\'{root_password}\'); FLUSH PRIVILEGES;"')

            # Signal server to stop.
            # Note, `sudo service mysql stop` and `sudo /etc/init.d/mysql stop` and `mysqladmin shutdown` don't seem to work with mysqld_safe.
            r.sudo("[ -f /var/run/mysqld/mysqld.pid ] && kill `sudo cat /var/run/mysqld/mysqld.pid` || true")

            # Confirm server stopped.
            r.run('sleep 10')
            self.assert_mysql_stopped()

            self.start()
        else:
            raise NotImplementedError('Unknown method: %s' % method)

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

    @task
    def drop_database(self, name):
        raise NotImplementedError

    @task
    def drop_views(self, name=None, site=None):
        """
        Drops all views.
        """
        r = self.database_renderer
        result = r.sudo("mysql --batch -v -h {db_host} "
            #"-u {db_root_username} -p'{db_root_password}' "
            "-u {db_user} -p'{db_password}' "
            "--execute=\"SELECT GROUP_CONCAT(CONCAT(TABLE_SCHEMA,'.',table_name) SEPARATOR ', ') AS views "
            "FROM INFORMATION_SCHEMA.views WHERE TABLE_SCHEMA = '{db_name}' ORDER BY table_name DESC;\"")
        result = re.findall(
            r'^views[\s\t\r\n]+(.*)',
            result,
            flags=re.IGNORECASE|re.DOTALL|re.MULTILINE)
        if not result:
            return
        r.env.db_view_list = result[0]
        #cmd = ("mysql -v -h {db_host} -u {db_root_username} -p'{db_root_password}' " \
        r.sudo("mysql -v -h {db_host} -u {db_user} -p'{db_password}' " \
            "--execute=\"DROP VIEW {db_view_list} CASCADE;\"")

    @task
    @runs_once
    def exists(self, **kwargs):
        """
        Returns true if a database with the given name exists. False otherwise.
        """
        name = kwargs.pop('name', 'default')
        site = kwargs.pop('site', None)
        r = self.database_renderer(name=name, site=site)
        ret = r.run('mysql -h {db_host} -u {db_root_username} '\
            '-p"{db_root_password}" -N -B -e "SELECT IF(\'{db_name}\''\
            ' IN(SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA), '\
            '\'exists\', \'notexists\') AS found;"')
        if ret is not None:
            ret = 'notexists' not in (ret or 'notexists')
        if ret is not None:
            msg = '%s database on site %s %s exist.' \
                % (name.title(), env.SITE, 'DOES' if ret else 'DOES NOT')
            if ret:
                print(green(msg))
            else:
                print(red(msg))
            return ret

    @task
    @runs_once
    def create(self, **kwargs):
        name = kwargs.pop('name', 'default')
        site = kwargs.pop('site', None)
        drop = int(kwargs.pop('drop', 0))
        #post_process = int(kwargs.pop('post_process', 0))

        r = self.database_renderer(name=name, site=site)

        # Do nothing if we're not dropping and the database already exists.
        print('Checking to see if database already exists...')
        if self.exists(name=name, site=site) and not drop:
            print('Database already exists. Aborting creation. '\
                'Use drop=1 to override.')
            return

        r.env.db_drop_flag = '--drop' if drop else ''

        if int(drop):
            r.sudo("mysql -v -h {db_host} -u {db_root_username} -p'{db_root_password}' "\
                "--execute='DROP DATABASE IF EXISTS {db_name}'")

        r.sudo("mysqladmin -h {db_host} -u {db_root_username} -p'{db_root_password}' create {db_name}")

        self.set_collation(name=name, site=site)

        # Create user.
        with self.settings(warn_only=True):
            r.run("mysql -v -h {db_host} -u {db_root_username} -p'{db_root_password}' "\
                "--execute=\"GRANT USAGE ON *.* TO {db_user}@'%%'; DROP USER {db_user}@'%%';\"")

        # Grant user access to the database.
        r.run("mysql -v -h {db_host} -u {db_root_username} "\
            "-p'{db_root_password}' --execute=\"GRANT ALL PRIVILEGES "\
            "ON {db_name}.* TO {db_user}@'%%' IDENTIFIED BY "\
            "'{db_password}'; FLUSH PRIVILEGES;\"")
        #TODO:why is this necessary? why doesn't the user@% pattern above give
        #localhost access?!
        r.run("mysql -v -h {db_host} -u {db_root_username} "\
            "-p'{db_root_password}' --execute=\"GRANT ALL PRIVILEGES "\
            "ON {db_name}.* TO {db_user}@{db_host} IDENTIFIED BY "\
            "'{db_password}'; FLUSH PRIVILEGES;\"")

    @task
    @runs_once
    def load(self, dump_fn='', prep_only=0, force_upload=0, from_local=0, name=None, site=None, dest_dir=None, force_host=None):
        """
        Restores a database snapshot onto the target database server.

        If prep_only=1, commands for preparing the load will be generated,
        but not the command to finally load the snapshot.
        """

        r = self.database_renderer(name=name, site=site)
        r.pc('Loading database snapshot.')

        # Render the snapshot filename.
        r.env.dump_fn = self.get_default_db_fn(fn_template=dump_fn, dest_dir=dest_dir).strip()

        from_local = int(from_local)

        prep_only = int(prep_only)

        missing_local_dump_error = r.format("Database dump file {dump_fn} does not exist.")

        # Copy snapshot file to target.
        if self.is_local:
            r.env.remote_dump_fn = dump_fn
        else:
            r.env.remote_dump_fn = '/tmp/' + os.path.split(r.env.dump_fn)[-1]

        if not prep_only and not self.is_local:
            #if int(force_upload) or (not self.is_local and not r.file_exists(r.env.remote_dump_fn)):
            if not self.dryrun:
                assert os.path.isfile(r.env.dump_fn), missing_local_dump_error
            #if self.verbose:
                #print('Uploading MySQL database snapshot...')
            #r.put(
                #local_path=r.env.dump_fn,
                #remote_path=r.env.remote_dump_fn)
            self.upload_snapshot(name=name, site=site)

        if self.is_local and not prep_only and not self.dryrun:
            assert os.path.isfile(r.env.dump_fn), missing_local_dump_error

        if force_host:
            r.env.db_host = force_host

        # Drop the database if it's there.
        r.run("mysql -v -h {db_host} -u {db_root_username} -p'{db_root_password}' --execute='DROP DATABASE IF EXISTS {db_name}'")

        # Now, create the database.
        r.run("mysqladmin -h {db_host} -u {db_root_username} -p'{db_root_password}' create {db_name}")

        # Create user
        with settings(warn_only=True):
            r.run("mysql -v -h {db_host} -u {db_root_username} -p'{db_root_password}' --execute=\"DROP USER '{db_user}'@'%%';"
                "FLUSH PRIVILEGES;\"")
        with settings(warn_only=True):
            r.run("mysql -v -h {db_host} -u {db_root_username} -p'{db_root_password}' --execute=\"CREATE USER '{db_user}'@'%%' IDENTIFIED BY '{db_password}'; "
                "GRANT ALL PRIVILEGES ON *.* TO '{db_user}'@'%%' WITH GRANT OPTION; "
                "FLUSH PRIVILEGES;\"")
        self.set_collation(name=name, site=site)

        self.set_max_packet_size(name=name, site=site)

        # Run any server-specific commands (e.g. to setup permissions) before
        # we load the data.
        for command in r.env.preload_commands:
            r.run(command)

        # Restore the database content from the dump file.
        if not prep_only:
            r.run(r.env.load_command)

        self.set_collation(name=name, site=site)

    @task
    def shell(self, name='default', site=None, use_root=0, **kwargs):
        """
        Opens a SQL shell to the given database, assuming the configured database
        and user supports this feature.
        """
        r = self.database_renderer(name=name, site=site)

        if int(use_root):
            kwargs = dict(
                db_user=r.env.db_root_username,
                db_password=r.env.db_root_password,
                db_host=r.env.db_host,
                db_name=r.env.db_name,
            )
            r.env.update(kwargs)

        if not name:
            r.env.db_name = ''

        r.run('/bin/bash -i -c "mysql -u {db_user} -p\'{db_password}\' -h {db_host} {db_name}"')

    @task(precursors=['packager', 'user'])
    def configure(self, do_packages=0, name='default', site=None):

        r = self.database_renderer(name=name, site=site)

        if int(do_packages):
            self.prep_root_password()
            self.install_packages()

        self.set_root_password()

        if r.env.custom_mycnf:
            r.env.conf = self.conf_path
            self.vprint('mysql.conf:', r.env.conf)
            fn = r.render_to_file('mysql/my.template.cnf', extra=r.env)
            r.put(
                local_path=fn,
                remote_path=r.env.conf,
                use_sudo=True,
            )

        if r.env.allow_remote_connections:

            # Enable remote connections.
            r.sudo("sed -i 's/127.0.0.1/0.0.0.0/g' {conf}")

            # Enable root logins from remote connections.
            r.sudo('mysql -u {db_root_username} -p"{db_root_password}" '
                '--execute="USE mysql; '
                'GRANT ALL ON *.* to {db_root_username}@\'%%\' IDENTIFIED BY \'{db_root_password}\'; '
                'FLUSH PRIVILEGES;"')

            self.restart()

class MySQLClientSatchel(Satchel):

    name = 'mysqlclient'

    @property
    def packager_system_packages(self):
        return {
            (UBUNTU, '12.04'): ['libmysqlclient-dev', 'mysql-client'],
            (UBUNTU, '14.04'): ['libmysqlclient-dev', 'mysql-client'],
            (UBUNTU, '16.04'): ['libmysqlclient-dev', 'mysql-client'],
        }

    @task(precursors=['packager'])
    def configure(self, *args, **kwargs):
        pass

mysql = MySQLSatchel()
mysqlclient = MySQLClientSatchel()

def query(query, use_sudo=True, **kwargs):
    """
    Run a MySQL query.
    """
    func = use_sudo and run_as_root or run

    user = kwargs.get('mysql_user') or env.get('mysql_user')
    password = kwargs.get('mysql_password') or env.get('mysql_password')

    options = [
        '--batch',
        '--raw',
        '--skip-column-names',
    ]
    if user:
        options.append('--user=%s' % quote(user))
    if password:
        options.append('--password=%s' % quote(password))
    options = ' '.join(options)

    return func('mysql %(options)s --execute=%(query)s' % {
        'options': options,
        'query': quote(query),
    })


def user_exists(name, host='localhost', **kwargs):
    """
    Check if a MySQL user exists.
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = query("""
            use mysql;
            SELECT COUNT(*) FROM user
                WHERE User = '%(name)s' AND Host = '%(host)s';
            """ % {
                'name': name,
                'host': host,
            }, **kwargs)
    return res.succeeded and (int(res) == 1)


def create_user(name, password, host='localhost', **kwargs):
    """
    Create a MySQL user.

    Example::

        import burlap

        # Create DB user if it does not exist
        if not burlap.mysql.user_exists('dbuser'):
            burlap.mysql.create_user('dbuser', password='somerandomstring')

    """
    with settings(hide('running')):
        query("CREATE USER '%(name)s'@'%(host)s' IDENTIFIED BY '%(password)s';" % {
            'name': name,
            'password': password,
            'host': host
        }, **kwargs)
    puts("Created MySQL user '%s'." % name)


def database_exists(name, **kwargs):
    """
    Check if a MySQL database exists.
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = query("SHOW DATABASES LIKE '%(name)s';" % {
            'name': name
        }, **kwargs)

    return res.succeeded and (res == name)


def create_database(name, owner=None, owner_host='localhost', charset='utf8',
                    collate='utf8_general_ci', **kwargs):
    """
    Create a MySQL database.

    Example::

        import burlap

        # Create DB if it does not exist
        if not burlap.mysql.database_exists('myapp'):
            burlap.mysql.create_database('myapp', owner='dbuser')

    """
    with settings(hide('running')):

        query("CREATE DATABASE %(name)s CHARACTER SET %(charset)s COLLATE %(collate)s;" % {
            'name': name,
            'charset': charset,
            'collate': collate
        }, **kwargs)

        if owner:
            query("GRANT ALL PRIVILEGES ON %(name)s.* TO '%(owner)s'@'%(owner_host)s' WITH GRANT OPTION;" % {
                'name': name,
                'owner': owner,
                'owner_host': owner_host
            }, **kwargs)

    puts("Created MySQL database '%s'." % name)

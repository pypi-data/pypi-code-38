import os

from fabric.api import runs_once

from burlap.constants import *
from burlap.db import DatabaseSatchel
from burlap.decorators import task, runs_once

class MongoDBSatchel(DatabaseSatchel):
    """
    Represents a MongoDB server.

    Installation follows the instructions outlined in the tutorial:

        https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
    """

    name = 'mongodb'

    def set_defaults(self):
        super(MongoDBSatchel, self).set_defaults()

        self.env.dump_command = 'mongodump -h {db_host}:{db_port} -v --username={db_user} --password={db_password} --gzip --archive={dump_fn}'
        self.env.dump_fn_template = '{dump_dest_dir}/db_mongodb_{SITE}_{ROLE}_{db_name}_$(date +%Y%m%d).archive'

        #self.env.load_command = 'gunzip < {remote_dump_fn} | pg_restore --jobs=8 -U {db_root_username} --format=c --create --dbname={db_name}'
        #self.env.load_command = 'gunzip < {remote_dump_fn} | pg_restore -U {db_root_username} --format=c --create --dbname={db_name}'
        self.env.load_command = 'mongorestore --drop --gzip --noIndexRestore --archive={remote_dump_fn}'
        #https://docs.mongodb.com/v3.0/tutorial/build-indexes-in-the-background/

        self.env.db_port = 9001

        self.env.watchdog_enabled = False
        self.env.watchdog_cron_schedule = None

        self.define_cron_job(
            name='mongomonitor',
            template='etc_crond_mongomonitor',
            # script_path='/etc/cron.d/mongomonitor',
            command='/usr/local/bin/mongomonitor',
            schedule=self.env.watchdog_cron_schedule
        )

    @task
    def install_watchdog(self):
        if not self.env.watchdog_enabled:
            return
        assert self.env.watchdog_cron_schedule, 'No schedule defined for the watchdog!'
        self.install_script(
            local_path='mongodb/mongomonitor',
            remote_path='/usr/local/bin/mongomonitor',
        )
        self.install_cron_job(name='mongomonitor')

    @task
    def configure(self, *args, **kwargs):
        super(MongoDBSatchel, self).configure(*args, **kwargs)
        self.install_watchdog()

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['mongodb-org'],
        }

    @property
    def packager_repositories(self):
        ver = self.os_version
        if ver.type == LINUX:
            if ver.distro == UBUNTU:
                if ver.release == '14.04':
                    d = {
                        APT_SOURCE: [
                            (
                                'deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse',
                                '/etc/apt/sources.list.d/mongodb-org-3.4.list',
                            ),
                        ],
                        APT_KEY: [
                            ('hkp://keyserver.ubuntu.com:80', '0C49F3730359A14518585931BC711F9BA15703C6'),
                        ],
                    }
                    return d
                if ver.release == '16.04':
                    # https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-mongodb-on-ubuntu-16-04
                    # https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
                    d = {
                        APT_SOURCE: [
                            (
                                'deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse',
                                '/etc/apt/sources.list.d/mongodb-org-3.4.list',
                            ),
                        ],
                        APT_KEY: [
                            ('hkp://keyserver.ubuntu.com:80', '0C49F3730359A14518585931BC711F9BA15703C6'),
                        ],
                    }
                    return d
        raise NotImplementedError

    @task
    @runs_once
    def load(self, dump_fn='', prep_only=0, force_upload=0, from_local=0, name=None, site=None, dest_dir=None):
        """
        Restores a database snapshot onto the target database server.

        If prep_only=1, commands for preparing the load will be generated,
        but not the command to finally load the snapshot.
        """

        r = self.database_renderer(name=name, site=site)

        # Render the snapshot filename.
        r.env.dump_fn = self.get_default_db_fn(fn_template=dump_fn, dest_dir=dest_dir)

        from_local = int(from_local)

        prep_only = int(prep_only)

        missing_local_dump_error = r.format('Database dump file {dump_fn} does not exist.')

        # Copy snapshot file to target.
        if self.is_local:
            r.env.remote_dump_fn = dump_fn
        else:
            r.env.remote_dump_fn = '/tmp/' + os.path.split(r.env.dump_fn)[-1]

        if not prep_only and not self.is_local:
            if not self.dryrun:
                assert os.path.isfile(r.env.dump_fn), missing_local_dump_error
            r.pc('Uploading MongoDB database snapshot...')
#                 r.put(
#                     local_path=r.env.dump_fn,
#                     remote_path=r.env.remote_dump_fn)
            r.local('rsync -rvz --progress --no-p --no-g '
                '--rsh "ssh -o StrictHostKeyChecking=no -i {key_filename}" '
                '{dump_fn} {user}@{host_string}:{remote_dump_fn}')

        if self.is_local and not prep_only and not self.dryrun:
            assert os.path.isfile(r.env.dump_fn), missing_local_dump_error

        r.run_or_local(r.env.load_command)

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

mongodb = MongoDBSatchel()

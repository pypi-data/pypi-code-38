"""
Django-specific helper utilities.
"""
from __future__ import print_function

import os
import re
import sys
import traceback
import glob
from importlib import import_module
from collections import defaultdict
from pprint import pprint

import six
from six import StringIO

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task
from burlap.common import get_last_modified_timestamp
from burlap.trackers import BaseTracker


cmp = lambda a, b: (a > b) - (a < b)


class DjangoSettingsTracker(BaseTracker):
    """
    Tracks changes to one or more satchel settings.

    Has only two custom parameters:

        names = A list of Django setting names.

    """

    def __init__(self, names, *args, **kwargs):
        if isinstance(names, six.string_types):
            names = names.replace(',', ' ').split(' ')
        names = names or []
        assert isinstance(names, (tuple, list, set))
        names = sorted(set(_.strip() for _ in names if _.strip()))
        super(DjangoSettingsTracker, self).__init__(*args, **kwargs)
        self.names = names

    @property
    def names_string(self):
        return ', '.join(self.names)

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.names_string)

    def natural_key(self):
        return (self.names_string,)

    def get_thumbprint(self):
        """
        Calculates the current thumbprint of the item being tracked.
        """
        d = {}
        settings = dj.get_settings()
        for name in self.names:
            d[name] = getattr(settings, name)
        return d


class DjangoSatchel(Satchel):

    # We don't use "django" as the name so as to not conflict with the official django package.
    name = 'dj'

    def set_defaults(self):

        # This is the name of the executable to call to access Django's management features.
        self.env.manage_cmd = 'manage.py'

        # This is the name of your Django application.
        self.env.app_name = None

        # This is the import path to your Django settings file.
        self.env.settings_module = '{app_name}.settings'

        # The folder containing manage.py on the remote host. Must be absolute.
        self.env.project_dir = None

        # The folder containing manage.py on the local filesystem. May be relative to the fabfile directory.
        self.env.local_project_dir = None

        self.env.shell_template = 'cd {project_dir}; /bin/bash -i -c \"{manage_cmd} shell;\"'

        self.env.fixture_sets = {} # {name: [paths to Django fixtures]}

        # These apps will be migrated on a specific database, while faked
        # on all others.
        # This is necessary since South does not have proper support for
        # multi-database applications.
        #./manage migrate <app> --fake
        #./manage migrate --database=<database> <app>
        self.env.migrate_fakeouts = [] # [{database:<database>, app:<app>}]

        self.env.install_sql_path_template = '{src_dir}/{app_name}/*/sql/*'

        # The target version of Django to assume.
        self.env.version = (1, 6, 0)

        self.env.createsuperuser_cmd = 'createsuperuser'

        self.env.manage_media = True

        self.env.manage_migrations = True

        self.env.media_dirs = ['static']

        self.env.migrate_pre_command = ''

        # If true, ignores errors that happen when migrate is run.
        # Useful in multitenant dev environments where you don't want
        # one missing password to break the entire deployment.
        self.env.ignore_migration_errors = 0

        # The path relative to fab where the code resides.
        self.env.src_dir = 'src'

        self.env.manage_dir = 'src'

        self.env.ignore_migration_errors = 0

        # The relative or absolute path of the root static directory where collect_static places content.
        self.env.static_root = 'static'

        # Modules whose name start with one of these values will be deleted before settings are imported.
        self.env.delete_module_with_prefixes = []

        # Modules whose name contains any of these values will be deleted before settings are imported.
        self.env.delete_module_containing = []

        self.env.configure_media_command = 'cd {local_project_dir}; {manage_cmd} collectstatic --noinput'

    def has_database(self, name, site=None, role=None):
        settings = self.get_settings(site=site, role=role)
        return name in settings.DATABASES

    @task
    def get_settings(self, site=None, role=None):
        """
        Retrieves the Django settings dictionary.
        """
        r = self.local_renderer
        _stdout = sys.stdout
        _stderr = sys.stderr
        if not self.verbose:
            sys.stdout = StringIO()
            sys.stderr = StringIO()
        try:
            sys.path.insert(0, r.env.src_dir)

            # Temporarily override SITE.
            tmp_site = self.genv.SITE
            if site and site.endswith('_secure'):
                site = site[:-7]
            site = site or self.genv.SITE or self.genv.default_site
            self.set_site(site)

            # Temporarily override ROLE.
            tmp_role = self.genv.ROLE
            if role:
                self.set_role(role)

            try:
                # We need to explicitly delete sub-modules from sys.modules. Otherwise, reload() skips
                # them and they'll continue to contain obsolete settings.
                if r.env.delete_module_with_prefixes:
                    for name in sorted(sys.modules):
                        for prefix in r.env.delete_module_with_prefixes:
                            if name.startswith(prefix):
                                if self.verbose:
                                    print('Deleting module %s prior to re-import.' % name)
                                del sys.modules[name]
                                break

                for name in list(sys.modules):
                    for s in r.env.delete_module_containing:
                        if s in name:
                            del sys.modules[name]
                            break

                if r.env.settings_module in sys.modules:
                    del sys.modules[r.env.settings_module]

                #TODO:fix r.env.settings_module not loading from settings?
#                 print('r.genv.django_settings_module:', r.genv.django_settings_module, file=_stdout)
#                 print('r.genv.dj_settings_module:', r.genv.dj_settings_module, file=_stdout)
#                 print('r.env.settings_module:', r.env.settings_module, file=_stdout)
                if 'django_settings_module' in r.genv:
                    r.env.settings_module = r.genv.django_settings_module
                else:
                    r.env.settings_module = r.env.settings_module or r.genv.dj_settings_module
                if self.verbose:
                    print('r.env.settings_module:', r.env.settings_module, r.format(r.env.settings_module))
                module = import_module(r.format(r.env.settings_module))

                if site:
                    assert site == module.SITE, 'Unable to set SITE to "%s" Instead it is set to "%s".' % (site, module.SITE)

                # Works as long as settings.py doesn't also reload anything.
                import imp
                imp.reload(module)

            except ImportError as e:
                print('Warning: Could not import settings for site "%s": %s' % (site, e), file=_stdout)
                traceback.print_exc(file=_stdout)
                #raise # breaks *_secure pseudo sites
                return
            finally:
                if tmp_site:
                    self.set_site(tmp_site)
                if tmp_role:
                    self.set_role(tmp_role)
        finally:
            sys.stdout = _stdout
            sys.stderr = _stderr
            sys.path.remove(r.env.src_dir)
        return module

    def set_db(self, name=None, site=None, role=None):
        r = self.local_renderer
        name = name or 'default'
        site = site or r.env.get('SITE') or r.genv.SITE or r.genv.default_site
        role = role or r.env.get('ROLE') or r.genv.ROLE
        settings = self.get_settings(site=site, role=role)
        assert settings, 'Unable to load Django settings for site %s.' % (site,)
        r.env.django_settings = settings
        default_db = settings.DATABASES[name]
        if self.verbose:
            print('default_db:')
            pprint(default_db, indent=4)
        r.env.db_name = default_db['NAME']
        r.env.db_user = default_db.get('USER', r.genv.user) # sqlite doesn't have a user
        r.env.db_host = default_db.get('HOST', 'localhost') # sqlite doesn't have a host
        r.env.db_password = default_db.get('PASSWORD') # sqlite doesn't have a password
        r.env.db_engine = default_db['ENGINE']
        r.env.db_schema = 'public'
        # Django stores the schema in the database-specific options at ['OPTIONS']['options'].
        db_options = default_db.get('OPTIONS', {}).get('options', '')
        try:
            r.env.db_schema = re.findall(r'search_path=([a-zA-Z0-9_]+)', db_options)[0]
        except IndexError:
            pass

        if 'mysql' in r.env.db_engine.lower():
            r.env.db_type = 'mysql'
        elif 'postgres' in r.env.db_engine.lower() or 'postgis' in r.env.db_engine.lower():
            r.env.db_type = 'postgresql'
        elif 'sqlite' in r.env.db_engine.lower():
            r.env.db_type = 'sqlite'
        else:
            r.env.db_type = r.env.db_engine

        for k, v in r.genv.items():
            if not k.startswith(self.name.lower()+'_db_'):
                continue
            print('db.kv:', k, v)

        return default_db

    @task
    def install_sql(self, site=None, database='default', apps=None, stop_on_error=0, fn=None, sql=None):
        """
        Install custom SQL, by filename or string.
        """
        #from burlap.db import load_db_set

        stop_on_error = int(stop_on_error)

        site = site or ALL

        name = database

        r = self.local_renderer
        paths = glob.glob(r.format(r.env.install_sql_path_template))

        apps = [_ for _ in (apps or '').split(',') if _.strip()]
        if self.verbose:
            print('install_sql.apps:', apps)

        def cmp_paths(d0, d1):
            if d0[1] and d0[1] in d1[2]:
                return -1
            if d1[1] and d1[1] in d0[2]:
                return +1
            return cmp(d0[0], d1[0])

        def get_paths(t):
            """
            Returns SQL file paths in an execution order that respect dependencies.
            """
            data = [] # [(path, view_name, content)]
            for path in paths:
                if fn and fn not in path:
                    continue
                parts = path.split('.')
                if len(parts) == 3 and parts[1] != t:
                    continue
                if not path.lower().endswith('.sql'):
                    continue
                content = open(path, 'r').read()
                matches = re.findall(r'[\s\t]+VIEW[\s\t]+([a-zA-Z0-9_]{3,})', content, flags=re.IGNORECASE)
                view_name = ''
                if matches:
                    view_name = matches[0]
                    print('Found view %s.' % view_name)
                data.append((path, view_name, content))
            for d in sorted(data, cmp=cmp_paths):
                yield d[0]

        def run_paths(paths, cmd_template, max_retries=3):
            r = self.local_renderer
            paths = list(paths)
            error_counts = defaultdict(int) # {path:count}
            terminal = set()
            if self.verbose:
                print('Checking %i paths.' % len(paths))
            while paths:
                path = paths.pop(0)
                if self.verbose:
                    print('path:', path)
                app_name = re.findall(r'/([^/]+)/sql/', path)[0]
                if apps and app_name not in apps:
                    self.vprint('skipping because app_name %s not in apps' % app_name)
                    continue
                with self.settings(warn_only=True):
                    if self.is_local:
                        r.env.sql_path = path
                    else:
                        r.env.sql_path = '/tmp/%s' % os.path.split(path)[-1]
                        r.put(local_path=path, remote_path=r.env.sql_path)
                    ret = r.run_or_local(cmd_template)
                    if ret and ret.return_code:

                        if stop_on_error:
                            raise Exception('Unable to execute file %s' % path)

                        error_counts[path] += 1
                        if error_counts[path] < max_retries:
                            paths.append(path)
                        else:
                            terminal.add(path)
            if terminal:
                print('%i files could not be loaded.' % len(terminal), file=sys.stderr)
                for path in sorted(list(terminal)):
                    print(path, file=sys.stderr)
                print(file=sys.stderr)

        if self.verbose:
            print('install_sql.db_engine:', r.env.db_engine)

        for _site, site_data in self.iter_sites(site=site, no_secure=True):

            self.set_db(name=name, site=_site)

            if 'postgres' in r.env.db_engine or 'postgis' in r.env.db_engine:
                if sql:
                    r.env.sql = sql
                    with self.settings(warn_only=not stop_on_error):
                        r.run('psql --user={db_user} --no-password --host={db_host} -d {db_name} --command="{sql}"')
                else:
                    paths = list(get_paths('postgresql'))
                    run_paths(
                        paths=paths,
                        cmd_template="psql --host={db_host} --user={db_user} --no-password -d {db_name} -f {sql_path}")

            elif 'mysql' in r.env.db_engine:
                if sql:
                    raise NotImplementedError("Custom SQL commands are not yet supported for MySQL.")
                paths = list(get_paths('mysql'))
                run_paths(
                    paths=paths,
                    cmd_template="mysql -v -h {db_host} -u {db_user} -p'{db_password}' {db_name} < {sql_path}")

            else:
                raise NotImplementedError

    @task
    def createsuperuser(self, username='admin', email=None, password=None, site=None):
        """
        Runs the Django createsuperuser management command.
        """
        r = self.local_renderer
        site = site or self.genv.SITE
        self.set_site_specifics(site)
        options = ['--username=%s' % username]
        if email:
            options.append('--email=%s' % email)
        if password:
            options.append('--password=%s' % password)
        r.env.options_str = ' '.join(options)
        if self.is_local:
            r.env.project_dir = r.env.local_project_dir
        r.genv.SITE = r.genv.SITE or site
        r.run_or_local('export SITE={SITE}; export ROLE={ROLE}; cd {project_dir}; {manage_cmd} {createsuperuser_cmd} {options_str}')

    @task
    def loaddata(self, path, site=None):
        """
        Runs the Dango loaddata management command.

        By default, runs on only the current site.

        Pass site=all to run on all sites.
        """
        site = site or self.genv.SITE
        r = self.local_renderer
        r.env._loaddata_path = path
        for _site, site_data in self.iter_sites(site=site, no_secure=True):
            try:
                self.set_db(site=_site)
                r.env.SITE = _site
                r.sudo('export SITE={SITE}; export ROLE={ROLE}; '
                    'cd {project_dir}; '
                    '{manage_cmd} loaddata {_loaddata_path}')
            except KeyError:
                pass

    @task
    def manage(self, cmd, *args, **kwargs):
        """
        A generic wrapper around Django's manage command.
        """
        r = self.local_renderer
        environs = kwargs.pop('environs', '').strip()
        if environs:
            environs = ' '.join('export %s=%s;' % tuple(_.split('=')) for _ in environs.split(','))
            environs = ' ' + environs + ' '
        r.env.cmd = cmd
        r.env.SITE = r.genv.SITE or r.genv.default_site
        r.env.args = ' '.join(map(str, args))
        r.env.kwargs = ' '.join(
            ('--%s' % _k if _v in (True, 'True') else '--%s=%s' % (_k, _v))
            for _k, _v in kwargs.items())
        r.env.environs = environs
        if self.is_local:
            r.env.project_dir = r.env.local_project_dir
        r.run_or_local('export SITE={SITE}; export ROLE={ROLE};{environs} cd {project_dir}; {manage_cmd} {cmd} {args} {kwargs}')

    @task
    def manage_all(self, *args, **kwargs):
        """
        Runs manage() across all unique site default databases.
        """
        for site, site_data in self.iter_unique_databases(site='all'):
            if self.verbose:
                print('-'*80, file=sys.stderr)
                print('site:', site, file=sys.stderr)
            if self.env.available_sites_by_host:
                hostname = self.current_hostname
                sites_on_host = self.env.available_sites_by_host.get(hostname, [])
                if sites_on_host and site not in sites_on_host:
                    self.vprint('skipping site:', site, sites_on_host, file=sys.stderr)
                    continue
            self.manage(*args, **kwargs)

    def load_django_settings(self):
        """
        Loads Django settings for the current site and sets them so Django internals can be run.
        """
        r = self.local_renderer

        # Save environment variables so we can restore them later.
        _env = {}
        save_vars = ['ALLOW_CELERY', 'DJANGO_SETTINGS_MODULE']
        for var_name in save_vars:
            _env[var_name] = os.environ.get(var_name)

        try:

            # Allow us to import local app modules.
            if r.env.local_project_dir:
                sys.path.insert(0, r.env.local_project_dir)

            #TODO:remove this once bug in django-celery has been fixed
            os.environ['ALLOW_CELERY'] = '0'

#             print('settings_module:', r.format(r.env.settings_module))
            os.environ['DJANGO_SETTINGS_MODULE'] = r.format(r.env.settings_module)
#             os.environ['CELERY_LOADER'] = 'django'
#             os.environ['SITE'] = r.genv.SITE or r.genv.default_site
#             os.environ['ROLE'] = r.genv.ROLE or r.genv.default_role

            # In Django >= 1.7, fixes the error AppRegistryNotReady: Apps aren't loaded yet
            # Disabling, in Django >= 1.10, throws exception:
            # RuntimeError: Model class django.contrib.contenttypes.models.ContentType
            # doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
#             try:
#                 from django.core.wsgi import get_wsgi_application
#                 application = get_wsgi_application()
#             except (ImportError, RuntimeError):
#                 raise
#                 print('Unable to get wsgi application.')
#                 traceback.print_exc()

            # In Django >= 1.7, fixes the error AppRegistryNotReady: Apps aren't loaded yet
            try:
                import django
                django.setup()
            except AttributeError:
                # This doesn't exist in Django < 1.7, so ignore it.
                pass

            # Load Django settings.
            settings = self.get_settings()
            try:
                from django.contrib import staticfiles
                from django.conf import settings as _settings

                # get_settings() doesn't raise ImportError but returns None instead
                if settings is not None:
                    for k, v in settings.__dict__.items():
                        setattr(_settings, k, v)
                else:
                    raise ImportError
            except (ImportError, RuntimeError):
                print('Unable to load settings.')
                traceback.print_exc()

        finally:
            # Restore environment variables.
            for var_name, var_value in _env.items():
                if var_value is None:
                    del os.environ[var_name]
                else:
                    os.environ[var_name] = var_value

        return settings

    def iter_static_paths(self, ignore_import_error=False):
        self.load_django_settings()
        from django.contrib.staticfiles import finders, storage
        for finder in finders.get_finders():
            for path, _storage in finder.list(ignore_patterns=[]):
                yield path

    def iter_app_directories(self, ignore_import_error=False):
        settings = self.load_django_settings()
        if not settings:
            return
        _cwd = os.getcwd()
        if self.env.local_project_dir:
            os.chdir(self.env.local_project_dir)
        try:
            for app in settings.INSTALLED_APPS:
                try:
                    mod = import_module(app)
                except ImportError:
                    if ignore_import_error:
                        continue
                    else:
                        raise
                yield app, os.path.dirname(mod.__file__)
        finally:
            os.chdir(_cwd)

    def iter_south_directories(self, *args, **kwargs):
        for app_name, base_app_dir in self.iter_app_directories(*args, **kwargs):
            migrations_dir = os.path.join(base_app_dir, 'migrations')
            if not os.path.isdir(migrations_dir):
                continue
            yield app_name, migrations_dir

    def iter_migrations(self, d, *args, **kwargs):
        for fn in sorted(os.listdir(d)):
            if fn.startswith('_') or not fn.endswith('.py'):
                continue
            fqfn = os.path.join(d, fn)
            if not os.path.isfile(fqfn):
                continue
            yield fn

    def iter_unique_databases(self, site=None):
        site = site or ALL
        r = self.local_renderer
        prior_database_names = set()
        #print('iter_unique_databases.begin.site_default:', site)
        for _site, site_data in self.iter_sites(site=site, no_secure=True):
            #print('iter_unique_databases._site:', _site)
            self.set_db(site=_site)
            key = (r.env.db_name, r.env.db_user, r.env.db_host, r.env.db_engine)
            #print('iter_unique_databases._site:', _site, key)
            if key in prior_database_names:
                continue
            prior_database_names.add(key)
            r.env.SITE = _site
            yield _site, site_data

    @task
    def shell(self):
        """
        Opens a Django focussed Python shell.
        Essentially the equivalent of running `manage.py shell`.
        """
        r = self.local_renderer
        if '@' in self.genv.host_string:
            r.env.shell_host_string = self.genv.host_string
        else:
            r.env.shell_host_string = '{user}@{host_string}'
        r.env.shell_default_dir = self.genv.shell_default_dir_template
        r.env.shell_interactive_djshell_str = self.genv.interactive_shell_template
        r.run_or_local('ssh -t -i {key_filename} {shell_host_string} "{shell_interactive_djshell_str}"')

    @task
    def syncdb(self, site=None, all=0, database=None, ignore_errors=1): # pylint: disable=redefined-builtin
        """
        Runs the standard Django syncdb command for one or more sites.
        """
        r = self.local_renderer

        ignore_errors = int(ignore_errors)

        post_south = self.version_tuple >= (1, 7, 0)

        use_run_syncdb = self.version_tuple >= (1, 9, 0)

        # DEPRECATED: removed in Django>=1.7
        r.env.db_syncdb_all_flag = '--all' if int(all) else ''

        r.env.db_syncdb_database = ''
        if database:
            r.env.db_syncdb_database = ' --database=%s' % database

        if self.is_local:
            r.env.project_dir = r.env.local_project_dir

        site = site or self.genv.SITE
        for _site, site_data in r.iter_unique_databases(site=site):
            r.env.SITE = _site
            with self.settings(warn_only=ignore_errors):
                if post_south:
                    if use_run_syncdb:
                        r.run_or_local(
                            'export SITE={SITE}; export ROLE={ROLE}; cd {project_dir}; '
                            '{manage_cmd} migrate --run-syncdb --noinput {db_syncdb_database}')
                    else:
                        # Between Django>=1.7,<1.9 we can only do a regular migrate, no true syncdb.
                        r.run_or_local(
                            'export SITE={SITE}; export ROLE={ROLE}; cd {project_dir}; '
                            '{manage_cmd} migrate --noinput {db_syncdb_database}')
                else:
                    r.run_or_local(
                        'export SITE={SITE}; export ROLE={ROLE}; cd {project_dir}; '
                        '{manage_cmd} syncdb --noinput {db_syncdb_all_flag} {db_syncdb_database}')

    @property
    def version_tuple(self):
        r = self.local_renderer
        return tuple(r.env.version)

    @task
    def migrate(self, app='', migration='', site=None, fake=0, ignore_errors=None, skip_databases=None, database=None, migrate_apps='', delete_ghosts=1):
        """
        Runs the standard South migrate command for one or more sites.
        """
    #     Note, to pass a comma-delimted list in a fab command, escape the comma with a back slash.
    #
    #         e.g.
    #
    #             fab staging dj.migrate:migrate_apps=oneapp\,twoapp\,threeapp

        r = self.local_renderer

        ignore_errors = int(r.env.ignore_migration_errors if ignore_errors is None else ignore_errors)

        delete_ghosts = int(delete_ghosts)

        post_south = self.version_tuple >= (1, 7, 0)

        if self.version_tuple >= (1, 9, 0):
            delete_ghosts = 0

        skip_databases = (skip_databases or '')
        if isinstance(skip_databases, six.string_types):
            skip_databases = [_.strip() for _ in skip_databases.split(',') if _.strip()]

        migrate_apps = migrate_apps or ''
        migrate_apps = [
            _.strip().split('.')[-1]
            for _ in migrate_apps.strip().split(',')
            if _.strip()
        ]
        if app:
            migrate_apps.append(app)

        r.env.migrate_migration = migration or ''
        r.env.migrate_fake_str = '--fake' if int(fake) else ''
        r.env.migrate_database = '--database=%s' % database if database else ''
        r.env.migrate_merge = '--merge' if not post_south else ''
        r.env.delete_ghosts = '--delete-ghost-migrations' if delete_ghosts and not post_south else ''
        self.vprint('project_dir0:', r.env.project_dir, r.genv.get('dj_project_dir'), r.genv.get('project_dir'))
        self.vprint('migrate_apps:', migrate_apps)

        if self.is_local:
            r.env.project_dir = r.env.local_project_dir

        # CS 2017-3-29 Don't bypass the iterator. That causes reversion to the global env that could corrupt the generated commands.
        #databases = list(self.iter_unique_databases(site=site))#TODO:remove
        # CS 2017-4-24 Don't specify a single site as the default when none is supplied. Otherwise all other sites will be ignored.
        #site = site or self.genv.SITE
        site = site or ALL
        databases = self.iter_unique_databases(site=site)
        for _site, site_data in databases:
            self.vprint('-'*80, file=sys.stderr)
            self.vprint('site:', _site, file=sys.stderr)

            if self.env.available_sites_by_host:
                hostname = self.current_hostname
                sites_on_host = self.env.available_sites_by_host.get(hostname, [])
                if sites_on_host and _site not in sites_on_host:
                    self.vprint('skipping site:', _site, sites_on_host, file=sys.stderr)
                    continue

            if not migrate_apps:
                migrate_apps.append(' ')

            for _app in migrate_apps:
                # In cases where we're migrating built-in apps or apps with dotted names
                # e.g. django.contrib.auth, extract the name used for the migrate command.
                r.env.migrate_app = _app.split('.')[-1]
                self.vprint('project_dir1:', r.env.project_dir, r.genv.get('dj_project_dir'), r.genv.get('project_dir'))
                r.env.SITE = _site
                with self.settings(warn_only=ignore_errors):
                    r.run_or_local(
                        'export SITE={SITE}; export ROLE={ROLE}; {migrate_pre_command} cd {project_dir}; '
                        '{manage_cmd} migrate --noinput {migrate_merge} --traceback '
                        '{migrate_database} {delete_ghosts} {migrate_app} {migrate_migration} '
                        '{migrate_fake_str}')

    @task
    def migrate_all(self, *args, **kwargs):
        kwargs['site'] = 'all'
        return self.migrate(*args, **kwargs)

    @task
    def truncate(self, app):
        assert self.genv.SITE, 'This should only be run for a specific site.'
        r = self.local_renderer
        r.env.app = app
        r.run('rm -f {app_dir}/{app}/migrations/*.py')
        r.run('rm -f {app_dir}/{app}/migrations/*.pyc')
        r.run('touch {app_dir}/{app}/migrations/__init__.py')
        r.run('export SITE={SITE}; export ROLE={ROLE}; cd {app_dir}; {manage_cmd} schemamigration {app} --initial')
        r.run('export SITE={SITE}; export ROLE={ROLE}; cd {app_dir}; {manage_cmd} migrate {app} --fake')

    @task
    def manage_async(self, command='', name='process', site=ALL, exclude_sites='', end_message='', recipients=''):
        """
        Starts a Django management command in a screen.

        Parameters:

            command :- all arguments passed to `./manage` as a single string

            site :- the site to run the command for (default is all)

        Designed to be ran like:

            fab <role> dj.manage_async:"some_management_command --force"

        """
        exclude_sites = exclude_sites.split(':')
        r = self.local_renderer
        for _site, site_data in self.iter_sites(site=site, no_secure=True):
            if _site in exclude_sites:
                continue
            r.env.SITE = _site
            r.env.command = command
            r.env.end_email_command = ''
            r.env.recipients = recipients or ''
            r.env.end_email_command = ''
            if end_message:
                end_message = end_message + ' for ' + _site
                end_message = end_message.replace(' ', '_')
                r.env.end_message = end_message
                r.env.end_email_command = r.format('{manage_cmd} send_mail --subject={end_message} --recipients={recipients}')
            r.env.name = name.format(**r.genv)
            r.run(
                'screen -dmS {name} bash -c "export SITE={SITE}; '\
                'export ROLE={ROLE}; cd {project_dir}; '\
                '{manage_cmd} {command} --traceback; {end_email_command}"; sleep 3;')

    @task
    def get_media_timestamp(self, last_timestamp=None):
        """
        Retrieves the most recent timestamp of the media in the static root.

        If last_timestamp is given, retrieves the first timestamp more recent than this value.
        """
        r = self.local_renderer
        _latest_timestamp = -1e9999999999999999
        for path in self.iter_static_paths():
            path = r.env.static_root + '/' + path
            self.vprint('checking timestamp of path:', path)
            if not os.path.isfile(path):
                continue
            #print('path:', path)
            _latest_timestamp = max(_latest_timestamp, get_last_modified_timestamp(path) or _latest_timestamp)
            if last_timestamp is not None and _latest_timestamp > last_timestamp:
                break
        self.vprint('latest_timestamp:', _latest_timestamp)
        return _latest_timestamp

    @task
    def has_media_changed(self):
        print('Checking to see if Django static media has changed...')
        lm = self.last_manifest
        # Unless this is our first time running, this should always be non-None.
        last_timestamp = lm.latest_timestamp
        current_timestamp = self.get_media_timestamp(last_timestamp=last_timestamp)
        self.vprint('last_timestamp:', last_timestamp)
        self.vprint('current_timestamp:', current_timestamp)
        changed = current_timestamp != last_timestamp
        if changed:
            print('It has.')
        else:
            print('It has not.')
        return changed

    def get_migration_fingerprint(self):
        data = {} # {app: latest_migration_name}
        for app_name, _dir in self.iter_app_directories(ignore_import_error=True):
            #print('app_name, _dir:', app_name, _dir)
            migration_dir = os.path.join(_dir, 'migrations')
            if not os.path.isdir(migration_dir):
                continue
            for migration_name in self.iter_migrations(migration_dir):
                data[app_name] = migration_name
        if self.verbose:
            print('%s.migrations:' % self.name)
            pprint(data, indent=4)
        return data

    def record_manifest(self):
        manifest = super(DjangoSatchel, self).record_manifest()
        manifest['latest_timestamp'] = self.get_media_timestamp()
        manifest['migrations'] = self.get_migration_fingerprint()
        return manifest

    @task(precursors=['packager', 'pip'])
    def configure_media(self, *args, **kwargs):
        if self.has_media_changed():
            r = self.local_renderer
            assert r.env.local_project_dir
            r.local(r.env.configure_media_command)

    @task(precursors=['packager', 'apache', 'pip', 'tarball', 'postgresql', 'mysql'])
    def configure_migrations(self):
        r = self.local_renderer
        assert r.env.local_project_dir
        last = self.last_manifest.migrations or {}
        current = self.current_manifest.get('migrations') or {}
        migrate_apps = []

        if self.verbose:
            print('djangomigrations.last:')
            pprint(last, indent=4)
            print('djangomigrations.current:')
            pprint(current, indent=4)

        for app_name in current:
            if current[app_name] != last.get(app_name):
                migrate_apps.append(app_name)

        if migrate_apps:
            self.vprint('%i apps with new migrations found!' % len(migrate_apps))
            self.vprint('migrate_apps:', migrate_apps)
            self.vprint('ignore_migration_errors:', self.env.ignore_migration_errors)
            # Note, Django's migrate command doesn't support multiple app name arguments
            # with all options, so we run it separately for each app.
            for app in migrate_apps:
                self.migrate(app=app, ignore_errors=self.env.ignore_migration_errors)
        else:
            self.vprint('No new migrations.')

    @task(precursors=['packager', 'tarball'])
    def configure(self, *args, **kwargs):
        if self.env.manage_media:
            self.configure_media()
        if self.env.manage_migrations:
            self.configure_migrations()

dj = DjangoSatchel()

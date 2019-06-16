# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Application Configuration
"""

from __future__ import unicode_literals, absolute_import

import os
import re
import sys
import shlex
import datetime
from six.moves import configparser
import warnings
import logging
import logging.config

import six

from rattail.util import load_entry_points, import_module_path
from rattail.exceptions import WindowsExtensionsNotInstalled, ConfigurationError
from rattail.files import temp_path
from rattail.logging import TimeConverter
from rattail.util import prettify


log = logging.getLogger(__name__)


def parse_bool(value):
    """
    Derive a boolean from the given string value.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if value.lower() in ('true', 'yes', 'on', '1'):
        return True
    return False


def parse_list(value):
    """
    Parse a configuration value, splitting by whitespace and/or commas and
    taking quoting into account, etc., yielding a list of strings.
    """
    if value is None:
        return []
    # Per the shlex docs (https://docs.python.org/2/library/shlex.html):
    # "Prior to Python 2.7.3, this module did not support Unicode input."
    if six.PY2 and isinstance(value, six.text_type):
        value = value.encode('utf-8')
    parser = shlex.shlex(value)
    parser.whitespace += ','
    parser.whitespace_split = True
    values = list(parser)
    for i, value in enumerate(values):
        if value.startswith('"') and value.endswith('"'):
            values[i] = value[1:-1]
    return values


class RattailConfig(object):
    """
    Rattail config object; this represents the sum total of configuration
    available to the running app.  The actual config available falls roughly
    into two categories: the "defaults" and the "db" (more on these below).
    The general idea here is that one might wish to provide some default
    settings within some config file(s) and/or the command line itself, but
    then allow all settings found in the database to override those defaults.
    However, all variations on this theme are supported, e.g. "use db settings
    but prefer those from file", "never use db settings", and so on.

    As for the "defaults" aspect of the config, this is read only once upon
    application startup.  It almost certainly involves one (or more) config
    file(s), but in addition to that, the application itself is free to embed
    default settings within the config object.  When this occurs, there will be
    no distinction made between settings which came from a file versus those
    which were established as defaults by the application logic.

    As for the "db" aspect of the config, of course this ultimately hinges upon
    the config defaults.  If a default Rattail database connection is defined,
    then the ``Setting`` table within that database may also be consulted for
    config values.  When this is done, the ``Setting.name`` is determined by
    concatenating the ``section`` and ``option`` arguments from the
    :meth:`get()` call, with a period (``'.'``) in between.
    """

    def __init__(self, files=[], usedb=None, preferdb=None):
        self.files_requested = []
        self.files_read = []
        if six.PY3:
            self.parser = configparser.ConfigParser()
        else: # PY2
            self.parser = configparser.SafeConfigParser()
        for path in files:
            self.read_file(path)
        self.usedb = usedb
        if self.usedb is None:
            self.usedb = self.getbool('rattail.config', 'usedb', usedb=False, default=False)
        self.preferdb = preferdb
        if self.usedb and self.preferdb is None:
            self.preferdb = self.getbool('rattail.config', 'preferdb', usedb=False, default=False)

        # Attempt to detect lack of SQLAlchemy libraries etc.  This allows us
        # to avoid installing those on a machine which will not need to access
        # a database etc.
        self._session_factory = None
        if self.usedb:
            try:
                from rattail.db import Session
            except ImportError: # pragma: no cover
                log.warning("config created with `usedb = True`, but can't import "
                            "`rattail.db.Session`, so setting `usedb = False` instead",
                            exc_info=True)
                self.usedeb = False
                self.preferdb = False
            else:
                self._session_factory = lambda: (Session(), True)

    def read_file(self, path, recurse=True):
        """
        Read in config from the given file.
        """
        path = os.path.abspath(path)
        if path in self.files_requested:
            log.debug("ignoring config file which was already requested: {0}".format(path))
            return

        log.debug("will attempt to read config from file: {0}".format(path))
        self.files_requested.append(path)

        if six.PY3:
            ConfigParser = configparser.ConfigParser
        else: # PY2
            ConfigParser = configparser.SafeConfigParser
        parser = ConfigParser(dict(
            here=os.path.dirname(path),
        ))
        if not parser.read(path):
            log.debug("ConfigParser.read() failed")
            return

        # If recursing, walk the complete config file inheritance chain.
        if recurse:
            if parser.has_section('rattail.config'):
                if parser.has_option('rattail.config', 'include'):
                    includes = parse_list(parser.get('rattail.config', 'include'))
                    for included in includes:
                        self.read_file(included, recurse=True)

        # Okay, now we can finally read this file into our main parser.
        self.parser.read(path)
        self.files_read.append(path)
        log.info("config was read from file: {0}".format(path))

    def configure_logging(self):
        """
        This first checks current config to determine whether or not we're
        supposed to be configuring logging at all.  If not, nothing more is
        done.

        If we are to configure logging, then this will save the current config
        parser defaults to a temporary file, and use this file to configure
        Python's standard logging module.
        """
        if not self.getbool('rattail.config', 'configure_logging', usedb=False, default=False):
            return

        # Coerce all logged timestamps to the local timezone, if possible.
        logging.Formatter.converter = TimeConverter(self)

        # Flush all current config to a single file, for input to fileConfig().
        path = temp_path(suffix='.conf')
        with open(path, 'wt') as f:
            self.parser.write(f)

        try:
            logging.config.fileConfig(path, disable_existing_loggers=False)
        except configparser.NoSectionError as error:
            log.warning("tried to configure logging, but got NoSectionError: {0}".format(error))
        else:
            log.debug("configured logging")
        finally:
            os.remove(path)

    def setdefault(self, section, option, value):
        """
        Establishes a new default for the given setting, if none exists yet.
        The effective default value is returned in all cases.
        """
        exists = True
        if not self.parser.has_section(section):
            self.parser.add_section(section)
            exists = False
        elif not self.parser.has_option(section, option):
            exists = False
        if not exists:
            self.parser.set(section, option, value)
        return self.parser.get(section, option)

    def set(self, section, option, value):
        """
        Set a value within the config's parser data set, i.e. the "defaults".
        This should probably be used sparingly, though one expected use is
        within tests (for convenience).
        """
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, option, value)

    def get(self, section, option, usedb=None, preferdb=None, session=None, default=None):
        """
        Retrieve a value from config.
        """
        usedb = usedb if usedb is not None else self.usedb
        if usedb:
            preferdb = preferdb if preferdb is not None else getattr(self, 'preferdb', False)
        else:
            preferdb = False
        
        if usedb and preferdb:
            value = self._getdb(section, option, session=session)
            if value is not None:
                return value

        if self.parser.has_option(section, option):
            return self.parser.get(section, option)

        if usedb and not preferdb:
            value = self._getdb(section, option, session=session)
            if value is not None:
                return value

        return default

    def _getdb(self, section, option, session=None):
        """
        Retrieve a config value from database settings table.
        """
        from rattail.db import api

        close = False
        if session is None:
            session, close = self._session_factory()
        value = api.get_setting(session, '{}.{}'.format(section, option))
        if close:
            session.close()
        return value

    def setdb(self, section, option, value, session=None):
        """
        Set a config value in the database settings table.  Note that the
        ``value`` arg should be a Unicode object.
        """
        from rattail.db import api

        close = False
        if session is None:
            session, close = self._session_factory()
        api.save_setting(session, '{}.{}'.format(section, option), value)
        if close:
            session.commit()
            session.close()

    def getbool(self, *args, **kwargs):
        """
        Retrieve a boolean value from config.
        """
        value = self.get(*args, **kwargs)
        return parse_bool(value)

    def getint(self, *args, **kwargs):
        """
        Retrieve an integer value from config.
        """
        value = self.get(*args, **kwargs)
        if value is None:
            return None
        if isinstance(value, int):
            return value
        return int(value)

    def getdate(self, *args, **kwargs):
        """
        Retrieve a date value from config.
        """
        value = self.get(*args, **kwargs)
        if value is None:
            return None
        if isinstance(value, datetime.date):
            return value
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()

    def getlist(self, *args, **kwargs):
        """
        Retrieve a list of string values from a single config option.
        """
        value = self.get(*args, **kwargs)
        if value is None:
            return None
        if isinstance(value, six.string_types):
            return parse_list(value)
        return value            # maybe a caller-provided default?

    def get_dict(self, section):
        """
        Convenience method which returns a dictionary of options contained
        within the given section.  Note that this method only supports the
        "default" config settings, i.e. those within the underlying parser.
        """
        settings = {}
        if self.parser.has_section(section):
            for option in self.parser.options(section):
                settings[option] = self.parser.get(section, option)
        return settings

    def require(self, section, option, **kwargs):
        """
        Fetch a value from current config, and raise an error if no value can
        be found.
        """
        if 'default' in kwargs:
            warnings.warn("You have provided a default value to the `RattailConfig.require()` "
                          "method.  This is allowed but also somewhat pointless, since `get()` "
                          "would suffice if a default is known.", UserWarning)

        msg = kwargs.pop('msg', None)
        value = self.get(section, option, **kwargs)
        if value is not None:
            return value

        if msg is None:
            msg = "Missing or invalid config"
        msg = "{0}; please set '{1}' in the [{2}] section of your config file".format(
            msg, option, section)
        raise ConfigurationError(msg)

    ##############################
    # convenience methods
    ##############################

    def app_title(self, default=None):
        """
        Returns official display title for the current app.
        """
        if not default:
            return self.require('rattail', 'app_title')
        return self.get('rattail', 'app_title', default=default)

    def node_title(self, default=None):
        """
        Returns official display title for the current app.
        """
        title = self.get('rattail', 'node_title')
        if title:
            return title
        return self.app_title(default=default)

    def node_type(self, default=None):
        """
        Returns the "type" of current node.  What this means will generally
        depend on the app logic.
        """
        try:
            return self.require('rattail', 'node_type', usedb=False)
        except ConfigurationError:
            if default:
                return default
            raise

    def production(self):
        """
        Returns boolean indicating whether the app is running in production mode
        """
        return self.getbool('rattail', 'production', default=False)

    def demo(self):
        """
        Returns boolean indicating whether the app is running in demo mode
        """
        return self.getbool('rattail', 'demo', default=False)

    def versioning_enabled(self):
        """
        Returns boolean indicating whether data versioning is enabled.
        """
        return self.getbool('rattail.db', 'versioning.enabled', usedb=False,
                            default=False)

    def appdir(self, require=True):
        """
        Returns path to the 'app' dir, if known.
        """
        get = self.require if require else self.get
        return get('rattail', 'appdir')

    def workdir(self, require=True):
        """
        Returns boolean indicating whether the config indicates production mode.
        """
        get = self.require if require else self.get
        return get('rattail', 'workdir')

    def batch_filedir(self, key=None):
        """
        Returns path to root folder where batches (optionally of type 'key')
        are stored.
        """
        path = os.path.abspath(self.require('rattail', 'batch.files'))
        if key:
            return os.path.join(path, key)
        return path

    def batch_filepath(self, key, uuid, filename=None, makedirs=False):
        """
        Returns absolute path to a batch's data folder, with optional filename
        appended.  If ``makedirs`` is set, the batch data folder will be
        created if it does not already exist.
        """
        rootdir = self.batch_filedir(key)
        filedir = os.path.join(rootdir, uuid[:2], uuid[2:])
        if makedirs and not os.path.exists(filedir):
            os.makedirs(filedir)
        if filename:
            return os.path.join(filedir, filename)
        return filedir

    def export_filedir(self, key=None):
        """
        Returns path to root folder where exports (optionally of type 'key')
        are stored.
        """
        path = os.path.abspath(self.require('rattail', 'export.files'))
        if key:
            return os.path.join(path, key)
        return path

    def export_filepath(self, key, uuid, filename=None, makedirs=False):
        """
        Returns absolute path to export data file, generated from the given args.
        """
        rootdir = self.export_filedir(key)
        filedir = os.path.join(rootdir, uuid[:2], uuid[2:])
        if makedirs and not os.path.exists(filedir):
            os.makedirs(filedir)
        if filename:
            return os.path.join(filedir, filename)
        return filedir

    def upgrade_filedir(self):
        """
        Returns path to root folder where upgrade files are stored.
        """
        path = os.path.abspath(self.require('rattail.upgrades', 'files'))
        return path

    def upgrade_filepath(self, uuid, filename=None, makedirs=False):
        """
        Returns absolute path to upgrade data file, generated from the given args.
        """
        rootdir = self.upgrade_filedir()
        filedir = os.path.join(rootdir, uuid[:2], uuid[2:])
        if makedirs and not os.path.exists(filedir):
            os.makedirs(filedir)
        if filename:
            return os.path.join(filedir, filename)
        return filedir

    def upgrade_command(self, default='/bin/sleep 30'):
        """
        Returns command to be used when performing upgrades.
        """
        # NOTE: we don't allow command to be specified in DB, for security reasons..
        return self.getlist('rattail.upgrades', 'command', default=default, usedb=False)

    def datasync_url(self):
        """
        Returns configured URL for managing datasync daemon.
        """
        return self.get('rattail.datasync', 'url')

    def get_enum(self):
        """
        Returns a reference to configured 'enum' module; defaults to
        :mod:`rattail.enum`.
        """
        spec = self.get('rattail', 'enum', default='rattail.enum')
        return import_module_path(spec)

    def get_model(self):
        """
        Returns a reference to configured 'model' module; defaults to
        :mod:`rattail.db.model`.
        """
        spec = self.get('rattail', 'model', default='rattail.db.model', usedb=False)
        return import_module_path(spec)

    def product_key(self):
        """
        Returns the name of the attribute which should be treated as the
        canonical product key field, e.g. 'upc' or 'item_id' etc.
        """
        return self.get('rattail', 'product.key', default='upc')

    def product_key_title(self, key=None):
        """
        Returns the title string to be used when displaying product key field,
        e.g. "UPC" or "Part No." etc.
        """
        title = self.get('rattail', 'product.key_title')
        if title:
            return title
        if not key:
            key = self.product_key()
        if key == 'upc':
            return "UPC"
        if key == 'item_id':
            return "Item ID"
        return prettify(key)

    def single_store(self):
        """
        Returns boolean indicating whether the system is configured to behave
        as if it belongs to a single Store.
        """
        return self.getbool('rattail', 'single_store', default=False)

    def get_store(self, session):
        """
        Returns a :class:`rattail.db.model.Store` instance corresponding to app
        config, or ``None``.
        """
        from rattail.db import api

        store = self.get('rattail', 'store')
        if store:
            return api.get_store(session, store)


    ##############################
    # deprecated methods
    ##############################

    def options(self, section):
        warnings.warn("RattailConfig.option() is deprecated, please find "
                      "another way to accomplish what you're after.",
                      DeprecationWarning)
        return self.parser.options(section)

    def has_option(self, section, option):
        warnings.warn("RattailConfig.has_option() is deprecated, please find "
                      "another way to accomplish what you're after.",
                      DeprecationWarning)
        return self.parser.has_option(section, option)


class ConfigExtension(object):
    """
    Base class for all config extensions.
    """
    key = None

    def __repr__(self):
        return "ConfigExtension(key={0})".format(repr(self.key))

    def configure(self, config):
        """
        All subclasses should override this method, to extend the config object
        in any way necessary etc.
        """


def make_config(files=None, usedb=None, preferdb=None, env=None, winsvc=None, extend=True, versioning=None):
    """
    Returns a new config object, initialized with the given parameters and
    further modified by all registered config extensions.

    :param versioning: Controls whether or not the versioning system is
       configured with the new config object.  If ``True``, versioning will be
       configured.  If ``False`` then it will not be configured.  If ``None``
       (the default) then versioning will be configured only if the config
       object itself says that it should be.
    """
    if env is None:
        env = os.environ
    if files is None:
        files = env.get('RATTAIL_CONFIG_FILES')
        if files is not None:
            files = files.split(os.pathsep)
        else:
            files = default_system_paths() + default_user_paths()
    elif isinstance(files, six.string_types):
        files = [files]

    # If making config for a Windows service, we must read the default config
    # file(s) first, and check it to see if there is an alternate config file
    # which should be considered the "root" file.  Normally we specify the root
    # config file(s) via command line etc., but there is no practical way to
    # pass parameters to a Windows service.  This way we can effectively do
    # just that, via config.
    if winsvc is not None:
        parser = configparser.SafeConfigParser()
        parser.read(files)
        if parser.has_section('rattail.config'):
            key = 'winsvc.{0}'.format(winsvc)
            if parser.has_option('rattail.config', key):
                files = parse_list(parser.get('rattail.config', key))

    # Initial config object will have values read from the given file paths,
    # and kwargs, but no other app defaults etc. will have been applied yet.
    config = RattailConfig(files, usedb=usedb, preferdb=preferdb)
    config.configure_logging()

    if config.getbool('rattail', 'suppress_psycopg2_wheel_warning', usedb=False):
        # TODO: revisit this, does it require action from us?
        # suppress this warning about psycopg2 wheel; not sure what it means yet
        # exactly but it's causing frequent noise for us...
        warnings.filterwarnings(
            'ignore',
            r'^The psycopg2 wheel package will be renamed from release 2\.8; in order to keep '
            'installing from binary please use "pip install psycopg2-binary" instead\. For details '
            'see: <http://initd.org/psycopg/docs/install.html#binary-install-from-pypi>\.',
            UserWarning,
            r'^psycopg2$',
        )

    # Apply extra config for all available extensions.
    if extend:
        extensions = load_entry_points('rattail.config.extensions')
        for extension in extensions.values():
            log.debug("applying '{0}' config extension".format(extension.key))
            extension().configure(config)

    # maybe configure versioning
    if versioning is None:
        versioning = config.versioning_enabled()
    if versioning:
        from rattail.db.config import configure_versioning
        configure_versioning(config)

    return config


def default_system_paths():
    """
    Returns a list of default system-level config file paths, according to the
    current platform.
    """
    if sys.platform == 'win32':

        # Use the Windows Extensions libraries to fetch official defaults.
        try:
            from win32com.shell import shell, shellcon
        except ImportError:
            raise WindowsExtensionsNotInstalled
        else:
            return [
                os.path.join(shell.SHGetSpecialFolderPath(
                    0, shellcon.CSIDL_COMMON_APPDATA), 'rattail.conf'),
                os.path.join(shell.SHGetSpecialFolderPath(
                    0, shellcon.CSIDL_COMMON_APPDATA), 'rattail', 'rattail.conf'),
            ]

    return [
        '/etc/rattail.conf',
        '/etc/rattail/rattail.conf',
        '/usr/local/etc/rattail.conf',
        '/usr/local/etc/rattail/rattail.conf',
    ]


def default_user_paths():
    """
    Returns a list of default user-level config file paths, according to the
    current platform.
    """
    if sys.platform == 'win32':

        # Use the Windows Extensions libraries to fetch official defaults.
        try:
            from win32com.shell import shell, shellcon
        except ImportError:
            raise WindowsExtensionsNotInstalled
        else:
            return [
                os.path.join(shell.SHGetSpecialFolderPath(
                    0, shellcon.CSIDL_APPDATA), 'rattail.conf'),
                os.path.join(shell.SHGetSpecialFolderPath(
                    0, shellcon.CSIDL_APPDATA), 'rattail', 'rattail.conf'),
            ]

    return [
        os.path.expanduser('~/.rattail.conf'),
        os.path.expanduser('~/.rattail/rattail.conf'),
    ]


def get_user_dir(create=False):
    """
    Returns a path to the "preferred" user-level folder, in which additional
    config files (etc.) may be placed as needed.  This essentially returns a
    platform-specific variation of ``~/.rattail/``.

    If ``create`` is ``True``, then the folder will be created if it does not
    already exist.
    """
    if sys.platform == 'win32':

        # Use the Windows Extensions libraries to fetch official defaults.
        try:
            from win32com.shell import shell, shellcon
        except ImportError:
            raise WindowsExtensionsNotInstalled
        else:
            path = os.path.join(shell.SHGetSpecialFolderPath(
                0, shellcon.CSIDL_APPDATA), 'rattail')

    else:
        path = os.path.expanduser('~/.rattail')

    if create and not os.path.exists(path):
        os.mkdir(path)
    return path


def get_user_file(filename, createdir=False):
    """
    Returns a full path to a user-level config file location.  This is obtained
    by first calling :func:`get_user_dir()` and then joining the result with
    ``filename``.

    The ``createdir`` argument will be passed to :func:`get_user_dir()` as its
    ``create`` arg, and may be used to ensure the user-level folder exists.
    """
    return os.path.join(get_user_dir(create=createdir), filename)


class ConfigProfile(object):
    """
    Generic class to represent a config "profile", as used by the filemon and
    datasync daemons, etc.

    .. todo::
       This clearly needs more documentation.
    """

    @property
    def section(self):
        """
        Each subclass of ``ConfigProfile`` must define this.
        """
        raise NotImplementedError

    def _config_string(self, option, **kwargs):
        return self.config.get(self.section, '{0}.{1}'.format(self.key, option), **kwargs)

    def _config_boolean(self, option, default=None):
        return self.config.getbool(self.section, '{0}.{1}'.format(self.key, option),
                                   default=default)

    def _config_int(self, option, minimum=1, default=None):
        """
        Retrieve the *integer* value for the given option.
        """
        option = '{}.{}'.format(self.key, option)

        # try to read value from config
        value = self.config.getint(self.section, option)
        if value is not None:

            # found a value; validate it
            if value < minimum:
                log.warning("config value %s is too small; falling back to minimum "
                            "of %s for option: %s", value, minimum, option)
                value = minimum

        # or, use default value, if valid
        elif default is not None and default >= minimum:
            value = default

        # or, just use minimum value
        else:
            value = minimum

        return value

    def _config_list(self, option):
        return parse_list(self._config_string(option))


class FreeTDSLoggingFilter(logging.Filter):
    """
    Custom logging filter, to suppress certain "write to server failed"
    messages relating to FreeTDS database connections.  They seem harmless and
    just cause unwanted error emails.
    """

    def __init__(self, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        self.pattern = re.compile(r'(?:Read from|Write to) the server failed')

    def filter(self, record):
        if (record.name == 'sqlalchemy.pool.QueuePool'
            and record.funcName == '_finalize_fairy'
            and record.levelno == logging.ERROR
            and record.msg == "Exception during reset or similar"
            and record.exc_info
            and self.pattern.search(six.text_type(record.exc_info[1]))):

            # Log this as a warning instead of error, to cut down on our noise.
            record.levelno = logging.WARNING
            record.levelname = 'WARNING'

        return True

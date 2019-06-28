import codecs
import errno
import getopt
import glob
import os
import platform
import re
import signal
import socket
import stat
import sys
import tempfile
import threading
import warnings

import pkg_resources

from supervisor import (
    helpers,
    loggers,
    states,
    xmlrpc,
    poller
)
from supervisor.compat import (
    PY3,
    ConfigParser,
    as_bytes, as_string,
    xmlrpclib,
    StringIO,
    basestring
)
from supervisor.datatypes import (
    process_or_group_name,
    boolean,
    integer,
    existing_dirpath,
    byte_size,
    signal_number,
    list_of_exitcodes,
    dict_of_key_value_pairs,
    logfile_name,
    list_of_strings,
    octal_type,
    existing_directory,
    logging_level,
    inet_address,
    InetStreamSocketConfig,
    url,
    Automatic,
    auto_restart,
    profile_options
)
from supervisor.medusa import asyncore_25 as asyncore
from supervisor.utils import raise_not_implemented


def _read_version_txt():
    mydir = os.path.abspath(os.path.dirname(__file__))
    version_txt = os.path.join(mydir, 'version.txt')
    with open(version_txt, 'r') as f:
        return f.read().strip()


VERSION = _read_version_txt()


def normalize_path(v):
    return os.path.normpath(os.path.abspath(os.path.expanduser(v)))


class Dummy(object):
    pass


class Options(object):
    stderr = sys.stderr
    stdout = sys.stdout
    exit = sys.exit
    warnings = warnings

    uid = gid = None

    progname = sys.argv[0]
    configfile = None
    schemadir = None
    configroot = None
    here = None

    # Class variable deciding whether positional arguments are allowed.
    # If you want positional arguments, set this to 1 in your subclass.
    positional_args_allowed = 0

    def __init__(self, require_configfile=True):
        """Constructor.

        Params:
        require_configfile -- whether we should fail on no config file.
        """
        self.names_list = []
        self.short_options = []
        self.long_options = []
        self.options_map = {}
        self.default_map = {}
        self.required_map = {}
        self.environ_map = {}
        self.attr_priorities = {}
        self.require_configfile = require_configfile
        self.add(None, None, "h", "help", self.help)
        self.add("configfile", None, "c:", "configuration=")

        here = os.path.dirname(os.path.dirname(sys.argv[0]))
        searchpaths = [os.path.join(here, 'etc', 'supervisord.conf'),
                       os.path.join(here, 'supervisord.conf'),
                       'supervisord.conf',
                       'etc/supervisord.conf',
                       '/etc/supervisord.conf']
        self.searchpaths = searchpaths

        self.environ_expansions = {}
        for k, v in os.environ.items():
            self.environ_expansions['ENV_%s' % k] = v

    def default_configfile(self):
        """Return the name of the found config file or print usage/exit."""
        config = None
        for path in self.searchpaths:
            if os.path.exists(path):
                config = path
                break
        if config is None and self.require_configfile:
            self.usage('No config file found at default paths (%s); '
                       'use the -c option to specify a config file '
                       'at a different path' % ', '.join(self.searchpaths))
        return config

    def help(self, dummy):
        """Print a long help message to stdout and exit(0).

        Occurrences of "%s" in are replaced by self.progname.
        """
        help = self.doc + "\n"
        if help.find("%s") > 0:
            help = help.replace("%s", self.progname)
        self.stdout.write(help)
        self.exit(0)

    def usage(self, msg):
        """Print a brief error message to stderr and exit(2)."""
        self.stderr.write("Error: %s\n" % str(msg))
        self.stderr.write("For help, use %s -h\n" % self.progname)
        self.exit(2)

    def add(self,
            name=None,  # attribute name on self
            confname=None,  # dotted config path name
            short=None,  # short option name
            long=None,  # long option name
            handler=None,  # handler (defaults to string)
            default=None,  # default value
            required=None,  # message if not provided
            flag=None,  # if not None, flag value
            env=None,  # if not None, environment variable
            ):
        """Add information about a configuration option.

        This can take several forms:

        add(name, confname)
            Configuration option 'confname' maps to attribute 'name'
        add(name, None, short, long)
            Command line option '-short' or '--long' maps to 'name'
        add(None, None, short, long, handler)
            Command line option calls handler
        add(name, None, short, long, handler)
            Assign handler return value to attribute 'name'

        In addition, one of the following keyword arguments may be given:

        default=...  -- if not None, the default value
        required=... -- if nonempty, an error message if no value provided
        flag=...     -- if not None, flag value for command line option
        env=...      -- if not None, name of environment variable that
                        overrides the configuration file or default
        """
        if flag is not None:
            if handler is not None:
                raise ValueError("use at most one of flag= and handler=")
            if not long and not short:
                raise ValueError("flag= requires a command line flag")
            if short and short.endswith(":"):
                raise ValueError("flag= requires a command line flag")
            if long and long.endswith("="):
                raise ValueError("flag= requires a command line flag")
            handler = lambda arg, flag=flag: flag

        if short and long:
            if short.endswith(":") != long.endswith("="):
                raise ValueError("inconsistent short/long options: %r %r" % (
                    short, long))

        if short:
            if short[0] == "-":
                raise ValueError("short option should not start with '-'")
            key, rest = short[:1], short[1:]
            if rest not in ("", ":"):
                raise ValueError("short option should be 'x' or 'x:'")
            key = "-" + key
            if key in self.options_map:
                raise ValueError("duplicate short option key '%s'" % key)
            self.options_map[key] = (name, handler)
            self.short_options.append(short)

        if long:
            if long[0] == "-":
                raise ValueError("long option should not start with '-'")
            key = long
            if key[-1] == "=":
                key = key[:-1]
            key = "--" + key
            if key in self.options_map:
                raise ValueError("duplicate long option key '%s'" % key)
            self.options_map[key] = (name, handler)
            self.long_options.append(long)

        if env:
            self.environ_map[env] = (name, handler)

        if name:
            if not hasattr(self, name):
                setattr(self, name, None)
            self.names_list.append((name, confname))
            if default is not None:
                self.default_map[name] = default
            if required:
                self.required_map[name] = required

    def _set(self, attr, value, prio):
        current = self.attr_priorities.get(attr, -1)
        if prio >= current:
            setattr(self, attr, value)
            self.attr_priorities[attr] = prio

    def realize(self, args=None, doc=None, progname=None):
        """Realize a configuration.

        Optional arguments:

        args     -- the command line arguments, less the program name
                    (default is sys.argv[1:])

        doc      -- usage message (default is __main__.__doc__)
        """
        # Provide dynamic default method arguments
        if args is None:
            args = sys.argv[1:]
        if progname is None:
            progname = sys.argv[0]
        if doc is None:
            try:
                import __main__
                doc = __main__.__doc__
            except Exception:
                pass
        self.progname = progname
        self.doc = doc

        self.options = []
        self.args = []

        # Call getopt
        try:
            self.options, self.args = getopt.getopt(
                args, "".join(self.short_options), self.long_options)
        except getopt.error as exc:
            self.usage(str(exc))

        # Check for positional args
        if self.args and not self.positional_args_allowed:
            self.usage("positional arguments are not supported: %s" % (str(self.args)))

        # Process options returned by getopt
        for opt, arg in self.options:
            name, handler = self.options_map[opt]
            if handler is not None:
                try:
                    arg = handler(arg)
                except ValueError as msg:
                    self.usage("invalid value for %s %r: %s" % (opt, arg, msg))
            if name and arg is not None:
                if getattr(self, name) is not None:
                    self.usage("conflicting command line option %r" % opt)
                self._set(name, arg, 2)

        # Process environment variables
        for envvar in self.environ_map.keys():
            name, handler = self.environ_map[envvar]
            if envvar in os.environ:
                value = os.environ[envvar]
                if handler is not None:
                    try:
                        value = handler(value)
                    except ValueError as msg:
                        self.usage("invalid environment value for %s %r: %s"
                                   % (envvar, value, msg))
                if name and value is not None:
                    self._set(name, value, 1)

        if self.configfile is None and "supervisord" in self.progname:  # pragma: no cover
            self.warnings.warn(
                'Supervisord is searching for its configuration file in default locations '
                '(including its current working directory); you '
                'probably want to specify a "-c" argument specifying an '
                'absolute path to a configuration file for improved '
                'security.'
            )

            self.configfile = self.default_configfile()

        self.process_config()

    def process_config(self, do_usage=True):
        """Process configuration data structure.

        This includes reading config file if necessary, setting defaults etc.
        """
        if self.configfile:
            self.process_config_file(do_usage)

        # Copy config options to attributes of self.  This only fills
        # in options that aren't already set from the command line.
        for name, confname in self.names_list:
            if confname:
                parts = confname.split(".")
                obj = self.configroot
                for part in parts:
                    if obj is None:
                        break
                    # Here AttributeError is not a user error!
                    obj = getattr(obj, part)
                self._set(name, obj, 0)

        # Process defaults
        for name, value in self.default_map.items():
            if getattr(self, name) is None:
                setattr(self, name, value)

        # Process required options
        for name, message in self.required_map.items():
            if getattr(self, name) is None:
                self.usage(message)

    def process_config_file(self, do_usage):
        # Process config file
        if not hasattr(self.configfile, 'read'):
            self.here = os.path.abspath(os.path.dirname(self.configfile))
        try:
            self.read_config(self.configfile)
        except ValueError as msg:
            if do_usage:
                # if this is not called from an RPC method, run usage and exit.
                self.usage(str(msg))
            else:
                # if this is called from an RPC method, raise an error
                raise ValueError(msg)

    def exists(self, path):
        return os.path.exists(path)

    def open(self, fn, mode='r'):
        return open(fn, mode)

    def get_plugins(self, parser, factory_key, section_prefix):
        factories = []

        for section in parser.sections():
            if not section.startswith(section_prefix):
                continue

            name = section.split(':', 1)[1]
            factory_spec = parser.saneget(section, factory_key, None)
            if factory_spec is None:
                raise ValueError('section [%s] does not specify a %s' %
                                 (section, factory_key))
            try:
                factory = self.import_spec(factory_spec)
            except ImportError:
                raise ValueError('%s cannot be resolved within [%s]' % (
                    factory_spec, section))

            extras = {}
            for k in parser.options(section):
                if k != factory_key:
                    extras[k] = parser.saneget(section, k)
            factories.append((name, factory, extras))

        return factories

    def import_spec(self, spec):
        ep = pkg_resources.EntryPoint.parse("x=" + spec)
        if hasattr(ep, 'resolve'):
            # this is available on setuptools >= 10.2
            return ep.resolve()
        else:
            # this causes a DeprecationWarning on setuptools >= 11.3
            return ep.load(False)


class ServerOptions(Options):
    user = None
    sockchown = None
    sockchmod = None
    logfile = None
    loglevel = None
    pidfile = None
    passwdfile = None
    nodaemon = None
    environment = None
    serverurl = None
    httpservers = ()
    unlink_socketfiles = True
    mood = states.SupervisorStates.RUNNING
    job_handler = None

    def __init__(self):
        Options.__init__(self)
        self.configroot = Dummy()
        self.configroot.supervisord = Dummy()
        self.add(None, None, "v", "version", self.version)
        self.add("nodaemon", "supervisord.nodaemon", "n", "nodaemon", flag=1,
                 default=0)
        self.add("delaysecs", "supervisord.delaysecs", "p",
                 "delaysecs", default=0.2)
        self.add("user", "supervisord.user", "u:", "user=")
        self.add("umask", "supervisord.umask", "m:", "umask=",
                 octal_type, default='022')
        self.add("directory", "supervisord.directory", "d:", "directory=",
                 existing_directory)
        self.add("logfile", "supervisord.logfile", "l:", "logfile=",
                 existing_dirpath, default="supervisord.log")
        self.add("logfile_maxbytes", "supervisord.logfile_maxbytes",
                 "y:", "logfile_maxbytes=", byte_size,
                 default=50 * 1024 * 1024)  # 50MB
        self.add("logfile_backups", "supervisord.logfile_backups",
                 "z:", "logfile_backups=", integer, default=10)
        self.add("loglevel", "supervisord.loglevel", "e:", "loglevel=",
                 logging_level, default="info")
        self.add("pidfile", "supervisord.pidfile", "j:", "pidfile=",
                 existing_dirpath, default="supervisord.pid")
        self.add("identifier", "supervisord.identifier", "i:", "identifier=",
                 str, default="supervisor")
        self.add("childlogdir", "supervisord.childlogdir", "q:", "childlogdir=",
                 existing_directory, default=tempfile.gettempdir())
        self.add("minfds", "supervisord.minfds",
                 "a:", "minfds=", int, default=1024)
        self.add("minprocs", "supervisord.minprocs",
                 "", "minprocs=", int, default=200)
        self.add("nocleanup", "supervisord.nocleanup",
                 "k", "nocleanup", flag=1, default=0)
        self.add("strip_ansi", "supervisord.strip_ansi",
                 "t", "strip_ansi", flag=1, default=0)
        self.add("profile_options", "supervisord.profile_options",
                 "", "profile_options=", profile_options, default=None)
        # subprocess history by pid
        self.pidhistory = {}
        self.process_group_configs = []
        self.parse_warnings = []
        self.parse_infos = []
        self.signal_receiver = SignalReceiver()
        self.poller = poller.Poller(self)

    def version(self, dummy):
        """Print version to stdout and exit(0).
        """
        self.stdout.write('%s\n' % VERSION)
        self.exit(0)

    # TODO: not covered by any test, but used by dispatchers
    def getLogger(self, *args, **kwargs):
        return loggers.getLogger(*args, **kwargs)

    def realize(self, *arg, **kw):
        Options.realize(self, *arg, **kw)
        section = self.configroot.supervisord

        if not self.loglevel:
            self.loglevel = section.loglevel

        if self.logfile:
            logfile = self.logfile
        else:
            logfile = section.logfile

        self.logfile = normalize_path(logfile)

        if self.pidfile:
            pidfile = self.pidfile
        else:
            pidfile = section.pidfile

        self.pidfile = normalize_path(pidfile)

        self.rpcinterface_factories = section.rpcinterface_factories
        self.server_configs = section.server_configs

        # fall back to an inet socket
        if self.serverurl is None:
            for config in [config for config in self.server_configs if config['family'] is socket.AF_INET]:
                host = config['host']
                port = config['port']
                if not host:
                    host = 'localhost'
                self.serverurl = 'http://%s:%s' % (host, port)

        # self.serverurl may still be None if no servers at all are
        # configured in the config file

        self.identifier = section.identifier

    def process_config(self, do_usage=True):
        Options.process_config(self, do_usage=do_usage)

        new = self.configroot.supervisord.process_group_configs
        self.process_group_configs = new

    def read_config(self, fp):
        # Clear parse warnings, since we may be re-reading the
        # config a second time after a reload.
        self.parse_warnings = []
        self.parse_infos = []

        section = self.configroot.supervisord
        need_close = False
        if not hasattr(fp, 'read'):
            if not self.exists(fp):
                raise ValueError("could not find config file %s" % fp)
            try:
                fp = self.open(fp, 'r')
                need_close = True
            except (IOError, OSError):
                raise ValueError("could not read config file %s" % fp)

        parser = UnhosedConfigParser()
        parser.expansions = self.environ_expansions
        try:
            try:
                parser.read_file(fp)
            except AttributeError:
                # noinspection PyDeprecation
                parser.readfp(fp)
        except ConfigParser.ParsingError as why:
            raise ValueError(str(why))
        finally:
            if need_close:
                fp.close()

        host_node_name = platform.node()
        expansions = {'here': self.here,
                      'host_node_name':host_node_name}
        expansions.update(self.environ_expansions)
        if parser.has_section('include'):
            parser.expand_here(self.here)
            if not parser.has_option('include', 'files'):
                raise ValueError(".ini file has [include] section, but no "
                                 "files setting")
            files = parser.get('include', 'files')
            files = expand(files, expansions, 'include.files')
            files = files.split()
            if hasattr(fp, 'name'):
                base = os.path.dirname(os.path.abspath(fp.name))
            else:
                base = '.'
            for pattern in files:
                pattern = os.path.join(base, pattern)
                filenames = glob.glob(pattern)
                if not filenames:
                    self.parse_warnings.append(
                        'No file matches via include "%s"' % pattern)
                    continue
                for filename in sorted(filenames):
                    self.parse_infos.append(
                        'Included extra file "%s" during parsing' % filename)
                    try:
                        parser.read(filename)
                    except ConfigParser.ParsingError as why:
                        raise ValueError(str(why))
                    else:
                        parser.expand_here(
                            os.path.abspath(os.path.dirname(filename))
                        )

        sections = parser.sections()
        if 'supervisord' not in sections:
            raise ValueError('.ini file does not include supervisord section')

        common_expansions = {'here': self.here}

        def get(opt, default, **kwargs):
            expansions = kwargs.get('expansions', {})
            expansions.update(common_expansions)
            kwargs['expansions'] = expansions
            return parser.getdefault(opt, default, **kwargs)

        section.minfds = integer(get('minfds', 1024))
        section.minprocs = integer(get('minprocs', 200))

        directory = get('directory', None)
        if directory is None:
            section.directory = None
        else:
            section.directory = existing_directory(directory)

        section.user = get('user', None)
        section.umask = octal_type(get('umask', '022'))
        section.logfile = existing_dirpath(get('logfile', 'supervisord.log'))
        section.logfile_maxbytes = byte_size(get('logfile_maxbytes', '50MB'))
        section.logfile_backups = integer(get('logfile_backups', 10))
        section.loglevel = logging_level(get('loglevel', 'info'))
        section.pidfile = existing_dirpath(get('pidfile', 'supervisord.pid'))
        section.identifier = get('identifier', 'supervisor')
        section.nodaemon = boolean(get('nodaemon', 'false'))
        section.delaysecs = float(get("delaysecs", 0.2))

        tempdir = tempfile.gettempdir()
        section.childlogdir = existing_directory(get('childlogdir', tempdir))
        section.nocleanup = boolean(get('nocleanup', 'false'))
        section.strip_ansi = boolean(get('strip_ansi', 'false'))

        environ_str = get('environment', '')
        environ_str = expand(environ_str, expansions, 'environment')
        section.environment = dict_of_key_value_pairs(environ_str)
        # Process rpcinterface plugins before groups to allow custom events to
        # be registered.
        section.rpcinterface_factories = self.get_plugins(
            parser,
            'supervisor.rpcinterface_factory',
            'rpcinterface:'
        )
        section.process_group_configs = self.process_groups_from_parser(parser)
        for group in section.process_group_configs:
            for proc in group.process_configs:
                env = section.environment.copy()
                env.update(proc.environment)
                proc.environment = env
        section.server_configs = self.server_configs_from_parser(parser)
        section.profile_options = None
        return section

    def process_groups_from_parser(self, parser):
        groups = []
        all_sections = parser.sections()
        homogeneous_exclude = []

        common_expansions = {'here': self.here}

        def get(section, opt, default, **kwargs):
            expansions = kwargs.get('expansions', {})
            expansions.update(common_expansions)
            kwargs['expansions'] = expansions
            return parser.saneget(section, opt, default, **kwargs)

        # process heterogeneous groups
        for section in all_sections:
            if not section.startswith('group:'):
                continue
            group_name = process_or_group_name(section.split(':', 1)[1])
            programs = list_of_strings(get(section, 'programs', None))
            priority = integer(get(section, 'priority', 999))
            group_processes = []
            for program in programs:
                program_section = "program:%s" % program
                if not program_section in all_sections:
                    raise ValueError(
                        '[%s] names unknown program %s' % (section, program))
                homogeneous_exclude.append(program_section)
                processes = self.processes_from_section(parser, program_section,
                                                        group_name,
                                                        ProcessConfig)
                group_processes.extend(processes)
            groups.append(
                ProcessGroupConfig(self, group_name, priority, group_processes)
            )

        # process "normal" homogeneous groups
        for section in all_sections:
            if not section.startswith('program:') or section in homogeneous_exclude:
                continue
            program_name = process_or_group_name(section.split(':', 1)[1])
            priority = integer(get(section, 'priority', 999))
            processes = self.processes_from_section(parser, section, program_name,
                                                    ProcessConfig)
            groups.append(
                ProcessGroupConfig(self, program_name, priority, processes)
            )

        # process "event listener" homogeneous groups
        for section in all_sections:
            if not section.startswith('eventlistener:'):
                continue
            pool_name = section.split(':', 1)[1]
            # give listeners a "high" default priority so they are started first
            # and stopped last at mainloop exit
            priority = integer(get(section, 'priority', -1))
            buffer_size = integer(get(section, 'buffer_size', 10))

            result_handler = get(section, 'result_handler',
                                 'supervisor.dispatchers:default_handler')
            try:
                result_handler = self.import_spec(result_handler)
            except ImportError:
                raise ValueError('%s cannot be resolved within [%s]' % (
                    result_handler, section))

            pool_event_names = [x.upper() for x in
                                list_of_strings(get(section, 'events', ''))]
            pool_event_names = set(pool_event_names)
            if not pool_event_names:
                raise ValueError('[%s] section requires an "events" line' %
                                 section)

            from supervisor.events import EventTypes

            pool_events = []
            for pool_event_name in pool_event_names:
                pool_event = getattr(EventTypes, pool_event_name, None)
                if pool_event is None:
                    raise ValueError('Unknown event type %s in [%s] events' %
                                     (pool_event_name, section))
                pool_events.append(pool_event)

            redirect_stderr = boolean(get(section, 'redirect_stderr', 'false'))
            if redirect_stderr:
                raise ValueError('[%s] section sets redirect_stderr=true '
                                 'but this is not allowed because it will interfere '
                                 'with the eventlistener protocol' % section)

            processes = self.processes_from_section(parser, section, pool_name,
                                                    EventListenerConfig)

            groups.append(
                EventListenerPoolConfig(self, pool_name, priority, processes,
                                        buffer_size, pool_events,
                                        result_handler)
            )

        # process fastcgi homogeneous groups
        for section in all_sections:
            if not section.startswith('fcgi-program:') or section in homogeneous_exclude:
                continue
            program_name = process_or_group_name(section.split(':', 1)[1])
            priority = integer(get(section, 'priority', 999))
            fcgi_expansions = {'program_name': program_name}

            socket = get(section, 'socket', None, expansions=fcgi_expansions)
            if not socket:
                raise ValueError('[%s] section requires a "socket" line' %
                                 section)

            try:
                socket_config = self.parse_fcgi_socket(socket)
            except ValueError as e:
                raise ValueError('%s in [%s] socket' % (str(e), section))

            processes = self.processes_from_section(parser, section, program_name,
                                                    FastCGIProcessConfig)
            groups.append(
                FastCGIGroupConfig(self, program_name, priority, processes,
                                   socket_config)
            )

        groups.sort()
        return groups

    def parse_fcgi_socket(self, sock,
                          proc_uid=None,
                          socket_owner=None,
                          socket_mode=None):
        if socket_owner is not None or socket_mode is not None:
            raise ValueError("socket_owner and socket_mode params should"
                             + " only be used with a Unix domain socket")

        m = re.match(r'tcp://([^\s:]+):(\d+)$', sock)
        if m:
            host = m.group(1)
            port = int(m.group(2))
            return InetStreamSocketConfig(host, port)

        raise ValueError("Bad socket format %s", sock)

    def processes_from_section(self, parser, section, group_name,
                               klass=None):
        try:
            return self._processes_from_section(
                parser, section, group_name, klass)
        except ValueError as e:
            filename = parser.section_to_file.get(section, self.configfile)
            raise ValueError('%s in section %r (file: %r)'
                             % (e, section, filename))

    def _processes_from_section(self, parser, section, group_name,
                                klass=None):
        """tag: subprocess"""
        if klass is None:
            klass = ProcessConfig
        programs = []

        program_name = process_or_group_name(section.split(':', 1)[1])
        host_node_name = platform.node()
        common_expansions = {
            'here': self.here,
            'program_name': program_name,
            'host_node_name': host_node_name,
            'group_name': group_name
        }

        def get(section, opt, *args, **kwargs):
            expansions = kwargs.get('expansions', {})
            expansions.update(common_expansions)
            kwargs['expansions'] = expansions
            return parser.saneget(section, opt, *args, **kwargs)

        # cpu settings
        cpupriority = get(section, 'cpupriority', None)
        cpuaffinity = integer(get(section, 'cpuaffinity', 0))

        # system settings
        systemjob = boolean(get(section, 'systemjob', 'true'))

        # default settings
        priority = integer(get(section, 'priority', 999))
        autostart = boolean(get(section, 'autostart', 'true'))
        autorestart = auto_restart(get(section, 'autorestart', 'unexpected'))
        startsecs = integer(get(section, 'startsecs', 1))
        startretries = integer(get(section, 'startretries', 3))
        stopsignal = signal_number(get(section, 'stopsignal', 'TERM'))
        stopwaitsecs = integer(get(section, 'stopwaitsecs', 10))
        stopasgroup = boolean(get(section, 'stopasgroup', 'false'))
        killasgroup = boolean(get(section, 'killasgroup', stopasgroup))
        exitcodes = list_of_exitcodes(get(section, 'exitcodes', '0,2'))
        # see also redirect_stderr check in process_groups_from_parser()
        redirect_stderr = boolean(get(section, 'redirect_stderr', 'false'))
        numprocs = integer(get(section, 'numprocs', 1))
        numprocs_start = integer(get(section, 'numprocs_start', 0))
        environment_str = get(section, 'environment', '', do_expand=False)
        stdout_cmaxbytes = byte_size(get(section, 'stdout_capture_maxbytes', '0'))
        stdout_events = boolean(get(section, 'stdout_events_enabled', 'false'))
        stderr_cmaxbytes = byte_size(get(section, 'stderr_capture_maxbytes', '0'))
        stderr_events = boolean(get(section, 'stderr_events_enabled', 'false'))
        serverurl = get(section, 'serverurl', None)
        if serverurl and serverurl.strip().upper() == 'AUTO':
            serverurl = None

        # find uid from "user" option
        # user = get(section, 'user', None)

        umask = get(section, 'umask', None)
        if umask is not None:
            umask = octal_type(umask)

        process_name = process_or_group_name(
            get(section, 'process_name', '%(program_name)s', do_expand=False))

        if numprocs > 1:
            if not '%(process_num)' in process_name:
                # process_name needs to include process_num when we
                # represent a group of processes
                raise ValueError(
                    '%(process_num) must be present within process_name when '
                    'numprocs > 1')

        if stopasgroup and not killasgroup:
            raise ValueError(
                "Cannot set stopasgroup=true and killasgroup=false"
            )

        for process_num in range(numprocs_start, numprocs + numprocs_start):
            expansions = common_expansions
            expansions.update({'process_num': process_num})
            expansions.update(self.environ_expansions)

            environment = dict_of_key_value_pairs(
                expand(environment_str, expansions, 'environment'))

            directory = get(section, 'directory', None)

            logfiles = {}

            for k in ('stdout', 'stderr'):
                n = '%s_logfile' % k
                lf_val = get(section, n, Automatic)
                if isinstance(lf_val, basestring):
                    lf_val = expand(lf_val, expansions, n)
                lf_val = logfile_name(lf_val)
                logfiles[n] = lf_val

                bu_key = '%s_logfile_backups' % k
                backups = integer(get(section, bu_key, 10))
                logfiles[bu_key] = backups

                mb_key = '%s_logfile_maxbytes' % k
                maxbytes = byte_size(get(section, mb_key, '50MB'))
                logfiles[mb_key] = maxbytes

                sy_key = '%s_syslog' % k
                syslog = boolean(get(section, sy_key, False))
                logfiles[sy_key] = syslog

                if lf_val is Automatic and not maxbytes:
                    self.parse_warnings.append(
                        'For [%s], AUTO logging used for %s without '
                        'rollover, set maxbytes > 0 to avoid filling up '
                        'filesystem unintentionally' % (section, n))

            if redirect_stderr:
                if logfiles['stderr_logfile'] not in (Automatic, None):
                    self.parse_warnings.append(
                        'For [%s], redirect_stderr=true but stderr_logfile has '
                        'also been set to a filename, the filename has been '
                        'ignored' % section)
                # never create an stderr logfile when redirected
                logfiles['stderr_logfile'] = None

            command = get(section, 'command', None, expansions=expansions)
            if command is None:
                raise ValueError('program section %s does not specify a command' % section)

            pconfig = klass(
                self,
                name=expand(process_name, expansions, 'process_name'),
                command=command,
                directory=directory,
                umask=umask,
                priority=priority,
                autostart=autostart,
                autorestart=autorestart,
                startsecs=startsecs,
                startretries=startretries,
                uid=self.uid,
                cpupriority=cpupriority,
                cpuaffinity=cpuaffinity,
                systemjob=systemjob,
                stdout_logfile=logfiles['stdout_logfile'],
                stdout_capture_maxbytes=stdout_cmaxbytes,
                stdout_events_enabled=stdout_events,
                stdout_logfile_backups=logfiles['stdout_logfile_backups'],
                stdout_logfile_maxbytes=logfiles['stdout_logfile_maxbytes'],
                stdout_syslog=logfiles['stdout_syslog'],
                stderr_logfile=logfiles['stderr_logfile'],
                stderr_capture_maxbytes=stderr_cmaxbytes,
                stderr_events_enabled=stderr_events,
                stderr_logfile_backups=logfiles['stderr_logfile_backups'],
                stderr_logfile_maxbytes=logfiles['stderr_logfile_maxbytes'],
                stderr_syslog=logfiles['stderr_syslog'],
                stopsignal=stopsignal,
                stopwaitsecs=stopwaitsecs,
                stopasgroup=stopasgroup,
                killasgroup=killasgroup,
                exitcodes=exitcodes,
                redirect_stderr=redirect_stderr,
                environment=environment,
                serverurl=serverurl)

            programs.append(pconfig)

        programs.sort()  # asc by priority
        return programs

    def _parse_servernames(self, parser, stype):
        options = []
        for section in parser.sections():
            if section.startswith(stype):
                parts = section.split(':', 1)
                if len(parts) > 1:
                    name = parts[1]
                else:
                    name = None  # default sentinel
                options.append((name, section))
        return options

    def _parse_username_and_password(self, parser, section):
        get = parser.saneget
        username = get(section, 'username', None)
        password = get(section, 'password', None)
        if username is None and password is not None:
            raise ValueError(
                'Must specify username if password is specified in [%s]'
                % section)
        return {'username': username, 'password': password}

    def server_configs_from_parser(self, parser):
        configs = []
        inet_serverdefs = self._parse_servernames(parser, 'inet_http_server')
        for name, section in inet_serverdefs:
            config = {}
            get = parser.saneget
            config.update(self._parse_username_and_password(parser, section))
            config['name'] = name
            config['family'] = socket.AF_INET
            port = get(section, 'port', None)
            if port is None:
                raise ValueError('section [%s] has no port value' % section)
            host, port = inet_address(port)
            config['host'] = host
            config['port'] = port
            config['section'] = section
            configs.append(config)

        if self._parse_servernames(parser, 'unix_http_server'):
            raise ValueError('section [unix_http_server] not supported.\n'
                             'remove this from supervisord.conf')
        return configs

    @raise_not_implemented
    def daemonize(self):
        """dummy"""
        pass

    def write_pidfile(self):
        pid = os.getpid()
        try:
            with open(self.pidfile, 'w') as f:
                f.write('%s\n' % pid)
        except (IOError, OSError):
            self.logger.critical('could not write pidfile %s' % self.pidfile)
        else:
            self.logger.info('supervisord started with pid %s' % pid)

    def cleanup(self):
        self._try_unlink(self.pidfile)

    def _try_unlink(self, path):
        try:
            os.unlink(path)
        except OSError:
            pass

    def close_httpservers(self):
        dispatcher_servers = []
        for config, server in self.httpservers:
            server.close()
            # server._map is a reference to the asyncore socket_map
            for dispatcher in self.get_socket_map().values():
                dispatcher_server = getattr(dispatcher, 'server', None)
                if dispatcher_server is server:
                    dispatcher_servers.append(dispatcher)
        for server in dispatcher_servers:
            # TODO: try to remove this entirely.
            # For unknown reasons, sometimes an http_channel
            # dispatcher in the socket map related to servers
            # remains open *during a reload*.  If one of these
            # exists at this point, we need to close it by hand
            # (thus removing it from the asyncore.socket_map).  If
            # we don't do this, 'cleanup_fds' will cause its file
            # descriptor to be closed, but it will still remain in
            # the socket_map, and eventually its file descriptor
            # will be passed to # select(), which will bomb.  See
            # also http://www.plope.com/software/collector/253
            server.close()

    def close_logger(self):
        try:
            self.logger.close()
        except AttributeError:
            # Pywin32 : PyTraceObject error
            pass

    def setsignals(self):
        thread = threading.current_thread()
        if thread.getName() == "MainThread":
            receive = self.signal_receiver.receive
            signal.signal(signal.SIGTERM, receive)
            signal.signal(signal.SIGINT, receive)
            signal.signal(signal.SIGABRT, receive)

    def get_signal(self):
        return self.signal_receiver.get_signal()

    def openhttpservers(self, supervisord):
        try:
            self.httpservers = self.make_http_servers(supervisord)
        except socket.error as why:
            if why.args[0] == errno.EADDRINUSE:
                self.usage('Another program is already listening on '
                           'a port that one of our HTTP servers is '
                           'configured to use.  Shut this program '
                           'down first before starting supervisord.')
            else:
                help = 'Cannot open an HTTP server: socket.error reported'
                errorname = errno.errorcode.get(why.args[0])
                if errorname is None:
                    self.usage('%s %s' % (help, why.args[0]))
                else:
                    self.usage('%s errno.%s (%d)' %
                               (help, errorname, why.args[0]))
            self.unlink_socketfiles = False
        except ValueError as why:
            self.usage(why.args[0])

    def get_autochildlog_name(self, name, identifier, channel):
        prefix = '%s-%s---%s-' % (name, channel, identifier)
        logfile = self.mktempfile(
            suffix='.log',
            prefix=prefix,
            dir=self.childlogdir)
        return logfile

    def clear_autochildlogdir(self):
        # must be called after realize()
        childlogdir = self.childlogdir
        fnre = re.compile(r'.+?---%s-\S+\.log\.{0,1}\d{0,4}' % self.identifier)
        try:
            filenames = os.listdir(childlogdir)
        except (IOError, OSError):
            self.logger.warn('Could not clear childlog dir')
            return

        for filename in filenames:
            if fnre.match(filename):
                pathname = os.path.join(childlogdir, filename)
                try:
                    self.remove(pathname)
                except (OSError, IOError):
                    self.logger.warn('Failed to clean up \'%r\'' % pathname)

    def get_socket_map(self):
        return asyncore.socket_map

    @raise_not_implemented
    def cleanup_fds(self):
        """dummy"""
        pass

    def kill(self, pid, sig):
        self.pidhistory[pid].process.send_signal(sig)

    def set_uid(self):
        if self.uid is None:
            if False and os.getuid() == 0:
                return 'Supervisor running as root (no user in config file)'
            return None
        msg = self.dropPrivileges(self.uid)
        if msg is None:
            return 'Set uid to user %s' % self.uid
        return msg

    @raise_not_implemented
    def dropPrivileges(self, user):
        """dummy"""
        pass

    def register_pid(self, pid, sproc):
        self.pidhistory[pid] = sproc

    def get_pid_history(self, pid):
        """Returns the subprocess registered for id"""
        return self.pidhistory[pid]

    def remove_pid_history(self, pid):
        """Removes the registered subprocess for id"""
        del self.pidhistory[pid]

    def waitpid(self):
        stopped = []
        for pid in self.pidhistory:
            subprocess = self.pidhistory[pid]
            process = subprocess.process
            if process.poll() is not None:
                stopped.append((pid, (process.poll(), process.message)))
        if not stopped:
            stopped.append((None, None))
        return stopped

    @raise_not_implemented
    def set_rlimits(self):
        """dummy"""
        pass

    def make_logger(self, critical_messages, warn_messages, info_messages):
        # must be called after realize() and after supervisor does setuid()
        format = '%(asctime)s %(levelname)s %(message)s\n'
        self.logger = loggers.getLogger(self.loglevel)
        loggers.handle_file(
            self.logger,
            self.logfile,
            format,
            rotating=True,
            maxbytes=self.logfile_maxbytes,
            backups=self.logfile_backups,
        )
        if self.nodaemon:
            loggers.handle_stdout(self.logger, format)
        for msg in critical_messages:
            self.logger.critical(msg)
        for msg in warn_messages:
            self.logger.warn(msg)
        for msg in info_messages:
            self.logger.info(msg)

    def make_http_servers(self, supervisord):
        from supervisor.http import make_http_servers

        return make_http_servers(self, supervisord)

    def close_fd(self, fd):
        try:
            os.close(fd)
        except OSError:
            pass

    def fork(self):
        return 0  # os.fork()

    def dup2(self, frm, to):
        return os.dup2(frm, to)

    def setpgrp(self):
        return None  # os.setpgrp()

    def stat(self, filename):
        return os.stat(filename)

    @raise_not_implemented
    def execve(self, filename, argv, **kwargs):
        """dummy"""
        pass

    def mktempfile(self, suffix, prefix, dir):
        # set os._urandomfd as a hack around bad file descriptor bug
        # seen in the wild, see
        # http://www.plope.com/software/collector/252
        os._urandomfd = None
        fd, filename = tempfile.mkstemp(suffix, prefix, dir)
        os.close(fd)
        return filename

    def remove(self, path):
        os.remove(path)

    def _exit(self, code):
        """dummy interface"""
        pass

    def setumask(self, mask):
        """dummy interface"""
        pass

    def get_path(self):
        """Return a list corresponding to $PATH, or a default."""
        path = []
        if "PATH" in os.environ:
            p = os.environ["PATH"]
            if p:
                path = p.split(os.pathsep)
        return path

    def get_pid(self):
        return os.getpid()

    def check_execv_args(self, filename, argv, st):
        if st is None:
            raise NotFound("can't find command %r" % filename)

        elif stat.S_ISDIR(st[stat.ST_MODE]):
            raise NotExecutable("command at %r is a directory" % filename)

        elif not (stat.S_IMODE(st[stat.ST_MODE]) & 73):
            # 73 is spelled 0111 in py2, 0o111 in py3
            raise NotExecutable("command at %r is not executable" % filename)

        elif not os.access(filename, os.X_OK):
            raise NoPermission("no permission to run command %r" % filename)

    def reopenlogs(self):
        self.logger.info('supervisord logreopen')
        for handler in self.logger.handlers:
            if hasattr(handler, 'reopen'):
                handler.reopen()

    def readfd(self, stream):
        """
        The work of this method is to read the data stream of a process, but without blocking
        the work of the supervisor. A buffer of data is being read in a thread and when the total
        data is reached is given in return for one of the Dispatcher objects responsible.
        """
        return stream.readline()

    def write(self, fd, data):
        return os.write(fd if type(fd) is int else fd.fileno(), as_bytes(data))

    def process_environment(self):
        os.environ.update(self.environment or {})

    def chdir(self, dir):
        """dummy interface only"""
        pass

    def make_pipes(self, pid, stderr=True):
        """ Create pipes for parent to child stdin/stdout/stderr
        communications.  Open fd in non-blocking mode so we can read them
        in the mainloop without blocking.  If stderr is False, don't
        create a pipe for stderr. """
        try:
            process = self.pidhistory[pid].process
        except KeyError:
            raise IOError('pid (%s)' % pid)
        pipes = {
            'stdin': process.stdin,
            'stdout': helpers.StreamAsync(
                process.stdout,
                name='stdout-pid-{0:d}'.format(pid)
            )
        }
        if stderr:
            pipes['stderr'] = helpers.StreamAsync(
                process.stderr,
                name='stderr-pid-{0:d}'.format(pid)
            )
        else:
            pipes['stderr'] = None
        return pipes

    def close_parent_pipes(self, pipes):
        for fdname in ('stdin', 'stdout', 'stderr'):
            fd = pipes.get(fdname)
            if fd is not None:
                self.close_fd(fd)

    def close_child_pipes(self, pipes):
        for fdname in ('child_stdin', 'child_stdout', 'child_stderr'):
            fd = pipes.get(fdname)
            if fd is not None:
                self.close_fd(fd)


class ClientOptions(Options):
    positional_args_allowed = 1

    interactive = None
    prompt = None
    serverurl = None
    username = None
    password = None
    history_file = None

    def __init__(self):
        Options.__init__(self, require_configfile=False)
        self.configroot = Dummy()
        self.configroot.supervisorctl = Dummy()
        self.configroot.supervisorctl.interactive = None
        self.configroot.supervisorctl.prompt = 'supervisor'
        self.configroot.supervisorctl.serverurl = None
        self.configroot.supervisorctl.username = None
        self.configroot.supervisorctl.password = None
        self.configroot.supervisorctl.history_file = None

        from supervisor.supervisorctl import DefaultControllerPlugin

        default_factory = ('default', DefaultControllerPlugin, {})
        # we always add the default factory. If you want to a supervisorctl
        # without the default plugin, please write your own supervisorctl.
        self.plugin_factories = [default_factory]

        self.add("interactive", "supervisorctl.interactive", "i",
                 "interactive", flag=1, default=0)
        self.add("prompt", "supervisorctl.prompt", default="supervisor")
        self.add("serverurl", "supervisorctl.serverurl", "s:", "serverurl=",
                 url, default="http://localhost:9001")
        self.add("username", "supervisorctl.username", "u:", "username=")
        self.add("password", "supervisorctl.password", "p:", "password=")
        self.add("history", "supervisorctl.history_file", "r:", "history_file=")

    def realize(self, *arg, **kw):
        Options.realize(self, *arg, **kw)
        if not self.args:
            self.interactive = 1

    def read_config(self, fp):
        section = self.configroot.supervisorctl
        need_close = False
        if not hasattr(fp, 'read'):
            self.here = os.path.dirname(normalize_path(fp))
            if not self.exists(fp):
                raise ValueError("could not find config file %s" % fp)
            try:
                fp = self.open(fp, 'r')
                need_close = True
            except (IOError, OSError):
                raise ValueError("could not read config file %s" % fp)

        parser = UnhosedConfigParser()
        parser.expansions = self.environ_expansions
        parser.mysection = 'supervisorctl'
        try:
            parser.read_file(fp)
        except AttributeError:
            parser.readfp(fp)
        if need_close:
            fp.close()
        sections = parser.sections()
        if not 'supervisorctl' in sections:
            raise ValueError('.ini file does not include supervisorctl section')
        serverurl = parser.getdefault('serverurl', 'http://localhost:9001')
        if serverurl.startswith('unix://'):
            sf = serverurl[7:]
            path = expand(sf, {'here': self.here}, 'serverurl')
            path = normalize_path(path)
            serverurl = 'unix://%s' % path
        section.serverurl = serverurl

        # The defaults used below are really set in __init__ (since
        # section==self.configroot.supervisorctl)
        section.prompt = parser.getdefault('prompt', section.prompt)
        section.username = parser.getdefault('username', section.username)
        section.password = parser.getdefault('password', section.password)
        history_file = parser.getdefault('history_file', section.history_file)

        if history_file:
            history_file = normalize_path(history_file)
            section.history_file = history_file
            self.history_file = history_file
        else:
            section.history_file = None
            self.history_file = None

        self.plugin_factories += self.get_plugins(
            parser,
            'supervisor.ctl_factory',
            'ctlplugin:'
        )

        return section

    # TODO: not covered by any test, but used by supervisorctl
    def getServerProxy(self):
        return xmlrpclib.ServerProxy(
            # dumbass ServerProxy won't allow us to pass in a non-HTTP url,
            # so we fake the url we pass into it and always use the transport's
            # 'serverurl' to figure out what to attach to
            'http://127.0.0.1',
            transport=xmlrpc.SupervisorTransport(self.username,
                                                 self.password,
                                                 self.serverurl)
        )


_marker = []


class UnhosedConfigParser(ConfigParser.RawConfigParser):
    mysection = 'supervisord'

    def __init__(self, *args, **kwargs):
        # inline_comment_prefixes was added in Python 3 but its default makes
        # RawConfigParser behave differently than it did on Python 2.  This
        # makes it behave the same by default on Python 2 and 3.
        if PY3 and ('inline_comment_prefixes' not in kwargs):
            kwargs['inline_comment_prefixes'] = (';', '#')

        ConfigParser.RawConfigParser.__init__(self, *args, **kwargs)

        self.section_to_file = {}
        self.expansions = {}

    def read_string(self, string, source='<string>'):
        '''Parse configuration data from a string.  This is intended
        to be used in tests only.  We add this method for Py 2/3 compat.'''
        try:
            return ConfigParser.RawConfigParser.read_string(
                self, string, source)  # Python 3.2 or later
        except AttributeError:
            return self.readfp(StringIO(string))

    def read(self, filenames, **kwargs):
        '''Attempt to read and parse a list of filenames, returning a list
        of filenames which were successfully parsed.  This is a method of
        RawConfigParser that is overridden to build self.section_to_file,
        which is a mapping of section names to the files they came from.
        '''
        if isinstance(filenames, basestring):  # RawConfigParser compat
            filenames = [filenames]

        ok_filenames = []
        for filename in filenames:
            sections_orig = self._sections.copy()

            ok_filenames.extend(
                ConfigParser.RawConfigParser.read(self, [filename], **kwargs))

            diff = frozenset(self._sections) - frozenset(sections_orig)
            for section in diff:
                self.section_to_file[section] = filename
        return ok_filenames

    def saneget(self, section, option, default=_marker, do_expand=True,
                expansions={}):
        try:
            optval = self.get(section, option)
        except ConfigParser.NoOptionError:
            if default is _marker:
                raise
            else:
                optval = default

        if do_expand and isinstance(optval, basestring):
            combined_expansions = dict(
                list(self.expansions.items()) + list(expansions.items()))

            optval = expand(optval, combined_expansions,
                            "%s.%s" % (section, option))

        return optval

    def getdefault(self, option, default=_marker, expansions={}, **kwargs):
        return self.saneget(self.mysection, option, default=default,
                            expansions=expansions, **kwargs)

    def expand_here(self, here):
        if here is None:
            return
        HERE_FORMAT = '%(here)s'
        for section in self.sections():
            for key, value in self.items(section):
                if HERE_FORMAT in value:
                    value = value.replace(HERE_FORMAT, here)
                    self.set(section, key, value)


class Config(object):
    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.name < other.name

        return self.priority < other.priority

    def __le__(self, other):
        if self.priority == other.priority:
            return self.name <= other.name

        return self.priority <= other.priority

    def __gt__(self, other):
        if self.priority == other.priority:
            return self.name > other.name

        return self.priority > other.priority

    def __ge__(self, other):
        if self.priority == other.priority:
            return self.name >= other.name

        return self.priority >= other.priority

    def __repr__(self):
        return '<%s instance at %s named %s>' % (self.__class__, id(self),
                                                 self.name)


class ProcessConfig(Config):
    req_param_names = [
        'name', 'uid', 'command', 'directory', 'umask', 'priority',
        'autostart', 'autorestart', 'startsecs', 'startretries',
        'stdout_logfile', 'stdout_capture_maxbytes',
        'stdout_events_enabled', 'stdout_syslog',
        'stdout_logfile_backups', 'stdout_logfile_maxbytes',
        'stderr_logfile', 'stderr_capture_maxbytes',
        'stderr_logfile_backups', 'stderr_logfile_maxbytes',
        'stderr_events_enabled', 'stderr_syslog',
        'stopsignal', 'stopwaitsecs', 'stopasgroup', 'killasgroup',
        'exitcodes', 'redirect_stderr']
    optional_param_names = [
        'environment', 'serverurl',
        'cpupriority', 'cpuaffinity',
        'systemjob'
    ]

    def __init__(self, options, **params):
        self.options = options
        for name in self.req_param_names:
            setattr(self, name, params[name])
        for name in self.optional_param_names:
            setattr(self, name, params.get(name, None))

    def __eq__(self, other):
        if not isinstance(other, ProcessConfig):
            return False

        for name in self.req_param_names + self.optional_param_names:
            if Automatic in [getattr(self, name), getattr(other, name)]:
                continue
            if getattr(self, name) != getattr(other, name):
                return False

        return True

    def create_autochildlogs(self):
        # temporary logfiles which are erased at start time
        get_autoname = self.options.get_autochildlog_name
        sid = self.options.identifier
        name = self.name
        if self.stdout_logfile is Automatic:
            self.stdout_logfile = get_autoname(name, sid, 'stdout')
        if self.stderr_logfile is Automatic and not self.redirect_stderr:
            self.stderr_logfile = get_autoname(name, sid, 'stderr')

    def make_process(self, group=None):
        from supervisor.process import Subprocess

        process = Subprocess(self)
        process.group = group
        return process

    def make_dispatchers(self, proc):
        use_stderr = not self.redirect_stderr
        pipes = self.options.make_pipes(proc.pid, use_stderr)
        stdout_fd = pipes['stdout']
        stderr_fd = pipes['stderr']
        stdin_fd = pipes['stdin']
        dispatchers = {}
        from supervisor import events
        from supervisor.dispatchers import (
            PStreamOutputDispatcher,
            POutputDispatcher,
            PInputDispatcher
        )
        if stdout_fd is not None:
            if isinstance(stdout_fd, helpers.StreamAsync):
                dispatcher = PStreamOutputDispatcher
            else:
                dispatcher = POutputDispatcher
            etype = events.ProcessCommunicationStdoutEvent
            dispatchers[stdout_fd] = dispatcher(proc, etype, stdout_fd)
        if stderr_fd is not None:
            etype = events.ProcessCommunicationStderrEvent
            if isinstance(stdout_fd, helpers.StreamAsync):
                dispatcher = PStreamOutputDispatcher
            else:
                dispatcher = POutputDispatcher
            dispatchers[stderr_fd] = dispatcher(proc, etype, stderr_fd)
        if stdin_fd is not None:
            dispatchers[stdin_fd] = PInputDispatcher(proc, 'stdin', stdin_fd)
        return dispatchers, pipes


class EventListenerConfig(ProcessConfig):
    def make_dispatchers(self, proc):
        # always use_stderr=True for eventlisteners because mixing stderr
        # messages into stdout would break the eventlistener protocol
        use_stderr = True
        pipes = self.options.make_pipes(proc.pid, use_stderr)
        stdout_fd = pipes['stdout']
        stderr_fd = pipes['stderr']
        stdin_fd = pipes['stdin']
        dispatchers = {}
        from supervisor import events
        from supervisor.dispatchers import (
            PStreamEventListenerDispatcher,
            PStreamOutputDispatcher,
            PEventListenerDispatcher,
            POutputDispatcher,
            PInputDispatcher
        )
        from supervisor import helpers
        if stdout_fd is not None:
            if isinstance(stdout_fd, helpers.StreamAsync):
                dispatcher = PStreamEventListenerDispatcher
            else:
                dispatcher = PEventListenerDispatcher
            dispatchers[stdout_fd] = dispatcher(proc, 'stdout', stdout_fd)
        if stderr_fd is not None:
            etype = events.ProcessCommunicationStderrEvent
            if isinstance(stdout_fd, helpers.StreamAsync):
                dispatcher = PStreamOutputDispatcher
            else:
                dispatcher = POutputDispatcher
            dispatchers[stderr_fd] = dispatcher(proc, etype, stderr_fd)
        if stdin_fd is not None:
            dispatchers[stdin_fd] = PInputDispatcher(proc, 'stdin', stdin_fd)
        return dispatchers, pipes


class FastCGIProcessConfig(ProcessConfig):
    def make_process(self, group=None):
        if group is None:
            raise NotImplementedError('FastCGI programs require a group')
        from supervisor.process import FastCGISubprocess

        process = FastCGISubprocess(self)
        process.group = group
        return process

    def make_dispatchers(self, proc):
        dispatchers, p = ProcessConfig.make_dispatchers(self, proc)
        # FastCGI child processes expect the FastCGI socket set to
        # file descriptor 0, so supervisord cannot use stdin
        # to communicate with the child process
        stdin_fd = p['stdin']
        if stdin_fd is not None:
            dispatchers[stdin_fd].close()
        return dispatchers, p


class ProcessGroupConfig(Config):
    def __init__(self, options, name, priority, process_configs):
        self.options = options
        self.name = name
        self.priority = priority
        self.process_configs = process_configs

    def __eq__(self, other):
        if not isinstance(other, ProcessGroupConfig):
            return False

        if self.name != other.name:
            return False
        if self.priority != other.priority:
            return False
        if self.process_configs != other.process_configs:
            return False

        return True

    def after_setuid(self):
        for config in self.process_configs:
            config.create_autochildlogs()

    def make_group(self):
        from supervisor.process import ProcessGroup

        return ProcessGroup(self)


class EventListenerPoolConfig(Config):
    def __init__(self, options, name, priority, process_configs, buffer_size,
                 pool_events, result_handler):
        self.options = options
        self.name = name
        self.priority = priority
        self.process_configs = process_configs
        self.buffer_size = buffer_size
        self.pool_events = pool_events
        self.result_handler = result_handler

    def __eq__(self, other):
        if not isinstance(other, EventListenerPoolConfig):
            return False

        if ((self.name == other.name) and
            (self.priority == other.priority) and
            (self.process_configs == other.process_configs) and
            (self.buffer_size == other.buffer_size) and
            (self.pool_events == other.pool_events) and
            (self.result_handler == other.result_handler)):
            return True

        return False

    def after_setuid(self):
        for config in self.process_configs:
            config.create_autochildlogs()

    def make_group(self):
        from supervisor.process import EventListenerPool

        return EventListenerPool(self)


class FastCGIGroupConfig(ProcessGroupConfig):
    def __init__(self, options, name, priority, process_configs, socket_config):
        ProcessGroupConfig.__init__(
            self,
            options,
            name,
            priority,
            process_configs,
        )
        self.socket_config = socket_config

    def __eq__(self, other):
        if not isinstance(other, FastCGIGroupConfig):
            return False

        if self.socket_config != other.socket_config:
            return False

        return ProcessGroupConfig.__eq__(self, other)

    def make_group(self):
        from supervisor.process import FastCGIProcessGroup

        return FastCGIProcessGroup(self)


def readFile(filename, offset, length):
    """ Read length bytes from the file named by filename starting at
    offset """

    absoffset = abs(offset)
    abslength = abs(length)

    try:
        with codecs.open(filename, 'rb', encoding='UTF-8') as f:
            if absoffset != offset:
                # negative offset returns offset bytes from tail of the file
                if length:
                    raise ValueError('BAD_ARGUMENTS')
                f.seek(0, 2)
                sz = f.tell()
                pos = int(sz - absoffset)
                if pos < 0:
                    pos = 0
                f.seek(pos)
                data = f.read(absoffset)
            else:
                if abslength != length:
                    raise ValueError('BAD_ARGUMENTS')
                if length == 0:
                    f.seek(offset)
                    data = f.read()
                else:
                    f.seek(offset)
                    data = f.read(length)
    except (OSError, IOError):
        raise ValueError('FAILED')

    return data


def tailFile(filename, offset, length):
    """
    Read length bytes from the file named by filename starting at
    offset, automatically increasing offset and setting overflow
    flag if log size has grown beyond (offset + length).  If length
    bytes are not available, as many bytes as are available are returned.
    """

    try:
        with open(filename, 'rb') as f:
            overflow = False
            f.seek(0, 2)
            sz = f.tell()

            if sz > (offset + length):
                overflow = True
                offset = sz - 1

            if (offset + length) > sz:
                if offset > (sz - 1):
                    length = 0
                offset = sz - length

            if offset < 0:
                offset = 0
            if length < 0:
                length = 0

            if length == 0:
                data = b''
            else:
                f.seek(offset)
                data = f.read(length)

            offset = sz
            return [as_string(data), offset, overflow]
    except (OSError, IOError):
        return ['', offset, False]


# Helpers for dealing with signals and exit status

def decode_wait_status(sts):
    """Decode the status returned by wait() or waitpid().

    Return a tuple (exitstatus, message) where exitstatus is the exit
    status, or -1 if the process was killed by a signal; and message
    is a message telling what happened.  It is the caller's
    responsibility to display the message.
    """
    try:
        es, msg = sts
    except TypeError:
        es, msg = sts, "unknown termination cause(%s)" % sts
    return es, msg


_signames = None


def signame(sig):
    """Return a symbolic name for a signal.

    Return "signal NNN" if there is no corresponding SIG name in the
    signal module.
    """

    if _signames is None:
        _init_signames()
    return _signames.get(sig) or "signal %d" % sig


def _init_signames():
    global _signames
    d = {}
    for k, v in signal.__dict__.items():
        k_startswith = getattr(k, "startswith", None)
        if k_startswith is None:
            continue
        if k_startswith("SIG") and not k_startswith("SIG_"):
            d[v] = k
    _signames = d


class SignalReceiver(object):
    def __init__(self):
        self._signals_recvd = []

    def receive(self, sig, frame):
        if sig not in self._signals_recvd:
            self._signals_recvd.append(sig)

    def get_signal(self):
        if self._signals_recvd:
            sig = self._signals_recvd.pop(0)
        else:
            sig = None
        return sig


# miscellaneous utility functions

def expand(s, expansions, name):
    try:
        return s % expansions
    except KeyError as ex:
        available = list(expansions.keys())
        available.sort()
        raise ValueError(
            'Format string %r for %r contains names (%s) which cannot be '
            'expanded. Available names: %s' %
            (s, name, str(ex), ", ".join(available)))
    except Exception as ex:
        raise ValueError(
            'Format string %r for %r is badly formatted: %s' %
            (s, name, str(ex))
        )


def make_namespec(group_name, process_name):
    # we want to refer to the process by its "short name" (a process named
    # process1 in the group process1 has a name "process1").  This is for
    # backwards compatibility
    if group_name == process_name:
        name = process_name
    else:
        name = '%s:%s' % (group_name, process_name)
    return name


def split_namespec(namespec):
    names = namespec.split(':', 1)
    if len(names) == 2:
        # group and process name differ
        group_name, process_name = names
        if not process_name or process_name == '*':
            process_name = None
    else:
        # group name is same as process name
        group_name, process_name = namespec, namespec
    return group_name, process_name


# exceptions

class ProcessException(Exception):
    """ Specialized exceptions used when attempting to start a process """


class BadCommand(ProcessException):
    """ Indicates the command could not be parsed properly. """


class NotExecutable(ProcessException):
    """ Indicates that the filespec cannot be executed because its path
    resolves to a file which is not executable, or which is a directory. """


class NotFound(ProcessException):
    """ Indicates that the filespec cannot be executed because it could not
    be found """


class NoPermission(ProcessException):
    """ Indicates that the file cannot be executed because the supervisor
    process does not possess the appropriate UNIX filesystem permission
    to execute the file. """

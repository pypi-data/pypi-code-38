# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Console Commands
"""

from __future__ import unicode_literals, absolute_import

import os
import sys
import json
import time
import platform
import argparse
import datetime
import socket
import shutil
import subprocess
import warnings
import logging
from getpass import getpass

import six
import humanize

from rattail import __version__
from rattail.core import Object
from rattail.util import load_entry_points, load_object
from rattail.progress import ConsoleProgress, SocketProgress
from rattail.config import make_config, parse_list
from rattail.util import progress_loop
from rattail.time import make_utc
from rattail.db.config import configure_versioning


log = logging.getLogger(__name__)


class ArgumentParser(argparse.ArgumentParser):
    """
    Custom argument parser.

    This overrides some of the parsing logic which is specific to the primary
    command object.
    """

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        args.argv = argv
        return args


def date_argument(string):
    """
    Validate and coerce a date argument.

    This function is designed be used as the ``type`` parameter when calling
    ``ArgumentParser.add_argument()``, e.g.::

       parser = ArgumentParser()
       parser.add_argument('--date', type=date_argument)
    """
    try:
        date = datetime.datetime.strptime(string, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError("Date must be in YYYY-MM-DD format")
    return date


def dict_argument(string):
    """
    Coerce the given string to a Python dictionary.  The string is assumed to
    be JSON-encoded; this function merely invokes ``json.loads()`` on it.

    This function is designed be used as the ``type`` parameter when calling
    ``ArgumentParser.add_argument()``, e.g.::

       parser = ArgumentParser()
       parser.add_argument('--date', type=dict_argument)
    """
    try:
        return json.loads(string)
    except json.decoder.JSONDecodeError:
        raise argparse.ArgumentTypeError("Argument must be valid JSON-encoded string")


def list_argument(string):
    """
    Coerce the given string to a list of strings, splitting on whitespace
    and/or commas.

    This function is designed be used as the ``type`` parameter when calling
    ``ArgumentParser.add_argument()``, e.g.::

       parser = ArgumentParser()
       parser.add_argument('--things', type=list_argument)
    """
    return parse_list(string)


@six.python_2_unicode_compatible
class Command(Object):
    """
    The primary command for the application.

    This effectively *is* the ``rattail`` console application.  It mostly
    provides the structure for subcommands, which really do all the work.

    This command is designed to be subclassed, should your application need
    similar functionality.
    """
    name = 'rattail'
    version = __version__
    description = "Rattail Software Framework"
    long_description = """
Rattail is a retail software framework.

Copyright (c) 2010-2015 Lance Edgar <lance@edbob.org>

This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to redistribute it under certain conditions.
See the file COPYING.txt for more information.
"""

    stdout = sys.stdout
    stderr = sys.stderr

    def __init__(self, **kwargs):
        super(Command, self).__init__(**kwargs)
        self.subcommands = load_entry_points('{}.commands'.format(self.name.replace('-', '_')))

    def __str__(self):
        return self.name

    @property
    def db_config_section(self):
        """
        Name of section in config file which should have database connection
        info.  This defaults to ``'rattail.db'`` but may be overridden so the
        command framework can sit in front of a non-Rattail database if needed.

        This is used to auto-configure a "default" database engine for the app,
        when any command is invoked.
        """
        return 'rattail.db'

    @property
    def db_session_factory(self):
        """
        Reference to the "primary" ``Session`` class, which will be configured
        automatically during app startup.  Defaults to :class:`rattail.db.Session`.
        """
        from rattail.db import Session
        return Session

    @property
    def db_model(self):
        """
        Reference to the Python module which is to be used as the primary data
        model.  Defaults to ``rattail.db.model``.
        """
        return self.config.get_model()

    def iter_subcommands(self):
        """
        Iterate over the subcommands.

        This is a generator which yields each associated :class:`Subcommand`
        class sorted by :attr:`Subcommand.name`.
        """
        for name in sorted(self.subcommands):
            yield self.subcommands[name]

    def print_help(self):
        """
        Print help text for the primary command.

        The output will include a list of available subcommands.
        """
        # TODO: this should leverage parser config...
        self.stdout.write("""{0.description}

Usage: {0.name} [options] <command> [command-options]

Options:
  -c PATH, --config=PATH
                    Config path (may be specified more than once)
  -P, --progress    Show progress indicators (where relevant)
  -R, --runas       Optional username to impersonate when running command
  -V, --version     Display program version and exit

Commands:\n""".format(self))

        for cmd in self.iter_subcommands():
            self.stdout.write("  {0:<16s}  {1}\n".format(cmd.name, cmd.description))

        self.stdout.write("\nTry '{0} help <command>' for more help.\n".format(self.name))

    def run(self, *args):
        """
        Parse command line arguments and execute appropriate subcommand.
        """
        parser = ArgumentParser(
            prog=self.name,
            description=self.description,
            add_help=False,
            )

        parser.add_argument('-c', '--config', action='append', dest='config_paths',
                            metavar='PATH')

        # TODO: i think these aren't really being used in practice..?
        parser.add_argument('-n', '--no-init', action='store_true', default=False)
        parser.add_argument('--no-extend-config', dest='extend_config', action='store_false')

        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('-P', '--progress', action='store_true', default=False)
        parser.add_argument('--progress-socket',
                            help="Optional socket (e.g. localhost:8487) to which progress info should be written.")
        parser.add_argument('--runas', '-R', metavar='USERNAME',
                            help="Optional username to impersonate when running the command.  "
                            "This is only relevant for / used by certain commands.")
        parser.add_argument('--stdout', metavar='PATH', type=argparse.FileType('w'),
                            help="Optional path to which STDOUT should be effectively redirected.")
        parser.add_argument('--stderr', metavar='PATH', type=argparse.FileType('w'),
                            help="Optional path to which STDERR should be effectively redirected.")

        # data versioning
        parser.add_argument('--versioning', action='store_true',
                            help="Force *enable* of data versioning.  If set, then --no-versioning "
                            "cannot also be set.  If neither is set, config will determine whether "
                            "or not data versioning should be enabled.")
        parser.add_argument('--no-versioning', action='store_true',
                            help="Force *disable* of data versioning.  If set, then --versioning "
                            "cannot also be set.  If neither is set, config will determine whether "
                            "or not data versioning should be enabled.")

        parser.add_argument('-V', '--version', action='version',
                            version="%(prog)s {0}".format(self.version))
        parser.add_argument('command', nargs='*')

        # Parse args and determine subcommand.
        args = parser.parse_args(list(args))
        if not args or not args.command:
            self.print_help()
            return

        # TODO: can we make better args so this is handled by argparse somehow?
        if args.versioning and args.no_versioning:
            sys.stderr.write("Cannot pass both --versioning and --no-versioning\n")
            sys.exit(1)

        # Show (sub)command help if so instructed, or unknown subcommand.
        cmd = args.command.pop(0)
        if cmd == 'help':
            if len(args.command) != 1:
                self.print_help()
                return
            cmd = args.command[0]
            if cmd not in self.subcommands:
                self.print_help()
                return
            cmd = self.subcommands[cmd](parent=self)
            cmd.parser.print_help()
            return
        elif cmd in self.subcommands:
            if '-h' in args.argv or '--help' in args.argv:
                cmd = self.subcommands[cmd](parent=self)
                cmd.parser.print_help()
                return
        else:
            self.print_help()
            return

        # Okay, we should be done needing to print help messages.  Now it's
        # safe to redirect STDOUT/STDERR, if necessary.
        if args.stdout:
            self.stdout = args.stdout
        if args.stderr:
            self.stderr = args.stderr

        # if args say not to "init" then we make a sort of empty config
        if args.no_init:
            self.config = make_config([], extend=False, versioning=False)

        else: # otherwise we make a proper config, and maybe turn on versioning
            logging.basicConfig()
            self.config = make_config(args.config_paths, extend=args.extend_config, versioning=False)
            if args.versioning:
                configure_versioning(self.config, force=True)
            elif not args.no_versioning:
                configure_versioning(self.config)

        # instantiate the subcommand
        subcmd = self.subcommands[cmd](self, self.config)

        # figure out if/how subcommand should show progress
        subcmd.show_progress = args.progress
        subcmd.progress = None
        if subcmd.show_progress:
            if args.progress_socket:
                host, port = args.progress_socket.split(':')
                subcmd.progress = SocketProgress(host, int(port))
            else:
                subcmd.progress = ConsoleProgress

        # maybe should be verbose
        subcmd.verbose = args.verbose

        # TODO: make this default to something from config?
        subcmd.runas_username = args.runas or None

        # and finally, run the subcommand
        log.debug("running '%s %s' with args: %s", self.name, subcmd.name, args.argv)
        subcmd._run(*(args.command + args.argv))


class Subcommand(object):
    """
    Base class for application subcommands.
    """
    name = 'UNDEFINED'
    description = 'UNDEFINED'

    def __init__(self, parent=None, config=None, show_progress=None):
        self.parent = parent
        self.config = config
        self.stdout = getattr(parent, 'stdout', sys.stdout)
        self.stderr = getattr(parent, 'stderr', sys.stderr)
        self.show_progress = show_progress
        self.progress = ConsoleProgress if show_progress else None
        self.parser = argparse.ArgumentParser(
            prog='{0} {1}'.format(getattr(self.parent, 'name', 'UNDEFINED'), self.name),
            description=self.description)
        self.add_parser_args(self.parser)

    def __repr__(self):
        return "Subcommand(name={0})".format(repr(self.name))

    @property
    def model(self):
        return self.parent.db_model

    def add_parser_args(self, parser):
        """
        Configure additional arguments for the subcommand argument parser.
        """
        pass

    def make_session(self):
        session = self.parent.db_session_factory()
        user = self.get_runas_user(session=session)
        if user:
            session.set_continuum_user(user)
        return session

    def get_runas_user(self, session=None, username=None):
        """
        Returns a proper User object, which the app should "run as"
        """
        from sqlalchemy.orm.exc import NoResultFound
        from rattail.db.util import short_session

        if username is None:
            if hasattr(self, 'runas_username'):
                username = self.runas_username
            if not username and self.config:
                username = self.config.get('rattail', 'runas.default')
        if username:
            user = None
            with short_session(session) as s:
                try:
                    user = s.query(self.model.User).filter_by(username=username).one()
                except NoResultFound:
                    pass
                else:
                    if not session:
                        s.expunge(user)
            return user

    def progress_loop(self, func, items, factory=None, **kwargs):
        return progress_loop(func, items, factory or self.progress, **kwargs)
            
    def _run(self, *args):
        args = self.parser.parse_args(list(args))
        return self.run(args)

    def run(self, args):
        """
        Run the subcommand logic.
        """
        raise NotImplementedError


class CloneDatabase(Subcommand):
    """
    Clone (supported) data from a source DB to a target DB
    """
    name = 'clonedb'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('source_engine',
                            help="SQLAlchemy engine URL for the source database.")
        parser.add_argument('target_engine',
                            help="SQLAlchemy engine URL for the target database.")
        parser.add_argument('-m', '--model', default='rattail.db.model',
                            help="Dotted path of Python module which contains the data model.")
        parser.add_argument('-C', '--classes', nargs='*',
                            help="Model classes which should be cloned.  Possible values here "
                            "depends on which module contains the data model.  If no classes "
                            "are specified, all available will be cloned.")

    def run(self, args):
        from sqlalchemy import create_engine, orm
        from rattail.util import import_module_path

        model = import_module_path(args.model)
        classes = args.classes
        assert classes

        source_engine = create_engine(args.source_engine)
        target_engine = create_engine(args.target_engine)
        model.Base.metadata.drop_all(bind=target_engine)
        model.Base.metadata.create_all(bind=target_engine)

        Session = orm.sessionmaker()
        src_session = Session(bind=source_engine)
        dst_session = Session(bind=target_engine)

        for clsname in classes:
            log.info("cloning data for model: %s", clsname)
            cls = getattr(model, clsname)
            src_query = src_session.query(cls)
            count = src_query.count()
            log.debug("found %d %s records to clone", count, clsname)
            if not count:
                continue

            mapper = orm.class_mapper(cls)
            key_query = src_session.query(*mapper.primary_key)

            prog = None
            if self.progress:
                prog = self.progress("Cloning data for model: {0}".format(clsname), count)
            for i, key in enumerate(key_query, 1):

                src_instance = src_query.get(key)
                dst_session.merge(src_instance)
                dst_session.flush()

                if prog:
                    prog.update(i)
            if prog:
                prog.destroy()

        src_session.close()
        dst_session.commit()
        dst_session.close()


class DataSync(Subcommand):
    """
    Manage the data sync daemon
    """
    name = 'datasync'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')

        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        check = subparsers.add_parser('check', help="(DEPRECATED) Check for stale (lingering) changes in queue")
        check.set_defaults(subcommand='check')

        check_queue = subparsers.add_parser('check-queue', help="Check for stale (lingering) changes in queue")
        check_queue.set_defaults(subcommand='check-queue')

        check_watchers = subparsers.add_parser('check-watchers', help="Check for dead watcher threads")
        check_watchers.set_defaults(subcommand='check-watchers')

        wait = subparsers.add_parser('wait', help="Wait for changes to be processed")
        wait.set_defaults(subcommand='wait')

        parser.add_argument('-p', '--pidfile', metavar='PATH', default='/var/run/rattail/datasync.pid',
                            help="Path to PID file.")
        parser.add_argument('--daemonize', action='store_true', default=True, # TODO: should default to False
                            help="Daemonize when starting.")
        parser.add_argument('--no-daemonize',
                            '-D', '--do-not-daemonize', # TODO: (re)move these?
                            action='store_false', dest='daemonize',
                            help="Do not daemonize when starting.")
        parser.add_argument('-T', '--timeout', metavar='MINUTES', type=int, default=0,
                            help="Optional timeout (in minutes) for use with the 'wait' or 'check' commands.  "
                            "If specified for 'wait', the waiting still stop after the given number of minutes "
                            "and exit with a nonzero code to indicate failure.  If specified for 'check', the "
                            "command will perform some health check based on the given timeout, and exit with "
                            "nonzero code if the check fails.")

    def run(self, args):
        from rattail.datasync.daemon import DataSyncDaemon

        if args.subcommand == 'wait':
            self.wait(args)

        elif args.subcommand == 'check':
            self.check_queue(args)

        elif args.subcommand == 'check-queue':
            self.check_queue(args)

        elif args.subcommand == 'check-watchers':
            self.check_watchers(args)

        else: # manage the daemon
            daemon = DataSyncDaemon(args.pidfile, config=self.config)
            if args.subcommand == 'stop':
                daemon.stop()
            else: # start
                try:
                    daemon.start(daemonize=args.daemonize)
                except KeyboardInterrupt:
                    if not args.daemonize:
                        self.stderr.write("Interrupted.\n")
                    else:
                        raise

    def wait(self, args):
        model = self.model
        session = self.make_session()
        started = make_utc()
        log.debug("will wait for current change queue to clear")
        last_logged = started

        changes = session.query(model.DataSyncChange)
        count = changes.count()
        log.debug("there are %d changes in the queue", count)
        while count:
            try:
                now = make_utc()

                if args.timeout and (now - started).seconds >= (args.timeout * 60):
                    log.warning("datasync wait timed out after %d minutes, with %d changes in queue",
                                args.timeout, count)
                    sys.exit(1)

                if (now - last_logged).seconds >= 60:
                    log.debug("still waiting, %d changes in the datasync queue", count)
                    last_logged = now

                time.sleep(1)
                count = changes.count()

            except KeyboardInterrupt:
                self.stderr.write("Waiting cancelled by user\n")
                session.close()
                sys.exit(1)

        session.close()
        log.debug("all datasync changes have been processed")

    def check_queue(self, args):
        """
        Perform general queue / health check for datasync.
        """
        model = self.model
        session = self.make_session()

        # looking for changes which have been around for "timeout" minutes
        timeout = args.timeout or 90
        cutoff = make_utc() - datetime.timedelta(seconds=60 * timeout)
        changes = session.query(model.DataSyncChange)\
                         .filter(model.DataSyncChange.obtained < cutoff)\
                         .count()
        session.close()

        # if we found stale changes, then "fail" - otherwise we'll "succeed"
        if changes:
            # TODO: should log set of unique payload types, for troubleshooting
            log.debug("found %s changes, in queue for %s minutes", changes, timeout)
            self.stderr.write("Found {} changes, in queue for {} minutes\n".format(changes, timeout))
            sys.exit(1)

        log.info("found no changes in queue for %s minutes", timeout)

    def check_watchers(self, args):
        """
        Perform general health check for datasync watcher threads.
        """
        from rattail.datasync.config import load_profiles
        from rattail.datasync.util import get_lastrun

        profiles = load_profiles(self.config)
        session = self.make_session()

        # cutoff is "timeout" minutes before "now"
        timeout = args.timeout or 15
        cutoff = make_utc() - datetime.timedelta(seconds=60 * timeout)

        dead = []
        for key in profiles:

            # looking for watcher "last run" time older than "timeout" minutes
            lastrun = get_lastrun(self.config, key, tzinfo=False, session=session)
            if lastrun and lastrun < cutoff:
                dead.append(key)

        session.close()

        # if we found dead watchers, then "fail" - otherwise we'll "succeed"
        if dead:
            self.stderr.write("Found {} watcher threads dead for {} minutes: {}\n".format(len(dead), timeout, ', '.join(dead)))
            sys.exit(1)

        log.info("found no watcher threads dead for %s minutes", timeout)


class EmailBouncer(Subcommand):
    """
    Interacts with the email bouncer daemon.  This command expects a
    subcommand; one of the following:

    * ``rattail bouncer start``
    * ``rattail bouncer stop``
    """
    name = 'bouncer'
    description = "Manage the email bouncer daemon"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        parser.add_argument('-p', '--pidfile', metavar='PATH', default='/var/run/rattail/bouncer.pid',
                            help="Path to PID file.")
        parser.add_argument('--daemonize', action='store_true', default=True, # TODO: should default to False
                            help="Daemonize when starting.")
        parser.add_argument('--no-daemonize',
                            '-D', '--do-not-daemonize', # TODO: (re)move these?
                            action='store_false', dest='daemonize',
                            help="Do not daemonize when starting.")

    def run(self, args):
        from rattail.bouncer.daemon import BouncerDaemon

        daemon = BouncerDaemon(args.pidfile, config=self.config)
        if args.subcommand == 'stop':
            daemon.stop()
        else: # start
            try:
                daemon.start(daemonize=args.daemonize)
            except KeyboardInterrupt:
                if not args.daemonize:
                    self.stderr.write("Interrupted.\n")
                else:
                    raise


class DateOrganize(Subcommand):
    """
    Organize files in a given directory, according to date
    """
    name = 'date-organize'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('folder', metavar='PATH',
                            help="Path to directory containing files which are "
                            "to be organized by date.")

    def run(self, args):
        today = datetime.date.today()
        for filename in sorted(os.listdir(args.folder)):
            path = os.path.join(args.folder, filename)
            if os.path.isfile(path):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                if mtime.date() < today:
                    datedir = mtime.strftime(os.sep.join(('%Y', '%m', '%d')))
                    datedir = os.path.join(args.folder, datedir)
                    if not os.path.exists(datedir):
                        os.makedirs(datedir)
                    shutil.move(path, datedir)


class DatabaseSyncCommand(Subcommand):
    """
    Controls the database synchronization service.
    """

    name = 'dbsync'
    description = "Manage the database synchronization service"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        if sys.platform == 'linux2':
            parser.add_argument('-p', '--pidfile',
                                help="Path to PID file", metavar='PATH')
            parser.add_argument('-D', '--do-not-daemonize',
                                action='store_false', dest='daemonize', default=True,
                                help="Do not daemonize when starting.")

    def run(self, args):
        from rattail.db.sync import linux as dbsync

        if args.subcommand == 'start':
            try:
                dbsync.start_daemon(self.config, args.pidfile, args.daemonize)
            except KeyboardInterrupt:
                if not args.daemonize:
                    self.stderr.write("Interrupted.\n")
                else:
                    raise

        elif args.subcommand == 'stop':
            dbsync.stop_daemon(self.config, args.pidfile)


class Dump(Subcommand):
    """
    Do a simple data dump.
    """

    name = 'dump'
    description = "Dump data to file."

    def add_parser_args(self, parser):
        parser.add_argument(
            '--output', '-o', metavar='FILE',
            help="Optional path to output file.  If none is specified, "
            "data will be written to standard output.")
        parser.add_argument(
            'model', help="Model whose data will be dumped.")

    def get_model(self):
        """
        Returns the module which contains all relevant data models.

        By default this returns ``rattail.db.model``, but this method may be
        overridden in derived commands to add support for extra data models.
        """
        from rattail.db import model
        return model

    def run(self, args):
        from rattail.db import Session
        from rattail.db.dump import dump_data

        model = self.get_model()
        if hasattr(model, args.model):
            cls = getattr(model, args.model)
        else:
            self.stderr.write("Unknown model: {0}\n".format(args.model))
            sys.exit(1)

        progress = None
        if self.show_progress: # pragma no cover
            progress = ConsoleProgress

        if args.output:
            output = open(args.output, 'wb')
        else:
            output = self.stdout

        session = Session()
        dump_data(session, cls, output, progress=progress)
        session.close()

        if output is not self.stdout:
            output.close()


class FileMonitorCommand(Subcommand):
    """
    Interacts with the file monitor service; called as ``rattail filemon``.
    This command expects a subcommand; one of the following:

    * ``rattail filemon start``
    * ``rattail filemon stop``

    On Windows platforms, the following additional subcommands are available:

    * ``rattail filemon install``
    * ``rattail filemon uninstall`` (or ``rattail filemon remove``)

    .. note::
       The Windows Vista family of operating systems requires you to launch
       ``cmd.exe`` as an Administrator in order to have sufficient rights to
       run the above commands.

    .. See :doc:`howto.use_filemon` for more information.
    """

    name = 'filemon'
    description = "Manage the file monitor daemon"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        if sys.platform in ('linux', 'linux2'):
            parser.add_argument('-p', '--pidfile',
                                help="Path to PID file.", metavar='PATH')
            parser.add_argument('--daemonize', action='store_true', default=True, # TODO: should default to False
                                help="Daemonize when starting.")
            parser.add_argument('--no-daemonize',
                                '-D', '--do-not-daemonize', # TODO: (re)move these?
                                action='store_false', dest='daemonize',
                                help="Do not daemonize when starting.")

        elif sys.platform == 'win32': # pragma no cover

            install = subparsers.add_parser('install', help="Install service")
            install.set_defaults(subcommand='install')
            install.add_argument('-a', '--auto-start', action='store_true',
                                 help="Configure service to start automatically.")
            install.add_argument('-U', '--username',
                                 help="User account under which the service should run.")

            remove = subparsers.add_parser('remove', help="Uninstall (remove) service")
            remove.set_defaults(subcommand='remove')

            uninstall = subparsers.add_parser('uninstall', help="Uninstall (remove) service")
            uninstall.set_defaults(subcommand='remove')

    def run(self, args):
        if sys.platform in ('linux', 'linux2'):
            from rattail.filemon import linux as filemon

            if args.subcommand == 'start':
                filemon.start_daemon(self.config, args.pidfile, args.daemonize)

            elif args.subcommand == 'stop':
                filemon.stop_daemon(self.config, args.pidfile)

        elif sys.platform == 'win32': # pragma no cover
            self.run_win32(args)

        else:
            self.stderr.write("File monitor is not supported on platform: {0}\n".format(sys.platform))
            sys.exit(1)

    def run_win32(self, args): # pragma no cover
        from rattail.win32 import require_elevation
        from rattail.win32 import service
        from rattail.win32 import users
        from rattail.filemon import win32 as filemon

        require_elevation()

        options = []
        if args.subcommand == 'install':

            username = args.username
            if username:
                if '\\' in username:
                    server, username = username.split('\\')
                else:
                    server = socket.gethostname()
                if not users.user_exists(username, server):
                    sys.stderr.write("User does not exist: {0}\\{1}\n".format(server, username))
                    sys.exit(1)

                password = ''
                while password == '':
                    password = getpass(b"Password for service user: ").strip()
                options.extend(['--username', r'{0}\{1}'.format(server, username)])
                options.extend(['--password', password])

            if args.auto_start:
                options.extend(['--startup', 'auto'])

        service.execute_service_command(filemon, args.subcommand, *options)

        # If installing with custom user, grant "logon as service" right.
        if args.subcommand == 'install' and args.username:
            users.allow_logon_as_service(username)

        # TODO: Figure out if the following is even required, or if instead we
        # should just be passing '--startup delayed' to begin with?

        # If installing auto-start service on Windows 7, we should update
        # its startup type to be "Automatic (Delayed Start)".
        # TODO: Improve this check to include Vista?
        if args.subcommand == 'install' and args.auto_start:
            if platform.release() == '7':
                name = filemon.RattailFileMonitor._svc_name_
                service.delayed_auto_start_service(name)


class LoadHostDataCommand(Subcommand):
    """
    Loads data from the Rattail host database, if one is configured.
    """

    name = 'load-host-data'
    description = "Load data from host database"

    def run(self, args):
        from .db import get_engines
        from .db import load

        engines = get_engines(self.config)
        if 'host' not in engines:
            sys.stderr.write("Host engine URL not configured.\n")
            sys.exit(1)

        proc = load.LoadProcessor(self.config)
        proc.load_all_data(engines['host'], ConsoleProgress)


class MakeAppDir(Subcommand):
    """
    Create a conventional 'app' dir for a virtual environment
    """
    name = 'make-appdir'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--path', metavar='PATH',
                            help="Path where the app folder is to be established.  If not "
                            "specified, a default will be assumed based on the virtual "
                            "environment, e.g. '/envs/rattail/app'.")
        parser.add_argument('-U', '--user', metavar='USERNAME',
                            help="Linux username which should be given ownership to the various "
                            "data folders which are to be created.  This is used when the app(s) "
                            "are to normally be ran as the 'rattail' user for instance.  Use "
                            "of this option probably requires 'sudo' or equivalent.")

    def run(self, args):
        import pwd

        if args.path:
            app_path = os.path.abspath(args.path)
            if os.path.basename(app_path) != 'app':
                app_path = os.path.join(app_path, 'app')
        else:
            app_path = os.path.join(sys.prefix, 'app')
        app_path = app_path.rstrip('/')

        if not os.path.exists(app_path):
            os.mkdir(app_path)

        if args.user:
            pwdata = pwd.getpwnam(args.user)
        for name in ['batch', 'log', 'sessions', 'work']:
            path = os.path.join(app_path, name)
            if not os.path.exists(path):
                os.mkdir(path)
            if args.user:
                os.chown(path, pwdata.pw_uid, pwdata.pw_gid)

        self.stdout.write("Rattail app dir generated at: {}\n".format(app_path))


class MakeConfig(Subcommand):
    """
    Generate stub config file(s) where you want them
    """
    name = 'make-config'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('-T', '--type', metavar='NAME', default='rattail',
                            help="Type of config file to create; defaults to 'rattail' "
                            "which will generate 'rattail.conf'")
        parser.add_argument('-O', '--output', metavar='PATH', default='.',
                            help="Path where the config file is to be generated.  This can "
                            "be the full path including filename, or just the folder, in which "
                            "case the filename is inferred from 'type'.  Default is to current "
                            "working folder.")

    def find_template(self, name):
        from rattail.files import resource_path

        template_paths = self.config.getlist('rattail.config', 'templates',
                                             default=['rattail:data/config'])
        for template_path in template_paths:
            path = resource_path('{}/{}.conf'.format(template_path.rstrip('/'), name))
            if os.path.exists(path):
                return path

    def run(self, args):
        template_path = self.find_template(args.type)
        if not template_path:
            self.stderr.write("config template not found for type: {}\n".format(args.type))
            sys.exit(1)

        output_path = os.path.abspath(args.output)
        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, os.path.basename(template_path))

        shutil.copy(template_path, output_path)
        self.stdout.write("Config file generated at: {}\n".format(output_path))


class MakeUser(Subcommand):
    """
    Create a new user account in a given system
    """
    name = 'make-user'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('username',
                            help="Username for the new user.")
        parser.add_argument('--system', default='rattail',
                            help="System in which to create the new user; defaults to "
                            "rattail; must be one of: rattail, windows")
        parser.add_argument('-A', '--admin', action='store_true',
                            help="Whether the new user should have admin rights within "
                            "the system (if applicable).")
        parser.add_argument('--password',
                            help="Optional password to set for the new user.")
        parser.add_argument('--full-name',
                            help="Full (display) name for the new user (if applicable).")
        parser.add_argument('--comment',
                            help="Comment string for the new user (if applicable).")

    def run(self, args):
        mkuser = getattr(self, 'mkuser_{}'.format(args.system), None)
        if mkuser:
            if mkuser(args):
                self.stdout.write("created new user in '{}' system: {}\n".format(
                    args.system, args.username))
        else:
            self.stderr.write("don't know how to make user for '{}' system\n".format(args.system))
            sys.exit(1)

    def user_exists(self, args):
        self.stdout.write("user already exists in '{}' system: {}\n".format(
            args.system, args.username))
        sys.exit(1)

    def obtain_password(self, args):
        if args.password:
            return args.password
        try:
            password = None
            while not password:
                password = getpass(b"enter password for new user: ").strip()
        except KeyboardInterrupt:
            self.stderr.write("\noperation canceled by user\n")
            sys.exit(2)
        return password

    def mkuser_rattail(self, args):
        from rattail.db import auth

        session = self.parent.db_session_factory()
        model = self.parent.db_model
        if session.query(model.User).filter_by(username=args.username).count():
            session.close()
            return self.user_exists(args)

        user = model.User(username=args.username)
        auth.set_user_password(user, self.obtain_password(args))
        if args.admin:
            user.roles.append(auth.administrator_role(session))
        if args.full_name:
            kwargs = {'display_name': args.full_name}
            words = args.full_name.split()
            if len(words) == 2:
                kwargs.update({'first_name': words[0], 'last_name': words[1]})
            user.person = model.Person(**kwargs)
        session.add(user)
        session.commit()
        session.close()
        return True

    def mkuser_windows(self, args):
        if sys.platform != 'win32':
            self.stderr.write("sorry, only win32 platform is supported\n")
            sys.exit(1)

        from rattail.win32 import users
        from rattail.win32 import require_elevation

        require_elevation()

        if users.user_exists(args.username):
            return self.user_exists(args)

        return users.create_user(args.username, self.obtain_password(args),
                                 full_name=args.full_name, comment=args.comment)


class MakeUUID(Subcommand):
    """
    Generate a new UUID
    """
    name = 'make-uuid'
    description = __doc__.strip()

    def run(self, args):
        from rattail.core import get_uuid

        self.stdout.write("{}\n".format(get_uuid()))


class PalmCommand(Subcommand):
    """
    Manages registration for the HotSync Manager conduit; called as::

       rattail palm
    """

    name = 'palm'
    description = "Manage the HotSync Manager conduit registration"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        register = subparsers.add_parser('register', help="Register Rattail conduit")
        register.set_defaults(subcommand='register')

        unregister = subparsers.add_parser('unregister', help="Unregister Rattail conduit")
        unregister.set_defaults(subcommand='unregister')

    def run(self, args):
        from rattail import palm
        from rattail.win32 import require_elevation
        from rattail.exceptions import PalmError

        require_elevation()

        if args.subcommand == 'register':
            try:
                palm.register_conduit()
            except PalmError as error:
                sys.stderr.write("{}\n".format(error))

        elif args.subcommand == 'unregister':
            try:
                palm.unregister_conduit()
            except PalmError as error:
                sys.stderr.write("{}\n".format(error))
                

class RunAndMail(Subcommand):
    """
    Run a command as subprocess, and email the result/output
    """
    name = 'run-n-mail'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--key', default='run_n_mail',
                            help="Config key for email settings")
        # TODO: these all seem like good ideas, but not needed yet?
        # parser.add_argument('--from', '-F', metavar='ADDRESS',
        #                     help="Override value of From: header")
        # parser.add_argument('--to', '-T', metavar='ADDRESS',
        #                     help="Override value of To: header (may specify more than once)")
        # parser.add_argument('--cc', metavar='ADDRESS',
        #                     help="Override value of Cc: header (may specify more than once)")
        # parser.add_argument('--bcc', metavar='ADDRESS',
        #                     help="Override value of Bcc: header (may specify more than once)")
        parser.add_argument('--subject', '-S',
                            help="Override value of Subject: header (i.e. value after prefix)")
        parser.add_argument('cmd', metavar='COMMAND',
                            help="Command which should be ran, and result of which will be emailed")

    def run(self, args):
        from rattail.mail import send_email

        cmd = parse_list(args.cmd)
        log.info("will run command as subprocess: %s", cmd)
        run_began = make_utc()

        try:
            # TODO: must we allow for shell=True in some situations? (clearly not yet)
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            retcode = 0
            log.info("command completed successfully")
        except subprocess.CalledProcessError as error:
            output = error.output
            retcode = error.returncode
            log.warn("command exited with code: %s", retcode)

        run_ended = make_utc()
        runtime = run_ended - run_began
        runtime_pretty = humanize.naturaldelta(runtime)

        kwargs = {}
        if args.subject:
            kwargs['subject_template'] = args.subject

        send_email(self.config, args.key, {
            'cmd': cmd,
            'run_began': run_began,
            'run_ended': run_ended,
            'runtime': runtime,
            'runtime_pretty': runtime_pretty,
            'retcode': retcode,
            'output': output,
        }, **kwargs)


class RunSQL(Subcommand):
    """
    Run (first statement of) a SQL script against a database
    """
    name = 'runsql'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('engine',
                            help="SQLAlchemy engine URL for the database.")
        parser.add_argument('script', type=argparse.FileType('r'),
                            help="Path to file which contains a SQL script.")
        parser.add_argument('--max-width', type=int, default=80,
                            help="Max table width when displaying results.")

    def run(self, args):
        import sqlalchemy as sa
        import texttable

        sql = []
        for line in args.script:
            line = line.strip()
            if line and not line.startswith('--'):
                sql.append(line)
                if line.endswith(';'):
                    break

        sql = ' '.join(sql)
        engine = sa.create_engine(args.engine)

        result = engine.execute(sql)
        rows = result.fetchall()
        if rows:
            table = texttable.Texttable(max_width=args.max_width)
            table.add_rows([rows[0].keys()] + rows)
            self.stdout.write("{}\n".format(table.draw()))


class Upgrade(Subcommand):
    """
    Upgrade the local Rattail app
    """
    name = 'upgrade'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--description',
                            help="Description for the new/matched upgrade.")
        parser.add_argument('--enabled', action='store_true', default=True,
                            help="Indicate the enabled flag should be ON for the new/matched upgrade.  "
                            "Note that this is the default if you do not specify.")
        parser.add_argument('--no-enabled', action='store_false', dest='enabled',
                            help="Indicate the enabled flag should be OFF for the new/matched upgrade.")
        parser.add_argument('--create', action='store_true',
                            help="Create a new upgrade with the given attributes.")
        parser.add_argument('--execute', action='store_true',
                            help="Execute the upgrade.  Note that if you do not specify "
                            "--create then the upgrade matching the given attributes "
                            "will be read from the database.  If such an upgrade is not "
                            "found or is otherwise invalid (e.g. already executed), "
                            "the command will fail.")
        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.")

    def run(self, args):
        from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
        from rattail.upgrades import get_upgrade_handler

        if not args.create and not args.execute:
            self.stderr.write("Must specify --create and/or --execute\n")
            sys.exit(1)

        session = self.make_session()
        model = self.model
        user = self.get_runas_user(session)

        if args.create:
            upgrade = model.Upgrade()
            upgrade.description = args.description
            upgrade.created = make_utc()
            upgrade.created_by = user
            upgrade.enabled = args.enabled
            session.add(upgrade)
            session.flush()
            log.info("user '%s' created new upgrade: %s", user.username, upgrade)

        else:
            upgrades = session.query(model.Upgrade)\
                              .filter(model.Upgrade.enabled == args.enabled)
            if args.description:
                upgrades = upgrades.filter(model.Upgrade.description == args.description)
            try:
                upgrade = upgrades.one()
            except NoResultFound:
                self.stderr.write("no matching upgrade found\n")
                session.rollback()
                session.close()
                sys.exit(1)
            except MultipleResultsFound:
                self.stderr.write("found {} matching upgrades\n".format(upgrades.count()))
                session.rollback()
                session.close()
                sys.exit(1)

        if args.execute:
            if upgrade.executed:
                self.stderr.write("upgrade has already been executed: {}\n".format(upgrade))
                session.rollback()
                session.close()
                sys.exit(1)
            if not upgrade.enabled:
                self.stderr.write("upgrade is not enabled for execution: {}\n".format(upgrade))
                session.rollback()
                session.close()
                sys.exit(1)

            # execute upgrade
            handler = get_upgrade_handler(self.config)
            log.info("will now execute upgrade: %s", upgrade)
            if not args.dry_run:
                handler.mark_executing(upgrade)
                session.commit()
                handler.do_execute(upgrade, user, progress=self.progress)
            log.info("user '%s' executed upgrade: %s", user.username, upgrade)

        if args.dry_run:
            session.rollback()
            log.info("dry run, so transaction was rolled back")
        else:
            session.commit()
            log.info("transaction was committed")
        session.close()


def main(*args):
    """
    The primary entry point for the Rattail command system.
    """
    if args:
        args = list(args)
    else:
        args = sys.argv[1:]

    cmd = Command()
    cmd.run(*args)

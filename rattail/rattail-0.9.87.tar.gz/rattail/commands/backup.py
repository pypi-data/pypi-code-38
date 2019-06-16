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
Backup commands
"""

from __future__ import unicode_literals, absolute_import

import os
import re
import subprocess
import logging

import six

from rattail.commands.core import Subcommand


log = logging.getLogger(__name__)


class Backup(Subcommand):
    """
    Backup the database(s) and/or files for this machine
    """
    name = 'backup'
    description = __doc__.strip()

    def add_parser_args(self, parser):

        parser.add_argument('--list-dbs', action='store_true',
                            help="List all databases which may be backed up, then exit.")

        parser.add_argument('--dbdump', action='store_true',
                            help="Dump some or all databases during the backup run.  Exactly "
                            "which databases are dumped, will depend on other parameters.")
        parser.add_argument('--no-dbdump', action='store_true',
                            help="Do NOT dump any databases during the backup run.")

        parser.add_argument('--dbdump-include', action='append', dest='included_dbs', metavar='NAME',
                            help="Name of database to include in the dump.  May be specified "
                            "more than once.  Note that if this parameter is used, then ONLY "
                            "those databases specified will be backed up. Also, the --dbdump-exclude "
                            "parameter(s) will be ignored.")
        parser.add_argument('--dbdump-exclude', action='append', dest='excluded_dbs', metavar='NAME',
                            help="Name of database to exclude from the dump.  May be specified "
                            "more than once.  Note that if the --dbdump-include parameter is specified, "
                            "then this parameter will be ignored.")

        parser.add_argument('--dbdump-output', default='/root/data', metavar='PATH',
                            help="Location of output folder for db dumps.  Default is /root/data")

        parser.add_argument('--rsync', action='store_true',
                            help="Push all files to remote location via rsync.")
        parser.add_argument('--no-rsync', action='store_true',
                            help="Do NOT push files to remote location via rsync.")

        parser.add_argument('--rsync-include', action='append', dest='included_prefixes', metavar='PREFIX',
                            help="File prefix which should be included in the rsync run.  Actually, a "
                            "separate rsync call is made for each prefix.  May be specified more than "
                            "once.  Note that if this parameter is used, then ONLY those prefixes specified "
                            "will be rsync'ed.  Also, the --rsync-exclude parameter(s) will be ignored.")
        parser.add_argument('--rsync-exclude', action='append', dest='excluded_prefixes', metavar='PREFIX',
                            help="File prefix which should be excluded from the rsync run.  May be "
                            "specified more than once.  Note that if the --rsync-include parameter is "
                            "specified, then this parameter will be ignored.")

        parser.add_argument('--rsync-remote-host', metavar='ADDRESS',
                            help="Assuming the rsync destination is another server, this should be the "
                            "hostname or IP address of that server.  Or you could set it to an empty string, "
                            "which signifies that the rsync remote destination is another folder on localhost.")
        parser.add_argument('--rsync-remote-prefix', metavar='PREFIX',
                            help="File prefix for the rsync destination.  If --rsync-remote-host is an empty "
                            "string, this prefix must exist on localhost.  Otherwise the prefix must exist on "
                            "the rsync remote host.")

        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the motions as much as possible, to get an idea "
                            "of what the full backup would do, but don't actually do anything.")

    def run(self, args):

        if args.list_dbs:

            mysql_names = self.get_mysql_names()
            if mysql_names:
                width = max([len(name) for name in mysql_names])
                self.stdout.write("\nmysql\n")
                self.stdout.write("{}\n".format('-' * width))
                for name in mysql_names:
                    self.stdout.write("{}\n".format(name))

            postgres_names = self.get_postgres_names()
            if postgres_names:
                width = max([len(name) for name in postgres_names])
                self.stdout.write("\npostgres\n")
                self.stdout.write("{}\n".format('-' * width))
                for name in postgres_names:
                    self.stdout.write("{}\n".format(name))

            if mysql_names or postgres_names:
                self.stdout.write("\n")
            else:
                self.stdout.write("no databases found\n")

        else: # not listing dbs, so will dump and/or rsync

            if args.dbdump and args.no_dbdump:
                raise RuntimeError("Must specify either --dbdump or --no-dbump, but not both")
            if args.rsync and args.no_rsync:
                raise RuntimeError("Must specify either --rsync or --no-rsync, but not both")

            # we dump dbs by default, unless user or config file says not to
            if not args.no_dbdump and self.config.getbool('rattail.backup', 'dbdump', usedb=False, default=True):
                outdir = args.dbdump_output
                if not os.path.exists(outdir):
                    os.mkdir(outdir)

                if args.included_dbs:
                    include = args.included_dbs
                else:
                    include = self.config.getlist('rattail.backup', 'dbdump.include', usedb=False)

                if args.excluded_dbs:
                    exclude = args.excluded_dbs
                else:
                    exclude = self.config.getlist('rattail.backup', 'dbdump.exclude', usedb=False)

                self.dump_mysql_databases(outdir, include=include, exclude=exclude, dry_run=args.dry_run)
                self.dump_postgres_databases(outdir, include=include, exclude=exclude, dry_run=args.dry_run)

            # we rsync by default, unless user or config file says not to
            if not args.no_rsync and self.config.getbool('rattail.backup', 'rsync', usedb=False, default=True):
                self.rsync_files(include=args.included_prefixes,
                                 exclude=args.excluded_prefixes,
                                 dry_run=args.dry_run)

    def rsync_files(self, include=None, exclude=None, dry_run=False):
        remote_host = self.config.require('rattail.backup', 'rsync.remote_host', usedb=False)
        remote_prefix = self.config.require('rattail.backup', 'rsync.remote_prefix', usedb=False)
        if not remote_prefix.startswith('/'):
            raise RuntimeError("Remote prefix is not absolute path: {}".format(remote_prefix))
        if remote_host:
            remote_prefix = '{}:{}'.format(remote_host, remote_prefix)

        if include:
            prefixes = include
        else:
            prefixes = self.config.getlist('rattail.backup', 'rsync.include', usedb=False, default=[
                '/etc',
                '/home',
                '/opt',
                '/root',
                '/srv',
                '/usr/local',
                '/var',
            ])

        if exclude is None:
            exclude = self.config.getlist('rattail.backup', 'rsync.exclude', usedb=False)

        for prefix in prefixes:
            if not prefix.startswith('/'):
                raise RuntimeError("Prefix is not absolute path: {}".format(prefix))

        for prefix in prefixes:
            others = list(prefixes)
            others.remove(prefix)
            for other in others:
                if other.startswith(prefix):
                    raise RuntimeError("Prefix {} is redundant due to prefix {}".format(
                        other, prefix))

        for prefix in prefixes:
            if not os.path.exists(prefix):
                log.warning("skipping prefix which doesn't exist locally: %s", prefix)
                continue

            excluded = []
            if exclude:
                excluded = [pattern for pattern in exclude if pattern.startswith(prefix)]
            log.info("running rsync for prefix: %s", prefix)

            parent = os.path.dirname(prefix)
            if parent == '/':
                destination = remote_prefix
                excludes = ['--exclude={}'.format(pattern) for pattern in excluded]

            else: # prefix parent is not root (/) dir
                destination = '{}{}/'.format(remote_prefix, parent)

                # exclusion patterns must apparently be relative in this case,
                # i.e. to the topmost folder being synced
                excludes = []
                for pattern in excluded:
                    pattern = '/'.join(pattern.split('/')[2:])
                    excludes.append('--exclude={}'.format(pattern))

                # and must also create the parent folder on remote side
                cmd = ['rsync', '--dirs', '--perms', '--times', '--group', '--owner', parent, remote_prefix]
                log.debug("rsync command is: %s", cmd)
                if not dry_run:
                    subprocess.check_call(cmd)

            # okay let's rsync
            rsync = ['rsync', '--archive', '--delete-during', '--partial']
            if self.verbose:
                rsync.append('--progress')
            cmd = rsync + excludes + [prefix, destination]
            log.debug("rsync command is: %s", cmd)
            if not dry_run:
                subprocess.check_call(cmd)

    def get_mysql_names(self, include=None, exclude=None, exclude_builtin=True):
        try:
            output = subprocess.check_output([
                'mysql', '--execute', "show databases;",
                '--batch', '--skip-column-names',
            ])
        except Exception as error:
            if six.PY3 and isinstance(error, FileNotFoundError):
                # assuming there is no mysql binary
                return []
            raise
        output = output.decode('ascii') # TODO: how to detect this etc.?

        names = output.split('\n')
        names = [name.strip() for name in names if name.strip()]

        if exclude_builtin:
            builtins = [
                'mysql',
                'information_schema',
                'performance_schema',
            ]
            for name in builtins:
                if name in names:
                    names.remove(name)

        return self.filter_names(names, include, exclude)

    def get_postgres_names(self, include=None, exclude=None, exclude_builtin=True):
        output = subprocess.check_output([
            'sudo', '-u', 'postgres', 'psql', '--list', '--tuples-only',
        ])
        output = output.decode('ascii') # TODO: how to detect this etc.?

        names = []
        for line in output.split('\n'):
            line = line.strip()
            if line and '|' in line and not line.startswith('|'):
                name = line.split('|')[0].strip()
                names.append(name)

        if exclude_builtin:
            builtins = [
                'postgres',
                'template0',
                'template1',
            ]
            for name in builtins:
                if name in names:
                    names.remove(name)

        return self.filter_names(names, include, exclude)

    def filter_names(self, names, include, exclude):
        if include:
            names = [name for name in names if name in include]
        elif exclude:
            names = [name for name in names if name not in exclude]
        return names

    def dump_mysql_databases(self, outdir, include=None, exclude=None, dry_run=False):
        names = self.get_mysql_names(include=include, exclude=exclude)
        for name in names:
            log.info("dumping mysql db: %s", name)
            if not dry_run:
                sql_path = os.path.join(outdir, '{}-mysql.sql'.format(name))
                mysqldump = ['mysqldump']
                if self.verbose:
                    mysqldump.append('--verbose')
                cmd = mysqldump + [name, '--result-file={}'.format(sql_path)]
                log.debug("mysqldump command is: %s", cmd)
                subprocess.check_call(cmd)
                subprocess.check_call(['gzip', '--force', sql_path])
                gz_path = "{}.gz".format(sql_path)
                log.debug("dump completed, file is at %s", gz_path)

    def dump_postgres_databases(self, outdir, include=None, exclude=None, dry_run=False):
        names = self.get_postgres_names(include=include, exclude=exclude)
        for name in names:
            log.info("dumping postgres db: %s", name)
            if not dry_run:
                sql_path = os.path.join(outdir, '{}-postgres.sql'.format(name))
                tmp_path = '/tmp/{}.sql'.format(name)
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                pg_dump = ['sudo', '-u', 'postgres', 'pg_dump']
                if self.verbose:
                    pg_dump.append('--verbose')
                cmd = pg_dump + [name, '--file={}'.format(tmp_path)]
                log.debug("pg_dump command is: %s", cmd)
                subprocess.check_call(cmd)
                subprocess.check_call(['chown', 'root:', tmp_path])
                subprocess.check_call(['mv', tmp_path, sql_path])
                subprocess.check_call(['gzip', '--force', sql_path])
                gz_path = "{}.gz".format(sql_path)
                log.debug("dump completed, file is at %s", gz_path)

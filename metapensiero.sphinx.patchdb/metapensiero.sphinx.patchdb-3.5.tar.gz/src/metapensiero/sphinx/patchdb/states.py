# -*- coding: utf-8 -*-
# :Project:   PatchDB -- States management
# :Created:   ven 15 apr 2016 09:39:08 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

from collections import deque, namedtuple
from io import open
from os import remove, stat
from os.path import exists, join
from tempfile import gettempdir
from time import localtime, strftime

from .contexts import get_context_from_args


OK, UNAVAILABLE, USAGE = 0, 1, 128


State = namedtuple('State', ['state', 'patchid', 'revision'])


class StatesIndex(object):
    def __init__(self, dir, empty=False):
        self.index_name = join(dir, "patchdb-backups.index")
        self.index_file = None
        self.empty = empty

    def __bool__(self):
        return exists(self.index_name)

    def __enter__(self):
        assert self.index_file is None
        self.index_file = open(self.index_name, "w" if self.empty else "a", encoding='utf-8')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.index_file.close()

    def __iter__(self):
        with open(self.index_name, encoding='utf-8') as index:
            for line in index:
                state, patchid, revision = line.rstrip().split('\t')
                yield State(state, patchid, revision)

    def append(self, state):
        assert self.index_file is not None
        self.index_file.write("%s\t%s\t%s\n" % (state.state, state.patchid, state.revision))


def list_states(args):
    "List database states, possibly only those associated with a backup."

    index = StatesIndex(args.backups_dir)
    if not index:
        return UNAVAILABLE

    outfmt = '%s\t%s\t%s@%s' if args.tsv else "[%s] %s <%s@%s>"

    seen = set()
    for state in index:
        bck = join(args.backups_dir, state.state)
        if not exists(bck) or state.state in seen:
            continue
        print(outfmt % (strftime('%c', localtime(stat(bck).st_mtime)),
                        state.state, state.patchid, state.revision))
        seen.add(state.state)

    return OK


def cleanup_old_states(args):
    "Delete old snapshots."

    index = StatesIndex(args.backups_dir)
    if not index:
        return UNAVAILABLE

    all_states = set()
    try:
        last = deque(maxlen=args.keep_last)
    except ValueError:
        print("Invalid --keep-last argument!")
        return USAGE

    for state in index:
        if exists(join(args.backups_dir, state.state)):
            all_states.add(state.state)
            last.append(state)

    for state in all_states - set(s.state for s in last):
        bck = join(args.backups_dir, state)
        if args.dry_run:
            print("Would remove %s" % bck)
        else:
            remove(bck)
            print("Removed %s" % bck)

    if not args.dry_run:
        with StatesIndex(args.backups_dir, empty=True) as index:
            for state in last:
                index.append(state)
        count = len(last)
        print("Kept most recent %d snapshot%s" % (count, '' if count == 1 else 's'))


def restore_state(args):
    "Restore the given state of the database from a backup."

    sqlctx = get_context_from_args(args)
    if sqlctx is None:
        print("You must select exactly one database with either “--postgresql”,"
              " “--firebird”, “--mysql” or “--sqlite”!")
        return USAGE

    bck = join(args.backups_dir, args.state)
    if not exists(bck):
        print("State %s does not have a backup, sorry!" % args.state)
        return UNAVAILABLE

    sqlctx.closeConnection()

    try:
        sqlctx.restore(bck)
    except NotImplementedError as e:
        print("Error: %s" % e)
        return UNAVAILABLE
    else:
        return OK


def main():
    from argparse import ArgumentParser
    import locale
    import logging

    locale.setlocale(locale.LC_ALL, '')

    parser = ArgumentParser(description="Database states management")
    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help="Emit debug messages.")

    subparsers = parser.add_subparsers()

    subp = subparsers.add_parser('list', help=list_states.__doc__)
    subp.add_argument("backups_dir", nargs='?', default=gettempdir(),
                      help="Directory containing the backups, by default “%(default)s”.")
    subp.add_argument("--tsv", default=False, action="store_true",
                      help="Emit a “tab separated values” list.")
    subp.set_defaults(func=list_states)

    subp = subparsers.add_parser('clean', help=cleanup_old_states.__doc__)
    subp.add_argument("backups_dir", nargs='?', default=gettempdir(),
                      help="Directory containing the backups, by default “%(default)s”.")
    subp.add_argument("-k", "--keep-last", metavar="N", type=int, default=5,
                      help="Keep last N (%(default)s by default) snapshots,"
                      " remove older ones.")
    subp.add_argument("-n", "--dry-run", default=False, action="store_true",
                      help="Don't remove anything.")
    subp.set_defaults(func=cleanup_old_states)

    subp = subparsers.add_parser('restore', help=restore_state.__doc__)
    subp.add_argument("state",
                      help="The id of the state that shall be restored.")
    subp.add_argument("backups_dir", nargs='?', default=gettempdir(),
                      help="Directory containing the backups.")
    subp.add_argument("--postgresql", metavar="DSN",
                      help="Select the PostgreSQL context. DSN is a string of the kind"
                      " “host=localhost dbname=mydb user=myself password=ouch”.")
    subp.add_argument("--firebird", metavar="DSN",
                      help="Select the Firebird context.")
    subp.add_argument("--sqlite", metavar="DATABASE",
                      help="Select the SQLite context.")
    subp.add_argument("--mysql", metavar="DBNAME",
                      help="Select the MySQL context.")
    subp.add_argument("-u", "--username", metavar="USER",
                      help="Username to log into the database.")
    subp.add_argument("-p", "--password", metavar="PASSWORD",
                      help="Password")
    subp.add_argument("--host", metavar="HOSTNAME", default="localhost",
                      help="Host name where MySQL server runs, defaults to “localhost”.")
    subp.add_argument("--port", metavar="PORT", default=3306, type=int,
                      help="Port number used by the MySQL server, defaults to “3306”.")
    subp.add_argument("--charset", metavar="CHARSET", default="utf8mb4",
                      help="Encoding used by the MySQL driver, defaults to “utf8mb4”.")
    subp.add_argument("--driver", metavar="DRIVER", default="pymysql",
                      help="Driver to access MySQL, defaults to “pymysql”.")
    subp.set_defaults(func=restore_state)

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="[%(levelname).1s] %(message)s")

    return args.func(args) if hasattr(args, 'func') else OK


if __name__ == '__main__':
    from sys import exit

    exit(main())

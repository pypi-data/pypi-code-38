# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Apply collected patches to a database
# :Created:   Wed Nov 12 23:10:22 2003
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2003, 2009, 2010, 2012, 2013, 2014, 2015, 2016, 2017 Lele Gaifax
#

from collections import Counter
from os.path import isabs
import sys
import tempfile

import pkg_resources
import enlighten
from toposort import CircularDependencyError

from .contexts import ExecutionContext, ExecutionError, get_context_from_args
from .locale import gettext as _, ngettext, setup as setup_i18n
from .patch import DependencyError
from .manager import DuplicatedScriptError, Missing3rdPartyModule, patch_manager


OK, SOFTWARE, DATAERR, CONFIG, USAGE = 0, 1, 2, 3, 128


def path_spec(ps):
    if isabs(ps) or ':' not in ps:
        return ps
    pkgname, subpath = ps.split(':', 1)
    return pkg_resources.resource_filename(pkgname, subpath)


def workhorse(args, progress):
    sqlctx = get_context_from_args(args)
    if sqlctx is None:
        print(_("You must select exactly one database with either “--postgresql”,"
                " “--firebird”, “--mysql” or “--sqlite”!"))
        return USAGE

    if args.backups_dir != 'None' and not args.dry_run:
        sqlctx.backup(args.backups_dir)

    try:
        pm = patch_manager(args.storage)
    except (DuplicatedScriptError, Missing3rdPartyModule) as e:
        print(_("Error: %s") % e)
        return DATAERR

    if args.assertions:
        try:
            sqlctx.addAssertions(args.assertions)
        except ValueError as e:
            print("Invalid assertion: %s" % e)
            return CONFIG

    if args.variables:
        try:
            sqlctx.addVariables(args.variables)
        except ValueError as e:
            print(_("Invalid variable: %s") % e)
            return CONFIG

    try:
        patches = pm.neededPatches(sqlctx)
    except DependencyError as e:
        print(_("\nError: %s") % e)
        return DATAERR

    execute = ExecutionContext.execute

    try:
        count = 0
        npatches = len(patches)
        if npatches > 0:
            with progress.counter(total=npatches, desc=_('Upgrading:'), unit='script') as pbar:
                for p in patches:
                    if p is not None:
                        count += 1
                        execute(p, args)
                    pbar.update()
        if not args.dry_run and not args.quiet:
            print()
            print(ngettext("Done, applied %d script",
                           "Done, applied %d scripts",
                           count) % count)
        return OK
    except (DependencyError, ExecutionError) as e:
        write = sys.stderr.write
        write(_("\nError: %s") % e)
        write('\n')
        return DATAERR
    except CircularDependencyError as e:
        # Minimize problematic dependencies removing leaves, that is scripts
        # that have not dependants
        while True:
            deps_count = Counter()
            for script, deps in e.data.items():
                for dep in deps:
                    deps_count[dep] += 1
            leaves = [script for script in e.data if deps_count[script] == 0]
            if leaves:
                for leaf in leaves:
                    del e.data[leaf]
            else:
                break
        write = sys.stderr.write
        count = len(e.data)
        write("\n%s\n\n" % (_("Error: circular dependencies among %d scripts") % len(e.data)))
        write('digraph cycle {\n')
        for script, deps in e.data.items():
            sid = "%s@%d" % (script[0].replace('"', r'\"'), script[1])
            for dep in deps:
                did = "%s@%d" % (dep[0].replace('"', r'\"'), dep[1])
                write('  "%s" -> "%s";\n' % (sid, did))
        write('}\n')
        return DATAERR


def main():
    import locale
    import logging
    from argparse import ArgumentParser
    from pkg_resources import get_distribution

    locale.setlocale(locale.LC_ALL, '')
    setup_i18n()

    version = get_distribution('metapensiero.sphinx.patchdb').version
    parser = ArgumentParser(description=_("Database script applier"))

    parser.add_argument("storage", type=path_spec, nargs='+',
                        help=_("One or more archives containing collected scripts."
                               " May be either plain file names or package relative paths"
                               " like “package.name:some/file”."))
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    parser.add_argument("--postgresql", metavar="DSN",
                        help=_("Select the PostgreSQL context. DSN is a string of the kind"
                               " “host=localhost dbname=mydb user=myself password=ouch”."))
    parser.add_argument("--firebird", metavar="DSN",
                        help=_("Select the Firebird context."))
    parser.add_argument("--sqlite", metavar="DATABASE",
                        help=_("Select the SQLite context."))
    parser.add_argument("--mysql", metavar="DBNAME",
                        help=_("Select the MySQL context."))
    parser.add_argument("-u", "--username", metavar="USER",
                        help=_("Username to log into the database."))
    parser.add_argument("-p", "--password", metavar="PASSWORD",
                        help=_("Password"))
    parser.add_argument("--host", metavar="HOSTNAME", default="localhost",
                        help=_("Host name where MySQL server runs, defaults to “localhost”."))
    parser.add_argument("--port", metavar="PORT", default=3306, type=int,
                        help=_("Port number used by the MySQL server, defaults to “3306”."))
    parser.add_argument("--charset", metavar="CHARSET", default="utf8mb4",
                        help=_("Encoding used by the MySQL driver, defaults to “utf8mb4”."))
    parser.add_argument("--driver", metavar="DRIVER", default="pymysql",
                        help=_("Driver to access MySQL, defaults to “pymysql”."))
    parser.add_argument("-l", "--log-file", metavar="FILE",
                        dest="log_path",
                        help=_("Specify where to write the execution log."))
    parser.add_argument("--assume-already-applied", default=False, action="store_true",
                        help=_("Assume missing patches are already applied, do not"
                               " re-execute them."))
    parser.add_argument("--assert", metavar="NAME", action="append", dest="assertions",
                        help=_("Introduce an arbitrary assertion usable as a pre-condition"
                               " by the scripts. NAME may be a simple string or something like"
                               " “production=true”. This option may be given multiple times."))
    parser.add_argument("--define", metavar="VAR", action="append", dest="variables",
                        help=_("Define an arbitrary variable usable as “{{VARNAME}}” within"
                               " a script. VAR must be something like “varname=value”."
                               " This option may be given multiple times."))
    parser.add_argument("-n", "--dry-run", default=False, action="store_true",
                        help=_("Don't apply patches, just list them."))
    parser.add_argument("-q", "--quiet", default=False, action="store_true",
                        help=_("Be quiet, emit only error messages."))
    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help=_("Emit debug messages."))
    parser.add_argument("-b", "--backups-dir", metavar="DIR", default=tempfile.gettempdir(),
                        help=_("Perform a backup of the database in directory DIR"
                               " (by default “%(default)s”) before doing anything."
                               " Specify “None” to disable backups."))

    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.WARNING if args.quiet else logging.INFO
    if args.log_path:
        logging.basicConfig(filename=args.log_path, level=level,
                            format="%(asctime)s [%(levelname).1s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    else:
        logging.basicConfig(level=level, format="[%(levelname).1s] %(message)s")

    with enlighten.get_manager(enabled=not args.quiet) as progress:
        return workhorse(args, progress)


if __name__ == '__main__':
    from sys import exit
    from traceback import print_exc

    try:
        status = main()
    except Exception:
        print_exc()
        status = SOFTWARE
    exit(status)

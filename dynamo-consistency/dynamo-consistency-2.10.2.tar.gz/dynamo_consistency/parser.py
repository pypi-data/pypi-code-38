"""
Module that parses the command line for dynamo-consistency
"""

import os
import sys

import optparse

from ._version import __version__

# My executables
# Also include exec.py because dynamo runs everything after renaming it to that
EXES = ['exec.py', 'check-phedex', 'dynamo-consistency', 'set-status',
        'consistency-web-install', 'consistency-invalidate',
        'consistency-dump-tree']

def get_parser(modname='__main__', # pylint: disable=too-complex
               prog=os.path.basename(sys.argv[0])):
    """
    :param str modname: The module to fetch the ``__doc__`` optionally ``__usage__`` from.
                        If you want the parser for a particular file,
                        this would usually be ``__name__``
    :param str prog: The name for the program that we want the parser for

    :returns: A parser based on the program name and the arguments to pass it
    :rtype: optparse.OptionParser, list
    """

    mod = sys.modules[modname]
    usage = '%s\n%s' % (mod.__usage__, mod.__doc__) if '__usage__' in dir(mod) else None

    parser = optparse.OptionParser(usage=usage, version='dynamo-consistency %s' % __version__)

    # Don't add all the options for irrelevant scripts
    # Keep in mind, dynamo renames everything to "exec.py" before running it
    # Sphinx does the weird thing where it imports all the executables at the same time
    add_all = prog in ['exec.py', 'dynamo-consistency'] or prog == 'sphinx-build'

    parser.add_option('--config', metavar='FILE', dest='CONFIG',
                      help='Sets the location of the configuration file to read.')

    selection_group = optparse.OptionGroup(parser, 'Selection Options')

    if add_all or prog in ['consistency-invalidate', 'consistency-dump-tree']:
        selection_group.add_option('--site', metavar='PATTERN', dest='SITE_PATTERN',
                                   help='Sets the pattern used to select a site to run on next.')

    if add_all:
        selection_group.add_option('--lock', metavar='NAME', dest='LOCK_NAME',
                                   help='Sets the lock name that should be used for this run.',
                                   default=None)

    if prog == 'consistency-dump-tree':
        selection_group.add_option('--remote', action='store_true', dest='REMOTE',
                                   help='Dump the remote site listing instead of the inventory')

    if add_all or prog == 'consistency-dump-tree':
        selection_group.add_option('--date-string', metavar='YYYYMMDD', dest='DATESTRING',
                                   help='Set the datestring to pull for RAL-Reader listers')

    log_group = optparse.OptionGroup(parser, 'Logging Options')

    if add_all:
        log_group.add_option('--update-summary', action='store_true', dest='UPDATESUMMARY',
                             help='Forces the update of the summary table, even if loading trees')
        log_group.add_option('--email', action='store_true', dest='EMAIL',
                             help='Send an email on uncaught exception.')

    log_group.add_option('--info', action='store_true', dest='INFO',
                         help='Displays logs down to info level.')

    log_group.add_option('--debug', action='store_true', dest='DEBUG',
                         help='Displays logs down to debug level.')

    backend_group = optparse.OptionGroup(
        parser, 'Behavior Options',
        'These options will change the backend loaded and actions taken')

    if add_all:
        backend_group.add_option('--no-orphan', action='store_true', dest='NOORPHAN',
                                 help='Do not delete any orphan files.')
        backend_group.add_option('--cms', action='store_true', dest='CMS',
                                 help='Run actions specific to CMS collaboration data.')
        backend_group.add_option('--no-sam', action='store_true', dest='NOSAM',
                                 help='Disables the SAM readiness check.')
        backend_group.add_option('--more-logs', action='store_true', dest='MORELOGS',
                                 help='Clean any "AdditionalLogDeletions" directories.')

    if add_all or prog in ['consistency-dump-tree']:
        backend_group.add_option('--unmerged', action='store_true', dest='UNMERGED',
                                 help='Run actions on "/store/unmerged".')
        backend_group.add_option('--v1', action='store_true', dest='V1',
                                 help='Connect to Dynamo database directly')

    if add_all:
        backend_group.add_option('--v1-reporting', action='store_true', dest='V1_REPORTING',
                                 help='Connect to Dynamo database directly for registry only.')
        backend_group.add_option('--cnf', metavar='FILE', dest='CNF', default='/etc/my.cnf',
                                 help='Point to a non-default location of a ``my.cnf`` file.')

    if add_all or prog in ['consistency-dump-tree'] or prog.startswith('test_'):
        backend_group.add_option('--test', action='store_true', dest='TEST',
                                 help='Run with a test instance of backend module.')

    for group in [selection_group, log_group, backend_group]:
        if group.option_list:
            parser.add_option_group(group)

    argv = sys.argv if prog in EXES else [
        arg for arg in sys.argv if arg in
        [opt.get_opt_string() for opt in parser.option_list] +
        [opt.get_opt_string()
         for group in parser.option_groups
         for opt in group.option_list]
    ]

    if prog.startswith('test_'):
        argv.append('--test')

    return parser, argv


PARSER, ARGV = get_parser()

OPTS, ARGS = PARSER.parse_args(ARGV)

if os.path.basename(sys.argv[0]) != 'sphinx-build':
    def pretty_exe(_):
        """A dummy since we don't care about the docs here"""
        pass

else:
    import inspect
    # We only get here while running Sphinx.
    # In that case, you should also install what's in docs/requirements.txt
    from customdocs import pretty_exe_doc  # pylint: disable=import-error

    def pretty_exe(name):
        """
        Modifies the calling module's doc string

        :param str name: The desired heading for the new docstring
        """

        mod = inspect.getmodule(inspect.stack()[1][0])
        pretty_exe_doc(name, lambda: get_parser(mod.__name__, name)[0], 2)

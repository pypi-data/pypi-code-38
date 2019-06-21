#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Aug 13:43:21 2015
#

"""
Execute PAD algorithms on a database with presentation attacks.
"""


import argparse
import os
import sys

import bob.core

logger = bob.core.log.setup("bob.pad.base")

from bob.pad.base.database import PadDatabase

from . import FileSelector
from .. import database
from bob.bio.base import tools


def is_idiap():
    return os.path.isdir("/idiap") and "USER" in os.environ


def command_line_parser(description=__doc__, exclude_resources_from=[]):
    """command_line_parser(description=__doc__, exclude_resources_from=[]) -> parsers

    Creates an :py:class:`argparse.ArgumentParser` object that includes the minimum set of command line
    options (which is not so few).
    The ``description`` can be overwritten, but has a (small) default.

    Included in the parser, several groups are defined.
    Each group specifies a set of command line options.
    For the configurations, registered resources are listed, which can be limited by the
    ``exclude_resources_from`` list of extensions.

    It returns a dictionary, containing the parser object itself (in the ``'main'`` keyword), and
    a list of command line groups.

    **Parameters:**

    description : str
      The documentation of the script.

    exclude_resources_from : [str]
      A list of extension packages, for which resources should not be listed.

    **Returns:**

    parsers : dict
      A dictionary of parser groups, with the main parser under the 'main' key.
      Feel free to add more options to any of the parser groups.
    """
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     conflict_handler='resolve')

    #######################################################################################
    ############## options that are required to be specified #######################
    config_group = tools.command_line_config_group(parser, package_prefix='bob.pad.',
                                                   exclude_resources_from=exclude_resources_from)

    #######################################################################################
    ############## options to modify default directories or file names ####################

    # directories differ between idiap and extern
    temp = "/idiap/temp/%s/database-name/sub-directory" % os.environ["USER"] if is_idiap() else "temp"
    results = "/idiap/user/%s/database-name/sub-directory" % os.environ["USER"] if is_idiap() else "results"
    database_replacement = "%s/.bob_bio_databases.txt" % os.environ["HOME"]

    dir_group = parser.add_argument_group('\nDirectories that can be changed according to your requirements')
    dir_group.add_argument('-T', '--temp-directory', metavar='DIR',
                           help='The directory for temporary files, default is: %s.' % temp)
    dir_group.add_argument('-R', '--result-directory', metavar='DIR',
                           help='The directory for resulting score files, default is: %s.' % results)

    file_group = parser.add_argument_group(
        '\nName (maybe including a path relative to the --temp-directory, if not specified otherwise) of files '
        'that will be generated. Note that not all files will be used by all algorithms')
    file_group.add_argument('--extractor-file', metavar='FILE', default='Extractor.hdf5',
                            help='Name of the file to write the feature extractor into '
                                 '(used only if the extractor requires training).')
    file_group.add_argument('--projector-file', metavar='FILE', default='Projector.hdf5',
                            help='Name of the file to write the feature projector into.')
    file_group.add_argument('-G', '--gridtk-database-file', metavar='FILE', default='submitted.sql3',
                            help='The database file in which the submitted jobs will be written; relative to the '
                                 'current directory (only valid with the --grid option).')
    file_group.add_argument('--experiment-info-file', metavar='FILE', default='Experiment.info',
                            help='The file where the configuration of all parts of the experiments are written; '
                                 'relative to te --result-directory.')
    file_group.add_argument('-D', '--database-directories-file', metavar='FILE', default=database_replacement,
                            help='An optional file, where database directories are stored (to avoid changing the '
                                 'database configurations)')

    sub_dir_group = parser.add_argument_group(
        '\nSubdirectories of certain parts of the tool chain. You can specify directories in case you want to '
        'reuse parts of the experiments (e.g. extracted features) in other experiments. Please note that these '
        'directories are relative to the --temp-directory, but you can also specify absolute paths')
    sub_dir_group.add_argument('--preprocessed-directory', metavar='DIR', default='preprocessed',
                               help='Name of the directory of the preprocessed data.')
    sub_dir_group.add_argument('--extracted-directory', metavar='DIR', default='extracted',
                               help='Name of the directory of the extracted features.')
    sub_dir_group.add_argument('--projected-directory', metavar='DIR', default='projected',
                               help='Name of the directory where the projected data should be stored.')
    sub_dir_group.add_argument('--score-directories', metavar='DIR', nargs='+', default=['scores'],
                               help='Name of the directory (relative to --result-directory) where to write '
                                    'the results to')
    sub_dir_group.add_argument('--grid-log-directory', metavar='DIR', default='gridtk_logs',
                               help='Name of the directory (relative to --temp-directory) where to log files '
                                    'are written; only used with --grid')

    flag_group = parser.add_argument_group('\nFlags that change the behavior of the experiment')
    bob.core.log.add_command_line_option(flag_group)
    flag_group.add_argument('-q', '--dry-run', action='store_true',
                            help='Only report the commands that will be executed, but do not execute them.')
    flag_group.add_argument('-F', '--force', action='store_true',
                            help='Force to erase former data if already exist')
    flag_group.add_argument('-Z', '--write-compressed-score-files', action='store_true',
                            help='Writes score files which are compressed with tar.bz2.')
    flag_group.add_argument('-S', '--stop-on-failure', action='store_true',
                            help='Try to recursively stop the dependent jobs from the SGE grid queue, '
                                 'when a job failed')
    flag_group.add_argument('-X', '--external-dependencies', type=int, default=[], nargs='+',
                            help='The jobs submitted to the grid have dependencies on the given job ids.')
    flag_group.add_argument('-B', '--timer', choices=('real', 'system', 'user'), nargs='*',
                            help='Measure and report the time required by the execution of the tool chain '
                                 '(only on local machine)')
    flag_group.add_argument('-L', '--run-local-scheduler', action='store_true',
                            help='Starts the local scheduler after submitting the jobs to the local queue '
                                 '(by default, local jobs must be started by hand, e.g., using ./bin/jman '
                                 '--local -vv run-scheduler -x)')
    flag_group.add_argument('-N', '--nice', type=int, default=10,
                            help='Runs the local scheduler with the given nice value')
    flag_group.add_argument('-D', '--delete-jobs-finished-with-status', choices=('all', 'failure', 'success'),
                            help='If selected, local scheduler jobs that finished with the given status are deleted '
                                 'from the --gridtk-database-file; otherwise the jobs remain in the database')
    flag_group.add_argument('-A', '--allow-missing-files', action='store_true',
                            help="If given, missing files will not stop the processing; this is helpful if not "
                                 "all files of the database can be processed; missing scores will be NaN.")
    flag_group.add_argument('-r', '--parallel', type=int,
                            help='This flag is a shortcut for running the commands on the local machine with '
                                 'the given amount of parallel threads; equivalent to --grid '
                                 'bob.bio.base.grid.Grid("local", number_of_parallel_threads=X) '
                                 '--run-local-scheduler --stop-on-failure.')

    flag_group.add_argument('-t', '--environment', dest='env', nargs='*', default=[],
                            help='Passes specific environment variables to the job.')

    return {
        'main': parser,
        'config': config_group,
        'dir': dir_group,
        'sub-dir': sub_dir_group,
        'file': file_group,
        'flag': flag_group
    }


def initialize(parsers, command_line_parameters=None, skips=[]):
    """initialize(parsers, command_line_parameters = None, skips = []) -> args

    Parses the command line and arranges the arguments accordingly.
    Afterward, it loads the resources for the database, preprocessor, extractor, algorithm and
    grid (if specified), and stores the results into the returned args.

    This function also initializes the :py:class:`FileSelector` instance by arranging the
    directories and files according to the command line parameters.

    If the ``skips`` are given, an '--execute-only' parameter is added to the parser, according skips are selected.

    **Parameters:**

    parsers : dict
      The dictionary of command line parsers, as returned from :py:func:`command_line_parser`.
      Additional arguments might have been added.

    command_line_parameters : [str] or None
      The command line parameters that should be interpreted.
      By default, the parameters specified by the user on command line are considered.

    skips : [str]
      A list of possible ``--skip-...`` options to be added and evaluated automatically.

    **Returns:**

    args : namespace
      A namespace of arguments as read from the command line.

    .. note:: The database, preprocessor, extractor, algorithm and grid (if specified) are actual
      instances of the according classes.
    """

    args = tools.command_line_skip_group(parsers, command_line_parameters, skips)
    args_dictionary = {'required': ['database', 'preprocessor', 'extractor', 'algorithm', 'sub_directory'],
                       'common': ['protocol', 'grid', 'parallel', 'verbose', 'groups', 'temp_directory',
                                  'result_directory', 'allow_missing_files', 'dry_run', 'force'],
                       'optional': ['preprocessed_directory', 'extracted_directory', 'projected_directory',
                                    'extractor_file', 'projector_file']
                       }
    keywords = (
        "protocol",
        "groups",
        "parallel",
        "preferred_package",
        "temp_directory",
        "result_directory",
        "extractor_file",
        "projector_file",
        "gridtk_database_file",
        "experiment_info_file",
        "database_directories_file",
        "preprocessed_directory",
        "extracted_directory",
        "projected_directory",
        "score_directories",
        "grid_log_directory",
        "verbose",
        "dry_run",
        "force",
        "write_compressed_score_files",
        "stop_on_failure",
        "run_local_scheduler",
        "external_dependencies",
        "timer",
        "nice",
        "delete_jobs_finished_with_status",
        "allow_missing_files",
        "env",
    )
    args = tools.parse_config_file(parsers, args, args_dictionary, keywords, skips)

    args = tools.set_extra_flags(args)

    # protocol command line override
    if args.protocol is not None:
        args.database.protocol = args.protocol  # set the protocol if it is specified

    protocol = 'None' if args.database.protocol is None else args.database.protocol

    # result files
    args.info_file = os.path.join(args.result_directory, protocol, args.experiment_info_file)

    # sub-directorues that depend on the database
    extractor_sub_dir = protocol if args.database.training_depends_on_protocol and \
                                    args.extractor.requires_training else '.'
    projector_sub_dir = protocol if args.database.training_depends_on_protocol and \
                                    args.algorithm.requires_projector_training else extractor_sub_dir

    # Database directories, which should be automatically replaced
    if isinstance(args.database, PadDatabase):
        args.database.replace_directories(args.database_directories_file)

    # initialize the file selector
    FileSelector.create(
        database=args.database,
        extractor_file=os.path.join(args.temp_directory, extractor_sub_dir, args.extractor_file),
        projector_file=os.path.join(args.temp_directory, projector_sub_dir, args.projector_file),
        preprocessed_directory=os.path.join(args.temp_directory, args.preprocessed_directory),
        extracted_directory=os.path.join(args.temp_directory, extractor_sub_dir, args.extracted_directory),
        projected_directory=os.path.join(args.temp_directory, projector_sub_dir, args.projected_directory),
        score_directories=[os.path.join(args.result_directory, protocol, z) for z in args.score_directories],
        compressed_extension='.tar.bz2' if args.write_compressed_score_files else '',
        default_extension='.hdf5',
    )

    return args


def groups(args):
    """groups(args) -> groups

    Returns the groups, for which the files must be preprocessed, and features must be extracted and projected.
    This function should be used in order to eliminate the training files (the ``'train'`` group), when no
    training is required in this experiment.

    **Parameters:**

    args : namespace
      The interpreted command line arguments as returned by the :py:func:`initialize` function.

    **Returns:**

    groups : [str]
      A list of groups, for which data needs to be treated.
    """
    groups = args.groups[:]
    if args.extractor.requires_training or args.algorithm.requires_projector_training:
        groups.append('train')
    return groups


def command_line(cmdline):
    """command_line(cmdline) -> str

    Converts the given options to a string that can be executed in a terminal.
    Parameters are enclosed into ``'...'`` quotes so that the command line can interpret them (e.g., if they
    contain spaces or special characters).

    **Parameters:**

    cmdline : [str]
      A list of command line options to be converted into a string.

    **Returns:**

    str : str
      The command line string that can be copy-pasted into the terminal.
    """
    c = ""
    for cmd in cmdline:
        if str(cmd[0]) in '/-':
            c += "%s " % str(cmd)
        else:
            c += "'%s' " % str(cmd)
    return c


def write_info(args, command_line_parameters, executable):
    """Writes information about the current experimental setup into a file specified on command line.

    **Parameters:**

    args : namespace
      The interpreted command line arguments as returned by the :py:func:`initialize` function.

    command_line_parameters : [str] or ``None``
      The command line parameters that have been interpreted.
      If ``None``, the parameters specified by the user on command line are considered.

    executable : str
      The name of the executable (such as ``'./bin/spoof.py'``) that is used to run the experiments.
    """
    if command_line_parameters is None:
        command_line_parameters = sys.argv[1:]
    # write configuration
    try:
        bob.io.base.create_directories_safe(os.path.dirname(args.info_file))
        f = open(args.info_file, 'w')
        f.write("Command line:\n")
        f.write(command_line([executable] + command_line_parameters) + "\n\n")
        f.write("Configuration:\n")
        f.write("Database:\n%s\n\n" % args.database)
        f.write("Preprocessor:\n%s\n\n" % args.preprocessor)
        f.write("Extractor:\n%s\n\n" % args.extractor)
        f.write("Algorithm:\n%s\n\n" % args.algorithm)
    except IOError:
        logger.error("Could not write the experimental setup into file '%s'", args.info_file)

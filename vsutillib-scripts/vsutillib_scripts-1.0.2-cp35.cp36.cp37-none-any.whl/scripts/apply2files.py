#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import shlex
from pathlib import Path

from vsutillib.process import RunCommand
from vsutillib.files import getFileList

VERSION = '1.0.1'


class Command(object):
    """Command"""

    command = None
    arguments = None
    wildcard = None
    append = None


def parserArguments():
    """construct parser"""

    parser = argparse.ArgumentParser()

    parser.add_argument('directory',
                        nargs='+',
                        help='enter directory to process')
    parser.add_argument('-a',
                        '--arguments',
                        action='store',
                        default='',
                        help='optional arguments pass to command before file')
    parser.add_argument('-p',
                        '--append',
                        action='store',
                        default='',
                        help='optional arguments pass to command after file')
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        default=False,
                        help='just print commands')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        default=False,
                        help='increase verbosity')
    parser.add_argument('-c',
                        '--command',
                        action='store',
                        default='',
                        help='command to apply')
    parser.add_argument('-l',
                        '--logfile',
                        action='store',
                        default='commandLog.txt',
                        help='file to log output')
    parser.add_argument('-w',
                        '--wildcard',
                        action='store',
                        default='*',
                        help='wildcard to select files to process')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + VERSION)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-o',
                       '--onlycurrentdir',
                       action='store_true',
                       default=False,
                       help='don\'t proccess subdirectories')
    group.add_argument('-s',
                       '--onlysubdir',
                       action='store_true',
                       default=False,
                       help='don\'t proccess current working directory')

    return parser


def printToConsoleAndFile(oFile, msg):
    """print to console and write to logfile"""
    if oFile:
        oFile.write(msg.encode())
    print(msg)


def apply2files():
    """
    script to apply supplied command to file in directory
    and subdirectories if needed

    ::

        usage: apply2files.py [-h] [-a ARGUMENTS] [-d] [-o] [-v] [-c COMMAND]
                            [-l LOGFILE] [-w WILDCARD] [--version]
                            directory [directory ...]

        positional arguments:
        directory             enter directory to process

        optional arguments:
        -h, --help            show this help message and exit
        -a ARGUMENTS, --arguments ARGUMENTS
                                optional arguments pass to command before file
        -p ARGUMENTS, --append ARGUMENTS
                                optional arguments pass to command after file
        -d, --debug           just print commands
        -o, --onlycurrentdir  don't proccess subdirectories
        -v, --verbose         increase verbosity
        -c COMMAND, --command COMMAND
                                command to apply
        -l LOGFILE, --logfile LOGFILE
                                file to log output
        -w WILDCARD, --wildcard WILDCARD
                                wildcard to select files to process
        --version             show program's version number and exit

    """

    cmd = Command()

    parser = parserArguments()
    args = parser.parse_args()

    cwd = Path.cwd()
    lFile = Path(args.logfile)
    logFile = None

    if Path(lFile.parent).is_dir():
        lFile.touch(exist_ok=True)
    else:
        # cannot create log file
        # on command line
        lFile = Path('commandLog.txt')
        lFile.touch(exist_ok=True)

    logFile = lFile.open(mode='wb')

    cmd.command = args.command
    if not cmd.command:
        print('Nothing to do.')
        return None

    cmd.arguments = args.arguments
    cmd.append = args.append

    cmd.wildcard = None
    if args.wildcard:
        cmd.wildcard = args.wildcard
    else:
        cmd.wildcard = ''

    debug = args.debug
    recursive = (not args.onlycurrentdir) and (not args.onlysubdir)
    subdironly = args.onlysubdir

    print('Recursive {} subdironly {}'.format(recursive, subdironly))

    msg = 'Current directory {}\n'.format(str(cwd))
    printToConsoleAndFile(logFile, msg)

    fCheckOk = True
    for d in args.directory:

        p = Path(d)

        try:
            if not p.is_dir():
                msg = 'Invalid directory {}\n'.format(str(p))
                printToConsoleAndFile(logFile, msg)
                fCheckOk = False

        except OSError as error:
            msg = error.strerror
            fCheckOk = False

        if not fCheckOk:
            msg += "\n\nInput: {}"
            msg = msg.format(str(d))
            raise ValueError(msg)

    if not fCheckOk:
        printToConsoleAndFile(logFile, msg)
        return

    processLine = None
    if args.verbose:
        processLine = sys.stdout.write

    cli = RunCommand(processLine=processLine)

    for d in args.directory:

        msg = 'Working\n\nDirectory: [{}]\nWildcard:  {}\n\n'.format(
            str(Path(d).resolve()), cmd.wildcard)
        printToConsoleAndFile(logFile, msg)

        filesList = getFileList(d,
                                wildcard=cmd.wildcard,
                                fullpath=True,
                                recursive=recursive)

        nTotalFiles = len(filesList)

        count = 0
        noMatchFiles = []

        for of in filesList:

            if subdironly:
                if of.resolve().parent == Path.cwd():
                    print("By pass.")
                    continue

            f = str(of)

            qf = shlex.quote(f)

            cliCommand = cmd.command + " " + cmd.arguments + " " + qf + " " + cmd.append
            cli.command = cliCommand

            msg = 'Processing file [{}]\n'.format(f)
            printToConsoleAndFile(logFile, msg)

            if debug:

                msg = 'Debug Command: {}\n\n'.format(cliCommand)
                printToConsoleAndFile(logFile, msg)

            else:

                if cli.run():

                    if cli.output:
                        for line in cli.output:
                            logFile.write(line.encode())
                        logFile.write('\n\n'.encode())

        if count != nTotalFiles:
            msg = 'Bummer..'
            for f in noMatchFiles:
                msg = 'Check file \'{}\'\n'.format(f)
                logFile.write(msg.encode())


if __name__ == "__main__":
    apply2files()

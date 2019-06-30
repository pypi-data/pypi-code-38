#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compress DSF files into WavPack"""

import argparse
import sys
import shlex
from pathlib import Path

from vsutillib.process import RunCommand
from vsutillib.files import getFileList

VERSION = "1.0"


def parserArguments():
    """construct parser"""

    parser = argparse.ArgumentParser(
        description='compress dsf audio file to WavPack container')

    parser.add_argument('directory',
                        nargs='+',
                        help='enter directory to process')
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        default=False,
                        help='just print commands')
    parser.add_argument('-o',
                        '--onlycurrentdir',
                        action='store_true',
                        default=False,
                        help='don\'t proccess subdirectories')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        default=False,
                        help='increase verbosity')
    parser.add_argument('-c', '--command', help='command to apply')
    parser.add_argument('-l',
                        '--logfile',
                        action='store',
                        default='dsf2wv.txt',
                        help='file to log output')
    parser.add_argument('-w',
                        '--wildcard',
                        help='wildcard to select files to process')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + VERSION)

    return parser


def printToConsoleAndFile(oFile, msg):
    """print to console and write to logfile"""
    if oFile:
        oFile.write(msg.encode())
    print(msg)


def dsf2wv():
    """Main"""

    command = "wavpack -y --allow-huge-tags --import-id3"
    wildcard = '*.dsf'

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
        lFile = Path('dsf2wv.txt')
        lFile.touch(exist_ok=True)

    logFile = lFile.open(mode='wb')

    wildcard = None
    if args.wildcard:
        wildcard = args.wildcard
    else:
        wildcard = '*.dsf'

    debug = args.debug
    recursive = not args.onlycurrentdir

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

    cli = RunCommand(regexsearch=[
        r'created (.*?) in.* (.*?)%', r'sor.\W(.*?) Version (.*)\r',
        r'temp file (.*?) to (.*)!'
    ],
                     processLine=processLine)

    for d in args.directory:

        msg = 'Working in \n\nDirectory: [{}]\nWildcard:  {}\n\n'.format(
            str(Path(d).resolve()), wildcard)
        printToConsoleAndFile(logFile, msg)

        filesList = getFileList(d,
                                wildcard=wildcard,
                                fullpath=True,
                                recursive=recursive)

        nTotalFiles = len(filesList)

        count = 0
        noMatchFiles = []

        for of in filesList:

            f = str(of)

            qf = shlex.quote(f)

            cliCommand = command + " " + qf
            cli.command = cliCommand

            msg = 'Processing file [{}]\n'.format(f)
            printToConsoleAndFile(logFile, msg)

            if debug:

                msg = 'Command: {}\n\n'.format(cliCommand)
                printToConsoleAndFile(logFile, msg)

            else:

                if cli.run():

                    version = ""

                    if cli.regexmatch[1] is not None:
                        fc = cli.regexmatch[1]
                        version = "WavPack {} Version {} ".format(fc[0], fc[1])

                    if cli.regexmatch[0] is not None:
                        # File and compression ratio
                        fc = cli.regexmatch[0]

                        if fc:
                            if len(fc) == 2:
                                msg = '{}created file [{}] at {}% compression\n\n'.format(
                                    version, fc[0], fc[1])
                                printToConsoleAndFile(logFile, msg)
                                count += 1
                            else:
                                noMatchFiles.append(f)

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
    dsf2wv()

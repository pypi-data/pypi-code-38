#!/usr/bin/env python3
"""The Quantum Service Assembler (QSA) provides a command-line
interface to configure software projects and render or compile
code based on a declarative specification.
"""
import argparse
import os
import logging
import sys

from ioc.injector import ArgumentDependencyInjector

import qsa.cli.commands
from qsa.assembler import Assembler
from qsa.cli.runner import CommandRunner
from qsa.config import AssemblerConfig
from qsa.lib.repository import CodeRepository
from qsa.spec import QuantumSpecification


parser = argparse.ArgumentParser(__doc__)
parser.set_defaults(workdir=os.getenv('QSA_WORKDIR'))
commands = parser.add_subparsers(help='commands', dest='subcommand')
qsa.cli.commands.ignore.createparser(parser, commands)
qsa.cli.commands.init.createparser(parser, commands)
qsa.cli.commands.update.createparser(parser, commands)


def main():
    """Parse the command-line arguments and execute the appropriate
    QSA commands.
    """
    root = logging.getLogger('qsa')
    #root.setLevel(logging.DEBUG)

    #handler = logging.StreamHandler(sys.stderr)
    #handler.setLevel(logging.DEBUG)
    #formatter = logging.Formatter('[%(levelname)s]: %(message)s')
    #handler.setFormatter(formatter)
    #root.addHandler(handler)

    config = AssemblerConfig(workdir=os.getenv('QSA_WORKDIR'))
    injector = ArgumentDependencyInjector()
    injector.provide('codebase', CodeRepository(config.workdir))
    injector.provide('config', config)
    injector.provide('logger', root)
    injector.provide('subcommands', commands)

    assembler = Assembler(config, injector)
    quantum = QuantumSpecification(config, assembler)
    injector.provide('assembler', assembler)
    injector.provide('quantum', quantum)

    return run(config, parser.parse_args(), injector)


def run(config, args, injector):
    logger = logging.getLogger('qsa')
    if not args.subcommand:
        logger.debug("Running full QSA update in %s", args.workdir)
    else:
        logger.debug("Running command %s in %s",
            args.subcommand, args.workdir)
    injector.provide('args', args)
    runner = CommandRunner(config, injector)
    runner.run(args.func, args)


if __name__ == '__main__':
    main()

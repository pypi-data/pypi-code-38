"""Initializes a new QSA project."""
import os

from qsa.cli.exc import CommandError


def createparser(parent, commands):
    parser = commands.add_parser('init', help=__doc__)
    parser.add_argument('type', choices=['library', 'application', 'container-image', 'k8s'],
        help="specifies the project type.")
    parser.add_argument('--name',
        help="specifies the project symbolic name.")
    parser.add_argument('-l', dest='lang',
        help="specifies the project language, if applicable.")
    parser.add_argument('--force', action='store_true',
        help="force project init even if a Quantumfile exists.")
    parser.set_defaults(func=main)


def main(quantum, args):
    os.environ['QSA_INIT'] = '1'
    if args.type in ('application', 'library') and not args.lang:
        raise CommandError("Specify the programming language with the -l flag.")
    os.environ['QSA_PROJECT_NAME'] = args.name or ''
    quantum.init(args.type, args.name, language=args.lang,
        force=args.force)

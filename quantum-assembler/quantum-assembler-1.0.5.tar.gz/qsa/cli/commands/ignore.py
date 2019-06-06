from qsa.cli.exc import CommandError


def createparser(parent, commands):
    parser = commands.add_parser('ignore')
    parser.add_argument('-f', dest='filepath',
        help="ignore the given filepath.",
        default='')
    parser.add_argument('-d', dest='dirname',
        help="ignore the given directory.",
        default='')
    parser.add_argument('-p', dest='pattern',
        help="ignore the given pattern.",
        default='')
    parser.add_argument('-i', dest='inspect',
        help="check if the given path is ignored.")
    parser.set_defaults(func=main)


def main(args, config):
    if args.inspect:
        if config.isignored(args.inspect):
            print(
                f"Path {args.inspect} is ignored by the Quantum "
                " Service Assembler (QSA)")
        return

    if not (bool(args.filepath) ^ bool(args.dirname) ^ bool(args.pattern)):
        raise CommandError(
            "Specify either a filepath, directory or pattern "
            "using -f, -d or -p respectively.")
    config.ignore(args.filepath or args.dirname or args.pattern)

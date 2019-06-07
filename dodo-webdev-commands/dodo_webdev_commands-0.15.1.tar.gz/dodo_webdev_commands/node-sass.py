from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo
import os


def _args():
    parser = ArgumentParser()
    parser.add_argument('--watch', action="store_true")
    parser.add_argument('nodesass_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.nodesass = Dodo.get_config("/SASS/nodesass", "node-sass")
    args.src_map = Dodo.get_config("/SASS/src_map")
    return args


def _cmd_str(args, nodesass_args):
    cmds = []
    for src_file, output_file in args.src_map.items():
        cmds.append("{nodesass} {src_file} {output_file} {args}".format(
            nodesass=args.nodesass,
            src_file=src_file,
            output_file=output_file,
            args=" ".join(nodesass_args)))
    return " & ".join(cmds)


if Dodo.is_main(__name__):
    args = _args()
    for src_file, output_file in args.src_map.items():
        Dodo.run(["mkdir", "-p", os.path.dirname(output_file)])

    Dodo.run(["/bin/bash", "-c", _cmd_str(args, args.nodesass_args)])
    if args.watch:
        Dodo.run(
            ["/bin/bash", "-c",
             _cmd_str(args, args.nodesass_args + ['-w'])])

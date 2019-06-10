# coding: utf-8

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

import licant.util
from licant.core import WrongAction

import sys
import os

default_target = None

def make_freeargs_help(core):
    ret = """Specify target with format [target [action [args*]]]\n\nList of internal targets:\n"""

    for t in sorted(core.help_showed_targets, key=lambda x: x.tgt):
        ret += "{}: {}\n".format(t.tgt, t.__help__)

    return ret


def cli_argv_parse(argv, core):
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="print full system commands",
    )
    parser.add_argument(
        "-t",
        "--trace",
        action="store_true",
        default=False,
        help="print trace information",
    )
    parser.add_argument(
        "-j", "--threads", default=1, help="amount of threads for executor"
    )
    parser.add_argument(
        "-q",
        "--quite",
        action="store_true",
        default=False,
        help="don`t print shell operations",
    )
    parser.add_argument("freeargs", type=str, nargs="*", help=make_freeargs_help(core))

    parser.add_argument("--printruntime", action="store_true", default=False)

    opts = parser.parse_args(argv)
    args = opts.freeargs

    return opts, args


def execute_with_default_action(target, args):
    if not hasattr(target, "default_action"):
        licant.util.error(
            "target {} hasn't default_action (actions: {})".format(
                licant.util.yellow(target.tgt), licant.util.get_actions(target)
            )
        )
    return target.invoke(target.default_action, *args, critical=True)


def __cliexecute(args, default, core):
    global default_target
    default_target = default

    if len(args) == 0:
        if default is None:
            licant.util.error("default target isn't set")

        target = core.get(default)
        return execute_with_default_action(target, [])

    fnd = args[0]

    # Try look up fnd in targets
    if fnd in core.targets:
        target = core.get(fnd)

        if len(args) == 1 or isinstance(target, licant.core.Routine):
            return execute_with_default_action(target, args[1:])

        act = args[1]

        if not target.hasaction(act):
            licant.util.error(
                "{} is not action of target {}".format(
                    licant.util.yellow(act), licant.util.yellow(fnd)
                )
            )

        return target.invoke(act, *args[2:], critical=True)

    # Try look up fnd in actions of default_target
    if default is not None:
        dtarget = core.get(default)
        if dtarget.hasaction(fnd):
            return dtarget.invoke(fnd, *args[1:], critical=True)

    # Can't look fnd.
    licant.util.error(
        "Can't find routine "
        + licant.util.yellow(fnd)
        + ". Enough target or default target's action with same name."
    )


def cliexecute(default=None, colorwrap=False, argv=sys.argv[1:], core=licant.core.core):
    if colorwrap:
        print(licant.util.green("[start]"))

    opts, args = cli_argv_parse(argv, core)

    core.runtime["debug"] = opts.debug or opts.trace
    core.runtime["trace"] = opts.trace
    core.runtime["quite"] = opts.quite

    cpu_count = os.cpu_count()
    core.runtime["threads"] = cpu_count if opts.threads == "j" else int(opts.threads)

    if opts.printruntime:
        print("PRINT RUNTIME:", core.runtime)

    __cliexecute(args, default=default, core=core)

    if colorwrap:
        print(licant.util.yellow("[finish]"))

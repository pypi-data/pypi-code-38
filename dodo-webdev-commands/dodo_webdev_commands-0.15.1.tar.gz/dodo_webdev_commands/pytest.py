from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser()
    parser.add_argument('pytest_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.no_capture = not Dodo.get_config("/PYTEST/capture", True)
    args.html_report = Dodo.get_config("/PYTEST/html_report", None)
    args.test_file = Dodo.get_config("/PYTEST/test_file", None)
    args.pytest = Dodo.get_config("/PYTEST/pytest", "pytest")
    args.cwd = Dodo.get_config("/PYTEST/src_dir",
                               Dodo.get_config("/ROOT/src_dir"))
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(
        [
            args.pytest,
        ] + remove_trailing_dashes(
            args.pytest_args + ([args.test_file] if args.test_file else []) +
            (["--capture", "no"] if args.no_capture else []) +
            (["--html", args.html_report] if args.html_report else [])),
        cwd=args.cwd)

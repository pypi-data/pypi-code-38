from argparse import ArgumentParser
from dodo_commands.framework import Dodo, ConfigArg, CommandError
import os


def _args():
    parser = ArgumentParser()

    parser.add_argument(
        '--pip-requirements',
        dest='requirements_filename',
        help=
        'The pip requirements filename. If you use the value \'default\' then ${/SERVER/pip_requirements} from the configuration is used.'
    )
    parser.add_argument('--node-modules-dir', dest='node_modules_dir')

    args = Dodo.parse_args(parser,
                           config_args=[
                               ConfigArg('/SERVER/venv_dir', '--venv_dir'),
                           ])
    args.yarn = 'yarn'

    if args.requirements_filename == 'default':
        args.requirements_filename = Dodo.get_config(
            '/SERVER/pip_requirements')

    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if not args.requirements_filename and not args.node_modules_dir:
        raise CommandError(
            "Either --requirements-filename or --node_modules-dir is mandatory."
        )

    if args.requirements_filename:
        if not args.venv_dir:
            raise CommandError(
                "The venv_dir argument is mandatory if --requirements_filename is used."
            )
        pip = os.path.join(args.venv_dir, 'bin', 'pip')
        Dodo.run([pip, 'install', '-r', args.requirements_filename])
    if args.node_modules_dir:
        Dodo.run([args.yarn, 'install'],
                 cwd=os.path.abspath(os.path.join(args.node_modules_dir,
                                                  '..')))

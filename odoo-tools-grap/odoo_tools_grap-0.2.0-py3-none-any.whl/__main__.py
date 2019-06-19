# coding: utf-8
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import argcomplete
import configparser
import subprocess
import yaml
import os


def _generate_odoo_config_file(args):
    input_files = [os.path.join(args.folder, x) for x in args.input_files]
    config_repo_file = os.path.join(args.folder, args.config_repo_file)
    output_file = os.path.join(args.folder, args.output_file)

    # Read Input Files
    parser = configparser.ConfigParser()
    parser.read(input_files)

    # Compute Addons path
    stream = open(config_repo_file, 'r')
    data = yaml.safe_load(stream)

    addons_path = []
    for key in data.keys():
        path = os.path.join(args.folder, key)
        if path.split('/')[-1] == 'odoo':
            # Add two addons path
            addons_path.append(os.path.join(path, 'addons'))
            addons_path.append(os.path.join(path, args.odoo_version))
        else:
            addons_path.append(path)

    parser.set('options', 'addons_path', ','.join(addons_path))

    parser.write(open(output_file, 'w'))
    print("%s has been generated or updated." % (output_file))


def _display_diff(args):
    config_repo_file = os.path.join(args.folder, args.config_repo_file)

    # Compute Addons path
    stream = open(config_repo_file, 'r')
    data = yaml.safe_load(stream)

    addons_path_list = []
    for key in data.keys():
        path = os.path.join(args.folder, key)
        addons_path_list.append(path)

    for addons_path in sorted(addons_path_list):
        res = subprocess.check_output(['git', 'status'], cwd=addons_path)
        res = res.decode("utf-8")
        if "la copie de travail est propre" not in res or args.verbose:
            print("".rjust(120, "="))
            print(addons_path)
            print("".rjust(120, "="))
            print(res)


def get_parser():
    """Return :py:class:`argparse.ArgumentParser` instance for CLI."""

    main_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    main_parser.add_argument(
        'command',
        nargs='?',
        help='generate: Generate Odoo Config File.\n'
        'diff: display git diff.')

    main_parser.add_argument(
        '-f', '--folder',
        default='./',
        help='Targer folder')

    main_parser.add_argument(
        '-v', '--verbose',
        default=False,
        action='store_true',
        help='Verbose Mode')

    main_parser.add_argument(
        '-c', '--config-repo-file',
        dest='config_repo_file',
        type=str,
        default='repos.yml',
        nargs='?',
        help='Repositories file'
    ).completer = argcomplete.completers.FilesCompleter(
        allowednames=('.yaml', '.yml', '.json'), directories=False
    )

    main_parser.add_argument(
        '-i', '--input-files',
        dest='input_files',
        type=list,
        default=["./common.odoo.cfg", "./custom.odoo.cfg"],
        help='Template odoo Config File(s)'
    ).completer = argcomplete.completers.FilesCompleter(
        allowednames=('.cfg'), directories=False
    )

    main_parser.add_argument(
        '-o', '--output-file',
        dest='output_file',
        type=str,
        default="./odoo.cfg",
        help='Generated Odoo config file'
    ).completer = argcomplete.completers.FilesCompleter(
        allowednames=('.cfg'), directories=False
    )

    main_parser.add_argument(
        '-ov', '--odoo-version',
        dest='odoo_version',
        type=str,
        default='odoo',
        help="Possible value : 'odoo' or 'openerp'"
    )

    return main_parser


def main():
    parser = get_parser()
    argcomplete.autocomplete(parser, always_complete_options=False)
    args = parser.parse_args()

    try:
        if args.command == 'generate':
            _generate_odoo_config_file(args)
        elif args.command == 'diff':
            _display_diff(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

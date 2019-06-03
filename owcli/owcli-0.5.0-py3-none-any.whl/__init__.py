import os
import re
import sys
from importlib import import_module
from typing import List

from docopt import docopt


def head_while_options(doc: str) -> str:
    ret = ""
    for line in doc.split("\n"):
        if line.startswith("Options:"):
            return ret
        ret += line + "\n"


def create_doc(cli: str, commands: str, show_help: bool) -> str:
    commands_doc = (
        f"""Commands:
{commands}"""
        if show_help
        else ""
    )

    return f"""
Usage:
  {cli} <command> [<subcommand>] [<args>...]
  {cli} <command> [<subcommand>] (-h | --help)
  {cli} (-h | --help)
  {cli} --version

{commands_doc}"""


def create_doc_command(
    cli: str, command: str, description: str, subcommands: str, show_help: bool
) -> str:
    subcommands_doc = (
        f"""
Subcommands:
{subcommands}"""
        if show_help
        else ""
    )

    description_doc = f"{description}\n" if description else ""

    return f"""{description_doc}Usage:
  {cli} {command} [<subcommand>] [<args>...]
  {cli} {command} (-h | --help)
{subcommands_doc}"""


def command_not_found_format(command: str, commands: List[str]) -> str:
    cmds = "\n".join(commands)
    return f"""
| Command `{command}` is not found.
| Show available commands.
`{'-' * 79}

{cmds}"""


def subcommand_not_found_format(subcommand: str, command: str, subcommands: List[str]) -> str:
    cmds = "\n".join(subcommands)
    return f"""
| Subcommand `{subcommand}` is not found in `{command}` command.
| Show available subcommands.
`{'-' * 79}

{cmds}"""


def first_line_in_doc(path: str) -> str:
    return re.search(r'"""(.*)', open(path, encoding="utf-8").read()).group(1)


def run(cli: str, version: str, root: str):
    """
    :param cli: CLI file name
    :param version: Version
    :param root: Absolute path for root

    Example:
        ----
        docowl.run(cli="gtfs", version=__version__, root=os.path.dirname(os.path.realpath(__file__)))
        ----
    """
    root_dirname = os.path.basename(root)
    # Remove <args> to avoid parse errors.
    commands = [
        f'  {x:20}{first_line_in_doc(os.path.join(root, "commands", x, "main.py"))}'
        for x in sorted(os.listdir(f"{root}/commands"))
        if os.path.isdir(f"{root}/commands/{x}") and not x.startswith("_")
    ]

    doc = create_doc(cli=cli, commands="\n".join(commands), show_help=True)
    main_args = docopt(doc, argv=sys.argv[1:3], version=version, options_first=True)

    command: str = main_args.pop("<command>")
    if command in ["-h", "--help"]:
        print(create_doc(cli=cli, commands="\n".join(commands), show_help=True))
        sys.exit(0)

    try:
        cmd_module = import_module(f"{root_dirname}.commands.{command}.main")
    except ModuleNotFoundError:
        print(command_not_found_format(command, commands))
        sys.exit(1)

    subcommand: str = main_args.pop("<subcommand>")
    subcommands = [
        f'  {x:20}          {first_line_in_doc(os.path.join(root, "commands", command, x, "main.py"))}'
        for x in sorted(os.listdir(f"{root}/commands/{command}"))
        if os.path.isdir(f"{root}/commands/{command}/{x}") and not x.startswith("_")
    ]

    # Show global docs and abort
    if subcommand in ["-h", "--help"]:
        command_doc = (
            create_doc_command(cli, command, cmd_module.__doc__, "\n".join(subcommands), True)
            if subcommands
            else cmd_module.__doc__.format(cli=f"{cli} {command}")
        )
        print(command_doc)
        sys.exit(0)

    # Run without subcommand if there are no subcommands
    if hasattr(cmd_module, "run"):
        cmd_module.run(
            cmd_module.Args.from_dict(
                docopt(cmd_module.__doc__.format(cli=f"{cli} {command}")),
                restrict=False,
                force_cast=True,
            )
        )
        sys.exit(0)

    # Subcommand exists
    try:
        sub_cmd_module = import_module(f"{root_dirname}.commands.{command}.{subcommand}.main")
    except ModuleNotFoundError:
        if subcommand:
            print(subcommand_not_found_format(subcommand, command, subcommands))
        else:
            print(create_doc_command(cli, command, None, "\n".join(subcommands), False))
        sys.exit(1)

    if hasattr(sub_cmd_module, "run"):
        sub_cmd_module.run(
            sub_cmd_module.Args.from_dict(
                docopt(sub_cmd_module.__doc__.format(cli=f"{cli} {command} {subcommand}")),
                restrict=False,
                force_cast=True,
            )
        )
        sys.exit(0)

    print(f"Subcommand `{subcommand}` doesn't has `run` function.")
    sys.exit(1)

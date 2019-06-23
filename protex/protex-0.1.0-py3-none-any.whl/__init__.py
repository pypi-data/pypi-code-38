import sys

from .commands import load_all_files
from .lexer import Lexer
from .parser import Parser


def parse_with_lexer(lx, expand_input):
    commands = load_all_files()
    parser = Parser(lx, commands, filename=lx.source_file,
                    expand_input=expand_input)
    return parser.parse()


def parse_with_default(filename, expand_input=False):
    lexer = Lexer.from_file(filename)
    return parse_with_lexer(lexer, expand_input=expand_input)


def parse_stdin_with_default(expand_input=False):
    lexer = Lexer('stdin', sys.stdin)
    return parse_with_lexer(lexer, expand_input=expand_input)


def run_cli():
    import cli
    cli.App()

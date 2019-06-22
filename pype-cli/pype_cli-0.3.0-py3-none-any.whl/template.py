# -*- coding: utf-8 -*-
"""Not documented yet."""

# Pype's go-to library to create command-line interfaces.
# Visit <https://click.palletsprojects.com> for details.
import click

# For colored output pype includes the colorama library
from colorama import Fore, Style

# Used for convenience to name click command using the file's name
from pype.core import fname_to_name
# You can also call pype's own utility functions
from pype.util import cli
from pype.util.iotools import run_interactive


# Decorators to initialize a CLI-command with options
@click.command(name=fname_to_name(__file__), help=__doc__)
@click.option('--option', '-o', default='default', help='An option')
@click.option('--verbose', '-v', is_flag=True, help='A toggle')
def main(option, verbose):
    """Script's main entry point."""
    # Print out something in shiny colors
    cli.print_success('Yay!')
    cli.print_warning('Meh.')
    cli.print_error('Oh no!')

    # Use colorama directly
    print(Fore.RED + '- option:  ' + Style.DIM + Fore.GREEN + option)
    print(Fore.RED + '- verbose: ' + Style.DIM + Fore.GREEN + str(verbose))

    # Use a pype utility
    run_interactive('ls -la')

    # Your code goes here ...

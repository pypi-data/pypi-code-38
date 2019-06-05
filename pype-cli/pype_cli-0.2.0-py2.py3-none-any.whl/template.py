# -*- coding: utf-8 -*-
"""Not documented yet."""

# Pype's go-to library to create command-line interfaces.
# Visit <https://click.palletsprojects.com> for details.
import click

# For colored output pype includes the colorama library
from colorama import Fore, Style, init

# You can also call pype's own utility functions
from pype.util.iotools import run_interactive


# Decorators to initialize a CLI-command with options
@click.command(help=__doc__)
@click.option('--option', '-o', default='default', help='An option')
@click.option('--verbose', '-v', is_flag=True, help='A toggle')
def main(option, verbose):
    """Script's main entry point."""
    # Print out something in shiny colors
    print(Fore.RED + '- option:  ' + Style.DIM + Fore.GREEN + option)
    print(Fore.RED + '- verbose: ' + Style.DIM + Fore.GREEN + str(verbose))

    # Use a pype utility
    run_interactive('ls -la')

    # Your code goes here ...


if __name__ == '__main__':  # Only invoke main if called directly
    init(autoreset=True)  # Enables colored input with resets after each print
    main()

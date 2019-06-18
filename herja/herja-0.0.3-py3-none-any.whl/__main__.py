"""This module contains some useful tools for the owner of this repository."""


from .decorators import MainCommands


@MainCommands(
    ('test', 'Testing command.', [])
)
def main(args):
    """Handle arguments given to this module."""
    print(args)
    return 0

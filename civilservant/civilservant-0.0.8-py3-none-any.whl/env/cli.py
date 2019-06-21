import sys

from invoke.program import Program

from .__version__ import __version__
from .namespace import namespace


program = Program(
    name="CivilServant Environment Manager",
    namespace=namespace,
    binary="cs",
    version=__version__
)


def run():
    """Run the CivilServant task invoker."""
    if len(sys.argv) < 2:
        program.print_version()
        sys.argv.append("--list")
    program.run()


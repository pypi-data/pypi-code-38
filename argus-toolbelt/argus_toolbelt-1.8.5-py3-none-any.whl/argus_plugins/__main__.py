from argus_cli.plugin import run

from argus_plugins import argus_cli_module
# Import commands so that they get registered
from argus_plugins import *


def main():
    run(argus_cli_module)


if __name__ == "__main__":
    main()

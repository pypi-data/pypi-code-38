
from systematic.shell import Script

from .commands.info import Info
from .commands.split import Split


def main():
    script = Script()

    script.add_subcommand(Info())
    script.add_subcommand(Split())

    script.run()

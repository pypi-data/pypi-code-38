from qsa.ext.base import BaseExtension


class Extension(BaseExtension):
    name = command_name = 'autodetect'

    def handle(self, assembler, args):
        if not args.subcommand:
            return
        assembler.notify('autodetect')


from systematic.shell import ScriptCommand

from ...subnet import Network


class BaseCommand(ScriptCommand):

    def parse_args(self, args):
        self.networks = []
        if 'subnets' in args:
            try:
                for arg in args.subnets:
                    self.networks.append(Network(arg))
            except Exception as e:
                self.exit(1, 'Error parsing subnets: {}'.format(e))

        return args

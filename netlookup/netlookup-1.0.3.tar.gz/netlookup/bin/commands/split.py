
from .base import BaseCommand


class Split(BaseCommand):

    name = 'split'
    short_description = 'Show split subnet to prefixes'

    def __register_arguments__(self, parser):
        parser.add_argument('-s', '--subnet-prefix', type=int, help='Prefix length for split networks')
        parser.add_argument('subnets', nargs='*', help='Subnets to process')

    def run(self, args):
        if not args.subnets:
            self.exit(1, 'No subnets specified')

        for network in self.networks:
            prefixlen = args.subnet_prefix if args.subnet_prefix is not None else network.next_subnet_prefix
            if prefixlen is not None:
                try:
                    for subnet in network.subnet(prefixlen):
                        self.message(subnet)
                except Exception as e:
                    self.error('Error splitting {}: {}'.format(network, e))
            else:
                self.error('Network is not splittable {}'.format(network))

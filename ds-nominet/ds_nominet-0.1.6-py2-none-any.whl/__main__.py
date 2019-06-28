import argparse
from . import EPPConnection, EPP
from . import TESTBED_HOST, OTE_HOST, HOST

servers = {
        'testbed':TESTBED_HOST,
        'ote': OTE_HOST,
        'live': HOST}
parser = argparse.ArgumentParser(description='Nominet EPP client')
parser.add_argument(
    'cmd',
    choices=['hello', 'domain_delete', 'domain_check', 'domain_create', 'contact_update', 'contact_create'],
    help='EPP Command'
)
parser.add_argument('--host',
    choices=['testbed','ote','live'],
    required=False,
    nargs='?'
)
parser.add_argument(
    '-u', '--user',
    type=str,
    required=True,
)
parser.add_argument(
    '-p', '--password',
    type=str,
    required=True,
)

parser.add_argument(
        '--parameters',
        type=str,
        nargs='*',
        help='string of parameters in format: name:value (e.g. domain:nominet.uk)')
args = parser.parse_args()

if args.parameters:
    parsed_parameters = dict([tuple(param.split(":")) for param in args.parameters])
else:
    parsed_parameters = {}
epp_connection = EPPConnection(servers.get(args.host or 'live'), 700)
epp = EPP(epp_connection)

epp.login(args.user, args.password)

if args.cmd == 'domain_check':
    print(epp.domain_check(user=args.user, **parsed_parameters))

elif args.cmd == 'domain_create':
    print(epp.domain_create(user=args.user, password=args.password, **parsed_parameters))

elif args.cmd == 'domain_delete':
    print(epp.domain_delete(user=args.user, **parsed_parameters))

elif args.cmd == 'contact_create':
    print(epp.contact_create(**parsed_parameters))

elif args.cmd == 'contact_update':
    print(epp.contact_update(**parsed_parameters))

elif args.cmd == 'contact_check':
    print(epp.contact_check(user=args.user))

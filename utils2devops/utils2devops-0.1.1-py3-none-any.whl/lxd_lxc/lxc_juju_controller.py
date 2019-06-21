#!/home/alain/venv/utils2devops/bin/python
from utils2devops.lxd_lxc.base import parser
from utils2devops.lxd_lxc.container import Container


if __name__ == '__main__':
    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument('-status_controller', action='store_true', default=False,
                        help='give the status of all juju lxc controller')
    group2.add_argument('-delete_controller', action='store_true', default=False,
                        help='delete a juju lxc controller')
    group2.add_argument('-start_controller', action='store_true', default=False,
                        help='start a juju lxc controller')
    group2.add_argument('-stop_controller', action='store_true', default=False,
                        help='stop a juju lxc controller')
    group3 = parser.add_argument_group()
    group3.add_argument('-controller_uuid', default='', required=False, help='''
        All container of that controller UUID, get it with -d -statusAll''')

    args = parser.parse_args()
    if args.endpoint:
        object = Container(args.verbose, args.endpoint, args.cert)
    else:
        object = Container(args.verbose)
    if args.status_controller:
        object.status_controller()
    elif args.start_controller:
        object.start_controller(args.controller_uuid)
    elif args.stop_controller:
        object.stop_controller(args.controller_uuid)
    elif args.delete_controller and args.sure == 'YES_I_AM_SURE':
        object.delete_controller(args.controller_uuid)
    else:
        print(parser.format_help())

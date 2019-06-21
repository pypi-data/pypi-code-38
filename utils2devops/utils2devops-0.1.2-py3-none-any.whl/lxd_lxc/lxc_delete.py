#!/home/alain/venv/utils2devops/bin/python
from utils2devops.lxd_lxc.base import parser
from utils2devops.lxd_lxc.image import Image
from utils2devops.lxd_lxc.network import Network
from utils2devops.lxd_lxc.profile import Profile
from utils2devops.lxd_lxc.storage import Storage


if __name__ == '__main__':
    parser.add_argument('-deleteAllImages', action='store_true', default=False, required=False,
                        help='DELETE all lxc image')
    parser.add_argument('-deleteAllNetworks', action='store_true', default=False, required=False,
                        help='DELETE all lxc network')
    parser.add_argument('-deleteAllProfiles', action='store_true', default=False, required=False,
                        help='DELETE all lxc profile')
    parser.add_argument('-deleteAllStorages', action='store_true', default=False, required=False,
                        help='DELETE all lxc storage')
    str_sure = 'YES_I_AM_SURE'
    args = parser.parse_args()
    if args.deleteAllImages and args.sure == str_sure:
        if args.endpoint:
            object = Image(args.endpoint, args.cert)
        else:
            object = Image()
        object.delete_all()
    if args.deleteAllNetworks and args.sure == str_sure:
        if args.endpoint:
            object = Network(args.endpoint, args.cert)
        else:
            object = Network()
        object.delete_all()
    if args.deleteAllProfiles and args.sure == str_sure:
        if args.endpoint:
            object = Profile(args.endpoint, args.cert)
        else:
            object = Profile()
        object.delete_all()
    if args.deleteAllStorages and args.sure == str_sure:
        if args.endpoint:
            object = Storage(args.endpoint, args.cert)
        else:
            object = Storage()
        object.delete_all()
    else:
        print(parser.format_help())

# doc: https://pylxd.readthedocs.io/en/latest/networks.html
from time import sleep

from pylxd.exceptions import NotFound

from utils2devops.lxd_lxc import BaseLXD


class Network(BaseLXD):
    """ missing feature for command line """

    def delete_all(self):
        """
        Delete all network
        :return:
        """
        for obj in self.client.networks.all():
            if obj.used_by:
                print("Network not deleted, it's used by ", obj.used_by)
            elif obj.type != 'bridge':
                print("Network not deleted, it's not a bridge, it's ", obj.type)
            else:
                print('Deleting network: ', obj.name)
                try:
                    obj.delete()
                except NotFound as e:
                    print("got an exception '{}' can't delete it ".format(e))
                sleep(1)
        print('Done')

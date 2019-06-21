# doc: https://pylxd.readthedocs.io/en/latest/storage-pools.html
from time import sleep

from pylxd.exceptions import NotFound

from utils2devops.lxd_lxc import BaseLXD


class Storage(BaseLXD):
    """ missing feature for command line """

    def delete_all(self):
        for obj in self.client.storage_pools.all():
            if obj.used_by:
                print("Storage-pool not deleted, it's used by ", obj.used_by)
            else:
                print('Deleting Storage-pool: ', obj.name)
                try:
                    obj.delete()
                except NotImplementedError as e:
                    print("got an exception '{}' can't delete it ".format(e))
                except NotFound as e:
                    print("got an exception '{}' can't delete it ".format(e))
                sleep(1)
        print('''
        Due to the amount of work to do the real effect could take some minutes
        it better to check time to time with the command:
        lxc storage list
        ''')

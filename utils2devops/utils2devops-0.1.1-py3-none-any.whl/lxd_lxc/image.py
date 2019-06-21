# doc: https://pylxd.readthedocs.io/en/latest/images.html
from time import sleep

from utils2devops.lxd_lxc import BaseLXD


class Image(BaseLXD):
    """ missing feature for command line """

    def delete_all(self):
        for image in self.client.images.all():
            print('Deleting image: ', image.name)
            image.delete()
            sleep(1)
        print('''
        Due to the amount of work to do the real effect could take some minutes
        it better to check time to time with the command:
        lxc image list
        ''')

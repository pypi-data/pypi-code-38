"""
Creates a cloud-config script that can configure a VM on first boot.
This script configures disk partitioning and places a config file for the lando_worker program.

"""

from collections import defaultdict
import yaml

class CloudConfigScript(object):
    """
    Creates a cloud-config script that can partition/format volumes and place lando_worker configuration.
    """

    def __init__(self):
        self._content_dict = defaultdict(list)

    def add_write_file(self, content, path):
        write_file = {'content': content, 'path': path}
        self._content_dict['write_files'].append(write_file)

    def _set_disk_setup(self, device, table_type='gpt', layout=True):
        if not self._content_dict['disk_setup']:
            self._content_dict['disk_setup'] = {}
        disk_setup = {'table_type': table_type, 'layout': layout}

        self._content_dict['disk_setup'][device] = disk_setup

    def _add_fs_setup(self, device, label=None, fs_type='ext3'):
        fs_setup = {'filesystem': fs_type, 'device': device}
        if label:
            fs_setup['label'] = label
        self._content_dict['fs_setup'].append(fs_setup)

    def _add_mount(self, partition_device, mount_point):
        mount = [partition_device, mount_point]
        self._content_dict['mounts'].append(mount)

    def add_volume(self, partition, mount_point):
        """
        Adds the disk_setup, fs_setup, and mount sections to create a single partition on a disk,
        mounted at the provid

        :param partition: The device name of the partition, e.g. /dev/vdb1
        :param mount_point: The
        :return: None
        """
        device = self.device_name(partition)
        self._set_disk_setup(device)
        self._add_fs_setup(partition)
        self._add_mount(partition, mount_point)

    def add_manage_etc_hosts(self, value='localhost'):
        """
        Adds an entry for manage_etc_hosts
        The default is 'localhost', which ensures that the /etc/hosts file has an entry
        resolving the hostname to localhost.
        :param value: true, false, or 'localhost'
        :return: None
        """
        self._content_dict['manage_etc_hosts'] = value

    @staticmethod
    def device_name(partition_name):
        return partition_name.rstrip('1234567890')

    @property
    def content(self):
        return '#cloud-config\n\n{}'.format(yaml.dump(dict(self._content_dict)))


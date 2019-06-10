"""
Allows launching and terminating openstack virtual machines.
"""
import shade
import logging
import uuid


class CloudClient(object):
    """
    Wraps up openstack shade operations.
    """
    def __init__(self, credentials):
        """
        Setup internal client based on credentials in cloud_settings
        :credentials: dictionary of url, username, password, etc
        """
        self.cloud = shade.openstack_cloud(**credentials)

    def launch_instance(self, vm_settings, server_name, job_flavor_name, script_contents, volumes):
        """
        Start VM with the specified settings, name, and script to run on startup.
        :param vm_settings: config.VMSettings: settings for VM we want to create
        :param server_name: str: unique name for this VM
        :param job_flavor_name: str: name of flavor(RAM/CPUs) to use for the VM
        :param script_contents: str: contents of a cloud-init script (bash or #cloud-config)
        :param volumes: [str]: list of volume ids to attach to the VM
        :return: openstack instance created
        """
        instance = self.cloud.create_server(
            name=server_name,
            image=vm_settings.image_name,
            flavor=job_flavor_name,    # The flavor 'Root Disk' value has no effect due to using a volume for storage
            key_name=vm_settings.ssh_key_name,
            network=vm_settings.network_name,
            auto_ip=vm_settings.allocate_floating_ips,
            ip_pool=vm_settings.floating_ip_pool_name,
            userdata=script_contents,
            volumes=volumes)
        return instance

    def create_volume(self, size, name):
        """
        Create a volume with the specified size and name
        :param size: Size, in gigabytes, of the volume to create
        :param name: str: unique name for this volume
        :return: openstack volume created
        """
        volume = self.cloud.create_volume(size, name=name)
        return volume

    def terminate_instance(self, server_name, delete_floating_ip, volume_names):
        """
        Terminate a VM based on name.
        :param server_name: str: name of the VM to terminate
        :param delete_floating_ip: bool: should we try to delete an attached floating ip address
        :param volume_names: [str]: volume names to delete after deleting server
        """
        self.cloud.delete_server(server_name, delete_ips=delete_floating_ip, wait=True)
        for volume in volume_names:
            self.cloud.delete_volume(volume, wait=True)


class CloudService(object):
    """
    Service for creating and terminating virtual machines.
    """
    def __init__(self, config, vm_settings):
        """
        Setup configuration needed to connect to cloud service and
        :param config: Config config settings for vm and credentials
        :param vm_settings: VMSettings object with vm_project_name, image_name, network and IP settings
        """
        self.cloud_client = CloudClient(config.cloud_settings.credentials(vm_settings.vm_project_name))
        self.vm_settings = vm_settings

    def launch_instance(self, server_name, flavor_name, script_contents, volumes):
        """
        Start a new VM with the specified name and script to run on start.
        :param server_name: str: unique name for the server.
        :param flavor_name: str: name of flavor(RAM/CPUs) to use for the VM
        :param script_contents: str: bash script to be run when VM starts.
        :param volumes: [str]: list of volume ids to attach to the VM
        :return: instance, ip address: openstack instance object and the floating ip address assigned
        """
        instance = self.cloud_client.launch_instance(self.vm_settings, server_name, flavor_name, script_contents, volumes)
        return instance, instance.accessIPv4

    def terminate_instance(self, server_name, volume_names=[]):
        """
        Terminate the VM with server_name and deletes attached floating ip address
        :param server_name: str: name of the VM to terminate
        :param volume_names: [str]: list of volume names to delete after termination
        """
        logging.info('terminating instance {}'.format(server_name))
        self.cloud_client.terminate_instance(server_name, delete_floating_ip=self.vm_settings.allocate_floating_ips,
                                             volume_names=volume_names)

    def make_vm_name(self, job_id):
        """
        Create a unique vm name for this job id
        :param job_id: int: unique job id
        :return: str
        """
        return 'vm-job{}_{}'.format(job_id, uuid.uuid4())

    def create_volume(self, size, name):
        """
        Create a volume with the specified name and size
        :param size: int: size of volume in GB we will create for this VM
        :param name: str: unique name for the volume.
        :return: volume, volume id
        """
        volume = self.cloud_client.create_volume(size, name)
        return volume, volume.get('id')

    def make_volume_name(self, job_id):
        """
        Create a unique volume name for this job id
        :param job_id: int: unique job id
        :return: str
        """
        return 'vol-job{}_{}'.format(job_id, uuid.uuid4())


class FakeCloudService(object):
    """
    Fake cloud service so lando/lando_worker can be run locally.
    """
    def __init__(self, config, vm_settings):
        self.vm_settings = vm_settings

    def launch_instance(self, server_name, flavor_name, script_contents, volumes):
        print("Pretend we create vm: {}".format(server_name))
        return None, '127.0.0.1'

    def create_volume(self, size, name):
        print("Pretend to create a {} GB volume: {}".format(size, name))
        return None, 'volume-id'

    def terminate_instance(self, server_name, volume_names):
        print("Pretend we terminate: {}".format(server_name))
        print("Pretend we delete: {}".format(', '.join(volume_names)))

    def make_vm_name(self, job_id):
        return 'local_worker'

    def make_volume_name(self, job_id):
        return 'local_volume'

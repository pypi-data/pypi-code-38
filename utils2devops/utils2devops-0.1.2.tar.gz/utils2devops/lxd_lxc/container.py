# doc: https://pylxd.readthedocs.io/en/latest/containers.html
from time import sleep

from pylxd.exceptions import LXDAPIException

from utils2devops.lxd_lxc import BaseLXD


class Container(BaseLXD):
    """ missing feature for command line """

    @staticmethod
    def is_controller(container):
        if 'user.juju-is-controller' in container.config and\
                container.config['user.juju-is-controller']:
            return True
        return False

    @staticmethod
    def base_line(container):
        to_print = ''
        if Container.is_controller(container):
            to_print += 'Controller, '
        if 'user.juju-machine-id' in container.config:
            to_print += '{}, '.format(
                container.config['user.juju-machine-id']
            )
        if 'user.juju-units-deployed' in container.config:
            to_print += '{}, '.format(
                container.config['user.juju-units-deployed']
            )
        return to_print

    def delete_all(self, controller_uuid: str, model_uuid: str):
        for container in self.client.containers.all():
            if (container.config['user.juju-controller-uuid'] == controller_uuid
                    or container.config['user.juju-model-uuid'] == model_uuid) \
                    and not Container.is_controller(container):
                to_print = Container.base_line(container)
                if container.status == 'Running':
                    print('Stopping container: ', to_print, container.name)
                    container.stop()
                else:
                    print('Container {} already Stopped', container.name)
                sleep(1)
                print('Freezing container: ', to_print, container.name)
                container.freeze()
                sleep(1)
                print('Deleting container: ', to_print, container.name)
                container.delete()
        print('''
        Due to the amount of work to do the real effect could take some minutes
        it better to check time to time with the command:
        lxc list
        ''')

    def status_all(self):
        for container in self.client.containers.all():
            try:
                to_print = self.base_line(container)
                if self.VERBOSE == 1:
                    to_print += 'controller-uuid: {}, '.format(
                        container.config['user.juju-controller-uuid'],
                    )
                if self.VERBOSE == 2:
                    to_print += 'model-uuid: {}, '.format(
                        container.config['user.juju-model-uuid']
                    )
                to_print += 'name: {0: <10}, status: {1:15}'.format(
                    container.name, container.status)
                print(to_print)

            except AttributeError or LXDAPIException:
                print('{0: <25}:{1:25}'.format("container", 'Starting'))

    def start_all(self, controller_uuid: str, model_uuid: str):
        for container in self.client.containers.all():
            if (container.config['user.juju-controller-uuid'] == controller_uuid
                    or container.config['user.juju-model-uuid'] == model_uuid) \
                    and not Container.is_controller(container):
                if container.status != 'Running':
                    to_print = Container.base_line(container)
                    print('Starting container: ', to_print, container.name)
                    container.start()
                else:
                    print('"Container {} already Running', container.name)

    def stop_all(self, controller_uuid: str, model_uuid: str):
        for container in self.client.containers.all():
            if (container.config['user.juju-controller-uuid'] == controller_uuid
                    or container.config['user.juju-model-uuid'] == model_uuid) \
                    and not Container.is_controller(container):
                if container.status == 'Running':
                    to_print = Container.base_line(container)
                    print('Stopping container: ', to_print, container.name)
                    container.stop()
                else:
                    print('Container {} already Stopped', container.name)

    def delete_controller(self, controller_uuid: str):
        raise NotImplemented
        # for container in self.client.containers.all():
        #     if container.config['user.juju-controller-uuid'] == controller_uuid\
        #             and Container.is_controller(container):
        #         to_print = Container.base_line(container)
        #         if container.status == 'Running':
        #             print('Stopping container: ', to_print, container.name)
        #             container.stop()
        #         else:
        #             print('Container {} already Stopped', container.name)
        #         sleep(1)
        #         print('Freezing container: ', to_print, container.name)
        #         container.freeze()
        #         sleep(1)
        #         print('Deleting container: ', to_print, container.name)
        #         container.delete()
        # print('''
        # Due to the amount of work to do the real effect could take some minutes
        # it better to check time to time with the command:
        # lxc list
        # ''')

    def status_controller(self):
        for container in self.client.containers.all():
            if Container.is_controller(container):
                to_print = self.base_line(container)
                if self.VERBOSE:
                    to_print += 'controller-uuid: {}, '.format(
                        container.config['user.juju-controller-uuid'])
                to_print += 'Controller name: {0: <10}, status: {1:15}'.format(
                    container.name, container.status)
                print(to_print)

    def start_controller(self, controller_uuid: str):
        for container in self.client.containers.all():
            if container.config['user.juju-controller-uuid'] == controller_uuid\
                    and Container.is_controller(container):
                if container.status != 'Running':
                    to_print = Container.base_line(container)
                    print('Starting Controller: ', to_print, container.name)
                    container.start()
                else:
                    print('"Controller {} already Running', container.name)

    def stop_controller(self, controller_uuid: str):
        for container in self.client.containers.all():
            if container.config['user.juju-controller-uuid'] == controller_uuid\
                    and Container.is_controller(container):
                if container.status == 'Running':
                    to_print = Container.base_line(container)
                    print('Stopping Controller: ', to_print, container.name)
                    container.stop()
                else:
                    print('Controller {} already Stopped', container.name)


import docker
from docker.errors import APIError

from dvcr.utils import wait
from dvcr.network import DefaultNetwork


class BaseContainer(object):
    def __init__(self, port, image, tag, network=None):
        """ Constructor for Kafka """

        self.port = port

        self._network = network or DefaultNetwork()
        self._client = docker.from_env()

        print("Pulling {image}:{tag}".format(image=image, tag=tag))

        try:
            image = self._client.images.pull(repository=image, tag=tag)
            print("Pulled image " + image.id)
        except APIError as e:
            print("Could not pull image ({})".format(e))
            image = self._client.images.get(name=image + ":" + tag)
            print("Found image locally " + image.id)

        self.post_wait_hooks = []

    def register_post_wait_hook(self, fn, *args, **kwargs):

        self.post_wait_hooks.append((fn, args, kwargs))

    def wait(self):
        wait(target=self._container.name, port=self.port, network=self._network)

        for fn, args, kwargs in self.post_wait_hooks:
            print("executing post wait hook: " + str(fn))
            fn(*args, **kwargs)

        return self

    def delete(self):
        self._container.stop()
        self._container.remove()

    def __getattr__(self, item):
        return getattr(self._container, item)

    def __del__(self):
        self._network.delete()

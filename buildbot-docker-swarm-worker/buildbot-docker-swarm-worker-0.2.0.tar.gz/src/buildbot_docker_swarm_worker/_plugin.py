import secrets
import socket

import docker
from twisted.internet import defer, threads
from twisted.python import log
from buildbot.worker import AbstractLatentWorker


class DockerSwarmLatentWorker(AbstractLatentWorker):
    """
    Latent worker using Docker Swarm to instantiate workers on demand.

    Example:

        >>> from buildbot.plugins import worker
        >>> w = worker.DockerSwarmLatentWorker(
                "worker",
                "buildbot/buildbot-worker",
            )

    Args:
        name (str): Botname this machine will supply when it connects.
        image (str): The image name to use for the containers.

    """

    def __init__(self, name, image):
        password = secrets.token_hex(16)

        super().__init__(name, password, build_wait_timeout=0)

        def get_current_container():
            try:
                with open("/proc/self/cpuset") as f:
                    cid = f.read().strip().split("/")[-1]

                if cid:
                    return self.client.containers.get(cid)
            except (FileNotFoundError, docker.errors.NotFound):
                pass

        def get_container_networks():
            container = get_current_container()
            if container:
                return [
                    network
                    for network in container.attrs["NetworkSettings"]["Networks"]
                    if network != "ingress"
                ]

        def aslist(env):
            return list("=".join(item) for item in env.items())

        self.client = docker.from_env()
        self.service = None
        self.service_config = {
            "image": image,
            "init": True,
            "networks": get_container_networks(),
            "restart_policy": docker.types.RestartPolicy(condition="none"),
            "env": aslist(
                {
                    "BUILDMASTER": socket.gethostname(),
                    "WORKERNAME": name,
                    "WORKERPASS": password,
                }
            ),
        }

    def start_instance(self, build):
        """
        Instantiate a worker for the specified build.

        Creates a thread to start a Docker service.

        Args:
            build (:py:class:`buildbot.process.build.Build`): The
                build to be run on the worker.

        Returns:
            (:py:class:`twisted.internet.defer.Deferred`): A ``Deferred``
                with ``True`` to signal that the instance was started.
        """

        def follow_logs():
            for line in self.service.logs(
                stdout=True, stderr=True, follow=True, timestamps=False
            ):
                log.msg(f"worker {self.service.short_id}: {line}")
                if self.conn:
                    break

        def start():
            self.service = self.client.services.create(**self.service_config)
            follow_logs()
            return True

        if self.service:
            raise ValueError(f"worker already created with ID {self.service.short_id}")

        return threads.deferToThread(start)

    def stop_instance(self, fast=False):
        """
        Shut down the worker instance.

        Returns:
            (:py:class:`twisted.internet.defer.Deferred`)

        Args:
            fast (bool): ignored

        Creates a thread to remove the Docker service.
        """
        if not self.service:
            return defer.succeed(None)

        def stop():
            self.service.remove()
            self.service = None

        return threads.deferToThread(stop)

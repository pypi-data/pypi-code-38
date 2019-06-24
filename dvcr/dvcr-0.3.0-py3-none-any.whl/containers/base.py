import win32pipe
import time
from typing import Optional, Union, List, Callable

import docker
from docker.errors import APIError, DockerException
from docker.utils.socket import frames_iter

from dvcr.utils import wait, init_logger, bright
from dvcr.network import DefaultNetwork, Network

STDOUT = 1
STDERR = 2


class BaseContainer(object):
    def __init__(
        self,
        repo: str,
        tag: str,
        name: str,
        port: Optional[int] = None,
        network: Optional[Network] = None,
    ):

        self._logger = init_logger(name=name)

        self.port = port

        self._network = network or DefaultNetwork()
        self._client = docker.from_env()

        self._logger.info("Pulling %s:%s", bright(repo), tag)

        try:
            image = self._client.images.pull(repository=repo, tag=tag)
            self._logger.info("Pulled image %s:%s (%s)", bright(repo), tag, image.id)
        except APIError:
            self._logger.info("Could not pull %s:%s", bright(repo), tag)
            image = self._client.images.get(name=repo + ":" + tag)
            self._logger.info("Found %s:%s locally (%s)", bright(repo), tag, image.id)

        self.post_wait_hooks = []

    def register_post_wait_hook(self, fn: Callable, *args, **kwargs):

        self.post_wait_hooks.append([fn, args, kwargs])

    def wait(self):
        wait(
            target=self.name, port=self.port, network=self._network, logger=self._logger
        )

        for fn, args, kwargs in self.post_wait_hooks:
            self._logger.info("executing post wait hook: " + str(fn))
            fn(*args, **kwargs)

        return self

    def exec(self, cmd: List[str], path_or_buf: Union[str, bytes, None] = None):

        stdin = None

        if path_or_buf:
            try:
                with open(path_or_buf, "rb") as _file:
                    stdin = _file.read()
            except OSError:
                stdin = path_or_buf
                if isinstance(stdin, str):
                    stdin = stdin.encode("utf8")

        result = self._client.api.exec_create(container=self.id, cmd=cmd, stdin=True)
        exec_id = result["Id"]

        socket = self._client.api.exec_start(exec_id=exec_id, detach=False, socket=True)

        while stdin:
            n_bytes_written = socket.send(string=stdin)

            self._logger.debug("Written %s bytes", n_bytes_written)

            stdin = stdin[n_bytes_written:]

            if not stdin:
                break

        time.sleep(10)
        read_buffer = ""

        for stream, frame in frames_iter(socket=socket, tty=False):

            read_buffer += frame.decode("utf8")

            n_bytes_left = win32pipe.PeekNamedPipe(socket._handle, 4096)[1]

            self._logger.debug("Bytes left to read: %s", n_bytes_left)

            if n_bytes_left <= 0:
                self._logger.debug("No more bytes left to read")

                if read_buffer:
                    self._logger.info(read_buffer.strip("\n"))

                break

            if read_buffer.endswith("\n"):
                self._logger.info(read_buffer.strip("\n"))
                read_buffer = ""

        socket.close()

        exit_code = self._wait_for_cmd_completion(exec_id=exec_id)

        if exit_code != 0:
            raise DockerException("Command exited with code: {}".format(exit_code))

    def _wait_for_cmd_completion(self, exec_id):

        while True:
            result = self._client.api.exec_inspect(exec_id=exec_id)

            time.sleep(0.2)

            if not result["Running"]:
                return result["ExitCode"]

    def delete(self):
        self._container.stop()
        self._container.remove()
        self._logger.info("Deleted %s ♻", bright(self.name))

    def __getattr__(self, item):
        return getattr(self._container, item)

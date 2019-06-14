from typing import Dict, List, Optional

from conctl.base import ContainerRuntimeCtlBase, CompletedProcess


class DockerCtl(ContainerRuntimeCtlBase):
    """
    Control Containerd via `docker`.
    """
    def __init__(self, pipe=True) -> None:
        """
        :param pipe: Boolean pipe std*
        :return: None
        """
        super().__init__(pipe)
        self.runtime = 'docker'

    def _exec(self, *args: List[str]) -> CompletedProcess:
        """
        Run `docker`.

        :param args: List args
        :return: CompletedProcess
        """
        return super()._exec(*['docker'] + list(args))

    def run(self,
            name: str,
            image: str,
            mounts: Dict[str, str] = {},
            environment: Dict[str, str] = {},
            net_host: bool = False,
            privileged: bool = False,
            remove: bool = True,
            command: Optional[str] = None,
            args: List[str] = []) -> str:
        """
        Run a container.

        :param name: String
        :param image: String
        :param mounts: Dictionary String host path String container path
        :param environment:  Dictionary String key String value
        :param net_host: Boolean
        :param privileged: Boolean
        :param remove: Boolean
        :param command: String
        :param args: List String
        :return: String output
        """
        to_run: list = [
            'run',
            '--name', name
        ]

        for host, container in mounts.items():
            to_run.append('--volume')
            to_run.append('{}:{}'.format(host, container))

        for key, value in environment.items():
            to_run.append('--env')
            to_run.append('{}={}'.format(key, value))

        if net_host:
            to_run.append('--network=host')

        if privileged:
            to_run.append('--privileged')

        if remove:
            to_run.append('--rm')

        to_run.append(image)

        if command:
            to_run.append(command)

        if args:
            to_run += args

        return self._exec(*to_run)

    def delete(self, *container_ids) -> CompletedProcess:
        """
        Delete a container.

        :param container_ids: String
        :return: CompletedProcess
        """
        return self._exec(
            'rm', '-f', *container_ids
        )

    def pull(self,
             urls: List[str],
             username: Optional[str] = None,
             password: Optional[str] = None) -> CompletedProcess:
        """
        Pull images.

        :param urls: List String
        :param username: String
        :param password: String
        """
        if isinstance(urls, str):
            urls = [urls]

        for url in urls:
            if username or password:
                self._exec(
                    'login',
                    url,
                    '-u', username,
                    '-p', password
                )

            return self._exec(
                'pull',
                url
            )

    def load(self,
             path: str) -> CompletedProcess:
        """
        Load an image.

        :param path: String file path
        :return: CompletedProcess
        """
        return self._exec(
            'load', '--input', path
        )

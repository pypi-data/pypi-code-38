import asyncio
import logging
import functools

from contextlib import contextmanager, asynccontextmanager
from pathlib import Path

import jinja2

from unv.utils.tasks import Tasks, TasksManager, TaskRunError, register

from .settings import SETTINGS, DeployComponentSettings


def as_root(func):
    """Task will run from root, sets to self.user."""

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        with self._set_user('root'):
            return await func(self, *args, **kwargs)

    return wrapper


def nohost(task):
    task.__nohost__ = True
    return task


def onehost(task):
    task.__onehost__ = True
    return task


class DeployTasks(Tasks):
    def __init__(self, manager, lock, user, host):
        self.user = user
        self.public_ip = host['public_ip']
        self.private_ip = host['private_ip']
        self.port = host['port']

        self._current_prefix = ''
        self._logger = logging.getLogger(self.__class__.__name__)
        self._lock = lock

        super().__init__(manager)

    async def _calc_instances_count(self, count: int = 0, percent: int = 0):
        if percent:
            cpu_cores = int(await self._run('nproc --all'))
            cpu_cores = int(cpu_cores / 100.0 * percent)
            cpu_cores += count
            count = cpu_cores
        return count or 1

    def get_all_deploy_tasks(self):
        for task_class in self._manager.tasks.values():
            if issubclass(task_class, DeployTasks):
                yield task_class(self._manager, self._lock, self.user, {
                    'public_ip': self.public_ip,
                    'private_ip': self.private_ip,
                    'port': self.port
                })

    @contextmanager
    def _set_user(self, user):
        old_user = self.user
        self.user = user
        try:
            yield self
        finally:
            self.user = old_user

    @contextmanager
    def _set_host(self, host):
        old_public_ip, old_private_ip, old_port =\
            self.public_ip, self.private_ip, self.port
        self.public_ip, self.private_ip, self.port =\
            host['public_ip'], host['private_ip'], host['port']
        try:
            yield self
        finally:
            self.public_ip, self.private_ip, self.port =\
                old_public_ip, old_private_ip, old_port

    @contextmanager
    def _prefix(self, command):
        old_prefix = self._current_prefix
        self._current_prefix = f'{self._current_prefix} {command} '
        try:
            yield
        finally:
            self._current_prefix = old_prefix

    @asynccontextmanager
    async def _cd(self, path: Path, temporary=False):
        if temporary:
            await self._mkdir(path, delete=True)
        try:
            with self._prefix(f'cd {path} &&'):
                yield
        finally:
            if temporary:
                await self._rmrf(path)

    @as_root
    async def _sudo(self, command, strip=True):
        """Run command on server as root user."""
        return await self._run(command, strip)

    async def _wait(self, timeout: int):
        await asyncio.sleep(timeout)

    async def _reboot(self, timeout: int = 20):
        try:
            await self._sudo('reboot')
        except TaskRunError:
            pass
        await self._wait(timeout)

    async def _create_user(self):
        """Create user if not exist and sync ssh keys."""
        user = self.user

        with self._set_user('root'):
            try:
                await self._run("id -u {}".format(user))
            except TaskRunError:
                await self._run(
                    "adduser --quiet --disabled-password"
                    " --gecos \"{0}\" {0}".format(user)
                )

                local_ssh_public_key = Path('~/.ssh/id_rsa.pub')
                local_ssh_public_key = local_ssh_public_key.expanduser()
                keys_path = Path(
                    '/', 'home' if user != 'root' else '',
                    user, '.ssh'
                )

                await self._mkdir(keys_path)
                await self._run(f'chown -hR {user} {keys_path}')
                await self._run('echo "{}" >> {}'.format(
                    local_ssh_public_key.read_text().strip(),
                    keys_path / 'authorized_keys'
                ))

    @as_root
    async def _apt_install(self, *packages):
        with self._prefix('DEBIAN_FRONTEND=noninteractive'):
            await self._run('apt-get update -y -q')
            await self._run(
                'apt-get install -y -q --no-install-recommends '
                '--no-install-suggests {}'.format(' '.join(packages))
            )

    async def _run(self, command, strip=True, interactive=False) -> str:
        self._logger.debug(
            f'run [{self.user}@{self.public_ip}:{self.port}] '
            f'{self._current_prefix}{command}'
        )
        interactive_flag = '-t' if interactive else ''
        response = await self._local(
            f"ssh {interactive_flag} -p {self.port} "
            f"{self.user}@{self.public_ip} "
            f"'{self._current_prefix}{command}'",
            interactive=interactive
        ) or ''
        if strip:
            response = response.strip()
        return response

    async def _rmrf(self, path: Path):
        await self._run(f'rm -rf {path}')

    async def _mkdir(self, path: Path, delete=False):
        if delete:
            await self._rmrf(path)
        await self._run(f'mkdir -p {path}')

    async def _upload(self, local_path: Path, path: Path = '~/'):
        await self._local(
            f'scp -r -P {self.port} {local_path} '
            f'{self.user}@{self.public_ip}:{path}'
        )

    async def _rsync(self, local_dir, root_dir, exclude=None):
        exclude = [f"--exclude '{path}'" for path in exclude or []]
        exclude = ' '.join(exclude)
        await self._local(
            f'rsync -rave ssh --delete {exclude} {local_dir}/ '
            f'{self.user}@{self.public_ip}:{root_dir}'
        )

    async def _upload_template(
            self, local_path: Path, path: Path, context: dict = None):
        context = context or {}
        context.setdefault('deploy', self)

        async with self._lock:
            render_path = Path(f'{local_path}.render')
            template = jinja2.Template(
                local_path.read_text(), enable_async=True)
            render_path.write_text(await template.render_async(context))
            try:
                await self._upload(render_path, path)
            finally:
                render_path.unlink()

    async def _download_and_unpack(self, url: str, dest_dir: Path = Path('.')):
        await self._run(f'wget -q {url}')
        archive = url.split('/')[-1]
        await self._run(f'tar xf {archive}')
        archive_dir = archive.split('.tar')[0]

        await self._mkdir(dest_dir)
        await self._run(f'mv {archive_dir}/* {dest_dir}')

        await self._rmrf(archive)
        await self._rmrf(archive_dir)

    @register
    @onehost
    async def ssh(self):
        return await self._run('bash', interactive=True)

    @register
    @onehost
    @as_root
    async def root(self):
        return await self._run('bash', interactive=True)


class DeployComponentTasks(DeployTasks):
    SETTINGS = None

    def __init__(self, manager, lock, user, host, settings=None):
        settings = settings or self.__class__.SETTINGS
        if settings is None or \
                not isinstance(settings, DeployComponentSettings):
            raise ValueError(
                "Provide correct 'SETTINGS' value "
                "shoult be an instance of class 'DeployComponentSettings' not "
                f"[{settings}] value and type {type(settings)}"
            )
        self.settings = settings
        super().__init__(manager, lock, self.settings.user, host)

    @classmethod
    def get_namespace(cls):
        return cls.SETTINGS.NAME


class DeployTasksManager(TasksManager):
    def register_from_settings(self):
        for class_ in SETTINGS.task_classes:
            self.register(class_)

    def run_task(self, task_class, name, args):
        method = getattr(task_class, name)
        is_nohost = getattr(method, '__nohost__', False)
        is_onehost = getattr(method, '__onehost__', False)

        if issubclass(task_class, DeployTasks):
            if is_nohost:
                user = '__nohost__'
                hosts = [
                    ('', {'public_ip': None, 'private_ip': None, 'port': 0})
                ]
            else:
                user, hosts = self._get_user_with_hosts(task_class)

            if is_onehost and len(hosts) > 1:
                hosts_per_index = []
                for index, (host_name, host) in enumerate(hosts, start=1):
                    hosts_per_index.append([host_name, host])
                    print(f" ({index}) - {host_name} [{host['public_ip']}]")
                chosen_index = int(input('Please choose host to run task: '))
                hosts = [hosts_per_index[chosen_index]]

            async def run():
                lock = asyncio.Lock()
                tasks = [
                    getattr(task_class(self, lock, user, host), name)
                    for _, host in hosts
                ]
                await asyncio.gather(*[task(*args) for task in tasks])

            asyncio.run(run())
        else:
            return super().run_task(task_class, name, args)

    def _get_user_with_hosts(self, task_class):
        name = task_class.get_namespace()
        return (
            SETTINGS.get_component_user(name),
            list(SETTINGS.get_hosts(name))
        )

import asyncio

from pathlib import Path

from watchgod import awatch

from ...tasks import DeployComponentTasks, nohost, register, onehost
from ...settings import SETTINGS, DeployComponentSettings

from ..python import PythonTasks, PythonSettings
from ..systemd import SystemdTasksMixin


class AppSettings(DeployComponentSettings):
    NAME = 'app'
    SCHEMA = {
        'bin': {'type': 'string'},
        'instance': {'type': 'integer'},
        'settings': {'type': 'string'},
        'systemd': SystemdTasksMixin.SCHEMA,
        'watch': {
            'type': 'dict',
            'schema': {
                'dirs': {'type': 'list', 'schema': {'type': 'string'}},
                'exclude': {'type': 'list', 'schema': {'type': 'string'}}
            }
        }
    }
    DEFAULT = {
        'bin': 'app',
        'instance': 1,
        'settings': 'secure.prod',
        'systemd': {
            'template': 'app.service',
            'name': 'app_{instance}.service',
            'boot': True,
            'type': 'simple',
            'instances': {'count': 0, 'percent': 0},
            'context': {
                'limit_nofile': 2000,
                'description': "Application description",
            }
        },
        'watch': {
            'dirs': ['./src', './secure'],
            'exclude': ['__pycache__', '*.egg-info']
        }
    }

    @property
    def python(self):
        settings = self._data.get('python', {})
        settings['user'] = self.user
        return PythonSettings(settings)

    @property
    def bin(self):
        return str(self.python.root_abs / 'bin' / self._data['bin'])

    @property
    def module(self):
        return self._data['settings']

    @property
    def instance(self):
        return self._data['instance']

    @property
    def watch_dirs(self):
        return (Path(directory) for directory in self._data['watch']['dirs'])

    @property
    def watch_exclude(self):
        return self._data['watch']['exclude']


class AppTasks(DeployComponentTasks, SystemdTasksMixin):
    SETTINGS = AppSettings()

    def __init__(self, manager, lock, user, host, settings=None):
        super().__init__(manager, lock, user, host, settings)
        self._python = PythonTasks(
            manager, lock, user, host, self.settings.python)

    @register
    @nohost
    async def watch(self):
        await asyncio.gather(*[
            self._watch_and_sync_dir(directory)
            for directory in self.settings.watch_dirs
        ])

    async def _watch_and_sync_dir(self, directory):
        site_packages_abs = self.settings.python.site_packages_abs
        async for _ in awatch(directory):
            for _, host in SETTINGS.get_hosts(self.NAMESPACE):
                with self._set_user(self.settings.user), \
                        self._set_host(host):
                    for sub_dir in directory.iterdir():
                        if not sub_dir.is_dir():
                            continue
                        await self._rsync(
                            sub_dir, site_packages_abs / sub_dir.name,
                            self.settings.watch_exclude
                        )
                    await self.restart()

    @register
    async def build(self):
        await self._create_user()
        await self._python.build()

    @register
    @onehost
    async def shell(self):
        return await self._python.shell(
            prefix=f'SETTINGS={self.settings.module}')

    @register
    async def sync(self, type_=''):
        flag = '-I' if type_ == 'force' else '-U'
        name = (await self._local('python setup.py --name')).strip()
        version = (await self._local('python setup.py --version')).strip()
        package = f'{name}-{version}.tar.gz'

        async with self._lock:
            await self._local('pip install -e .')
            await self._local('python setup.py sdist bdist_wheel')
            await self._upload(Path('dist', package))
            await self._local('rm -rf ./build ./dist')

        await self._python.pip(f'install {flag} {package}')
        await self._rmrf(Path(package))
        await self._rsync(Path('secure'), Path('secure'))
        await self._sync_systemd_units()

    @register
    async def setup(self):
        await self.build()
        await self.sync()
        await self.start()

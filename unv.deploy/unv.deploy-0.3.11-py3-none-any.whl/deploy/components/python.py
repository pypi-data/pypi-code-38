from ..tasks import DeployComponentTasks
from ..settings import DeployComponentSettings


class PythonSettings(DeployComponentSettings):
    NAME = 'python'
    SCHEMA = {
        'root': {'type': 'string', 'required': True},
        'version': {'type': 'string', 'required': True},
        'user': {'type': 'string', 'required': True},
        'build': {
            'type': 'dict',
            'schema': {
                'fast': {'type': 'boolean'},
                'path': {'type': 'string'}
            },
            'required': True
        }
    }
    DEFAULT = {
        'user': 'python',
        'root': 'python',
        'version': '3.7.3',
        'build': {
            'fast': True,
            'path': '/tmp/python'
        }
    }

    @property
    def version(self):
        return self._data['version']

    @property
    def fast_build(self):
        return self._data['build']['fast']

    @property
    def build_path(self):
        return self._data['build']['path']

    @property
    def site_packages_abs(self):
        return (
            self.root_abs / 'lib' /
            f'python{self.version[:3]}' / 'site-packages'
        )


class PythonTasks(DeployComponentTasks):
    SETTINGS = PythonSettings()

    async def pip(self, command: str):
        return await self.run(f'pip3 {command}')

    async def run(
            self, command: str, interactive: int = False, prefix: str = ''):
        if prefix:
            prefix = f'{prefix} '
        return await self._run(
            f"{prefix}{self.settings.root_abs / 'bin' / command}",
            interactive=interactive
        )

    async def shell(self, prefix: str = ''):
        return await self.run('python3', interactive=True, prefix=prefix)

    async def build(self):
        version = self.settings.version
        fast_build = self.settings.fast_build
        build_path = self.settings.build_path

        await self._apt_install(
            'make', 'build-essential', 'libssl-dev', 'zlib1g-dev',
            'libbz2-dev', 'libreadline-dev', 'libsqlite3-dev', 'wget', 'curl',
            'llvm', 'libncurses5-dev', 'libncursesw5-dev', 'xz-utils',
            'tk-dev', 'tcl-dev', 'libffi-dev', 'wget'
        )
        await self._mkdir(self.settings.root, delete=True)

        async with self._cd(build_path, temporary=True):
            url = 'https://www.python.org/ftp/' \
                f'python/{version}/Python-{version}.tar.xz'
            await self._download_and_unpack(url)

            await self._run(
                './configure --prefix={0} '
                '--enable-loadable-sqlite-extensions --enable-shared '
                '--with-system-expat --enable-optimizations '
                'LDFLAGS="-L{0}/extlib/lib -Wl,--rpath={0}/lib '
                '-Wl,--rpath={0}/extlib/lib" '
                'CPPFLAGS="-I{0}/extlib/include"'.format(
                    self.settings.root_abs
                )
            )
            await self._run('make -j$(nproc) {}'.format(
                'build_all' if fast_build else 'build'))
            await self._run('make install > /dev/null')

        await self.pip('install wheel')
        await self.pip('install -U pip')
        await self.pip('install -U setuptools')

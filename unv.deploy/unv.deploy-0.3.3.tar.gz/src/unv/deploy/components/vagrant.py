from unv.utils.os import get_homepath
from unv.utils.tasks import register, Tasks

from ..settings import SETTINGS


class VagrantTasks(Tasks):
    NAMESPACE = 'vagrant'

    @register
    async def setup(self):
        await self._local('vagrant destroy -f')
        await self._local('vagrant up')
        await self._update_local_known_hosts()

    async def _update_local_known_hosts(self):
        # FIXME: stopped working properly
        ips = [host['public_ip'] for _, host in SETTINGS.get_hosts()]
        known_hosts = get_homepath() / '.ssh' / 'known_hosts'

        if known_hosts.exists():
            with known_hosts.open('r+') as f:
                hosts = f.readlines()
                f.seek(0)
                for host in hosts:
                    if any(ip in host for ip in ips):
                        continue
                    f.write(host)
                f.truncate()

        for ip in ips:
            await self._local(f'ssh-keyscan {ip} >> {known_hosts}')

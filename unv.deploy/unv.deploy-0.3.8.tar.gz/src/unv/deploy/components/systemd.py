from unv.utils.tasks import register


class SystemdTasksMixin:
    SCHEMA = {
        'type': 'dict',
        'schema': {
            'template': {'type': 'string'},
            'name': {'type': 'string'},
            'boot': {'type': 'boolean'},
            'type': {'type': 'string'},
            'local': {'type': 'boolean'},
            'config': {
                'type': 'list',
                'schema': {
                    'type': 'string'
                }
            },
            'instances': {
                'type': 'dict',
                'schema': {
                    'count': {'type': 'integer'},
                    'percent': {'type': 'integer'}
                }
            },
            'context': {
                'type': 'dict',
                'schema': {
                    'limit_nofile': {'type': 'integer'},
                    'description': {'type': 'string'}
                }
            }
        }
    }

    async def _get_systemd_services(self):
        systemd = self.settings.systemd
        name = systemd['name']
        count = await self._calc_instances_count(**systemd['instances'])
        for instance in range(1, count + 1):
            service = systemd.copy()
            service['name'] = name.format(instance=instance)
            service['instance'] = instance
            yield service

    async def _sync_systemd_units(self):
        services = [service async for service in self._get_systemd_services()]
        user = self.user if self.settings.systemd_local else 'root'

        for service in services:
            service_path = self.settings.systemd_dir / service['name']
            if self.settings.systemd_local:
                await self._mkdir(self.settings.systemd_dir)

            context = {'instance': service['instance']}.copy()
            context.update(service.get('context', {}))
            path = service['template']
            if not str(path).startswith('/'):
                path = (self.settings.local_root / service['template'])
                path = path.resolve()

            with self._set_user(user):
                await self._upload_template(path, service_path, context)

        with self._set_user(user):
            user_flag = '--user ' if self.settings.systemd_local else ''
            await self._run(f'systemctl {user_flag}daemon-reload')
            await self._systemctl('enable', boot_only=True)

    async def _systemctl(
            self, command: str, display=False, boot_only=False):
        results = []
        async for service in self._get_systemd_services():
            if 'manage' in service and not service['manage']:
                continue
            if boot_only and not service.get('boot', False):
                continue

            user_flag = '--user ' if self.settings.systemd_local else ''
            user = self.user if user_flag else 'root'

            with self._set_user(user):
                result = await self._run(
                    f'systemctl {user_flag}{command} {service["name"]}')
            results.append(result)
        return results

    @register
    async def start(self):
        await self._systemctl('start')

    @register
    async def stop(self):
        await self._systemctl('stop')

    @register
    async def restart(self):
        await self._systemctl('restart')

    @register
    async def status(self):
        results = await self._systemctl('status')
        for result in results:
            print(result)

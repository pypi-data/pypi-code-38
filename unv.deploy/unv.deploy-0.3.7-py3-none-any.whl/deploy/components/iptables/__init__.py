import jinja2

from pathlib import Path

from ...tasks import DeployComponentTasks, register
from ...settings import SETTINGS, DeployComponentSettings

from ..systemd import SystemdTasksMixin


class IPtablesSettings(DeployComponentSettings):
    NAME = 'iptables'
    SCHEMA = {
        'bin': {'type': 'string', 'required': True},
        'user': {'type': 'string', 'required': True},
        'rules': {
            'type': 'dict',
            'schema': {
                'template': {'type': 'string', 'required': True},
                'name': {'type': 'string', 'required': True}
            }
        },
        'systemd': SystemdTasksMixin.SCHEMA
    }
    DEFAULT = {
        'bin': '/sbin/iptables-restore',
        'user': 'root',
        'rules': {
            'template': 'ipv4.rules',
            'name': 'ipv4.rules'
        },
        'systemd': {
            'template': 'app.service',
            'name': 'iptables.service',
            'boot': True,
            'instances': {'count': 1}
        }
    }

    @property
    def rules_template(self):
        return self.local_root / self._data['rules']['template']

    @property
    def rules(self):
        return Path('/etc') / self._data['rules']['name']

    @property
    def bin(self):
        return f"{self._data['bin']} {self.rules}"


class IPtablesTasks(DeployComponentTasks, SystemdTasksMixin):
    SETTINGS = IPtablesSettings()

    @register
    async def sync(self):
        context = {
            'get_hosts': SETTINGS.get_hosts,
            'components': SETTINGS.get_components(self.public_ip)
        }
        rendered = []
        for task in self.get_all_deploy_tasks():
            get_template = getattr(task, 'get_iptables_template', None)
            if get_template is not None:
                template = jinja2.Template(
                    await get_template(), enable_async=True)
                context['deploy'] = task
                context['iptables_deploy'] = self
                rendered.append(await template.render_async(context))
                context.pop('deploy')
        context['components_templates'] = "\n".join([
            line.strip() for line in rendered
        ])

        await self._upload_template(
            self.settings.rules_template, self.settings.rules, context)
        await self._sync_systemd_units()

    @register
    async def setup(self):
        await self.sync()
        await self.start()

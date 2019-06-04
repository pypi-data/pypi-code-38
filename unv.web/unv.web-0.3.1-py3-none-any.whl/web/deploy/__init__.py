from pathlib import Path

from unv.deploy.components.app import AppComponentTasks, AppComponentSettings
from unv.deploy.settings import SETTINGS as DEPLOY_SETTINGS


class WebAppComponentSettings(AppComponentSettings):
    DEFAULT = {
        'bin': 'app',
        'settings': 'secure.production',
        'instance': 1,
        'host': '0.0.0.0',
        'port': 8000,
        'domain': 'app.local',
        'use_https': True,
        'ssl_certificate': 'secure/certs/fullchain.pem',
        'ssl_certificate_key': 'secure/certs/privkey.pem',
        'watch': {
            'dir': './src',
            'exclude': ['__pycache__', '*.egg-info']
        },
        'nginx': {
            'template': 'nginx.conf',
            'name': 'web.conf'
        },
        'iptables': {
            'v4': 'ipv4.rules'
        },
        'systemd': {
            'template': 'app.service',
            'name': 'app_{instance}.service',
            'boot': True,
            'instances': {'count': 1}
        },
        'static': {
            'public': {
                'url': '/static/public',
                'dir': 'static/public'
            },
            'private': {
                'url': '/static/private',
                'dir': 'static/private'
            }
        }
    }

    @property
    def ssl_certificate(self):
        return self.home_abs / self._data['ssl_certificate']

    @property
    def ssl_certificate_key(self):
        return self.home_abs / self._data['ssl_certificate_key']

    @property
    def host(self):
        return self._data['host']

    @property
    def port(self):
        return self._data['port']

    @property
    def nginx_config(self):
        nginx = self._data['nginx']
        template, path = nginx['template'], nginx['name']
        if not template.startswith('/'):
            template = (self.local_root / template).resolve()
        return Path(template), path

    @property
    def domain(self):
        return self._data['domain']

    @property
    def static_public_dir(self):
        return self.home_abs / Path(self._data['static']['public']['dir'])

    @property
    def static_private_dir(self):
        return self.home_abs / Path(self._data['static']['private']['dir'])

    @property
    def static_public_url(self):
        return self._data['static']['public']['url']

    @property
    def static_private_url(self):
        return self._data['static']['private']['url']

    @property
    def use_https(self):
        return self._data['use_https']

    @property
    def iptables_v4_rules(self):
        return (self.local_root / self._data['iptables']['v4']).read_text()


SETTINGS = WebAppComponentSettings()


class WebAppComponentTasks(AppComponentTasks):
    SETTINGS = SETTINGS

    async def get_iptables_template(self):
        return self.settings.iptables_v4_rules

    async def get_nginx_include_configs(self):
        return [self.settings.nginx_config]

    async def get_upstream_servers(self):
        for _, host in DEPLOY_SETTINGS.get_hosts(self.settings.NAME):
            with self._set_host(host):
                settings = self.settings.systemd['instances']
                count = await self._calc_instances_count(**settings)
            for instance in range(1, count + 1):
                yield f"{host['private_ip']}:{self.settings.port + instance}"

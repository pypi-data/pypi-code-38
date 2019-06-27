# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_nginx import settings
from polyaxon_nginx.schemas.base import get_config

OPTIONS = """
location ~ /{plugin_name}/proxy/([-_.:\w]+)/(.*) {{
    {resolver}
    rewrite_log on;
    rewrite ^/{plugin_name}/proxy/([-_.:\w]+)/(.*) /{plugin_name}/proxy/$1/$2 break;
    proxy_pass http://$1:{port};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}}
"""  # noqa


def get_dns_config(dns_prefix=None, dns_backend=None, dns_cluster=None):
    dns_prefix = dns_prefix or settings.DNS_PREFIX
    dns_backend = dns_backend or settings.DNS_BACKEND
    dns_cluster = dns_cluster or settings.DNS_CUSTOM_CLUSTER
    if not dns_prefix:
        dns_prefix = '{}.kube-system'.format(dns_backend)
    return '{dns_prefix}.svc.{dns_cluster}'.format(dns_prefix=dns_prefix, dns_cluster=dns_cluster)


def get_resolver():
    if settings.DNS_USE_RESOLVER:
        dns_config = get_dns_config()
        return 'resolver {} valid=5s;'.format(dns_config)
    return ''


def get_plugin_location_config(name, port):
    resolver = get_resolver()
    return get_config(options=OPTIONS,
                      indent=0,
                      plugin_name=name,
                      port=port,
                      resolver=resolver)


def get_plugins_location_config():
    plugins = []

    if settings.NGINX_PLUGINS:
        for plugin, config in settings.NGINX_PLUGINS.items():
            plugins.append(get_plugin_location_config(name=plugin, port=config['port']))

    return plugins

# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from unittest import TestCase

from polyaxon_nginx import settings
from polyaxon_nginx.schemas.listen import get_listen_config
from polyaxon_nginx.schemas.locations import get_locations_config
from polyaxon_nginx.schemas.logging import get_logging_config
from polyaxon_nginx.schemas.plugins import get_dns_config, get_plugins_location_config
from polyaxon_nginx.schemas.redirect import get_redirect_config
from polyaxon_nginx.schemas.ssl import get_ssl_config
from polyaxon_nginx.schemas.timeout import get_timeout_config
from polyaxon_nginx.schemas.ws import get_ws_location_config


class TestSchemas(TestCase):

    def test_timeout(self):
        expected = """
send_timeout 200;
keepalive_timeout 200;
uwsgi_read_timeout 200;
uwsgi_send_timeout 200;
client_header_timeout 200;
proxy_read_timeout 200;
"""
        settings.TIMEOUT = 200
        assert get_timeout_config() == expected

    def test_listen(self):
        expected = """
listen 80;
"""
        settings.SSL_ENABLED = False
        assert get_listen_config() == expected

        expected = """
listen 443 ssl;
ssl on;
"""
        settings.SSL_ENABLED = True
        assert get_listen_config() == expected

    def test_ssl(self):
        expected = """
# SSL
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# modern configuration
ssl_protocols TLSv1.2;
ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256;
ssl_prefer_server_ciphers on;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 1.1.1.1 1.0.0.1 8.8.8.8 8.8.4.4 208.67.222.222 208.67.220.220 valid=60s;
resolver_timeout 2s;

ssl_certificate      /etc/ssl/polyaxon.com.crt;
ssl_certificate_key  /etc/ssl/polyaxon.com.key;
"""  # noqa
        assert get_ssl_config() == expected

        expected = """
# SSL
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# modern configuration
ssl_protocols TLSv1.2;
ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256;
ssl_prefer_server_ciphers on;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 1.1.1.1 1.0.0.1 8.8.8.8 8.8.4.4 208.67.222.222 208.67.220.220 valid=60s;
resolver_timeout 2s;

ssl_certificate      /foo/polyaxon.com.crt;
ssl_certificate_key  /foo/polyaxon.com.key;
"""  # noqa
        settings.SSL_PATH = '/foo'
        assert get_ssl_config() == expected

    def test_redirect_config(self):
        expected = """
server {
    listen 80;
    return 301 https://$host$request_uri;
}
"""
        settings.SSL_ENABLED = False
        assert get_redirect_config() == ''
        settings.SSL_ENABLED = True
        assert get_redirect_config() == expected

    def test_logging(self):
        expected = """
error_log /polyaxon/logs/error.log warn;
"""
        settings.LOGGING_LEVEL = 'warn'
        assert get_logging_config() == expected

    def test_locations(self):
        expected = """
location /static/ {
    alias /polyaxon/static/;
    autoindex on;
    expires                   30d;
    add_header                Cache-Control private;
}


location /tmp/ {
    alias                     /tmp/;
    expires                   0;
    add_header                Cache-Control private;
    internal;
}


location /repos/ {
    root                      /repos;
    expires                   0;
    add_header                Cache-Control private;
    internal;
}


location /data/ {
    root                      /data;
    expires                   0;
    add_header                Cache-Control private;
    internal;
}


location /outputs/ {
    root                      /outputs;
    expires                   0;
    add_header                Cache-Control private;
    internal;
}
"""
        assert get_locations_config() == expected

    def test_no_plugins(self):
        assert get_plugins_location_config() == []

    def test_plugins(self):
        settings.NGINX_PLUGINS = {'tensorboard': {'port': 6006}, 'notebook': {'port': 8888}}
        assert len(get_plugins_location_config()) == 2

    def test_plugins_dns_resolver(self):
        expected = """
location ~ /tensorboard/proxy/([-_.:\w]+)/(.*) {
    
    rewrite_log on;
    rewrite ^/tensorboard/proxy/([-_.:\w]+)/(.*) /tensorboard/proxy/$1/$2 break;
    proxy_pass http://$1:6006;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}


location ~ /notebook/proxy/([-_.:\w]+)/(.*) {
    
    rewrite_log on;
    rewrite ^/notebook/proxy/([-_.:\w]+)/(.*) /notebook/proxy/$1/$2 break;
    proxy_pass http://$1:8888;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}
"""  # noqa
        settings.DNS_USE_RESOLVER = False
        assert '\n'.join(get_plugins_location_config()) == expected

        expected = """
location ~ /tensorboard/proxy/([-_.:\w]+)/(.*) {
    resolver kube-dns.kube-system.svc.new-dns valid=5s;
    rewrite_log on;
    rewrite ^/tensorboard/proxy/([-_.:\w]+)/(.*) /tensorboard/proxy/$1/$2 break;
    proxy_pass http://$1:6006;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}


location ~ /notebook/proxy/([-_.:\w]+)/(.*) {
    resolver kube-dns.kube-system.svc.new-dns valid=5s;
    rewrite_log on;
    rewrite ^/notebook/proxy/([-_.:\w]+)/(.*) /notebook/proxy/$1/$2 break;
    proxy_pass http://$1:8888;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}
"""  # noqa
        settings.DNS_PREFIX = 'kube-dns.kube-system'
        settings.DNS_USE_RESOLVER = True
        settings.DNS_CUSTOM_CLUSTER = 'new-dns'
        assert '\n'.join(get_plugins_location_config()) == expected

    def test_plugins_dns_backend(self):
        settings.DNS_USE_RESOLVER = True
        expected = """
location ~ /tensorboard/proxy/([-_.:\w]+)/(.*) {
    resolver kube-dns.kube-system.svc.cluster.local valid=5s;
    rewrite_log on;
    rewrite ^/tensorboard/proxy/([-_.:\w]+)/(.*) /tensorboard/proxy/$1/$2 break;
    proxy_pass http://$1:6006;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}


location ~ /notebook/proxy/([-_.:\w]+)/(.*) {
    resolver kube-dns.kube-system.svc.cluster.local valid=5s;
    rewrite_log on;
    rewrite ^/notebook/proxy/([-_.:\w]+)/(.*) /notebook/proxy/$1/$2 break;
    proxy_pass http://$1:8888;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}
"""  # noqa
        settings.DNS_CUSTOM_CLUSTER = 'cluster.local'
        assert get_dns_config() == 'kube-dns.kube-system.svc.cluster.local'
        assert '\n'.join(get_plugins_location_config()) == expected

        expected = """
location ~ /tensorboard/proxy/([-_.:\w]+)/(.*) {
    resolver kube-dns.kube-system.svc.new-dns valid=5s;
    rewrite_log on;
    rewrite ^/tensorboard/proxy/([-_.:\w]+)/(.*) /tensorboard/proxy/$1/$2 break;
    proxy_pass http://$1:6006;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}


location ~ /notebook/proxy/([-_.:\w]+)/(.*) {
    resolver kube-dns.kube-system.svc.new-dns valid=5s;
    rewrite_log on;
    rewrite ^/notebook/proxy/([-_.:\w]+)/(.*) /notebook/proxy/$1/$2 break;
    proxy_pass http://$1:8888;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}
"""  # noqa
        settings.DNS_CUSTOM_CLUSTER = 'new-dns'
        assert get_dns_config() == 'kube-dns.kube-system.svc.new-dns'
        assert '\n'.join(get_plugins_location_config()) == expected

    def test_plugins_dns_prefix(self):
        settings.DNS_USE_RESOLVER = True
        expected = """
location ~ /tensorboard/proxy/([-_.:\w]+)/(.*) {
    resolver coredns.kube-system.svc.cluster.local valid=5s;
    rewrite_log on;
    rewrite ^/tensorboard/proxy/([-_.:\w]+)/(.*) /tensorboard/proxy/$1/$2 break;
    proxy_pass http://$1:6006;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}


location ~ /notebook/proxy/([-_.:\w]+)/(.*) {
    resolver coredns.kube-system.svc.cluster.local valid=5s;
    rewrite_log on;
    rewrite ^/notebook/proxy/([-_.:\w]+)/(.*) /notebook/proxy/$1/$2 break;
    proxy_pass http://$1:8888;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}
"""  # noqa
        settings.DNS_PREFIX = 'coredns.kube-system'
        settings.DNS_CUSTOM_CLUSTER = 'cluster.local'
        assert get_dns_config() == 'coredns.kube-system.svc.cluster.local'
        assert '\n'.join(get_plugins_location_config()) == expected

        expected = """
location ~ /tensorboard/proxy/([-_.:\w]+)/(.*) {
    resolver kube-dns.new-system.svc.new-dns valid=5s;
    rewrite_log on;
    rewrite ^/tensorboard/proxy/([-_.:\w]+)/(.*) /tensorboard/proxy/$1/$2 break;
    proxy_pass http://$1:6006;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}


location ~ /notebook/proxy/([-_.:\w]+)/(.*) {
    resolver kube-dns.new-system.svc.new-dns valid=5s;
    rewrite_log on;
    rewrite ^/notebook/proxy/([-_.:\w]+)/(.*) /notebook/proxy/$1/$2 break;
    proxy_pass http://$1:8888;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
}
"""  # noqa
        settings.DNS_PREFIX = 'kube-dns.new-system'
        settings.DNS_CUSTOM_CLUSTER = 'new-dns'
        assert get_dns_config() == 'kube-dns.new-system.svc.new-dns'
        assert '\n'.join(get_plugins_location_config()) == expected

    def test_ws_location_config(self):
        # settings.NGINX_PLUGINS = {'tensorboard': {'port': 6006}, 'notebook': {'port': 8888}}
        expected = """
location ~ /ws {
    proxy_pass http://localhost:1337;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
}
"""
        assert get_ws_location_config() == expected

        settings.WS_PORT = 8888
        expected = """
location ~ /ws {
    proxy_pass http://localhost:8888;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Origin "";
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
}
"""
        assert get_ws_location_config() == expected

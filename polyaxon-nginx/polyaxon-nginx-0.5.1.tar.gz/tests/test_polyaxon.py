# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from unittest import TestCase

from polyaxon_nginx.schemas.polyaxon import get_polyaxon_config


class TestPolyaxonSchemas(TestCase):

    def test_polyaxon_config(self):
        expected = """
listen 80;


error_log /polyaxon/logs/error.log warn;


gzip                        on;
gzip_disable                "msie6";
gzip_types                  *;


charset utf-8;


client_max_body_size        4G;
client_body_buffer_size     50m;
client_body_in_file_only clean;
sendfile on;


send_timeout 600;
keepalive_timeout 600;
uwsgi_read_timeout 600;
uwsgi_send_timeout 600;
client_header_timeout 600;
proxy_read_timeout 600;


location / {
    include     /etc/nginx/uwsgi_params;
    uwsgi_pass  polyaxon;
    uwsgi_param Host				$host;
    uwsgi_param X-Real-IP			$remote_addr;
    uwsgi_param X-Forwarded-For		$proxy_add_x_forwarded_for;
    uwsgi_param X-Forwarded-Proto	$http_x_forwarded_proto;
}


error_page 500 502 503 504 /50x.html;


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
        assert get_polyaxon_config() == expected

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2019 Snowflake Computing Inc. All right reserved.
#

import os

from .compat import (TO_UNICODE)


def set_proxies(proxy_host, proxy_port, proxy_user=None, proxy_password=None):
    """
    Set proxy dict for requests
    """
    PREFIX_HTTP = 'http://'
    PREFIX_HTTPS = 'https://'
    proxies = None
    if proxy_host and proxy_port:
        if proxy_host.startswith(PREFIX_HTTP):
            proxy_host = proxy_host[len(PREFIX_HTTP):]
        elif proxy_host.startswith(PREFIX_HTTPS):
            proxy_host = proxy_host[len(PREFIX_HTTPS):]
        if proxy_user or proxy_password:
            proxy_auth = u'{proxy_user}:{proxy_password}@'.format(
                proxy_user=proxy_user if proxy_user is not None else '',
                proxy_password=proxy_password if proxy_password is not
                                                 None else ''
            )
        else:
            proxy_auth = u''
        proxies = {
            u'http': u'http://{proxy_auth}{proxy_host}:{proxy_port}'.format(
                proxy_host=proxy_host,
                proxy_port=TO_UNICODE(proxy_port),
                proxy_auth=proxy_auth,
            ),
            u'https': u'http://{proxy_auth}{proxy_host}:{proxy_port}'.format(
                proxy_host=proxy_host,
                proxy_port=TO_UNICODE(proxy_port),
                proxy_auth=proxy_auth,
            ),
        }
        os.environ['HTTP_PROXY'] = proxies[u'http']
        os.environ['HTTPS_PROXY'] = proxies[u'https']
    return proxies

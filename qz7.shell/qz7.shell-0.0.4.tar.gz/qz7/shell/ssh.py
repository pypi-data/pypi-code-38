"""
Functions to connect to server via ssh.
"""

import os
import time
import logging
from contextlib import contextmanager

import paramiko

DEFAULT_RETRIES = 10

log = logging.getLogger(__name__)

def get_ssh_config():
    """
    Load the ssh config file.
    """

    ssh_config = paramiko.SSHConfig()
    config_fname = os.path.expanduser("~/.ssh/config")
    if os.path.exists(config_fname):
        with open(config_fname) as fobj:
            ssh_config.parse(fobj)
    return ssh_config

class ProxyCommand(paramiko.ProxyCommand):
    """
    Better cleanup logic for proxycommand.
    """

    def close(self):
        if self.process.poll() is None:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass

    @property
    def closed(self):
        return self.process.poll() is not None

@contextmanager
def get_connect_config(ssh_config, hostname):
    """
    Get connect config.
    """

    cfg = {}

    user_config = ssh_config.lookup(hostname)
    for k in ('hostname', 'port'):
        if k in user_config:
            cfg[k] = user_config[k]

    if 'user' in user_config:
        cfg['username'] = user_config["user"]

    cfg["timeout"] = 120
    cfg["banner_timeout"] = 120
    cfg["auth_timeout"] = 120

    if 'proxycommand' in user_config:
        cfg['sock'] = ProxyCommand(user_config['proxycommand'])
        try:
            yield cfg
        finally:
            cfg['sock'].close()
    else:
        yield cfg

@contextmanager
def ssh_client_factory():
    client = paramiko.SSHClient()
    try:
        yield client
    finally:
        client.close()

@contextmanager
def make_ssh_client(hostname, retries=None):
    """
    Return a connected ssh client.
    """

    ssh_config = get_ssh_config()
    if retries is None:
        retries = DEFAULT_RETRIES

    last_exc = None
    for try_ in range(retries):
        with get_connect_config(ssh_config, hostname) as connect_config:
            with ssh_client_factory() as client:
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                try:
                    client.connect(**connect_config)
                    yield client
                    return
                except paramiko.ssh_exception.ProxyCommandFailure as exc:
                    log.info("Error connecting to {%s} (try {%d}), retrying ...", hostname, try_)
                    last_exc = exc
                    time.sleep(1)

    if last_exc is not None:
        raise last_exc # pylint: disable=raising-bad-type

@contextmanager
def get_ssh_client(hostname, retries=None):
    """
    Get a ssh client from the thread local cache.
    """

    with make_ssh_client(hostname, retries) as client:
        yield client

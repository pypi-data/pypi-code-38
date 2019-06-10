import socket
import os
import sys

from os import path
from cpbox.tool import template
from cpbox.tool import system

def fg_mode():
    return '-it' if sys.stdout.isatty() else '-i'

def base_docker_args(env=None, container_name=None, volumes=None, ports=None, current_user=False, envs=None, working_dir=None, auto_hostname=True, hostname=None):
    host_hostname_fqdn = socket.gethostname()
    host_hostname_short = host_hostname_fqdn.split('.')[0]
    args = '--name ' + container_name
    if auto_hostname:
        args += ' -h %s.docker.%s' % (container_name, host_hostname_short)
    else:
        if hostname:
            args += ' -h %s' % (hostname)
        else:
            args += ' -h %s' % (host_hostname_short)

    args += ' -e PUPPY_HOSTNAME=' + host_hostname_fqdn
    args += ' -e PUPPY_CONTAINER_NAME=' + container_name
    for key, value in os.environ.items():
        if key.startswith('PUPPY_'):
            args += ' -e %s="%s"' % (key, value)
    if env:
        args += ' -e PUPPY_ENV=' + env

    if working_dir:
        args += ' -w ' + working_dir

    if current_user:
        args += ' -u %s:%s' % (os.getuid(), os.getgid())

    if volumes:
        if isinstance(volumes, dict):
            args += ' ' + ' '.join(('-v ' + from_ + ':' + to_ for from_, to_ in volumes.items()))
        else:
            args += ' ' + ' '.join(('-v ' + item for item in volumes))
    if ports:
        if isinstance(ports, dict):
            args += ' ' + ' '.join(('-p ' + str(from_) + ':' + str(to_) for from_, to_ in ports.items()))
        else:
            args += ' ' + ' '.join(('-p ' + str(item) for item in ports))
    if envs:
        args += ' ' + ' '.join(('-e ' + item for item in envs))

    os_name = system.get_os_name()
    if os_name != 'mac':
        args += ' -v /etc/localtime:/etc/localtime'
    if path.isfile('/etc/devops'):
        args += ' -v /etc/devops/:/etc/devops/:ro'

    return args

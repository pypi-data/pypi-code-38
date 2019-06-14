from __future__ import (absolute_import, division, print_function, unicode_literals)

import click
import paramiko as paramiko

from .klass_print import Print


@click.group(invoke_without_command=True)
@click.option('config', '-c', type=click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True
), default='deploy.yml', required=True, )
def cli_deploy(config):
    """Deploy new Odoo developpement"""
    Print.info('Deploy it')
    # hostname = '192.168.0.50'
    # username = 'debian'
    # port = 22
    # password = 'debian'
    # src = '/cli_etl.py'
    # dst = '/tmp/x.py'
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    # print(" Connecting to %s \n with username=%s... \n" % (hostname, username))
    # t = paramiko.Transport(hostname, port)
    # t.connect(username=username, password=password)
    # stdin, stdout, stderr = client.exec_command('ls')
    # print("Copying file: %s to path: %s" % (src, dst))
    # # sftp = paramiko.SFTPClient.from_transport(t)
    # # sftp.put(src, dst)
    # time.sleep(0.1)  # some enviroment maybe need this.
    # stdin.write('root_password_goes_here\n')
    #
    #
    # stdin.flush()
    # print(stdout.readlines())
    # sftp.close()
    # t.close()

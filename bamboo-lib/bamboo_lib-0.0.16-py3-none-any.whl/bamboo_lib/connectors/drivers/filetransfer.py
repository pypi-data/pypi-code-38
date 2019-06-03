import paramiko
import os

from bamboo_lib.connectors.models import BaseDriver
from bamboo_lib.logger import logger


class FileTransferDriver(BaseDriver):
    TYPE = 'SCP Secure File Copy Driver'

    def __init__(self, **kwargs):
        self.key_filename = None
        self.port = 22
        self.password = None
        super(FileTransferDriver, self).__init__(**kwargs)
        if self.key_filename:
            self.key_filename = self.expand(self.key_filename)

    @staticmethod
    def expand(fpath):
        return os.path.expanduser(os.path.expandvars(fpath))

    def create_connection(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.server, self.port, self.user, self.password, key_filename=self.key_filename)
        return client

    def send_file(self, local_file, remote_file, params=None, use_fo=False):
        logger.info("Starting copy...")
        ssh_client = self.create_connection()
        sftp_client = ssh_client.open_sftp()
        if use_fo and isinstance(local_file, str):
            logger.warn("!WARNING! Trying to send remote file object but string provided")
        if use_fo:
            sftp_client.putfo(local_file, remote_file, confirm=False)
        else:
            local_file = self.expand(local_file)
            sftp_client.put(local_file, remote_file, confirm=False)
        sftp_client.close()
        logger.info("File transfer complete!")
        return True

    def run_command(self, command, params=None):
        logger.info("Starting copy...")
        ssh_client = self.create_connection()
        (stdin, stdout, stderr) = ssh_client.exec_command(command)
        if stderr:
            logger.error("SSH command stderror: \t{}".format(str(stderr)))
        output = [line.strip() for line in stdout.readlines()]
        return output

    def retrieve_file(self, remote_file, local_file, params=None):
        logger.info("Starting copy...")
        local_file = self.expand(local_file)
        ssh_client = self.create_connection()
        sftp_client = ssh_client.open_sftp()
        sftp_client.get(remote_file, local_file)
        ssh_client.close()
        logger.info("File transfer complete!")
        return local_file


if __name__ == '__main__':
    sd = FileTransferDriver(server="35.227.110.181", user='deploy', key_filename="/Users/jspeiser/.ssh/id_rsa_cdc_deploy")
    sd.send_file("/tmp/test.txt", "this_is_now_on_the_server.txt")

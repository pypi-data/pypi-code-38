# encoding: utf-8

import logging_helper
from scp import SCPClient
from paramiko import SSHClient, AutoAddPolicy
from conversionutil.dx import dx

logging = logging_helper.setup_logging()

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


class SCP(object):

    def __init__(self,
                 host,
                 username,
                 password,
                 port=22):
        self.host = host
        self.username = dx(username)
        self.password = dx(password)
        self.port = port

    def __open(self):
        logging.info('Connecting to {host}:{port}'.format(host=self.host,
                                                          port=self.port))

        logging.info("Connecting as '{user}'".format(user=self.username))

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(hostname=self.host,
                         username=self.username,
                         password=self.password)

        self.scp_session = SCPClient(self.ssh.get_transport())

    def __close(self):
        self.scp_session.close()
        self.ssh.close()

    def __run_command(self,
                      command,
                      **params):
        """
        Single call to 'command'(self, command, **params)
        of SCP client.
        """

        logging.info('scp.{command}({parameters})'.format(command=command,
                                                          parameters=params))
        self.__open()
        method = getattr(self.scp_session, command)
        result = method(**params)
        self.__close()
        return result

    def get(self,
            remotepath,
            localpath):
        """
        Single call to gett(self, remotepath, localpath)
        of SCP client.
        """
        self.__run_command(command='get',
                           remote_path=remotepath,
                           local_path=localpath)

    def put(self,
            localpath,
            remotepath):
        """
        Single call to put(self, localpath, remotepath)
        of SCP client.
        """
        self.__run_command(command='put',
                           files=localpath,
                           remote_path=remotepath)

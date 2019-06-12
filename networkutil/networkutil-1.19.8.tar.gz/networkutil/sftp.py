# encoding: utf-8

try:
    from StringIO import StringIO
except ModuleNotFoundError:
    from io import StringIO
import paramiko
import logging_helper
from conversionutil.dx import dx

logging = logging_helper.setup_logging()


class SFTPHelper(object):
    """
    SFTP_Helper is an abstraction of the the Paramiko
    SFTP client.

    http://www.lag.net/paramiko/docs/paramiko.SFTPClient-class.html

    e.g.
        sftp_client = SingleCommandSFTP(host     = "hostname",
                                        username = "username",
                                        password = "password")

        sftp_client.remove(path = '/mnt/a/b/file.txt')

    It is intended mainly for single operations as the
    connection is opened and closed for each command.
    For multiple commands it will be inefficient.
    """

    def __init__(self,
                 host,
                 username,
                 password=None,
                 host_key=None,
                 private_key=None,
                 port=22,
                 auto_connect=True):

        self.host = host
        self.username = username
        self.password = password
        self.__resolve_host_key(host_key)
        self.__resolve_private_key(private_key)
        self.port = port
        self._transport = None
        self._sftp_client = None
        if auto_connect:
            self.connect()

    def __resolve_private_key(self,
                              private_key):

        self.private_key = private_key  # (Can be None)

        if private_key is None:
            return
        try:
            self.private_key = paramiko.RSAKey.from_private_key(file_obj=StringIO(private_key))
            return
        except (IOError, paramiko.ssh_exception.SSHException):
            pass

        try:
            self.private_key = paramiko.RSAKey.from_private_key_file(filename=private_key)
            return
        except IOError:
            pass

        logging.warning(u'Could not create RSAKey from "{pk}"'
                        .format(pk=private_key))

    def __resolve_host_key(self,
                           host_key):
        if host_key:
            raise NotImplementedError(
                      u'__resolve_host_key host key '
                      u'not implemented yet.\n See '
                      u'http://www.programcreek.com/'
                      u'python/example/7445/paramiko.Transport\n'
                      u'for some ideas on how to do that!')
        else:
            self.host_key = host_key

    def connect(self):
        logging.info(u'Connecting to {host}:{port}'
                     .format(host=self.host,
                             port=self.port))

        self._transport = paramiko.Transport((self.host,
                                              self.port))

        logging.info(u"Connecting as '{user}'"
                     .format(user=self.username))

        self._transport.connect(hostkey=self.host_key,
                                username=self.username,
                                password=(dx(self.password)
                                          if self.password
                                          else self.password),
                                pkey=self.private_key)

        self._sftp_client = paramiko.SFTPClient.from_transport(self._transport)

    def disconnect(self):
        self._sftp_client.close()
        self._transport.close()

    def _run_command(self,
                     command,
                     **params):
        """
        Single call to 'command'(self, command, **params)
        of Paramiko SFTP client.
        """

        logging.debug(u'sftp_client.{command}({parameters})'
                      .format(command=command,
                              parameters=params))
        method = getattr(self._sftp_client, command)
        result = method(**params)
        return result

    def rename(self,
               oldpath,
               newpath):
        """
        Single call to rename(self, oldpath, newpath)
        of Paramiko SFTP client.
        """
        self._run_command(command='rename',
                          oldpath=oldpath,
                          newpath=newpath)

    def chmod(self,
              path,
              mode):
        """
        Single call to rename(self, oldpath, newpath)
        of Paramiko SFTP client.
        """
        self._run_command(command='chmod',
                          path=path,
                          mode=mode)

    def remove(self,
               path):
        """
        Single call to rename(self, oldpath, newpath)
        of Paramiko SFTP client.
        """
        self._run_command(command='remove',
                          path=path)

    def get(self,
            remotepath,
            localpath,
            callback=None):
        """
        Single call to gett(self, remotepath, localpath, callback=None)
        of Paramiko SFTP client.
        """
        self._run_command(command='get',
                          remotepath=remotepath,
                          localpath=localpath,
                          callback=callback)

    def put(self,
            localpath,
            remotepath,
            callback=None,
            confirm=True):
        """
        Single call to put(self, localpath, remotepath, callback=None, confirm=True)
        of Paramiko SFTP client.
        """
        self._run_command(command='put',
                          localpath=localpath,
                          remotepath=remotepath,
                          callback=callback,
                          confirm=confirm)

    def listdir(self,
                path=None):
        """
        Single call to listdir(self, path)
        of Paramiko SFTP client.
        """
        if path is None:
            return self._run_command(command='listdir')
        else:
            return self._run_command(command='listdir',
                                     path=path)

    def listdir_attr(self,
                     path):
        """
        Single call to listdir(self, path)
        of Paramiko SFTP client.
        """
        return self._run_command(command='listdir_attr',
                                 path=path)


class SingleCommandSFTP(SFTPHelper):
    """
    Like SFTPHelper, but does not maintain a connection.
    It makes a connection, runs the command and then disconnects
    """

    def __init__(self,
                 host,
                 username,
                 password=None,
                 host_key=None,
                 private_key=None,
                 port=22, ):
        super(SingleCommandSFTP, self).__init__(host=host,
                                                username=username,
                                                password=password,
                                                host_key=host_key,
                                                private_key=private_key,
                                                port=port,
                                                auto_connect=False)

    def _run_command(self,
                     command,
                     **params):
        """
        Connects, runs command and then disconnects.
        """

        logging.info(u'sftp_client.{command}({parameters})'
                     .format(command=command,
                             parameters=params))
        self.connect()
        method = getattr(self.sftp_client, command)
        result = method(**params)
        self.disconnect()
        return result


if __name__ == u"__main__":
    server = SFTPHelper(host=u'',
                        username=u'',
                        private_key=u'')

    print(server.listdir(u'./'))

    server.disconnect()

# encoding: utf-8

import logging_helper
from multiprocessing.pool import ThreadPool
from pyftpdlib.authorizers import DummyAuthorizer as _DummyAuthorizer
from pyftpdlib.handlers import FTPHandler as _FTPHandler
from pyftpdlib.servers import FTPServer as _FTPServer

logging = logging_helper.setup_logging()

READ_ONLY = 'elr'
WRITE_ONLY = 'adfmwM'
READ_WRITE = READ_ONLY + WRITE_ONLY


class FTPServer(object):

    def __init__(self,
                 interface='0.0.0.0',  # 0.0.0.0 must be used rather than empty string otherwise windows breaks
                 port=2121):

        self.interface = interface
        self.port = port
        self.address = (interface, port)

        self.pool = ThreadPool(processes=2)

        self.__stop = True  # Set termination flag

        self.authoriser = _DummyAuthorizer()
        self.handler = _FTPHandler
        self.handler.authorizer = self.authoriser

        self._conn_ref = None
        self.server = None

    def start(self):

        logging.info(u'Starting FTP Server on {int}:{port}...'.format(int=self.interface,
                                                                      port=self.port))

        # Run initialisation steps here
        self.__stop = False

        try:
            self.server = _FTPServer(self.address, self.handler)

            # Set default banner
            self.set_banner('pyftpdlib based ftpd server.')

            # Set number of connections (Default to only one host connection)
            self.set_max_connections(2)
            self.set_max_connections_per_ip(2)

        except Exception as err:
            logging.exception(err)
            logging.error(u'FTP Server failed to start ({destination}:{port})'.format(destination=self.interface,
                                                                                      port=self.port))

            self.__stop = True

        if not self.__stop:
            logging.info(u'FTP Server Started on {int}:{port}!'.format(int=self.interface,
                                                                       port=self.port))

            # Run Main loop
            self.pool.apply_async(func=self.__main_loop)

    def stop(self):

        logging.info(u'Stopping FTP Server, waiting for processes to complete...')

        # Signal loop termination
        self.__stop = True

        # Wait for running processes to complete
        self.pool.close()
        self.pool.join()

        logging.info(u'FTP Server Stopped')

    def __main_loop(self):

        logging.info(u'FTP ({int}): Waiting for lookup requests'.format(int=self.interface))

        while not self.__stop:
            self._conn_ref = self.server.serve_forever(timeout=1, blocking=False)

    @property
    def active(self):
        return not self.__stop

    def add_user(self,
                 username,
                 password,
                 directory,
                 permissions=READ_ONLY):
        logging.debug(u'Adding user: {un}; permissions: "{perm}"; Root folder: {d}'
                      .format(un=username,
                              perm=permissions,
                              d=directory))
        self.authoriser.add_user(username, password, directory, perm=permissions)

    def remove_user(self,
                    username):
        if self.authoriser.has_user(username):
            logging.debug(u'Removing user: {un}'.format(un=username))
            self.authoriser.remove_user(username)

    def set_banner(self,
                   message):
        self.handler.banner = message

    def set_max_connections(self,
                            num_conns):

        if self.server is not None:
            # We need at least one control and one data connection
            if num_conns < 2:
                num_conns = 2

            self.server.max_cons = num_conns

        else:
            logging.error(u'Cannot set max connections to {num}.  Server not started yet!'.format(num=num_conns))

    def set_max_connections_per_ip(self,
                                   num_conns):

        if self.server is not None:
            # We need at least one control and one data connection
            if num_conns < 2:
                num_conns = 2

            self.server.max_cons_per_ip = num_conns

        else:
            logging.error(u'Cannot set max connections per ip to {num}.  Server not started yet!'.format(num=num_conns))


if __name__ == u'__main__':
    ftp_dir = '/tmp/'

    srv = FTPServer('0.0.0.0', 2121)
    srv.add_user('testun', 'testpw', ftp_dir, READ_WRITE)
    srv.start()

    try:
        logging.info('READY')
        while True:
            pass

    except KeyboardInterrupt:
        srv.stop()

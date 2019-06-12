import logging
import psycopg2
import socket


class Db(object):
    params = None
    connection = None
    logger = None

    def __init__(self, params):
        self.send_keep_alive_probes = params.pop('send_keep_alive_probes', False)
        self.socket_idle_time = params.pop('socket_idle_time', 120)
        self.params = params
        self._make_connection()

    def _make_connection(self):
        logging.info(self.params)
        try:
            self.connection = psycopg2.connect(**self.params)
            if self.send_keep_alive_probes:
                self.socket_configuration()
        except psycopg2.DatabaseError as e:
            logging.error("Could not connect to the server: %s" % e)
        except psycopg2.Error as e:
            logging.error("Error %s" % e)
        except Exception as e:
            logging.error("Error %s" % e)

    def get_connection(self):
        return self.connection

    def socket_configuration(self):
        try:
            pg_socket = socket.fromfd(self.connection.fileno(),
                                      socket.AF_INET, socket.SOCK_STREAM)
            # Enable sending of keep-alive messages
            pg_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # Time the connection needs to remain idle before start sending
            # keep alive probes
            pg_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, self.socket_idle_time)
            # Time between individual keep alive probes
            pg_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
            # The maximum number of keep alive probes should send before dropping the connection
            pg_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
        except Exception as e:
            logging.error("Failed To Configure Socket")
            logging.error(e)

    '''
    Cursor will be created per crawler
    '''
    def get_cursor(self):
        try:
            cursor = self.connection.cursor()
            return cursor
        except Exception as err:
            logging.warning("Connection seems to have expired, remaking it")
            try:
                self._make_connection()
                cursor = self.connection.cursor()
                return cursor
            except Exception as e:
                logging.warning("Connection could not be made: %s" % e)
                return None

    def close_cursor(self, cursor):
        logging.info("Closing cursor...")
        cursor.close()

    def commit(self):
        self.connection.commit()

    def close_connection(self):
        logging.info("Closing connection...")
        self.connection.close()

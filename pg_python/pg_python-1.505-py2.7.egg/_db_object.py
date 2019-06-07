import logging
import psycopg2


class Db(object):
    params = None
    connection = None
    logger = None

    def __init__(self, params):
        self.params = params
        self._make_connection()

    def _make_connection(self):
        logging.info(self.params)
        try:
            self.connection = psycopg2.connect(**self.params)
        except psycopg2.DatabaseError as e:
            logging.error("Could not connect to the server: %s" % e)
        except psycopg2.Error as e:
            logging.error("Error %s" % e)
        except Exception as e:
            logging.error("Error %s" % e)

    def get_connection(self):
        return self.connection

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

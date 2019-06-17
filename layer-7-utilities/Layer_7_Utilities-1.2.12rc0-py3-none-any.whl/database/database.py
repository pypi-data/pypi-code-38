import psycopg2


class Database(object):
    def __init__(self):
        pass

    def get_conn(self, dbusername=None, dbpassword=None, dbhost='localhost', dbname='TheTraveler'):
        conn = psycopg2.connect(host=dbhost, dbname=dbname, user=dbusername, password=dbpassword)
        return conn


class oAuthDatabase(Database):
    def __init__(self, dbusername, dbpassword, dbhost, dbname):
        super(oAuthDatabase, self).__init__()
        self.oAuth_conn = self.get_conn(dbusername, dbpassword, dbhost, dbname)
        with self.oAuth_conn as conn:
            with conn.cursor() as c:
                c.execute("SET CLIENT_ENCODING TO 'UTF8';")

    def get_accounts(self, id):
        with self.oAuth_conn as conn:
            with conn.cursor('get_accounts') as c:
                c.execute("SELECT app_id, app_secret, username, password FROM oauth_data WHERE agent_of=%s", (id,))
                return c.fetchall()

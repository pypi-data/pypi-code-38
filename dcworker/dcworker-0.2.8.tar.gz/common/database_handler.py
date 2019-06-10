import psycopg2

class DatabaseHandler:
    def __init__(self, dbname, user, host, password, port=5432):
        self.dbname = dbname
        self.user = user
        self.host = host
        self.password = password
        self.port = port
        self.conn = None

    def get_conn(self):
        if self.conn is not None and self.conn.closed == 0:
            return self.conn
        else:
            self.safe_close_conn()
            try:
                print(f"Open new connection to database: {self.dbname}")
                self.conn = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    host=self.host,
                    password=self.password,
                    port=self.port)
            except Exception as e:
                print(f" failed to interaction with database due to exception: {e}")
                return None

            return self.conn

    def safe_close_conn(self):
        if self.conn is not None and self.conn.closed == 0:
            self.conn.close()

        self.conn = None

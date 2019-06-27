class Database:

    def __init__(self, connection):
        self.connection = connection

    def kill(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()

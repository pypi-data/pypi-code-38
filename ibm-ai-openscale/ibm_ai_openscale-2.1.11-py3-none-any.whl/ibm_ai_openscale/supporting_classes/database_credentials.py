class DatabaseCredentials:
    def __init__(self, credentials):
        self.credentials = credentials


class DB2(DatabaseCredentials):
    def __init__(self, credentials):
        DatabaseCredentials.__init__(self, credentials)


class PostgreSQL(DatabaseCredentials):
    def __init__(self, credentials):
        DatabaseCredentials.__init__(self, credentials)
import psycopg2


class VaultPsycopg:
    _vault_wrapper = None
    _database_connection = None

    __username = None
    __password = None

    database_config = {}
    vault_config = {}

    def __init__(self, database_config=None, vault_config=None):
        self.vault_config = vault_config
        self.database_config = database_config
        if vault_config:
            from vault_psycopg2.vault import Vault
            self._vault_wrapper = Vault.instance(**vault_config)

    @property
    def credentials(self):
        _ = self.connection
        return {
            "username": self.__username,
            "password": self.__password
        }

    @property
    def connection(self):
        if self._database_connection:
            try:
                cursor = self._database_connection.cursor()
                cursor.execute('SELECT 1')
                return self._database_connection
            except psycopg2.Error:
                pass

        if self._vault_wrapper and self.database_config.get('role') is not None:
            credentials = self._vault_wrapper.client.read('database/creds/' + self.database_config.get('role'))
            self.__username = credentials['data']['username']
            self.__password = credentials['data']['password']
        else:
            self.__username = self.database_config.get('user')
            self.__password = self.database_config.get('password')

        self._database_connection = psycopg2.connect(
            host=self.database_config.get('host'),
            port=self.database_config.get('port'),
            dbname=self.database_config.get('dbname'),
            user=self.__username,
            password=self.__password,
        )

        return self._database_connection

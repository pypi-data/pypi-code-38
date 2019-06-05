from strongr.secretsdomain.query import ListSecrets, GetSecret

class QueryFactory():
    _list_secrets = None

    def new_list_secrets(self):
        # flyweight pattern
        if self._list_secrets is None:
            self._list_secrets = ListSecrets()

        return self._list_secrets

    def new_get_secret(self, key):
        return GetSecret(key)

from server.db.backends.base.features import BaseDatabaseFeatures


class DummyDatabaseFeatures(BaseDatabaseFeatures):
    supports_transactions = False

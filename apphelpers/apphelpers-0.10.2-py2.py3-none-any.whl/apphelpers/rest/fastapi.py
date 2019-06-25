from apphelpers.db import dbtransaction


def factory(f, db):
    return dbtransaction(db)(f)

# -*- coding: utf-8 -*-


class DBSchemaInitialized(Exception):
    """Raised when a database schema has been initialized and an another
    attempt is being made to initialize it.

    """


__all__ = ('DBSchemaInitialized',)

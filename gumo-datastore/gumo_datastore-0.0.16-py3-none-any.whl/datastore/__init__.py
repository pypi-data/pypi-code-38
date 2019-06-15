from logging import getLogger

from gumo.core import EntityKey
from gumo.core import EntityKeyFactory

from gumo.datastore._configuration import configure
from gumo.datastore.domain.configuration import DatastoreConfiguration

from gumo.datastore.infrastructure.repository import datastore_transaction


__all__ = [
    configure.__name__,

    EntityKey.__name__,
    EntityKeyFactory.__name__,
    DatastoreConfiguration.__name__,

    datastore_transaction.__name__,
]

logger = getLogger('gumo.datastore')

from gumo.core.application.entity_key import KeyIDAllocator
from gumo.datastore.infrastructure.key_id_allocator import DatastoreKeyIDAllocator


def datastore_binder(binder):
    binder.bind(KeyIDAllocator, to=DatastoreKeyIDAllocator)

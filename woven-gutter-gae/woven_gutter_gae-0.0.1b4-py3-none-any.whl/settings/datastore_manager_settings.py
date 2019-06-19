from gutter.client import get_gutter_client

from gutter.storage.datastore_like_dict import DatastoreDict

datastore_dict = DatastoreDict(namespace='gutter_feature_flag', kind='switch')

# GUTTER
manager = get_gutter_client(
    storage=datastore_dict,
    autocreate=True
)

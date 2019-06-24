# check the input here: https://github.com/datalogue/scout/blob/master/src/main/scala/io/datalogue/scout/api/inputs.scala


from typing import Dict, List, Optional, Union
from datalogue.errors import DtlError
from datalogue.utils import _parse_list
from uuid import UUID


class DatastoreCollection:

    def __init__(self,
                 name: str,
                 storeIds: List[str],
                 description: str = None,
                 tags: List[str] = [],
                 datastore_collection_id: Optional[UUID] = None,
                 owner: Optional[Dict] = None,
                 organization: Optional[Dict] = None,
                 categories: Optional[List] = None,
                 access: Optional[Dict] = None,
                 metadata: Optional[Dict] = None,
                 ):
        """
        Builds pointer to a datastore collection.

        :param name: name of the pointer (mandatory)
        :param DatastoreIds: the datastore ids as a list (mandatory
        :param description: description of the datastore_collection (mandatory)
        :param tags: tags for the datastore_collection (mandatory)
        :param datastore_collection_id: exists if the object was defined
        :param owner:
        :param organization:
        :param categories:
        :param access:
        :param metadata:


        """
        self.name = name
        self.storeIds = storeIds
        self.id = datastore_collection_id
        self.description = description
        self.owner = owner
        self.organization = organization
        self.categories = categories
        self.tags = tags
        self.access = access
        self.metadata = metadata
        self._as_payload()

    def __eq__(self, other: 'DatastoreCollection'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = {
            "name": self.name,
            "storeIds": self.storeIds,
            "description": self.description,
            "tags": self.tags
        }

        # toDo unpack proper these values
        if self.id is not None:
            base['id'] = str(self.id)

        if self.owner is not None:
            base["owner"] = self.owner

        if self.organization is not None:
            base["organization"] = self.organization

        if self.categories is not None:
            base["categories"] = self.categories

        if self.access is not None:
            base["access"] = self.access

        if self.metadata is not None:
            base["metadata"] = self.metadata

        return base


def _datastore_collection_from_dict(json: dict) -> Union[DtlError, DatastoreCollection]:
    """Datastore Collection instance from dict."""
    name = json.get("name")
    if name is None:
        return DtlError("'name' for a datastore collection should be defined")

    datastore_collection_id = json.get("id")
    if datastore_collection_id is None:
        return DtlError("'id' for a datastore collection should be defined'")
    datastore_collection_id = UUID(datastore_collection_id)

    tags = json.get("tags")
    if tags is None:
        return DtlError("'tags' for a datastore collection should be defined'")

    #TODO? the `create_datastore_collection` does not return the storeIds

    # Todo?
    # the create function return key "stores"
    if 'stores' in json.keys():
        storeIds = json.get("stores")
    else:
        storeIds = json.get("storeIds")

    description = json.get('description')
    owner = json.get('owner')
    organization = json.get('organization')
    categories = json.get('categories')
    access = json.get('access')
    metadata = json.get('metadata')

    datastore_collection = DatastoreCollection(
                       name,
                       storeIds,
                       description,
                       tags,
                       datastore_collection_id,
                       owner,
                       organization,
                       categories,
                       access,
                       metadata
                    )

    return datastore_collection

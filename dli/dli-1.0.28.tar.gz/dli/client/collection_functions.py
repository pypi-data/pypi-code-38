import logging

from dli.client.exceptions import (
    CatalogueEntityNotFoundException,
    MissingMandatoryArgumentException,
    NoAccountSpecified,
)
from dli.siren import siren_to_entity, siren_to_dict

from dli.client.utils import ensure_count_is_valid, filter_out_unknown_keys, to_camel_cased_dict


logger = logging.getLogger(__name__)


class CollectionFunctions:
    _KNOWN_FIELDS = set(["name", "description", "managerId", "documentation", "keywords"])
    @property
    def __root(self):
        return self.ctx.memoized(
            self.get_root_siren().collections_root,
            "collections_root"
        )

    def create_collection(
        self,
        name,
        description,
        manager_id=None,
        documentation=None,
        keywords=None
    ):
        """
        Submit a request to create a new collection in the Data Catalogue.
        
        A Collection defines a group of packages that share thematic information. 
        For example, data for a specific asset class (i.e. CDS) could be a collection.

        See description for each parameter, and whether they are optional or mandatory.

        :param str name: A descriptive name of the collection. It should be unique across the Data Catalogue.
        :param str description: A short description of the collection.
        :keyword str manager_id: Optional. Defaults to your Data Lake Account if none provided. Account ID for the Data Lake Account representing
                            IHS Markit business unit that is responsible for creating and maintaining metadata for the collection in the Data Catalogue.
        :keyword str documentation: Optional. Documentation about the collection in markdown format.
        :keyword list[str] keywords: Optional. List of user-defined terms that can be used to find this
                         collection through the search interface.

        :returns: a newly created Collection
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                collection = client.create_collection(
                    name="my collection",
                    description="my collection description",
                )
        """

        if not manager_id:
            accounts = self.get_my_accounts()
            if len(accounts) > 1:
                raise NoAccountSpecified(accounts)

            manager_id = accounts[0].id
        
        payload = {
            "name": name,
            "description": description,
            "managerId": manager_id,
            "documentation": documentation,
            "keywords": keywords,           
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return siren_to_entity(self.__root.create_collection(__json=payload))

    def get_collection(self, id=None, name=None):
        """
        Fetches collection details for an existing collection. 

        :param str id: The id of the collection.
        :param str name: The name of the collection.

        :returns: NamedTuple representing a Collection instance
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Look up by collection id
                collection = client.get_collection('my_collection_id') 
                # or
                collection = client.get_collection(id='my_collection_id')

                # Alternatively look up by collection name
                collection = client.get_collection(name='my_collection')
                
        """
        if id:
            return siren_to_entity(self._get_collection(collection_id=id))
        
        if name:
            return siren_to_entity(self._get_collection(name=name))
        
        raise ValueError("Either collection id or name must be specified and must be non-empty in order to look up collection")

    def _get_collection(self, **kwargs):

        collection = self.__root.get_collection(**kwargs)

        if not collection:
            raise CatalogueEntityNotFoundException('Collection', params=kwargs)

        return collection

    def edit_collection(
        self,
        collection_id,
        **kwargs
    ):
        """
        Updates one or more fields in a collection.
        If keyword argument is not specified field keeps its old value.
        Optional enum and text type fields can be unset by passing ``None``.

        :param str collection_id: ID of the collection being edited.

        Keyword arguments:

        :param str name: Optional. A descriptive name of the collection. It should be unique across the Data Catalogue.
        :param str description: Optional. A short description of the collection.
        :param str manager_id: Optional. Account ID for the Data Lake Account representing IHS Markit business unit that is responsible
                            for creating and maintaining metadata for the collection in the Data Catalogue.
        :param str documentation: Optional. Documentation about the collection in markdown format.
        :param list[str] keywords: Optional. List of user-defined terms that can be used to find this
                            collection through the search interface.

        :returns: Updated collection
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                collection = client.edit_collection(
                    collection_id="my-collection-id",
                    description="Updated my collection description",
                )
        """
        if not collection_id:
            raise MissingMandatoryArgumentException('collection_id')

        collection = self._get_collection(collection_id=collection_id)

        fields = filter_out_unknown_keys(to_camel_cased_dict(kwargs), CollectionFunctions._KNOWN_FIELDS)
        collection_as_dict = siren_to_dict(collection)

        # drop the fields from collection dict that are not being edited
        for key in list(collection_as_dict.keys()):
            if key not in CollectionFunctions._KNOWN_FIELDS:
                del collection_as_dict[key]

        collection_as_dict.update(fields)

        result = collection.edit_collection(__json=collection_as_dict)
        return siren_to_entity(result)

    def delete_collection(self, collection_id):
        """
        Deletes an existing collection.

        :param str collection_id: The id of the collection to be deleted.

        :returns: None

        - **Sample**

        .. code-block:: python

                client.delete_collection(collection_id)

        """
        if not collection_id:
            raise MissingMandatoryArgumentException('collection_id')

        collection = self._get_collection(collection_id=collection_id)
        collection.delete_collection(collection_id=collection_id)
            
    def get_packages_for_collection(self, collection_id, count=100):
        """
        Returns a list of all packages grouped under a collection.

        :param str collection_id: The id of the collection.
        :param int count: Optional. Count of packages to be returned. Defaults to 100.

        :returns: List of all packages grouped under the collection.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                collection_id = 'my-collection-id'
                packages = client.get_packages_for_collection(collection_id, count=100)
        """
        if not collection_id:
            raise MissingMandatoryArgumentException('collection_id')
            
        ensure_count_is_valid(count)

        collection = self._get_collection(collection_id=collection_id)

        packages = collection.collection_packages(page_size=count).get_entities(rel="package")
        return [siren_to_entity(p) for p in packages]

"""
Usage
-----
Collection objects repesents a single Rockset collection.
These objects are generally created using a Rockset Client_
object using methods such as::

    from rockset import Client

    # connect to Rockset
    rs = Client(api_key=...)

    # create a new collection
    user_events = rs.Collection.create('user-events')

    # retrieve an existing collection
    users = rs.retrieve('users')

You can add documents to the collection using the ``add_docs()`` method. Each
document in a collection is uniquely identified by its ``_id`` field.

If documents added have ``_id`` fields that match existing documents,
then their contents will be merged. Otherwise, the new documents will be
added to the collection.

You can remove documents from a collection using the ``remove_docs()`` method.

Refer to the Query_ module for documentation and examples on how to query
collections.

Example
-------
::

    from rockset import Client, Q, F

    # connect securely to Rockset
    rs = Client()

    # retrieve the relevant collection
    emails = rs.Collection.retrieve('emails')

    # look for all emails to johndoe that contains the term 'secret'
    johndoe_secret_q = Q('emails').where(
        (F["to"].startswith('johndoe@')) & (F["body"][:] == 'secret')
    )

    # query the collection
    docs = rs.query(query=johndoe_secret_q).results()

.. _Collection.create:

Create a new collection
-----------------------
Creating a collection using the Client_ object is as simple as
calling ``client.Collection.create("my-new-collection")``::

    from rockset import Client
    rs = Client()
    new_collection = rs.Collection.create("my-new-collection")

    # create a collection in a workspace
    event-data-collection = rs.Collection.create("leads",
                                                 workspace="marketing")

    # create a collection and map timestamp field to event-time
    event-data-collection = rs.Collection.create("event-data-collection",
                            event_time_field="timestamp",
                            event_time_format="milliseconds_since_epoch",
                            event_time_default_timezone="UTC")

Creating a collection with a retention duration of 10 days::

    from rockset import Client
    rs = Client()
    new_collection_with_retention = rs.Collection.create("my-event-collection",
                                                    retention_secs=10*24*60*60)

.. _Collection.list:

List all collections
--------------------
List all collections in a workspace using the Client_ object using::

    from rockset import Client
    rs = Client()

    # list all collections in the commons workspace
    collections = rs.list()

    # list all collections in another workspace
    collections = rs.list(workspace='marketing')

.. _Collection.retrieve:

Retrieve an existing collection
-------------------------------
Retrive a collection to run various operations on that collection
such as adding or removing documents or executing queries::

    from rockset import Client
    rs = Client()
    users = rs.retrieve('users')

    # retrieve a collection in a workspace
    users = rs.retrieve('users', workspace='marketing')


.. _Collection.describe:

Describe an existing collection
-------------------------------
The ``describe`` method can be used to fetch all the details about the collection
such as what data sets act as the collection's sources, various performance and
usage statistics::

    from rockset import Client
    rs = Client()
    users = rs.retrieve('users')
    print(users.describe())

.. _Collection.drop:

Drop a collection
-----------------
Use the ``drop()`` method to remove a collection permanently from Rockset.

.. note:: This is a permanent and non-recoverable operation. Beware.

::

    from rockset import Client
    rs = Client()
    users = rs.retrieve('users')
    users.drop()

.. _Collection.add_docs:

Add documents to a collection
-----------------------------
Python dicts can be added as documents to a collection using the ``add_docs``
method. Documents are uniquely identified by the ``_id`` field. If an input
document does not have an ``_id`` field, then an unique id will be assigned
by Rockset.

If the ``_id`` field of an input document does not match an existing document,
then a new document will be created.

If the ``_id`` field of an input document matches an existing document,
then the new document will be merged with the existing document::

    from rockset import Client
    import json

    rs = Client()
    users = rs.Collection.retrieve('users')
    with open('my-json-array-of-dicts.json') as data_fh:
        ret = users.add_docs(json.load(data_fh))

.. _Collection.remove_docs:

Delete documents from a collection
----------------------------------
Remove documents from a collection using the ``remove_docs`` method::

    from rockset import Client

    rs = Client()
    users = rs.Collection.retrieve('users')
    users_to_remove = ['user007', 'user042', 'user435']
    docs_to_remove = [{'_id': u} for u in users_to_remove]
    ret = users.remove_docs(docs_to_remove)

"""
from .exception import InputError
from .resource import Resource

from rockset.swagger_client.api import (
    CollectionsApi, DocumentsApi, OrganizationsApi
)
from rockset.swagger_client.models import (
    AddDocumentsRequest, CreateCollectionRequest, DeleteDocumentsRequest
)


class Collection(Resource):
    @classmethod
    def create(
        cls,
        name,
        workspace="commons",
        description=None,
        sources=None,
        retention_secs=None,
        field_mappings=None,
        **kwargs
    ):
        """Creates a new Rockset collection.

        Use it via rockset.Client().Collection.create()

        Only alphanumeric characters, ``_``, and ``-`` are allowed
        in collection names.

        Args:
            name (str): name of the collection to be created.
            description (str): a human readable description of the collection
            sources (Source): array of Source objects that defines the set
                of input data sources for this collection
            retention_secs (int): an integer representing minimum duration (in seconds),
                for which documents are retained in this collection before being automatically deleted.
            field_mappings (FieldMapping): array of FieldMapping objects that
                defines the set of transformations to apply on all documents
        Returns:
            Collection: Collection object
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Collection.create() instead.'
            )
        client = kwargs.pop('client')

        if 'event_time_field' in kwargs:
            event_time_info = {}
            event_time_info['field'] = kwargs.pop('event_time_field')
            event_time_info['format'] = kwargs.pop('event_time_format', None)
            event_time_info['time_zone'] = kwargs.pop(
                'event_time_default_timezone', None
            )
            kwargs['event_time_info'] = event_time_info

        kwargs['description'] = description
        kwargs['sources'] = sources
        kwargs['retention_secs'] = retention_secs
        kwargs['field_mappings'] = field_mappings

        req = CreateCollectionRequest(name=name, **kwargs)
        collection = CollectionsApi(client).create(
            workspace=workspace, body=req
        ).get('data').to_dict()

        return cls(client=client, **collection)

    @classmethod
    def retrieve(cls, name, **kwargs):
        """Retrieves details of a single collection

        Use it via rockset.Client().Collection.retrieve()

        Args:
            name (str): Name of the collection

        Returns:
            Collection: Collection object
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Collection.create() instead.'
            )
        c = cls(name=name, **kwargs)
        c.describe()

        return c

    @classmethod
    def list(cls, **kwargs):
        """Returns list of all collections.

        Use it via rockset.Client().Collection.list()

        Returns:
            List: A list of Collection objects
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Collection.list() instead.'
            )
        client = kwargs.pop('client')
        workspace = kwargs.pop('workspace', 'commons')
        collections = CollectionsApi(client).list(workspace=workspace
                                                 ).get('data')

        ret = []
        for c in collections:
            if type(c) is dict:
                ret.append(cls(client=client, **c))
            else:
                ret.append(cls(client=client, **c.to_dict()))

        return ret

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'COLLECTION'
        super(Collection, self).__init__(*args, **kwargs)
        self.docs_per_call = 1000

    def _chopper(self, docs):
        return [
            docs[i:i + self.docs_per_call]
            for i in range(0, len(docs), self.docs_per_call)
        ]

    def _validate_doclist(self, docs):
        if type(docs) != list:
            raise InputError(message='arg "docs" is not a list of dicts')
        for doc in docs:
            if type(doc) != dict:
                raise InputError(
                    message='cannot add a document that is not a dict'
                )

    # instance methods
    def describe(self):
        """Returns all properties of the collection as a dict.

        Returns:
            dict: properties of the collection
        """
        return super(Collection, self).describe()

    def drop(self):
        """Deletes the collection represented by this object.

        If successful, the current object will contain
        a property named ``dropped`` with value ``True``

        Example::

            ...
            print(my_coll.asdict())
            my_coll.drop()
            print(my_coll.dropped)       # will print True
            ...
        """
        super(Collection, self).drop()
        return

    def query(self, q, timeout=None, flood_all_leaves=False):
        return super(Collection, self).query(
            q, timeout=timeout, flood_all_leaves=flood_all_leaves
        )

    def setstate(self, newstate):
        return super(Collection, self).setstate(newstate)

    def add_docs(self, docs, timeout=None):
        """Adds or merges documents to the collection. Provides document
        level atomicity.

        Documents within a collection are uniquely identified by the
        ``_id`` field.

        If the ``_id`` field of an input document does not match with
        any existing collection documents, then the input document will
        be inserted.

        If the ``_id`` field of an input document matches with an
        existing collection document, then the input document will be
        merged atomically as described below:

        * All fields present in both the input document and the collection
          document will be updated to values from the input document.
        * Fields present in the input document but not the collection
          document will be inserted.
        * Fields present in the collection document but not the input
          document will be left untouched.

        All fields within every input document will be inserted or updated
        atomically. No atomicity guarantees are provided across two different
        documents added.

        Args:
            docs (list of dicts): new documents to be added or merged
            timeout (int): Client side timeout. When specified,
                RequestTimeout_ exception will
                be thrown upon timeout expiration. By default, the client
                will wait indefinitely until it receives results or an
                error from the server.

        Returns:
            Dict: The response dict will have 1 field: ``data``

            The ``data`` field will be a list of document status records,
            one for each input document indexed in the same order as the list
            of input documents provided as part of the request. Each of those
            document status records will have fields such as the document
            ``_id``, ``_collection`` name, ``status`` describing if that
            particular document add request succeeded or not, and an optional
            ``error`` field with more details.
        """
        self._validate_doclist(docs)

        # chunk docs to operate in batches
        retval = []
        for chunk in self._chopper(docs):
            request = AddDocumentsRequest(data=chunk)
            retval.extend(
                DocumentsApi(self.client).add(
                    workspace=self.workspace,
                    collection=self.name,
                    body=request,
                    _request_timeout=timeout
                ).get('data')
            )

        return retval

    def remove_docs(self, docs, timeout=None):
        """Deletes documents from the collection. The ``_id`` field needs to
        be populated in each input document. Other fields in each document
        will be ignored.

        Args:
            docs (list of dicts): documents to be deleted.
            timeout (int): Client side timeout. When specified,
                RequestTimeout_ exception will
                be thrown upon timeout expiration. By default, the client
                will wait indefinitely until it receives results or an
                error from the server.

        Returns:
            Dict: The response dict will have 1 field: ``data``.

            The ``data`` field will be a list of document status records,
            one for each input document indexed in the same order as the list
            of input documents provided as part of the request. Each of those
            document status records will have fields such as the document
            ``_id``, ``_collection`` name, ``status`` describing if that
            particular document add request succeeded or not, and an optional
            ``error`` field with more details.
        """
        self._validate_doclist(docs)

        # chunk docs to operate in batches
        retval = []
        docids = [{'_id': doc.get('_id', None)} for doc in docs]
        for chunk in self._chopper(docids):
            request = DeleteDocumentsRequest(data=chunk)
            retval.extend(
                DocumentsApi(self.client).delete(
                    workspace=self.workspace,
                    collection=self.name,
                    body=request,
                    _request_timeout=timeout
                ).get('data')
            )
        return retval


__all__ = [
    'Collection',
]

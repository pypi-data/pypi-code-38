"""
Usage
-----
Client objects allow you to connect securely to the Rockset service.
All other API calls require a valid Client object.

In order to create a Client object, you will need a valid Rockset
API key. If you have access to the Rockset Console, then you can use
the console to create an API key. If not, please contact the
Rockset team at support@rockset.io

::

    from rockset import Client

    # connect securely to Rockset production API servers
    client = Client(api_server='api.rs2.usw2.rockset.com',
                    api_key='XKQL6YCU0zDUglhWHPMDDmDYyMxDHrASGk5apCnn3A07twh')

You can manage your api_key credentials using the ``rock`` command-line tool.
Run the ``rock configure`` tool to setup one or more api_key credentials and
select the one that you want all ``rock`` commands and the Python Rockset
Client to use. Once setup, you should expect the following to work.

::

    from rockset import Client

    # connect to the active credentials profile
    # you can see see the active profile by running ``rock configure ls``
    rs = Client()

    # connect to credentials profile 'prod' as defined by ``rock configure``
    rs = Client(profile='prod')


Example
-------

Connect to Rockset API server and then subsequently use the client object
to retrieve collections.

::

    from rockset import Client

    # connect securely to Rockset dev API server
    rs = Client(api_server='api-us-west-2.rockset.io',
                api_key='adkjf234rksjfa23waejf2')

    # list all collections in the account that I have access to
    all_collections = rs.Collection.list()

    # create a new collection; returns a collection object
    new_collection = rs.Collection.create('customer_info')

    # get details of an existing collection as a collection object
    users = rs.retrieve('users')

"""
import json
import logging
import os
import platform
import requests
import time
import tempfile
import yaml

import rockset

from rockset.collection import Collection
from rockset.credentials import Credentials
from rockset.cursor import Cursor
from rockset.exception import (
    AuthError, InputError, LimitReached, NotYetImplemented, RequestTimeout,
    ResourceSuspendedError, ServerError, TransientServerError
)
from rockset.field_mapping import FieldMapping
from rockset.integration import IntegrationClient
from rockset.query import Query
from rockset.source import Source
from rockset.workspace import Workspace

from rockset.swagger_client import (ApiClient, Configuration)
from rockset.swagger_client.rest import ApiException


class Client(object):
    """Securely connect to Rockset using an API key.

    Optionally, an alternate API server host can also be provided.
    If you have configured credentials using the ``rock configure``
    command, then those credentials will act as fall back values, when
    none of the api_key/api_server parameters are specified.

    Args:
        api_key (str): API key
        api_server (str): API server URL. Will default to https if URL
            does not specify a scheme.
        profile (str): Optionally, you can also specify name of your
            credentials profile setup using ``rock configure``

    Returns:
        Client: A Client object

    Raises:
        ValueError: when API key is not specified and
                    could not be fetched from ``rock`` CLI
                    credentials or api_server URL is invalid.
    """

    #: Maximum allowed length of a collection
    MAX_NAME_LENGTH = 2048

    #: Maximum allowed length of a field name
    MAX_FIELD_NAME_LENGTH = 10 * 1024

    #: Maximum allowed size of a field value
    MAX_FIELD_VALUE_BYTES = 4 * 1024 * 1024

    #: Maximum allowed length of ``_id`` field value
    MAX_ID_VALUE_LENGTH = 10 * 1024

    #: Maximum allowed levels of depth for nested documents
    MAX_NESTED_FIELD_DEPTH = 30

    #: Maximum allowed size of a single document
    MAX_DOCUMENT_SIZE_BYTES = 40 * 1024 * 1024

    # Config directory path
    @classmethod
    def config_dir(cls):
        """Returns name of the directory where Rockset credentials, config,
        and logs are stored.

        Defaults to ``"~/.rockset/"``

        Can be overriddden via ``ROCKSET_CONFIG_HOME`` env variable.
        """
        if 'ROCKSET_CONFIG_HOME' in os.environ:
            homedir = '%s' % os.path.expanduser(
                os.environ['ROCKSET_CONFIG_HOME']
            )
        elif platform.system() == 'Windows':
            homedir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
        else:
            homedir = os.path.expanduser('~')

        # if user does not have home dir, use tmpdir
        if not os.path.isdir(homedir):
            homedir = tempfile.gettempdir()

        # config dir is `homedir`/.rockset
        return os.path.join(homedir, '.rockset')

    # Constructor
    def __init__(
        self,
        api_key=None,
        api_server=None,
        profile=None,
        driver=None,
        **kwargs
    ):
        # inititalize api key and server
        self.api_key = api_key
        self.api_server = api_server

        # if both api key and server were not set, default to active profile
        if api_key is None or api_server is None:
            # read credentials from creds file if not supplied
            creds = Credentials()
            active_profile = creds.get(profile=profile)
            if api_key is None:
                self.api_key = active_profile.get('api_key', None)
            if api_server is None:
                self.api_server = active_profile.get('api_server', None)

        # no api_key => no soup for you
        if self.api_key is None:
            raise ValueError("api_key need to be specified")

        # default to api.rs2.usw2.rockset.com
        if self.api_server is None:
            self.api_server = 'api.rs2.usw2.rockset.com'

        # peel http scheme from api_server setting
        if self.api_server[:7] != 'http://' and self.api_server[:8
                                                               ] != 'https://':
            self.api_server = 'https://' + self.api_server

        configuration = Configuration()
        if 'HTTPS_PROXY' in os.environ:
            configuration.proxy = os.environ['HTTPS_PROXY']
        elif 'HTTP_PROXY' in os.environ:
            configuration.proxy = os.environ['HTTP_PROXY']

        self.user_agent = 'python'
        if driver is not None:
            self.user_agent += ':'
            self.user_agent += driver

        # init swagger client
        self.api_client = ApiClient(
            api_key=self.api_key,
            api_server=self.api_server,
            version=rockset.version(),
            user_agent=self.user_agent,
            configuration=configuration
        )

        # create instances of helper classes
        self.Collection = ClientCollection(client=self)
        self.Workspace = ClientWorkspace(client=self)
        self.Source = ClientSource(client=self)
        self.FieldMapping = ClientFieldMapping(client=self)
        self.Integration = IntegrationClient(client=self)

        # init config dir
        self.config_dir = Client.config_dir()
        if not os.path.isdir(self.config_dir):
            os.makedirs(self.config_dir)

        # init logging
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        return

    def _get_error_model(self, e):
        try:
            model = json.loads(e.body)
            return (model.get('message', None), model.get('type', None))
        except:
            pass
        return (None, None)

    def call_api(self, resource, method, *args, **kwargs):
        try:
            start_time = time.time()
            result = self.api_client.call_api(resource, method, *args, **kwargs)
        except ApiException as e:
            (message, errtype) = self._get_error_model(e)
            if e.status == 401:
                raise AuthError(code=e.status, message=message) from None
            elif e.status == 403 or e.status == 413 or e.status == 429:
                raise LimitReached(code=e.status, message=message, type=type) \
                    from None
            elif e.status == 400:
                raise InputError(
                    code=e.status, message=message, type=errtype
                ) from None
            elif e.status == 501:
                raise NotYetImplemented(
                    code=e.status, message=message, type=errtype
                ) from None
            elif e.status == 503 or e.status == 504:
                raise TransientServerError(
                    code=e.status, message=message, type=errtype
                ) from None
            elif e.status == 502:
                message = "502 error connecting to {}".format(self.api_server)
                elapsed = int(time.time() - start_time)
                raise RequestTimeout(message=message, timeout=elapsed) from None
            elif e.status > 400 and e.status < 500:
                raise InputError(
                    code=e.status, message=message, type=errtype
                ) from None
            elif e.status >= 500 and e.status < 530:
                raise ServerError(
                    code=e.status, message=message, type=errtype
                ) from None
            elif e.status == 530:
                raise ResourceSuspendedError(
                    code=e.status, message=message, type=errtype
                ) from None
            else:
                raise e
        return result

    def list(self, workspace="commons", **kwargs):
        """Returns list of all collections in a workspace.

        Args:
            workspace (str): Name of the workspace to list from

        Returns:
            List: A list of Collection objects
        """
        return Collection.list(client=self, workspace=workspace)

    def retrieve(self, name, workspace="commons"):
        """Retrieves a single collection

        Args:
            name (str): Name of the collection to be retrieved
            workspace (str): Name of the workspace the collection is in

        Returns:
            Collection: Collection object
        """
        return Collection.retrieve(name=name, workspace=workspace, client=self)

    def query(self, q, collection=None, **kwargs):
        """Execute a query against Rockset.

        This method prepares the given query object and binds it to
        a Cursor_ object, and returns that Cursor object. The request is not
        actually dispatched to the backend until the results are fetched
        from the cursor.

        Input query needs to be supplied as a Query_ object.

        Cursor objects are iterable, and you can iterate through a cursor to
        fetch the results. The entire result data set can also be retrieved
        from the cursor object using a single ``results()`` call.

        When you iterate through the cursor in a loop, the cursor objects
        implement automatic pagination behind the scenes. If the query
        returns a large number of results, with automatic pagination,
        only a portion of the results are buffered into the cursor at a
        time. As the cursor iterator reaches the end of the current batch,
        it will automatically issue a new query to fetch the next batch
        and seamlessly resume. Cursor's default iterator uses batch size
        of 10,000, and you can create an iterator of a different batch size
        using the iter() method in the cursor object.

        Example::

            ...
            rs = Client()
            cursor = rs.query(q)

            # fetch all results in 1 go
            all_results = cursor.results()

            # iterate through all results;
            # automatic pagination with default iterator batch size of 100
            # if len(all_results) == 21,442, then as part of looping
            # through the results, three distinct queries would be
            # issued with (limit, skip) of (10000, 0), (10000, 10000),
            # (10000, 20000)
            for result in cursor:
                print(result)

            # iterate through all results;
            # automatic pagination with iterator batch size of 20,000
            # if len(all_results) == 21,442, then as part of looping
            # through the results, two distinct queries would have
            # been issued with (limit, skip) of (20000, 0), (20000, 20000).
            for result in cursor.iter(20000):
                print(result)
            ...

        Args:
            q (Query): Input Query object
            timeout (int): Client side timeout. When specified, RequestTimeout_ \
            exception will be thrown upon timeout expiration. By default, \
            the client will wait indefinitely until it receives results or \
            an error from the server.

        Returns:
            Cursor: returns a cursor that can fetch query results with or
            without automatic pagination
        """
        # Collection is ignored.
        return self.sql(q, **kwargs)

    def sql(self, q, **kwargs):
        if not isinstance(q, Query):
            raise NotImplementedError(
                'query of type {} not supported'.format(type(q))
            )
        return Cursor(q=q, client=self)


Client.sql.__doc__ = Client.query.__doc__.replace('rs.query(', 'rs.sql(')


class ClientCollection(object):
    def __init__(self, client):
        self.client = client

    def create(self, name, workspace="commons", description=None, **kwargs):
        sources = [dict(s) for s in kwargs.pop('sources', [])]
        field_mappings = [dict(m) for m in kwargs.pop('field_mappings', [])]
        return Collection.create(
            name=name,
            workspace=workspace,
            description=description,
            sources=sources,
            field_mappings=field_mappings,
            client=self.client,
            **kwargs
        )

    def list(self, workspace="commons"):
        return Collection.list(client=self.client, workspace=workspace)

    def retrieve(self, name, workspace="commons"):
        return Collection.retrieve(
            name=name, workspace=workspace, client=self.client
        )


class ClientSource(object):
    def __init__(self, client):
        self.client = client

    def s3(self, *args, **kwargs):
        return Source.s3(*args, **kwargs)

    def dynamo(self, *args, **kwargs):
        return Source.dynamo(*args, **kwargs)

    def kinesis(self, *args, **kwargs):
        return Source.kinesis(*args, **kwargs)

    def gcs(self, *args, **kwargs):
        return Source.gcs(*args, **kwargs)

    def csv_params(self, *args, **kwargs):
        return Source.csv_params(*args, **kwargs)

    def xml_params(self, *args, **kwargs):
        return Source.xml_params(*args, **kwargs)


class ClientFieldMapping(object):
    def __init__(self, client):
        self.client = client

    def mapping(self, *args, **kwargs):
        return FieldMapping.mapping(*args, **kwargs)

    def input_field(self, *args, **kwargs):
        return FieldMapping.input_field(*args, **kwargs)

    def output_field(self, *args, **kwargs):
        return FieldMapping.output_field(*args, **kwargs)


class ClientWorkspace(object):
    def __init__(self, client):
        self.client = client

    def create(self, name, description=None, **kwargs):
        return Workspace.create(
            client=self.client, name=name, description=description
        )

    def list(self):
        return Workspace.list(client=self.client)

    def retrieve(self, name):
        return Workspace.retrieve(client=self.client, name=name)


__all__ = [
    'Client',
]

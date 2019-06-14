import functools
import itertools
import json
import logging
import os.path
import pprint
import re
from collections import Mapping, Sequence
from datetime import datetime
from itertools import islice
from os import environ
from tempfile import mkstemp
from time import sleep, time

# noinspection PyUnresolvedReferences
from builtins import map
from past.builtins import basestring
from requests import Session
from requests.exceptions import ConnectionError

from businessoptics.cached_file_getter import CachedTuplesCSV
from businessoptics.exceptions import APIError
from .utils import retry, join_urls, add_exception_info, strip_prefix, fix_types, ensure_list_if_string, only, \
    boto3_client_from_credentials

log = logging.getLogger(__name__)


def id_or_name(collection_url):
    """
    This decorator lets a method look up a resource by name instead of ID.

    The method must accept exactly one argument representing the ID of the resource
    that the method will return as a Client.

    The parameter collection_url is the URL the client will search through
    (relative to the client's base URL) to find the object with the right name.

    There must be exactly one object in the collection with the correct name.
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, resource_id):
            if isinstance(resource_id, basestring) and not resource_id.isdigit():
                resource_id = (self / collection_url).object_with_name(resource_id)['id']
            return method(self, resource_id)

        return wrapper

    return decorator


class Client(object):
    def __init__(self,
                 server='https://app.businessoptics.biz',
                 base_url='',
                 auth=None,
                 session=None,
                 impersonate=None):
        """
        Construct a new Client. Authentication details can either be passed in directly:

            Client(auth=('user@example.com', 'apikey'))

        or be extracted from environment vairables:
            * BUSINESSOPTICS_EMAIL
            * BUSINESSOPTICS_APIKEY

        or from a ~/.businessoptics_client.config JSON file of the form

            { "<username>": "<apikey>" }

        """
        super(Client, self).__init__()
        self.server = server
        self.base_url = strip_prefix(base_url, server)
        assert not (auth and session), "A Client can't take both auth details and an existing session"

        if session:
            self.session = session
        else:
            self.session = Session()

            if not auth:
                auth = self.get_credentials_from_env()

            if not auth or isinstance(auth, basestring):
                auth = self.get_credentials_from_file(auth)

            message = 'auth must be a pair of strings: (username, apikey)'
            assert isinstance(auth, Sequence), message
            assert (not isinstance(auth, basestring) and
                    len(auth) == 2 and
                    all(isinstance(x, basestring) for x in auth)), message
            self.session.headers.update({
                'Authorization': 'ApiKey {}:{}'.format(*auth)
            })

        if impersonate:
            self.session.cookies.update({'IMPERSONATION_EMAIL': impersonate})

    def get_credentials_from_file(self, username):
        """
        Extract authentication credentials from a JSON file of the form

            { "<username>": "<apikey>" }

        if no username is given the special default value is used: i.e.:

            config['default']

        """
        path = os.path.join(os.path.expanduser('~'), '.businessoptics_client.config')
        try:
            with open(path) as f:
                config = json.load(f)
        except (IOError, ValueError):
            add_exception_info('Failed to load JSON credentials file at ~/.businessoptics_client.config. '
                               'Create or fix the file or specify auth=(username, apikey).')
            raise

        if not username:
            try:
                username = config['default']
            except KeyError:
                raise Exception('No auth specified and no default username found in config.')

        try:
            apikey = config[username]
        except KeyError:
            raise Exception('No API key found for username %s in config' % username)

        return username, apikey

    def get_credentials_from_env(self):
        """
        Extract authentication credentials from environment variables.

        Auth details extracted from:
          * BUSINESSOPTICS_EMAIL
          * BUSINESSOPTICS_APIKEY
        """
        username = environ.get('BUSINESSOPTICS_EMAIL')
        apikey = environ.get('BUSINESSOPTICS_APIKEY')
        if username and apikey:
            return username, apikey
        else:
            return None

    @classmethod
    def at(cls, client, base_url=None):
        """
        Returns an object of type `cls` (must be a subclass of Client)
        at the same base URL as `client` or at the given `base_url`.
        Copies the session (and thus the authentication details) of `client`.
        """
        if base_url is None:
            base_url = client.base_url
        return cls(server=client.server,
                   base_url=base_url,
                   session=client.session)

    @classmethod
    def local(cls, auth=('development@businessoptics.biz', 'development'), *args, **kwargs):
        """
        Returns a client pointing to a local development server.
        """
        return cls(server='http://app.businessoptics.test', auth=auth, *args, **kwargs)

    @classmethod
    def staging(cls, *args, **kwargs):
        """
        Returns a client pointing to the staging environment.
        """
        return cls(server='https://app.businessoptics.net', *args, **kwargs)

    @classmethod
    def production(cls, *args, **kwargs):
        """
        Returns a client pointing to the production environment.
        This is the default, so you can simply use `Client()` instead.
        """
        return cls(*args, **kwargs)

    @retry(5, ConnectionError, log)
    def request(self, method, url='', **kwargs):
        url = join_urls(self.server, self.base_url, url)
        response = self.session.request(method, url, **kwargs)
        if response.status_code in (502, 503, 504):
            raise ConnectionError('Server returned code %s' % response.status_code)
        try:
            result = response.json()
        except ValueError:
            raise APIError(url, response, message='Failed to parse JSON')
        if result.get('status') != 'ok' or result.get('error') or result.get('state') == 'error':
            raise APIError(url, response, response_json=result)
        return result

    def get(self, url='', **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('GET', url, **kwargs)

    def options(self, url='', **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('OPTIONS', url, **kwargs)

    def head(self, url='', **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return self.request('HEAD', url, **kwargs)

    def post(self, url='', **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url='', **kwargs):
        return self.request('PUT', url, **kwargs)

    def patch(self, url='', **kwargs):
        return self.request('PATCH', url, **kwargs)

    def delete(self, url='', **kwargs):
        log.info('Sending DELETE request to %s', join_urls(self.base_url, url))
        return self.request('DELETE', url, **kwargs)

    def __div__(self, other):
        """
        Returns a copy of this client with `other` appended to the base URL.

        For example, given `c = Client()`:

        (c / 'api/v2/workspace') will have the base URL '/api/v2/workspace'
        (c / 'api/v2/workspace' / 3) will have the base URL '/api/v2/workspace/3'
        """
        return Client.at(self, base_url=join_urls(self.base_url, other))

    def __truediv__(self, other):
        return self.__div__(other)

    @property
    def root(self):
        return Client.at(self, base_url='')

    @property
    def api(self):
        return Client.at(self, base_url='/api/v2')

    @property
    def internal(self):
        return Client.at(self, base_url='/api/internal')

    @id_or_name('/api/v2/workspace')
    def workspace(self, resource_id):
        """
        Returns the Workspace with the given ID or name.

        If a name is given, it must be unique among all workspaces this user can access.
        """
        workspace = Workspace.at(self.api / 'workspace' / resource_id)
        workspace.id = resource_id
        return workspace

    def dashboard(self, resource_id):
        """
        Returns the Dashboard with the given ID.

        To find a dashboard by name, you must use a Workspace, e.g.

            Client().workspace(123).dashboard('<dashboard name>')

        Then the name must be unique among all dashboards within that workspace.
        """
        return Dashboard.at(self.api / 'dashboard' / resource_id)

    def dataset(self, resource_id):
        """
        Returns the Dataset with the given ID.

        To find a dataset by name, you must use a DataCollection, e.g.

            Client().DataCollection(123).dataset('<dataset name>')

        Then the name must be unique among all datasets within that collection.
        """
        return Dataset.at(self.api / 'dataset' / resource_id)

    @id_or_name('/api/v2/datacollection')
    def datacollection(self, resource_id):
        """
        Returns the DataCollection with the given ID or name.

        If a name is given, it must be unique among all data collections this user can access.
        """
        return DataCollection.at(self.api / 'datacollection' / resource_id)

    def query(self, resource_id):
        """
        Returns the Query with the given ID.
        """
        return Query.at(self.api / 'query' / resource_id)

    @property
    def full_url(self):
        return join_urls(self.server, self.base_url)

    def __repr__(self):
        return self.__class__.__name__ + '@' + self.full_url

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def object_with_name(self, name):
        collection = self.get('?expand=objects')['objects']
        return only(x for x in collection if x['name'].strip().lower() == name.strip().lower())


class Workspace(Client):

    def __init__(self, *args, **kwargs):
        super(Workspace, self).__init__(*args, **kwargs)
        self.id = None

    def query(self, ideas, parameters=None, **extra_post_fields):
        """
        Initiate a query for the given ideas in this workspace.

        :param ideas: a list of strings representing idea names,
            or a single space/comma separated string.
        :param parameters: a dictionary of knowledge parameters, where the keys
            are idea names.
        :param extra_post_fields: additional parameters for the request, e.g.
            execution_mode='hadoop'
        :return: a Query object.
        """
        ideas = ensure_list_if_string(ideas)
        parameters = fix_types(parameters or {})

        response = self.post('query', json=dict(knowledge_parameters=parameters,
                                                ideanames=ideas,
                                                **extra_post_fields))

        uri = response['uri']
        log.info('Started query in workspace %s for %s idea(s) including %s: %s',
                 self.id, len(ideas), ideas[0], join_urls(self.server, uri))
        query = Query.at(self, uri)
        query.ideas = ideas
        return query

    def quick(self, ideas, parameters=None, **extra_post_fields):
        """
        Similar to the `query` method, but runs the query immediately
        and returns a Quick object.
        """
        ideas = ensure_list_if_string(ideas)
        parameters = fix_types(parameters or {})

        response = self.post('quick', json=dict(knowledge_parameters=parameters,
                                                ideanames=ideas,
                                                **extra_post_fields))

        log.info('Performed quick query in workspace %s for %s idea(s) including %s: %s',
                 self.id, len(ideas), ideas[0], self.server)

        quick = Quick(response)
        quick.ideas = ideas
        return quick

    dashboard = id_or_name('dashboard')(Client.dashboard)

    def train(self, ideas):
        ideas = ensure_list_if_string(ideas)
        uri = self.post('train', json={'ideas': ideas})['uri']
        run = TrainingRun.at(self, uri)
        log.info('Training ideas %r in %s', ideas, run)
        return run

    @id_or_name('datasource')
    def dataset_connector(self, resource_id):
        return DatasetConnector.at(self.api / 'workspace/datasource' / resource_id)

    def idea(self, name):
        result = Idea.at(self / 'idea' / name)
        if result.get()['operator'] == 'data':
            result = DataIdea.at(result)
        result.workspace_resource = self
        return result


class DatasetConnector(Client):
    @property
    def dataset(self):
        return Dataset.at(self, self.get()['dataset'])


class Idea(Client):
    @property
    def parameters(self):
        return self.get('parameters')['values']


class DataIdea(Idea):
    @property
    def dataset_connector(self):
        return self.workspace_resource.dataset_connector(self.parameters['datasource'])


class Awaitable(Client):
    desired_state = 'complete'

    def __init__(self, *args, **kwargs):
        super(Awaitable, self).__init__(*args, **kwargs)
        self.state = None
        self.start_time = time()

    def await(self):
        """
        Poll the base URL every 2 seconds until desired_state is reached.
        """
        # Avoid logging 'Completed' every time this is called
        if self.state == self.desired_state:
            return

        while self.state != self.desired_state:
            state = self.get()['state']
            if state != self.state:
                log.debug('%s state is now %s', self, state)
            self.state = state
            if state != self.desired_state:
                sleep(2)
        log.info('Completed %s in %s seconds', self, round(time() - self.start_time, 1))


class Query(Awaitable):
    def __init__(self, *args, **kwargs):
        super(Query, self).__init__(*args, **kwargs)
        self.ideas = None

    def result(self, information_id=None):
        """
        Waits for the query to finish, then returns an IdeaResult for this query
        and the given information identifier.

        Usually this is not needed directly by scripts, and you can skip straight
        to the tuples(), tuple_generator(), or to_df() methods.

        The identifier is optional if only one idea was queried, and if this Query was
        created conventionally, e.g. `workspace.query('<idea>')`.
        """

        ideas = self.ideas
        if information_id is None:
            if ideas and len(ideas) == 1:
                information_id = ideas[0]
            else:
                raise ValueError(
                    'You must specify an information identifier for a result unless only one idea was queried')
        self.await()
        result = IdeaResult.at(self / 'result' / information_id)
        assert isinstance(result, IdeaResult)
        return result

    # Shortcuts to the corresponding methods of the result (see HasTuples):
    # =====================================================================

    def tuples(self, information_id=None, limit=None, offset=0, auto_parse=True):
        return self.result(information_id).tuples(limit, offset, auto_parse)

    def tuple_generator(self, information_id=None, limit=None, offset=0, auto_parse=True):
        return self.result(information_id).tuples(limit, offset, auto_parse)

    def to_df(self, information_id=None):
        return self.result(information_id).to_df()


class TrainingRun(Awaitable):
    pass


class Quick(object):
    """
    Encapsulates a quick query. Conforms to the standard query API.
    """

    def __init__(self, response):
        self.response = response
        self.ideas = None

    def result(self, information_id=None):
        ideas = self.ideas
        if information_id is None:
            if ideas and len(ideas) == 1:
                information_id = ideas[0]
            else:
                raise ValueError(
                    'You must specify an information identifier for a result '
                    'unless only one idea was queried')

        return QuickResult(self.response['results'][information_id])

    def tuples(self, information_id=None, limit=None, offset=0, auto_parse=True):
        return self.result(information_id).tuples(limit, offset, auto_parse)

    # there's no way to save memory with a generator with a quick query
    tuple_generator = tuples

    def to_df(self, information_id=None):
        return self.result(information_id).to_df()

    def await(self):
        """
        Simply a stub for query API compatibility
        """
        return


class QuickResult(object):
    """
    Provides a result API for quick results
    """
    def __init__(self, response):
        self.response = response

    def tuples(self, limit=None, offset=0, auto_parse=True):
        """
        Returns a list of tuples (dictionaries) corresponding to this result.

        If auto_parse is True (the default), datetime values will be
        parsed from strings into Python datetime objects.
        """
        response = self.response
        limit = HasTuples.check_infinite_limit(limit)

        datetime_dimensions = []
        if auto_parse:
            dimensions = response['structure']
            datetime_dimensions = [d['name'] for d in dimensions
                                   if d['type'].upper() == 'DATETIME']

        tuples = response['tuples'][offset:limit]
        for dim in datetime_dimensions:
            for tup in tuples:
                value = tup[dim]
                if value is not None:
                    datetime_format = '%Y-%m-%dT%H:%M:%S'
                    if 'T' not in value:
                        datetime_format = datetime_format.replace('T', ' ')
                    tup[dim] = datetime.strptime(value, datetime_format)

        return tuples

    # there's no way to save memory with a generator with a quick query
    tuple_generator = tuples

    def to_df(self):
        """
        Returns a pandas DataFrame containing the tuples of this resource.
        """
        import pandas  # you must install this separately

        return pandas.DataFrame(self.tuples())


class HasTuples(Client):
    """
    A mixin for classes with a tuples endpoint, i.e. Dataset and IdeaResult
    """

    def dimensions_dict(self):
        return {d['name']: d['type'] for d in self.get()['dimensions']}

    def tuples(self, *args, **kwargs):
        """
        Like tuple_generator, but returns a list.
        """
        return list(self.tuple_generator(*args, **kwargs))

    def tuple_generator(self,
                        limit=None,
                        offset=0,
                        auto_parse=True,
                        simple_filter=None,
                        complex_filter=None):
        """
        A generator of tuples (dictionaries) corresponding to this result.

        Paging is automatically handled so you generally don't need to worry
        about offset and limit, and you can set limit as high as you want.

        Unlike to_df this doesn't cache anything and will download the data
        every time it is called.

        If auto_parse is True (the default), datetime values will be
        parsed from strings into Python datetime objects.

        simple_filter and complex_filter are only applicable to datasets.
        Only one can be used at a time. They are optional.

        simple_filter must be a dict from column names to values,
        and only tuples where the values are equal will be returned.

        complex_filter must be a 3D list representing of disjuction of
        conjunctions of filters, e.g.

            complex_filter = [
                [
                    ['a', 'eq', 3],
                ],
                [
                    ['b', 'gte', 4],
                    ['c', 'neq', 5],
                ]
            ]

        means '(a == 3) OR (b >= 4 AND c != 5)'
        """
        datetime_dimensions = []
        if auto_parse:
            dimensions = self.get()['dimensions']
            datetime_dimensions = [d['name'] for d in dimensions
                                   if d['type'].upper() == 'DATETIME']
        limit = self.check_infinite_limit(limit)

        assert not (simple_filter and complex_filter), "Only one kind of filter is possible"

        if simple_filter:
            filter_params = dict(('filter.' + k, v) for k, v in simple_filter.items())
        elif complex_filter:
            filter_params = dict(
                ('tuples_filter.%s.%s.%s' % (i, dim, op), val)
                for i, conjunction in enumerate(complex_filter)
                for dim, op, val in conjunction)
        else:
            filter_params = {}

        while True:
            request_limit = min(2000, limit)
            response = self.get('tuples', params=dict(limit=request_limit, offset=offset, **filter_params))
            tuples = response['tuples']
            for tup in tuples:
                for dim in datetime_dimensions:
                    value = tup[dim]
                    if value is None:
                        continue
                    datetime_format = '%Y-%m-%dT%H:%M:%S'
                    if 'T' not in value:
                        datetime_format = datetime_format.replace('T', ' ')
                    tup[dim] = datetime.strptime(value, datetime_format)
                yield tup

            offset += request_limit
            limit -= request_limit
            if offset >= response['meta']['count'] or limit <= 0:
                return

    @staticmethod
    def check_infinite_limit(limit):
        if limit in (0, -1, None):
            limit = 9999999999
        return limit

    def stream(self):
        """
        Stream tuples (lists) using the stream endpoint.
        In general you should probably prefer the tuple_generator method.
        """
        return map(json.loads,
                   self.session.get(join_urls(self.server, self.base_url, 'stream'),
                                    stream=True
                                    ).iter_lines())

    def to_df(self):
        """
        Returns a pandas DataFrame containing the tuples of this resource.

        Caches the data to avoid downloading twice. This includes handling of cached queries.
        """
        import pandas  # you must install this separately
        import numpy

        csv_path = CachedTuplesCSV(self).path()
        dimension_types = self.dimensions_dict()
        type_map = dict(STRING=str, DATETIME=str, INTEGER=numpy.int64, REAL=numpy.float64, BOOLEAN=bool)
        pandas_types = {k: type_map[v.upper()] for k, v in dimension_types.items()}
        date_columns = [k for k, v in dimension_types.items()
                        if v.upper() == 'DATETIME']
        return pandas.read_csv(csv_path,
                               dtype=pandas_types,
                               parse_dates=date_columns,
                               keep_default_na=False)


class IdeaResult(HasTuples):
    def reingest_into_existing_dataset(self, dataset_id, **dimension_mappings):
        """
        Reingest the tuples from this result into an existing dataset with the given ID as an upsert.
        Dimension mappings should be specified as <result dimension>=<dataset dimension>.
        Note that sometimes the result dimension name is not exactly what you see in the query result.
        For example you should use value_renamed instead of value. Same for [start_|end_]datetime.
        """
        log.info('Reingesting %s into dataset %s', self, dataset_id)

        # Create default mappings where the names and types match on both sides
        dataset_dimensions = set(self.dataset(dataset_id).dimensions_dict().items())
        result_dimensions = set(self.dimensions_dict().items())
        matching_dimensions = dataset_dimensions & result_dimensions
        mappings = [dict(csv_name=name, db_name=name)
                    for name, _ in matching_dimensions
                    if name not in dimension_mappings]
        mappings += [dict(csv_name=key, db_name=value)
                     for key, value in dimension_mappings.items()]
        response = self.post('reingest_now', json=dict(dataset_id=dataset_id,
                                                       mappings=mappings))
        return DataUpdate.at(self, response['uri'])


class Dashboard(Client):
    def query_parameters(self):
        result = Query.at(self, self.post('query_parameters')['uri'])
        assert isinstance(result, Query)
        return result

    def parameter_options(self):
        query = self.query_parameters()
        result = []

        def add_parameters_from(obj):
            for p in obj['parameters']:
                add_parameter(p)

        def add_parameter(parameter):
            def add_to_result():
                parameter['options_tuples'] = tuples
                result.append(parameter)

            if parameter['type'] == 'section':
                add_parameters_from(parameter)
            elif parameter['type'] == 'multi_select':
                options_idea = parameter['options_idea']
                tuples = query.tuples(options_idea)
                tuples = [{selector['idea']: tup[selector['dimension']]
                           for selector in parameter['selectors']}
                          for tup in tuples]
                add_to_result()
            else:
                idea = parameter['idea']
                if parameter['type'] == 'hidden':
                    values = [parameter['value']]
                elif parameter['type'] == 'select':
                    options = parameter['options']
                    options_source = options['options_source']
                    if options_source == 'idea':
                        dimension = options['dimension']
                        tuples = query.tuples(options['idea'])
                        values = [t[dimension] for t in tuples]
                    elif options_source == 'list':
                        values = options['options']
                    else:
                        raise ValueError('Unknown options source %s' % options_source)
                else:
                    raise ValueError('Unknown parameter type %s', parameter['type'])
                tuples = [{idea: value} for value in values]
                add_to_result()

        add_parameters_from(self.get('display'))
        return result


class Dataset(HasTuples):
    @property
    def tableset(self):
        result = Tableset.at(self / 'tableset')
        assert isinstance(result, Tableset)
        result.dataset_resource = self
        return result

    @property
    def bigstore(self):
        result = Bigstore.at(self / 'bigstore')
        assert isinstance(result, Bigstore)
        result.dataset_resource = self
        return result

    @property
    def dataset_type(self):
        return getattr(self, self.get()['type'])

    def duplicate(self,
                  new_name,
                  copy_data=False,
                  set_keys=None,
                  add_keys=(),
                  remove_keys=(),
                  add_dimensions=(),
                  remove_dimensions=(),
                  datacollection=None,
                  ):
        """
        Create a copy of this dataset. The dimensions are the same unless otherwise specified.

        :param new_name: Name of the new dataset.

        :param copy_data: The new dataset is blank unless this is True.

        :param set_keys: List of dimension names that should be the keys of the new dataset.
            All other dimensions in the new dataset will not be keys.
            You cannot specify this in addition to either add_keys or remove_keys

        If you specify one or both of the below, you cannot specify set_keys.
        The new dataset will have the same keys as the original except for the changes below
        :param add_keys: List of dimension names that should be keys in the new dataset
        :param remove_keys: List of dimension names that should NOT be keys in the new dataset

        :param add_dimensions: List of dictionaries with keys [name, type, key, default]
            for dimensions to add to new dataset
        :param remove_dimensions: List of dimension names to not include in new dataset

        :param datacollection: Custom datacollection to put the new dataset in.
            By default the current collection is used.
        :rtype: Dataset
        """

        assert not (set_keys is not None and (add_keys or remove_keys)), "Invalid combination of arguments"
        if set_keys is not None:
            set_keys = set(ensure_list_if_string(set_keys))
        add_keys = set(ensure_list_if_string(add_keys))
        remove_keys = set(ensure_list_if_string(remove_keys))
        assert not add_keys.intersection(remove_keys)

        remove_dimensions = set(ensure_list_if_string(remove_dimensions))

        columns = self.get('tableset/column?expand=objects')['objects']
        dimensions = self.get()['dimensions']
        for dim, column in zip(dimensions, columns):
            name = dim['name']
            assert name == column['field_name']
            if set_keys is not None:
                dim['key'] = name in set_keys
            elif name in add_keys:
                dim['key'] = True
            elif name in remove_keys:
                dim['key'] = False
            else:
                dim.setdefault('key', False)

            dim['default'] = column['default']
            dim['type'] = dim['type'].lower()

        dimensions = [dim
                      for dim in dimensions
                      if dim['name'] not in remove_dimensions
                      ] + list(add_dimensions)

        if datacollection is None:
            datacollection = self.collection

        dup = datacollection.create_tablestore_dataset(new_name, dimensions)

        if copy_data:
            def tuples():
                for tup in self.tuple_generator():
                    for extra_dim in add_dimensions:
                        tup[extra_dim['name']] = None  # use default
                    for dim_name in remove_dimensions:
                        tup.pop(dim_name, None)
                    yield tup

            dup.upload_tuples(tuples())

        return dup

    @property
    def collection(self):
        """
        The DataCollection containing this dataset.
        """
        result = DataCollection.at(self, self.get()['data_collection'])
        assert isinstance(result, DataCollection)
        return result

    def rename(self, new_name):
        self.put(json={'name': new_name})
        log.info('Renamed %s to %r', self, new_name)

    # Shortcuts to the methods in Tableset/Bigstore:
    # =====================================

    def upload_tuples(self, *args, **kwargs):
        return self.tableset.upload_tuples(*args, **kwargs)

    def delete_tuples(self, *args, **kwargs):
        return self.tableset.delete_tuples(*args, **kwargs)

    def upload_df(self, *args, **kwargs):
        return self.dataset_type.upload_df(*args, **kwargs)


class Tableset(Client):

    def upload_tuples(self, tuples, truncate_columns=()):
        """
        Upload tuples to a dataset in batches.

        tuples: an iterable (e.g. list or generator) of dictionaries,
                each mapping column names to values.

                If a single dictionary or single list is given this is wrapped in a list,
                for convenience.

        truncate_columns: names of string dimensions to truncate to 250 characters

        Returns a list of the responses to each upload request.
        """

        if isinstance(tuples, Sequence) and len(tuples) == 0:
            log.info('Uploaded 0 tuples total to %s', self.full_url)
            return []

        column_objects = {c['field_name']: c for c in
                          self.get('column?expand=objects')['objects']}

        # If a single tuple is passed, wrap it in a list
        if isinstance(tuples, Mapping):
            tuples = [tuples]

        batch_size = 2000
        count = 0
        milestones = itertools.chain([4000, 10000, 20000, 50000],
                                     itertools.count(100000, 100000))
        current_milestone = 2000
        responses = []
        tuples = iter(tuples)  # ensures islice properly exhausts the iterator
        while True:
            batch = list(islice(tuples, batch_size))
            count += len(batch)
            if not batch:
                break
            batch = fix_types(batch)
            for tup in batch:
                for key, value in tup.items():
                    if value is None or (value == '' and column_objects[key]['field_type'].lower() != 'string'):
                        tup[key] = column_objects[key]['default']
                    if isinstance(value, basestring) and len(value) > 250:
                        if key in truncate_columns:
                            tup[key] = value[:250]
                        else:
                            raise ValueError(
                                'The key %r has a value of length %s. The maximum allowed is 250. ' %
                                (key, len(value)) +
                                'Set truncate_columns=%r in upload_tuples to automatically truncate before uploading. '
                                % (list(truncate_columns) + [key],) +
                                'Full tuple preview:\n%s' % pprint.pformat(tup)[:10000])
            responses.append(self.post('tuples', json={'tuples': batch}))
            if count >= current_milestone:
                log.info('Uploaded %s tuples so far to %s', count, self.full_url)
                current_milestone = next(milestones)
        log.info('Uploaded %s tuples total to %s', count, self.full_url)
        return responses

    def upload_df(self, df, *args, **kwargs):
        """
        Efficiently uploads a pandas dataframe.

        This will upload all the value columns, not the indexes. These are the columns that are
        returned by `df.columns`. Should you wish to upload the indexes simply go

        ```
        dataset.upload_df(df.reset_indexes())
        ```
        """

        def generate_tuples():
            for _, row in df.iterrows():
                yield dict(row)

        return self.upload_tuples(generate_tuples(), *args, **kwargs)

    def delete_tuples(self, filters=()):
        """
        filters should be a list of lists of dictionaries.
        Each sublist acts as a conjunctive clause in a disjunctive sentence, and each dictionary specifies a
        column name (`attribute`), comparison operation (`predicate`), and `value`.
        For example:

            [
                [
                    {
                     "attribute": "city",
                     "predicate": "=",
                     "value": "Cape Town"
                    }
                ],
                [
                    {
                     "attribute": "city",
                     "predicate": "=",
                     "value": "Durban"
                    },
                    {
                     "attribute": "income",
                     "predicate": "<=",
                     "value": "10000"
                    }
                ]
            ]

        This will delete all tuples where the city is Cape Town, or where the city
        is Durban and the income is less than or equal to 10000.
        """
        return self.delete('tuples', json={'filters': filters})


class Bigstore(Client):
    def upload_df(self, df):
        import pyarrow  # pip install pyarrow
        from pyarrow import parquet

        generated = self.get('generate_simple_update')
        bucket = generated['bucket']
        key = generated['key']
        s3 = boto3_client_from_credentials('s3', generated['credentials'])

        # Convert string columns to unicode
        for dim in self.dataset_resource.get()['dimensions']:
            name = dim['name']
            try:
                df[name]
            except KeyError:
                raise ValueError('dataframe is missing column %s' % name)

            if dim['type'].lower() != 'string':
                continue
            df[name] = df[name].str.decode('utf8')

        filename = mkstemp()[1]
        log.info('Writing dataframe to file %s', filename)
        table = pyarrow.Table.from_pandas(df, preserve_index=False)
        parquet.write_table(table, filename, flavor='spark')

        log.info('Uploading file parquet file %s to key %s', filename, key)
        s3.upload_file(filename, bucket, key)

        response = self.post('simple_update', json={'parquet_key': key})
        result = BigstoreUpdate.at(self, response['uri'])
        log.info('Started %s', result)
        return result


class BigstoreUpdate(Awaitable):
    pass


class DataUpdate(Awaitable):
    desired_state = 'done'


class DataCollection(Client):
    dataset = id_or_name('dataset')(Client.dataset)

    def create_tablestore_dataset(self, name, dimensions):
        """
        Create a new blank tablestore dataset in this collection.

        :type name: string
        :param dimensions: List of dictionaries with keys [name, type, key, default]
        :rtype: DataSet
        """

        for dim in dimensions:
            dim['name'] = dim['name'].lower()
            dim['type'] = dim['type'].lower()
            assert re.match(r'^[a-z_][a-z0-9_]*$', dim['name']), "Invalid dimension name %r" % dim['name']

        response = self.post('dataset/tableset/', json=dict(
            name=name,
            dimensions=dimensions,
        ))
        log.info('Created dataset with name %s, ID %s', name, response['id'])
        result = Dataset.at(self, response['uri'])
        assert isinstance(result, Dataset)
        return result

    def create_tablestore_dataset_from_df(self, name, df, keys=(), defaults=None):
        """
        Create a dataset from a pandas dataframe.

        Does not include index columns.

        `keys` (optional) should be a list of column names to set as keys.

        `defaults` (optional) should be a dict from column names to default values.
        """

        kind_mapping_table = """
        b boolean
        i integer
        u integer
        f real
        M datetime
        O string
        S string
        U string
        """

        kind_mapping = dict(line.split() for line in kind_mapping_table.strip().split('\n'))

        keys = [k.lower() for k in ensure_list_if_string(keys)]

        default_mapping = dict(
            string='',
            datetime='1970-01-01 00:00:00',
            real=-1,
            integer=-1,
            boolean='false'
        )

        defaults = {k.lower(): v for k, v in (defaults or {}).items()}

        def dimensions():
            for dname, dtype in zip(df.columns, df.dtypes):
                typ = kind_mapping.get(dtype.kind)
                if not typ:
                    raise TypeError('Column %r has unknown dtype %r' % (dname, dtype))

                dname = dname.lower()
                yield dict(
                    name=dname,
                    type=typ,
                    default=defaults.get(dname, default_mapping[typ]),
                    key=dname in keys,
                )

        dataset = self.create_tablestore_dataset(name, list(dimensions()))
        dataset.upload_df(df)

        return dataset

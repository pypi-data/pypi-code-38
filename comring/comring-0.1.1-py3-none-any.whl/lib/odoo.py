import requests
import json
import logging
import uuid
import re
import operator
import yaml
from cachetools import cached, cachedmethod, TTLCache
from cachetools.keys import hashkey
from functools import partial

LOGGER = logging.getLogger(__name__)

def redact_log(msg):
    return re.sub(r'"?(password|passwd)"?\s*:\s*(.*)([, }{])', '<redacted>\\3', msg)

class Odoo(object):
    def __init__(self, url):
        self._url = url

    def _post(self, path, payload, cookies=None):
        url_path = '/'.join([self._url, path])

        payload_str = json.dumps(payload)
                
        logging.debug(redact_log(payload_str))
        return requests.post(url_path,
                             data=payload_str,
                             headers={'content-type': 'application/json', 'accept': 'application/json'},
                             cookies=cookies
        ).json()

    def _call(self, path, params, sess_id=None):
        payload = {
            'id': uuid.uuid1().int,
            'jsonrpc': '2.0',
            'method': 'call',
            'params': params
        }
        cookies = None
        if sess_id:
            cookies = dict(session_id=sess_id)

        res = self._post(path, payload, cookies)
        error = None
        result = None
        if 'error' in res:
            error = res['error']
        if 'result' in res:
            result = res['result']
        return (error, result)

    def login(self, db, user, password):
        login_params = {
            'db': db,
            'login': user,
            'password': password
        }
        error, result = self._call('web/session/authenticate', login_params)
        if result:
            if result['uid']:
                return Client(self, result)
            else:
                logging.error('Authentication error')
                raise RuntimeError('No UID returned from authentication API')
        if error:
            logging.error('Error while logging in: %s', error)
            raise RuntimeError('Error while authenticating: {}'.format(error))
        raise NotImplementedError('Code should not reach this point')

class Client(object):
    def __init__(self, odoo, session):
        self._odoo = odoo
        self._session = session
        logging.debug('Client created %s', session)

    def get_session_data(self, key, default=None):
        return self._session.get(key, default)

    def get_user_context(self, key, default=None):
        return self._session.get('user_context', {}).get(key, default)

    def set_default_context(self, context):
        for context_key in self._session.get('user_context', {}):
            context.setdefault(context_key, self._session['user_context'][context_key])

    def call(self, model, method, args, kwargs):
        path = '/'.join(['web','dataset','call_kw',model,method])
        if not kwargs:
            kwargs = {}
        context = kwargs.setdefault('context', {})
        self.set_default_context(context)

        params = {
            'model': model,
            'method': method,
            'args': args,
            'kwargs': kwargs
        }
        error, result = self._odoo._call(path, params, self._session['session_id'])
        if error:
            logging.error('Error during RPC call: %s', error)
            return None
        return result

    def read(self, model, ids, fields, context=None):
        kwargs = {'fields': fields}
        if context:
            kwargs['context'] = context
        return self.call(model, 'read', [ids], kwargs)

    def read_one(self, model, single_id, fields, context=None):
        res = self.read(model, [single_id], fields, context)
        if len(res) > 1:
            raise Exception('Expected one, got {}'.format(len(res)))
        return res[0]

    def search(self, model, domain, context=None):
        kwargs = {}
        if context:
            kwargs['context'] = context
        return self.call(model, 'search', [domain], kwargs)

    def search_one(self, model, domain, context=None):
        ids = self.search(model, domain, context)
        if len(ids) != 1:
            raise Exception('Search expected to find 1, but found {} instead'.format(len(ids)))
        return ids[0]

    def search_first(self, model, domain, context=None):
        return self.search(model, domain, context)[0]

    def search_read(self, model, domain, fields, context=None):
        kwargs = {'fields': fields}
        if context:
            kwargs['context'] = context
        return self.call(model, 'search_read', [domain], kwargs)

    def search_read_one(self, model, domain, fields, context=None):
        res = self.search_read(model, domain, fields, context)
        if len(res) > 1:
            raise Exception('Search-Read expected to find 1, but found {} instead'.format(len(res)))
        return res[0]

    def search_read_first(self, model, domain, fields, context=None):
        return self.search_read(model, domain, fields, context)[0]

    def create(self, model, vals, context=None):
        kwargs = {}
        if context:
            kwargs['context'] = context
        return self.call(model, 'create', [vals], kwargs)

    def write(self, model, ids, vals, context=None):
        kwargs = {}
        if context:
            kwargs['context'] = context
        return self.call(model, 'write', [ids, vals], kwargs)


ttl_cache = TTLCache(100000, 3600)

class Instance(object):
    def __init__(self, alias='', name='', kind='', url='', database='', user='', password='', cache_size=50000, cache_ttl=3600):
        self.alias = alias
        self.name = name
        self.kind = kind
        self.url = url
        self.database = database
        self.user = user
        self.password = password
        self.client = None
        self.cache = TTLCache(cache_size, cache_ttl)

    def connect(self):
        if self.client:
            return self.client
        server = Odoo(self.url)
        self.client = server.login(self.database, self.user, self.password)
        if not self.client:
            return False
        return self.client
 
    @cachedmethod(operator.attrgetter('cache'))
    def cached_read(self, model, id, fields):
        return self.client.read_one(model, id, fields)

envs_info = {}

def load_envs(filename):
    data = None
    try:
        with open(filename, 'r') as f:
            data = yaml.safe_load(f.read())
    except Exception as e:
        LOGGER.error('Error opening file %s for loading envs', filename, exc_info=e)
        return False
    if data:
        for env in data['environments']:
            envs_info[env] = data['environments'][env]
    return True

instances = {}

def get_instance(env_alias):
    inst = instances.get(env_alias, None)
    if not inst:
        env = envs_info.get(env_alias, None)
        if not env:
            raise Exception('Invalid env alias: {}'.format(env_alias))
        inst = Instance(
                alias=env_alias, name=env['name'], kind=env['kind'],
                url=env['url'], database=env['database'],
                user=env['user'], password=env['password'])
        instances[env_alias] = inst
    return inst

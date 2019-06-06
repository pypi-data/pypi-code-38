import json
import logging
import re
from string import Template

import requests
import requests_oauthlib
from oauthlib.oauth2 import BackendApplicationClient, OAuth2Error, OAuth2Token

# Python 2 and 3: urllib compatibility between both versions
try:
    from urllib.parse import urlencode, urlparse, parse_qs
except ImportError:
    from urllib import urlencode
    from urlparse import urlparse, parse_qs

from sequoia import error, http, registry, auth, env
from sequoia.auth import AuthType
from sequoia.http import HttpResponse

DIRECT_MODEL = 'direct'


class Client(object):
    """OAuth2 Compliant Client SDK for interacting with Sequoia services.
    """

    def __init__(self, registry_url, proxies=None, user_agent=None, backoff_strategy=None, adapters=None,
                 request_timeout=None, model_resolution=None, **auth_kwargs):
        logging.debug('Client initialising with registry_url=%s ', registry_url)
        self._registry_url = registry_url
        self._auth = auth.Auth(**auth_kwargs)
        self._proxies = proxies
        self._user_agent = user_agent
        self._create_client()
        self._register_adapters(adapters)
        self._request_timeout = request_timeout or env.DEFAULT_REQUEST_TIMEOUT_SECONDS
        self._model_resolution = model_resolution
        self._http = http.HttpExecutor(self._auth,
                                       proxies=self._proxies,
                                       user_agent=self._user_agent,
                                       session=self._oauth,
                                       request_timeout=self._request_timeout,
                                       backoff_strategy=backoff_strategy
                                       )
        self._populate_registry()

    def _create_client(self):
        if self._auth.auth_style is auth.AuthType.CLIENT_GRANT:
            self._client = BackendApplicationClient(
                client_id=self._auth.grant_client_id)
            self._oauth = requests_oauthlib.OAuth2Session(client=self._client)
        elif self._auth.auth_style is AuthType.NO_AUTH:
            pass
        elif self._auth.auth_style is AuthType.BYO_TOKEN:
            data = {'token_type': 'bearer',
                    'access_token': self._auth.auth}
            self._token = OAuth2Token(data)
            self._oauth = requests_oauthlib.OAuth2Session(token=self._token)
        else:
            raise NotImplementedError('Authentication type not supported')

    def _populate_registry(self):
        self._registry = registry.Registry(self._registry_url, self._http)
        if self._auth and self._auth.auth_style:
            if self._auth.auth_style == AuthType.CLIENT_GRANT:
                self._token = self._get_token()

    def _get_token(self):
        identity = self._registry['identity'].location
        oauth_token_url = identity + '/oauth/token'
        try:
            token = self._oauth.fetch_token(token_url=oauth_token_url,
                                            auth=self._auth.auth, timeout=self._request_timeout)
        except OAuth2Error as oauth2_error:
            raise error.AuthorisationError(str(oauth2_error.args[0]), cause=oauth2_error)

        return token

    def _register_adapters(self, adapters):
        if adapters:
            for adapter_registration in adapters:
                if self._auth.auth_style is AuthType.NO_AUTH:
                    self._oauth = requests.Session()
                self._oauth.mount(adapter_registration[0],
                                  adapter_registration[1])

    def __getattr__(self, item):
        return self._create_service_proxy(item)

    def __getitem__(self, item):
        return self._create_service_proxy(item)

    def _create_service_proxy(self, item):
        if not item.startswith('_'):
            return ServiceProxy(self._http, self._registry[item], self._model_resolution)
        return self.__dict__.get(item)


class ServiceProxy(object):
    _service_models = dict()

    def __init__(self, http, service, model_resolution=None):
        self._service = service
        self._http = http
        if model_resolution:
            try:
                self._descriptor = ServiceProxy._service_models.get(service)
                if not self._descriptor:
                    self._descriptor = self._http.get(service.location + '/descriptor/raw?_pretty=true').json
                    ServiceProxy._service_models[service] = self._descriptor
            except Exception:
                self._descriptor = None
                logging.exception('Service `%s` model could not be fetched')

    def __getattr__(self, resource):
        return self._create_endpoint_proxy(resource)

    def _create_endpoint_proxy(self, resource):
        if not resource.startswith('_') and not resource == 'business':
            return ResourceEndpointProxy(self._http, self._service, resource, descriptor=self._descriptor)
        return self.__dict__.get(resource)

    def __getitem__(self, resource):
        if resource != 'business':
            return self._create_endpoint_proxy(resource)
        return self.business

    def business(self, path_template):
        return BusinessEndpointProxy(self._http, self._service, path_template=path_template)


class ResourceEndpointProxy(object):
    """Proxy endpoint providing read/store/browse operations over Sequoia API endpoint.
    """

    def __init__(self, http, service, resource, descriptor=None):
        self.http = http
        self.service = service
        self.resource = resource
        self.service = service
        self.url = service.location + '/data/' + resource
        self.descriptor = descriptor

    def read(self, owner, ref):
        return self.http.get(self.url + '/' + ref, self._create_owner_param(owner), resource_name=self.resource)

    def store(self, owner, json_object):
        return self.http.post(self.url + '/', json_object, self._create_owner_param(owner), resource_name=self.resource)

    def browse(self, owner, criteria=None, fields=None, query_string=None, prefetch_pages=1):
        params = criteria.get_criteria_params() if criteria else {}
        params.update(self._create_owner_param(owner))
        params.update(self._create_fields_params(fields))

        return PageBrowser(endpoint=self, resource_name=self.resource, criteria=criteria,
                           query_string=query_string, params=params, prefetch_pages=prefetch_pages)

    def _create_fields_params(self, fields):
        if fields:
            return {'fields': ','.join(sorted(map(str, fields)))}
        return {}

    def delete(self, owner, ref):
        if isinstance(ref, list):
            refs = ",".join(ref)
        else:
            refs = ref
        params = dict()
        params.update(ResourceEndpointProxy._create_owner_param(owner))
        return self.http.delete(self.url + "/" + refs, params=params, resource_name=self.resource)

    def update(self, owner, json_string, ref, version):
        # Fixme Version header is no longer supported by resourceful API
        json_object = json.loads(json_string)
        ResourceEndpointProxy.validate_reference_to_update_with_json_reference(json_object[0], ref)
        params = dict()
        params.update(ResourceEndpointProxy._create_owner_param(owner))
        headers = ResourceEndpointProxy._create_version_header(version)
        try:
            return self.http.put(self.url + '/' + ref, json_string, params, headers=headers,
                                 resource_name=self.resource)
        except error.HttpError as e:
            if self._is_not_matching_version_exception(e):
                raise error.NotMatchingVersion('Document cannot be updated. Version does not match.', cause=e)
            else:
                raise e

    @staticmethod
    def _create_owner_param(owner):
        return {'owner': owner}

    @staticmethod
    def validate_reference_to_update_with_json_reference(json, ref):
        if 'ref' not in json or 'owner' not in json or 'name' not in json:
            raise error.ReferencesMismatchException(
                'Reference to update %s does not match with the resource reference. '
                'Resource does not contain ref, owner or name' % ref)

        if json['ref'] != ref:
            raise error.ReferencesMismatchException(
                'Reference to update %s does not match with the resource reference %s.' % (ref, json['ref']))

        resource_reference = "%s:%s" % (json['owner'], json['name'])
        if resource_reference != ref:
            raise error.ReferencesMismatchException(
                'Reference to update %s does not match with the resource reference %s.' % (ref, resource_reference))

    @staticmethod
    def _create_version_header(version):
        return {'If-Match': '"' + version + '"'}

    @staticmethod
    def _is_not_matching_version_exception(e):
        return e.status_code == 412 and e.message['error'] == 'Precondition Failed' \
               and e.message['message'] == 'document cannot be changed - versions do not match'


class LinkedResourcesPageBrowser(object):
    def __init__(self, endpoint, main_page_browser, resource, owner):
        self._endpoint = endpoint
        self._owner = owner
        self._main_page_browser = main_page_browser
        self._main_page_linked_data_sent = False
        self._resource = resource
        self._current_page_browser = None
        self._next_items = None

    @property
    def resources(self):
        if all([self._main_page_browser.full_json, 'linked' in self._main_page_browser.full_json,
                self._resource in self._main_page_browser.full_json['linked']]):
            return self._main_page_browser.full_json['linked'][self._resource]
        return None

    def __iter__(self):
        return self

    def __next__(self):
        if not self._main_page_linked_data_sent:
            self._next_items = self._next_fields_in_linked_resources()
            self._main_page_linked_data_sent = True
            http_response = self._main_page_browser.__next__()
            if http_response.full_json['linked'][self._resource]:
                return http_response.full_json['linked'][self._resource]

        if self._current_page_browser:
            try:
                return self._current_page_browser.__next__().resources
            except StopIteration:
                pass

        if self._next_items:
            next_item = self._next_items.pop(0)
            self._current_page_browser = PageBrowser(endpoint=self._endpoint, resource_name=self._resource,
                                                     query_string=urlparse(next_item).query,
                                                     params={'owner': self._owner})
            return self._current_page_browser.__next__().resources

        self._main_page_linked_data_sent = False
        return self.__next__()

    def next(self):
        return self.__next__()

    def _next_fields_in_linked_resources(self):
        return [linked_item['next'] for linked_item in self._linked_links() if self._next_in_linked_item(linked_item)]

    def _next_in_linked_item(self, linked_item):
        return 'next' in linked_item and 'page' in linked_item and linked_item['page'] == 5

    def _linked_links(self):
        if self._main_page_browser.full_json and all([
                'linked' in self._main_page_browser.full_json['meta'],
                self._resource in self._main_page_browser.full_json['meta']['linked']]):
            return self._main_page_browser.full_json['meta']['linked'][self._resource]
        return []


class PageBrowser(object):
    """
    Sequoia resource service pagination browser. This browser will fetch the content of `prefetch_pages` first pages
    and then will do lazy pagination load of rest of pages till finding a page with no next link.
    """

    def __init__(self, endpoint=None, resource_name=None, criteria=None, query_string=None, params=None,
                 prefetch_pages=1):
        self._prefetch_queue = []
        self._resource_name = resource_name
        self._endpoint = endpoint
        self.params = params
        self._criteria = criteria
        self.response_builder = ResponseBuilder(descriptor=endpoint.descriptor, criteria=self._criteria)
        self.query_string = query_string
        self.next_url = self._build_url()
        if prefetch_pages > 0:
            self._prefetch(prefetch_pages)

    def _prefetch(self, pages):
        i = pages
        while i:
            self.next_url, response = self._fetch(self.next_url)
            if response:
                self._prefetch_queue.append(response)

            if not self.next_url:
                break
            i -= 1

    def _fetch(self, next_url):
        self._remove_owner_if_needed(self.params, next_url)
        response = self._endpoint.http.get(next_url, self.params, resource_name=self._resource_name)
        response_wrapper = self._get_response(self._endpoint, response)
        if self._next_page(response):
            return '%s%s' % (self._endpoint.service.location, self._next_page(response)), response_wrapper
        return None, response_wrapper

    def _get_response(self, endpoint, response):
        return HttpResponse(response.raw, resource_name=endpoint.resource,
                            model_builder=self.response_builder.build) if endpoint.descriptor else response

    def _build_url(self):
        url_without_params = '%s/data/%s' % (self._endpoint.service.location, self._resource_name)
        return '%s?%s' % (url_without_params, self.query_string) if self.query_string else url_without_params

    def linked(self, resource):
        pb = PageBrowser(endpoint=self._endpoint, resource_name=self._resource_name,
                         criteria=self._criteria, query_string=self.query_string,
                         params=self.params)
        return LinkedResourcesPageBrowser(self._endpoint, pb, resource, self.params.get('owner'))

    def __getattr__(self, name):
        if self._prefetch_queue:
            return getattr(self._prefetch_queue[0], name)
        return None

    def __iter__(self):
        return self

    def __next__(self):
        if self._prefetch_queue:
            return self._prefetch_queue.pop(0)

        if self.next_url:
            self.next_url, response = self._fetch(self.next_url)
            return response

        raise StopIteration()

    def next(self):
        return self.__next__()

    def _next_page(self, response):
        return response.full_json['meta'].get('next', None)

    def _remove_owner_if_needed(self, params, url):
        if self._query_string_contains_owner(url):
            params.pop('owner', None)
            return params
        return params

    def _query_string_contains_owner(self, url):
        result = urlparse(url)
        return 'owner' in parse_qs(result.query)


class BusinessEndpointProxy(object):
    """Proxy endpoint providing read/store/browse operations over Sequoia API Business Endpoints with NOAUTH.
    """

    def __init__(self, http, service, path_template):
        self.http = http
        self.service = service
        self.url = service.location
        self.path_template = path_template

    def store(self, service, owner, content, ref, params=None):
        url_template = Template(self.path_template)
        params_formatted = None
        if params:
            params_formatted = '?' + urlencode(params)
        url = self.url + url_template.safe_substitute(service=service, owner=owner, ref=ref,
                                                      params=params_formatted if params else '')
        response = self.http.post(url, content, None, None, resource_name=None)
        return HttpResponse(response.raw, resource_name=None, model_builder=None)

    def browse(self, service, **kwargs):
        url_template = Template(self.path_template)
        url = self.url + url_template.safe_substitute(service=service, **kwargs)
        return self.http.get(url, resource_name=None)

    @staticmethod
    def _create_owner_param(owner):
        return {'owner': owner}


class ResponseBuilder(object):

    def __init__(self, descriptor=None, criteria=None):
        # TODO Discover model in installed libraries
        self._descriptor = descriptor
        self._criteria = criteria

    def build(self, response_json, resource_name):
        if response_json.get(resource_name):
            return self._build_with_criteria_and_descriptor(response_json, resource_name)
        logging.warning('Resource `%s` not found in response.', resource_name)
        return None

    def _build_with_criteria_and_descriptor(self, response_json, resource_name):
        if self._criteria and self._descriptor:
            return [self._create_model_instance(resource_name, resource, response_json.get('linked')) for
                    resource in response_json.get(resource_name)]
        return response_json.get(resource_name)

    def _get_class_name(self, main_resource_name):
        return self._descriptor['resourcefuls'][main_resource_name]['singularName']

    def _get_relationship_key(self, main_resource_name, related_resoure_name):
        try:
            return self._descriptor['resourcefuls'][main_resource_name]['relationships'][related_resoure_name][
                'fieldNamePath']
        except KeyError:
            logging.warning('Included resource `%s` not listed as relationship in `%s` service metadata',
                            related_resoure_name, main_resource_name)
            return None

    def _create_model_instance(self, main_resource_name, main_resource, linked=None):
        return self._resolve_direct_inclusions(main_resource_name, main_resource, linked)

    def _resolve_direct_inclusions(self, main_resource_name, main_resource, linked=None):
        if linked:
            for inclusion in self._criteria.inclusion_entries:
                if inclusion.resource_name in linked:
                    main_resource[inclusion.resource_name] = self._resolve_direct_inclusion(inclusion.resource_name,
                                                                                            linked, main_resource_name,
                                                                                            main_resource)
                else:
                    logging.info('Resources `%s` not included in response', inclusion.resource_name)

        return main_resource

    def _resolve_direct_inclusion(self, resource_name, linked, parent_resource_name, parent_resource):
        linked_inclusions = linked[resource_name]
        relation_field = self._get_relationship_key(parent_resource_name, resource_name)
        if not relation_field:
            logging.info('Child resource `%s` could not be linked to `%s` parent resources', resource_name,
                         parent_resource_name)
            return None
        if relation_field in parent_resource:
            if linked_inclusions and 'ref' not in linked_inclusions[0]:
                logging.info('Linked resources with no `ref` field, linked resources skipped')
                return None
            return [self._create_model_instance(resource_name, entry, None)
                    for entry in linked_inclusions if entry['ref'] in parent_resource[relation_field]]
        logging.info('Parent resource `%s` with no linked `%s` resources', parent_resource_name,
                     resource_name)
        return None

    def _dash_to_camelcase(self, value):
        return re.sub(r'(?!^)-([a-zA-Z])', lambda m: m.group(1).upper(), value).title()

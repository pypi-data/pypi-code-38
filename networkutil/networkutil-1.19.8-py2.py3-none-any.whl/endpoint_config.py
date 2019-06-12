# encoding: utf-8

import ast
import attr
import json
import logging_helper
from future.builtins import str
from future.utils import python_2_unicode_compatible
from configurationutil import Configuration, cfg_params
from ._metadata import __version__, __authorshort__, __module_name__
from .resources import templates, schema

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
ENDPOINT_LOOKUP_CONFIG = u'endpoint_lookup'

ENDPOINTS_CONFIG = u'{c}.endpoints'.format(c=ENDPOINT_LOOKUP_CONFIG)
ENVIRONMENTS_CONFIG = u'{c}.environments'.format(c=ENDPOINT_LOOKUP_CONFIG)
APIS_CONFIG = u'{c}.apis'.format(c=ENDPOINT_LOOKUP_CONFIG)

TEMPLATE = templates.endpoints

ATTR_STRING_VALIDATOR = attr.validators.instance_of(str)


# Endpoint property keys
@attr.s(frozen=True)
class _EPConstant(object):
    port = attr.ib(default=u'port', init=False)
    env = attr.ib(default=u'environment', init=False)
    apis = attr.ib(default=u'apis', init=False)


EPConstant = _EPConstant()


# API property keys
@attr.s(frozen=True)
class _APIConstant(object):
    key = attr.ib(default=u'key', init=False)
    secret = attr.ib(default=u'secret', init=False)
    user = attr.ib(default=u'user', init=False)
    password = attr.ib(default=u'password', init=False)
    methods = attr.ib(default=u'methods', init=False)
    params = attr.ib(default=u'parameters', init=False)


APIConstant = _APIConstant()


def _register_endpoints_lookup_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=ENDPOINT_LOOKUP_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=schema.endpoints)

    return cfg


class EnvAndAPIs(object):

    def __init__(self):
        self._cfg = _register_endpoints_lookup_config()

    def get_apis(self):  # Only used internally to class

        apis = self._cfg[APIS_CONFIG]
        #logging.debug(u'APIS: {a}'.format(a=apis))  # This produces way too much log!

        # Return a copy so that the retrieved does not get modified in config unless explicitly requested!
        return apis.copy()

    def get_api_list(self):
        return self.get_apis().keys()

    def get_environments(self):

        environments = self._cfg[ENVIRONMENTS_CONFIG]
        logging.debug(u'ENVS: {e}'.format(e=environments))

        # Return a copy so that the retrieved does not get modified in config unless explicitly requested!
        return environments

    def get_apis_for_environment(self,
                                 env):

        return self._cfg.find(APIS_CONFIG, [(env, None)]).keys()

    def environment_is_used_by_api(self,  # method no longer necessary
                                   env):
        return bool(self.get_apis_for_environment(env))

    def get_environments_for_api(self,
                                 api):

        apis = self.get_apis()
        api = apis.get(api)

        return api.keys()

    def get_api_environment(self,  # Only used by Endpoints class below
                            api,
                            env):

        apis = self.get_apis()
        try:
            api_environments = apis[api]
        except KeyError:
            raise ValueError(u'API "{api}" not found in config.'
                             .format(api=api))
        try:
            return api_environments[env]
        except KeyError:
            raise ValueError(u'"{env}" environment not found for "{api}" API'
                             .format(env=env,
                                     api=api))


@python_2_unicode_compatible
class Endpoint(object):

    def __init__(self,
                 hostname,
                 port,
                 environment,
                 api,
                 methods=None,
                 **parameters):

        setattr(self, u'hostname', hostname)
        setattr(self, u'port', port)
        setattr(self, u'api', api)
        setattr(self, u'environment', environment)
        setattr(self, u'methods', methods if methods is not None else {})
        if isinstance(self.methods, str):
            self.methods = ast.literal_eval(self.methods)
        self._parameters = self._extract_parameters(parameters)

    def _extract_parameters(self,
                            parameters):

        """
        Takes a dict of key value pairs and turns then into instance attributes

        :param dict parameters:

        :return:
        """

        # If parameters has a parameters key lift it into top level dict
        if APIConstant.params in parameters:
            try:
                parameters.update(parameters[APIConstant.params])
            except ValueError:
                parameters.update(json.loads(parameters[APIConstant.params]))
            del parameters[APIConstant.params]

        # Set each parameter as an attribute
        for key, value in iter(parameters.items()):
            setattr(self, key, value)

        return parameters

    def endpoint(self,
                 method_name=None,
                 default_method=u''):

        method = self.method(method_name=method_name,
                             default_method=default_method)

        endpoint = u'{host}:{port}{method_sep}{method}'.format(host=self.hostname,
                                                               port=self.port,
                                                               method_sep=u'/' if not method.startswith(u'/') else u'',
                                                               method=method)
        return endpoint

    def method(self,
               method_name,
               default_method=u''):
        return self.methods.get(method_name, default_method)

    def url_match_length(self,
                         url):

        url_match_length = -1

        if u'://' in url:
            protocol, url = url.split(u'://')

        hostname = url.split(u'/')[0]

        if u':' in hostname:
            hostname, port = hostname.split(u':')

            if int(port) != self.port:
                return url_match_length

        if hostname != self.hostname:
            return url_match_length

        url_match_length = 0  # Match for hostname

        call = u'/'.join(url.split(u'/')[1:])

        for api_signature in self.methods.values():
            if (len(api_signature) > url_match_length and
                    call.startswith(api_signature)):
                url_match_length = len(api_signature)

        if url_match_length < 0:
            raise LookupError(u'URL does not match endpoint')

        return url_match_length

    def __str__(self):
        string = (u'hostname: {hostname}:{port}\n'
                  u'api: {api}\n'
                  u'environment: {env}\n'.format(hostname=self.hostname,
                                                 port=self.port,
                                                 api=self.api,
                                                 env=self.environment))

        if self.methods:
            methods = [u'{key}:{value}\n'.format(key=key,
                                                 value=value)
                       for key, value in iter(self.methods.items())]

            string += (u'methods: {methods}'
                       .format(methods=u'         '.join(methods)))

        for key, value in iter(self._parameters.items()):
            string += u'{key}: {value}\n'.format(key=key,
                                                 value=value)

        return string


class Endpoints(object):

    def __init__(self):
        self._cfg = _register_endpoints_lookup_config()
        self.env_and_apis = EnvAndAPIs()
        self._endpoints = self.__load_endpoints()

    def __load_endpoints(self):

        endpoints = []

        for ep_name, ep in iter(self.raw_endpoints.items()):
            for api in ep[EPConstant.apis]:
                ep_kwargs = {
                    u'hostname': ep_name,
                    u'port': ep[EPConstant.port],
                    u'environment': ep[EPConstant.env],
                    u'api': api
                }

                # Add API env config
                api_cfg = self.env_and_apis.get_api_environment(api, ep[EPConstant.env])
                ep_kwargs.update(api_cfg)

                endpoints.append(Endpoint(**ep_kwargs))

        return endpoints

    @property
    def raw_endpoints(self):

        endpoints = self._cfg[ENDPOINTS_CONFIG]
        logging.debug(u'Endpoints: {e}'.format(e=endpoints))

        # Return a copy so that modifications of the retrieved do not get saved in config unless explicitly requested!
        return endpoints.copy()

    def __iter__(self):
        return iter(self._endpoints)

    @staticmethod
    def __single_endpoint(endpoints,
                          conditions):

        """
        checks for endpoints list having just one item and returns it in that
        case or raises an exception otherwise

        :param endpoints: [Endpoint,...Endpoint].
        :param conditions: string indicating the list of conditions used
                           in the lookup. This is just for logging exceptions.
        :return: Endpoint
        """

        if isinstance(endpoints, Endpoint):
            return endpoints

        if len(endpoints) == 0:
            raise LookupError(u'No matching endpoints for {conditions}'
                              .format(conditions=conditions))

        elif len(endpoints) > 1:
            raise LookupError(u'Multiple matching endpoints for {conditions}'
                              .format(conditions=conditions))

        return endpoints[0]

    def get_endpoint(self,
                     api,
                     environment):

        logging.debug(api)
        logging.debug(environment)

        conditions = (u'api={api}; environment={environment}'
                      .format(api=api,
                              environment=environment))

        matching_endpoints = [endpoint for endpoint in self
                              if endpoint.api == api
                              and endpoint.environment == environment]

        return self.__single_endpoint(endpoints=matching_endpoints,
                                      conditions=conditions)

    def get_endpoint_for_request(self,
                                 url):

        logging.debug(url)
        best_match = - 1
        matched_endpoints = []

        for endpoint in self:
            try:
                matched_len = endpoint.url_match_length(url)
            except LookupError:
                pass
            else:
                if matched_len > -1:
                    if matched_len > best_match:
                        matched_endpoints = [endpoint]
                        best_match = matched_len

                    elif matched_len == best_match:
                        matched_endpoints.append(endpoint)

        if len(matched_endpoints) == 1:
            return matched_endpoints[-1]

        if len(matched_endpoints) == 0:
            raise LookupError(u'No endpoint match for: {url}'.format(url=url))

        raise LookupError(u'Multiple matching endpoints for: {url}\n'
                          u'(Check your endpoint config)'.format(url=url))

    def get_apis_for_host(self,
                          hostname):
        return [endpoint.api
                for endpoint in self
                if hostname == endpoint.hostname]

    def get_environment_for_host(self,
                                 hostname):

        matched_environments = set([endpoint.environment
                                    for endpoint in self
                                    if endpoint.hostname == hostname])

        if len(matched_environments) != 1:
            raise LookupError(u'Ambiguous environments for {hostname}'
                              .format(hostname=hostname))

        return matched_environments.pop()

    def get_endpoint_apis(self):
        endpoint_apis = {endpoint.hostname: [] for endpoint in self}
        for endpoint in self:
            endpoint_apis[endpoint.hostname].append(endpoint.api)
        return endpoint_apis

    def get_endpoint_for_api_and_environment(self,  # This is the same as self.get_endpoint!!
                                             api,
                                             environment):
        endpoints = [endpoint
                     for endpoint in self
                     if endpoint.api == api
                     and endpoint.environment == environment]

        if len(endpoints) > 1:
            raise ValueError(u"Multiple endpoints for API:{api}; "
                             u"Environment:{env}".format(api=api,
                                                         env=environment))
        elif not endpoints:
            raise ValueError(u"No endpoint matches API:{api}; "
                             u"Environment:{env}".format(api=api,
                                                         env=environment))
        return endpoints[0]

    # This one is not used
    def get_endpoints_for_apis_and_environment(self,
                                               apis,
                                               environment):
        return [self.get_endpoint_for_api_and_environment(
                    api=api,
                    environment=environment)
                for api in apis]

    def get_endpoints_for_api(self,  # Only used by APIFrame.delete_api
                              api):
        return [endpoint for endpoint in self if api == endpoint.api]

    def get_endpoints_for_environment(self,  # Only used by below
                                      env):
        return [endpoint for endpoint in self if endpoint.environment == env]

    def environment_is_used(self,  # Only used by EnvironmentsFrame.delete
                            env):
        return bool(self.get_endpoints_for_environment(env))

    def get_endpoints_for_environment_and_api(self,  # Only used by below
                                              api,
                                              env):
        return [endpoint for endpoint in self
                if api == endpoint.api and env == endpoint.environment]

    def environment_and_api_are_used_by_an_endpoint(self,  # Only used by APIFrame.delete_api_env
                                                    api,
                                                    env):
        return bool(self.get_endpoints_for_environment_and_api(api=api,
                                                               env=env))


try:
    null_endpoint

except NameError:
    null_endpoint = Endpoint(hostname=u'<endpoint_not_configured>',
                             port=0,
                             environment=u'Null',
                             api=u'Null')

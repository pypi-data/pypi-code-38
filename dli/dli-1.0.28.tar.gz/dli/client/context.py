import requests
from requests_toolbelt.adapters import host_header_ssl
from six.moves.urllib.parse import urlparse

from .dli_request_factory_factory import DliRequestFactoryFactory
from pypermedia import HypermediaClient
from pypermedia.client import SirenBuilder
from pypermedia.siren import SirenEntity, _create_action_fn

import jwt
import datetime
import logging


logger = logging.getLogger(__name__)


class Context(object):

    def __init__(self, api_key, api_root, host, auth_key):
        self.api_key = api_key
        self.api_root = api_root
        self.auth_key = auth_key
        self.cache = {}

        self.request_factory = DliRequestFactoryFactory(
            api_root, host, lambda: self.get_header_with_auth()
        ).request_factory

        self.request_session = self.create_request_session(
            api_root,
            host
        )

        self.s3_keys = {}
        self.token_expires_on = self.get_expiration_date(auth_key)

    @staticmethod
    def create_request_session(root, host):
        # build the requests sessions that pypermedia will use
        # to submit requests
        session = requests.Session()

        # when no dns is available and the user is using an ip address
        # to reach the catalogue
        # we need to force the cert validation to be against
        # the host header, and not the host in the uri
        # (we only do this if the scheme of the root is https)
        if host and urlparse(root).scheme == "https":
            session.mount(
                'https://',
                host_header_ssl.HostHeaderSSLAdapter()
            )

        return session

    @staticmethod
    def get_expiration_date(token):
        # use a default_timeout if the token can't be decoded
        # until the proper endpoint is added on the catalog
        default_timeout = (
            datetime.datetime.utcnow() +
            datetime.timedelta(minutes=55)
        )

        try:
            # get the expiration from the jwt auth token
            decoded_token = jwt.get_unverified_header(token)
            if 'exp' not in decoded_token:
                return default_timeout 

            return datetime.datetime.fromtimestamp(
                decoded_token['exp']
            )

        except Exception:
            return default_timeout

    @property
    def session_expired(self):
        # by default we don't want to fail if we could not decode the token
        # so if the ``token_expiry`` is undefined we assume the session
        # is valid
        if not self.token_expires_on:
            return False

        return datetime.datetime.utcnow() > self.token_expires_on

    def get_header_with_auth(self):
        auth_header = "Bearer {}".format(self.auth_key)
        return {"Authorization": auth_header}

    def uri_with_root(self, relative_path):
        return "{}/{}".format(self.api_root, relative_path)

    # not a decorator since we want to access the local
    # cache instance (which needs to be evicted when the session/context
    # is recreated)
    def memoized(self, func, key=None):
        key = key or func.__name__
        if key not in self.cache:
            self.cache[key] = func()

        return self.cache[key]

    def get_root_siren(self):
        return HypermediaClient.connect(
            self.api_root,
            session=self.request_session,
            request_factory=self.request_factory,
            builder=PatchedSirenBuilder
        )


class PatchedSirenBuilder(SirenBuilder):

    def _construct_entity(self, entity_dict):
        """
        We need to patch the actions as there is no ``radio`` support
        on the current pypermedia version.

        To avoid code duplication, this function will attempt to call the parent
        and replace the created actions with our custom ones.
        """

        # pypermedia does not like any custom attributes
        # not even those in the spec
        for action in entity_dict.get("actions", []):
            if "allowed" in action:
                del action["allowed"]

        entity = super(PatchedSirenBuilder, self)._construct_entity(entity_dict)

        return PatchedSirenEntity(
            classnames=entity.classnames,
            properties=entity.properties,
            actions=entity.actions,
            links=entity.links,
            entities=entity.entities,
            rel=entity.rel,
            verify=entity.verify,
            request_factory=entity.request_factory
        )


class PatchedSirenEntity(SirenEntity):

    def as_python_object(self):
        ModelClass = type(str(self.get_primary_classname()), (), self.properties)

        siren_builder = PatchedSirenBuilder(verify=self.verify, request_factory=self.request_factory)
        # add actions as methods
        for action in self.actions:
            method_name = SirenEntity._create_python_method_name(action.name)
            method_def = _create_action_fn(action, siren_builder)
            setattr(ModelClass, method_name, method_def)

        # add links as methods
        for link in self.links:
            for rel in link.rel:
                method_name = SirenEntity._create_python_method_name(rel)
                siren_builder = PatchedSirenBuilder(verify=self.verify, request_factory=self.request_factory)
                method_def = _create_action_fn(link, siren_builder)

                setattr(ModelClass, method_name, method_def)

        def get_entity(obj, rel):
            matching_entities = self.get_entities(rel) or []
            for x in matching_entities:
                yield x.as_python_object()

        setattr(ModelClass, 'get_entities', get_entity)

        return ModelClass()

"""
Patch boto3 functionality so that you can retrieve the arn
from any given resource instance
"""

import boto3
import os
from copy import copy
from boto3.exceptions import ResourceLoadException
from boto3.resources.params import create_request_parameters, build_param_structure, get_data_member
from botocore import xform_name
from string import Formatter

import inspect
import logging

logger = logging.getLogger(__name__)


class ServiceContext(object):
    def __init__(self,
                 service_name,
                 service_model,
                 service_waiter_model,
                 resource_json_definitions,
                 session=None):
        self._service_name = service_name
        self._service_model = service_model
        self._service_waiter_model = service_waiter_model
        self._resource_json_definitions = resource_json_definitions
        self._session = session
        if not self._session:
            # HACK: this is very brittle and should idealy be fixed with an
            # upstream patch https://github.com/boto/boto3/pull/898
            session = copy(inspect.currentframe().f_back.f_locals['self'])
            if session is None or type(session) != boto3.Session:
                raise Exception('Unable to get session from stack frame.')
            else:
                self._session = session

    @property
    def service_name(self):
        return self._service_name

    @property
    def service_model(self):
        return self._service_model

    @property
    def service_waiter_model(self):
        return self._service_waiter_model

    @property
    def resource_json_definitions(self):
        return self._resource_json_definitions

    @property
    def session(self):
        return self._session


class PatchedResourceFactory(boto3.resources.factory.ResourceFactory):
    def load_from_definition(self, *args, **kwargs):
        service_context = kwargs['service_context']
        cls = boto3.resources.factory.ResourceFactory.load_from_definition(
            self, *args, **kwargs)
        cls.meta.session = service_context._session
        attrs = {'meta': cls.meta}

        service_name = service_context.service_name
        resource_name = kwargs['resource_name']
        api_version = None  # TODO: multiple arn versions?
        loader = service_context._session._loader

        # Ensure the boto3-arn-patch data directory
        # is in the loader search path
        loader.search_paths.append(os.path.join(
            os.path.dirname(__file__), 'data'))

        arn_model = loader.load_service_model(service_name,
                                              'arns-1',
                                              api_version)

        arn_model = arn_model.get('resources', {}).get(resource_name, {})

        self._load_arn(attrs, cls.meta, arn_model)
        cls = type(cls.__name__, (cls, ), attrs)
        return cls

    def _load_arn(self, attrs, meta, arn_model): # noqa
        arn_config = arn_model.get('arn', False)

        # Only define an arn if the resource has a defined arn format
        if arn_config:
            arn_property = None
            format_string = arn_config.get('formatString', False)
            data_path = arn_config.get('dataPath', False)
            replace_args = arn_config.get('replace', False)

            if format_string:

                def construct_arn(self):
                    formatter = Formatter()
                    mapping = {}
                    keys = [k[1] for k in formatter.parse(format_string)
                            if k[1]]
                    keys = set(keys)

                    if 'partition' in keys:
                        keys.remove('partition')
                        mapping['partition'] = self.meta.client.meta.partition
                    if 'service' in keys:
                        keys.remove('service')
                        mapping['service'] = self.meta.service_name
                    if 'region' in keys:
                        keys.remove('region')
                        mapping['region'] = self.meta.session.region_name
                    if 'account-id' in keys:
                        keys.remove('account-id')
                        mapping['account-id'] = self.meta.session.account_id

                    # Currently supports account of only top level properties
                    for key in keys:
                        mapping[key] = getattr(self, key)
                        # TODO error handling
                    if isinstance(replace_args, list) and len(replace_args) == 2:
                        return format_string.format(**mapping).replace(replace_args[0], replace_args[1])
                    else:
                        return format_string.format(**mapping)

                arn_property = property(construct_arn)
            elif data_path:

                def arn_path_loader(self):
                    if self.meta.data is None:
                        if hasattr(self, 'load'):
                            self.load()
                        else:
                            raise ResourceLoadException(
                                '{0} has no load method'.format(
                                    self.__class__.__name__))

                    data = self.meta.data
                    for key in data_path:
                        data = data[key]  # TODO: Error handling
                    return data

                arn_property = property(arn_path_loader)

            if not (arn_property):
                raise (NotImplementedError)

            # Rename arn if an attribute already exists
            key = '_arn' if 'arn' in attrs else 'arn'
            attrs[key] = arn_property


class PatchedResourceMeta(boto3.resources.base.ResourceMeta):
    def __init__(self, *args, **kwargs):
        session = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)
        self.session = session



def _create_request_parameters(parent, request_model, params=None, index=None):
    """
    Handle request parameters that can be filled in from identifiers,
    resource data members or constants.

    By passing ``params``, you can invoke this method multiple times and
    build up a parameter dict over time, which is particularly useful
    for reverse JMESPath expressions that append to lists.

    :type parent: ServiceResource
    :param parent: The resource instance to which this action is attached.
    :type request_model: :py:class:`~boto3.resources.model.Request`
    :param request_model: The action request model.
    :type params: dict
    :param params: If set, then add to this existing dict. It is both
                   edited in-place and returned.
    :type index: int
    :param index: The position of an item within a list
    :rtype: dict
    :return: Pre-filled parameters to be sent to the request operation.
    """
    if params is None:
        params = {}

    for param in request_model.params:
        source = param.source
        target = param.target

        if source == 'identifier':
            # Resource identifier, e.g. queue.url
            value = getattr(parent, xform_name(param.name))
        elif source == 'data':
            # If this is a data member then it may incur a load
            # action before returning the value.
            value = get_data_member(parent, param.path)
        elif source in ['string', 'integer', 'boolean']:
            # These are hard-coded values in the definition
            value = param.value
        elif source == 'input':
            # This is provided by the user, so ignore it here
            continue
        elif source == 'arn':
            value = parent.arn
        else:
            raise NotImplementedError(
                'Unsupported source type: {0}'.format(source))

        build_param_structure(params, target, value, index)

    return params


def patch_session():
    @property
    def account_id(self):
        """
        The **read-only** account id.
        """
        try:
            return self._account_id
        except AttributeError:
            # TODO: Error handling
            account_id = self.client('sts').get_caller_identity()['Account']
            self._account_id = account_id
        return self._account_id

    logger.info('Patching Session.account_id')
    boto3.Session.account_id = account_id


def patch_service_context():
    logger.info('Patching ServiceContext')
    boto3.utils.ServiceContext = ServiceContext


def patch_create_request_parameters():
    logger.info('Patching create_request_parameter')
    boto3.resources.params.create_request_parameters = _create_request_parameters
    boto3.resources.action.create_request_parameters = _create_request_parameters
    boto3.resources.collection.create_request_parameters = _create_request_parameters


def patch_resource_factory():
    logger.info('Patching ResourceFactory')
    boto3.session.ResourceFactory = PatchedResourceFactory


def patch_resource_meta():
    logger.info('Patching ResourceMeta')
    boto3.resources.factory.ResourceMeta = PatchedResourceMeta
    boto3.resources.base.ResourceMeta = PatchedResourceMeta

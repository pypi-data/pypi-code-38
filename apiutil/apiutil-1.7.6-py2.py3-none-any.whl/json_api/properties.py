# -*- coding: utf-8 -*-

import json
from requests.models import Response
from tableutil import Table
from classutils.decorators import deprecated, class_cache_result, clear_class_cached_results
from . import MandatoryFieldMissing
from . import JsonApiRequestResponse

CLASS_NAME = u'class_name'
KEY = u'key'
MANDATORY = u'mandatory'
OPTIONAL = u'optional'
PROPERTY = u'property'
TYPE = u'cast'
PROPERTY_NAME = u'property_name'
PROPERTIES = u'properties'
DEFAULT = u'default'
ATTRIBUTES = u'attributes'
FILENAME = u"filename"
MIXIN_IMPORTS = u'mixin_imports'


class JsonApiPropertiesClass(object):

    ALLOW_REDIRECTS = False

    def __init__(self,
                 response=None,
                 request=None,
                 parent=None,
                 **kwargs):
        """
        Provides base class for API classes that use properties instead of
        keys into a dictionary.

        It's not mandatory to call __init__. You can explicitly set self.response_dict instead
        if that makes more sense in your subclass

        :param response: One of: None - Expect the request method to be overriden that returns
                                        one of the remaining response types...
                                 requests.models.Response - request has already been made
                                 JSON String - request has been made / this is part of a response
                                               hierarchy.
                                 Dictionary - JSON has already been unpacked. (Don't supply lists)
        :param parent: Can pass the parent object, so that a subclass can access its properties.
                       Useful inside the request method, for example.
        :param kwargs: additional parameters can be passed and stored for later use
        """

        if kwargs:
            self._kwargs = kwargs
        self._parent = parent

        if not request:
            try:
                request = self.get_property(u'_request')
            except ValueError:
                pass  # _request is not in the object tree

        if response is None:
            # No response, must fetch
            response = self._send_request(request)
            # May have to do something special for web socket requests
            # but for now rely on passing the request

        if isinstance(response, Response):
            self._request = request if request else response.url
            self._response = response
            response = response.json()

        elif isinstance(response, JsonApiRequestResponse):
            self._original_json_api_request_response = response
            self._request = response.request
            self._response = response.response
            response = response.response
        else:
            self._request = request
            self._response = response

        try:
            self._response_dict = json.loads(response)
        except:
            self._response_dict = response

        super(JsonApiPropertiesClass, self).__init__()  # Required for co-operative multiple inheritance

    def get_kwarg(self,
                  key):
       return self.get_property(u'_kwargs').get(key)


    @property
    def _request_headers(self):
        return None

    @property
    def _request_parameters(self):
        return None

    def _send_request(self,
                      request):
        raise NotImplementedError(u'response==None passed for response {cls} '
                                  u'where the _send_request method has not be overridden.'
                                  u'request=={request}'
                                  .format(cls=str(self.__class__),
                                          request=request))

    @deprecated
    def mandatory(self,
                  key):
        try:
            return self._response_dict[key]
        except KeyError:
            raise MandatoryFieldMissing(key)

    @deprecated
    def optional(self,
                 key,
                 default=None):

        try:
            return self._response_dict.get(key, default)
        except AttributeError:
            raise TypeError(u'API response is not JSON')

    def _get_mandatory_field_value(self,
                                   key,
                                   cast=None):
        try:
            return (cast(self._response_dict[key])
                    if cast
                    else self._response_dict[key])
        except KeyError:
            raise MandatoryFieldMissing(key)

    def _get_optional_field_value(self,
                                  key,
                                  default=None,
                                  cast=None):
        try:
            return (cast(self._response_dict.get(key, default))
                    if cast
                    else self._response_dict.get(key, default))
        except TypeError:
            raise TypeError(u'API response is not JSON')

    @clear_class_cached_results
    def _set_field_value(self,
                         key,
                         value):
        # No way to reverse cast. Not planning on solving this edge case.
        self._response_dict[key] = value

    def _json_dump_default(self):
        """
        Use to extend json.JSONEncoder or
        in json.dump/dumps calls as the default parameter value
        :return:
        """
        return self._response_dict

    @staticmethod
    def mandatory_field(key,
                        cast=None):
        return property(lambda self: self._get_mandatory_field_value(key=key,
                                                                     cast=cast),
                        lambda self, value: self._set_field_value(key=key,
                                                                  value=value)
                        )

    @staticmethod
    def optional_field(key,
                       default=None,
                       cast=None):
        return property(lambda self: self._get_optional_field_value(key=key,
                                                                    default=default,
                                                                    cast=cast),
                        lambda self, value: self._set_field_value(key=key,
                                                                  value=value))

    def get_property(self,
                     item):
        try:
            return getattr(self, item)
        except AttributeError:
            pass

        if self._parent is self:
            raise ValueError(u'Could not find "{item}" in object tree'.format(item=item))
        try:
            return self._parent.get_property(item)
        except AttributeError as ae:
            raise ValueError(u'Could not find "{item}" in object tree'.format(item=item))

    @property
    def _title(self):
        """Override to add a customised title to the table"""
        return self._request

    @property
    @class_cache_result
    def table(self):
        """
        Generates a table from self.response_dict.
        Override if a custom table is required.
        :return: Table instance
        """
        try:
            conversions = self.CONVERSIONS
        except:
            conversions = None

        return Table.init_from_tree(tree=self._response_dict,
                                    title=self._title,
                                    conversions=conversions)

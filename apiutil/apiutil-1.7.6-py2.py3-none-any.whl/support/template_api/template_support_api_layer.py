# encoding: utf-8

from apiutil.support import APISupportLayer
from ._exceptions import TemplateAPIError, TemplateAPIMissing, TemplateAPIUnresponsive
from .apis import template


class EmptyTemplateAPILayer(APISupportLayer):
    """ An Empty API support layer!  Pretty useless really! """


class TemplateAPILayer(APISupportLayer):
    """ An API support layer with a single API """

    APIS = [
        template
    ]

    # Custom Exceptions
    API_ERROR = TemplateAPIError
    API_MISSING = TemplateAPIMissing
    API_UNRESPONSIVE = TemplateAPIUnresponsive

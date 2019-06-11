# -*- coding: utf-8 -*-

from apiutil.support import APIError, APIMissing, APIUnresponsive

__all__ = ['TemplateAPIUnresponsive',
           'TemplateAPIMissing',
           'TemplateAPIError']


class TemplateAPIUnresponsive(APIUnresponsive):
    pass


class TemplateAPIMissing(APIMissing):
    pass


class TemplateAPIError(APIError):
    pass

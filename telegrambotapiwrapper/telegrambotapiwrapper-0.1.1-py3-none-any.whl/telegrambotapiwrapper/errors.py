# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""Application еxceptions."""


class Error(Exception):
    """Base exception class."""


class ResponseError(Error):
    """Errors related to responses from the API."""


class RequestError(Error):
    """Errors related to API requests."""


class RequestResultIsNotOk(ResponseError):
    """Exception thrown when API response is not OK."""

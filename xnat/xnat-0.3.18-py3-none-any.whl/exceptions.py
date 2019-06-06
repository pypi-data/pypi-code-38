# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The specific exceptions that are thrown by XNATpy
"""

from __future__ import absolute_import
import requests


class XNATError(Exception):
    """
    General base class for all XNAT related errors
    """


class XNATValueError(XNATError, ValueError):
    """
    XNATpy specific value error
    """


class XNATResponseError(XNATValueError):
    """
    XNATpy error when the response value is not correct
    """


class XNATIOError(XNATError, IOError):
    """
    XNATpy error for when there are IO problems
    """


class XNATUploadError(XNATIOError):
    """
    XNATpy error for when there is a problem uploading
    """


class XNATSSLError(XNATError, requests.exceptions.SSLError):
    """
    XNATpy error for when there is an SSL problem
    """


# Inherit from ValueError for backwards compatibility (they used to be value errors)
class XNATAuthError(XNATError, ValueError):
    """
    XNATpy error for when there is a problem with logging in or authentication
    """


class XNATLoginFailedError(XNATAuthError):
    """
    Failed to login, this usually means the credentials are incorrect.
    """


class XNATExpiredCredentialsError(XNATAuthError):
    """
    The users credentials are expired and should be updated in the web interface of XNAT
    """

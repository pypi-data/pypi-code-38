# Copyright 2011-2015 Biomedical Imaging Group Rotterdam, Departments of
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

from __future__ import absolute_import
from __future__ import unicode_literals
import mimetypes
import collections

from .prearchive import PrearchiveSession
from .exceptions import XNATResponseError, XNATValueError

TokenResult = collections.namedtuple('TokenResult', ('alias', 'secret'))


class Services(object):
    """
    The class representing all service functions in XNAT found in the
    /data/services REST directory
    """
    def __init__(self, xnat_session):
        self._xnat_session = xnat_session

    @property
    def xnat_session(self):
        return self._xnat_session

    def dicom_dump(self, src, fields=None):
        """
        Retrieve a dicom dump as a JSON data structure
        See the XAPI documentation for more detailed information: `DICOM Dump Service <https://wiki.xnat.org/display/XAPI/DICOM+Dump+Service+API>`_

        :param str src: The url of the scan to generate the DICOM dump for
        :param list fields: Fields to filter for DICOM tags. It can either a tag name or tag number in the format GGGGEEEE (G = Group number, E = Element number)
        :return: JSON object (dict) representation of DICOM header
        :rtype: dict
        """
        query_string = {'src': src}
        if fields is not None:
            if not isinstance(fields, (list, str)):
                raise XNATValueError('The fields argument to .dicom_dump() should be list or a str and not {}'.format(type(fields)))
            query_string['field'] = fields

        return self.xnat_session.get_json('/data/services/dicomdump', query=query_string)['ResultSet']['Result']

    def import_(self, path, overwrite=None, quarantine=False, destination=None,
                trigger_pipelines=None, project=None, subject=None,
                experiment=None, content_type=None):
        """
        Import a file into XNAT using the import service. See the
        `XNAT wiki <https://wiki.xnat.org/pages/viewpage.action?pageId=6226268>`_
        for a detailed explanation.

        :param str path: local path of the file to upload and import
        :param str overwrite: how the handle existing data (none, append, delete)
        :param bool quarantine: flag to indicate session should be quarantined
        :param bool trigger_pipelines: indicate that archiving should trigger pipelines
        :param str destination: the destination to upload the scan to
        :param str project: the project in the archive to assign the session to
        :param str subject: the subject in the archive to assign the session to
        :param str experiment: the experiment in the archive to assign the session content to
        :param str content_type: overwite the content_type (by the mimetype will be guessed)
        :return:
        """
        query = {}
        if overwrite is not None:
            if overwrite not in ['none', 'append', 'delete']:
                raise ValueError('Overwrite should be none, append or delete!')
            query['overwrite'] = overwrite

        if quarantine:
            query['quarantine'] = 'true'

        if trigger_pipelines is not None:
            if isinstance(trigger_pipelines, bool):
                if trigger_pipelines:
                    query['triggerPipelines'] = 'true'
                else:
                    query['triggerPipelines'] = 'false'
            else:
                raise TypeError('trigger_pipelines should be a boolean')

        if destination is not None:
            query['dest'] = destination

        if project is not None:
            query['project'] = project

        if subject is not None:
            query['subject'] = subject

        if experiment is not None:
            query['session'] = experiment

        # Get mimetype of file
        if content_type is None:
            content_type, _ = mimetypes.guess_type(path)

        uri = '/data/services/import'
        response = self.xnat_session.upload(uri=uri, file_=path, query=query, content_type=content_type, method='post')

        if response.status_code != 200:
            raise XNATResponseError('The response for uploading was ({}) {}'.format(response.status_code, response.text))

        # Create object, the return text should be the url, but it will have a \r\n at the end that needs to be stripped
        response_text = response.text.strip()
        if response_text.startswith('/data/prearchive'):
            return PrearchiveSession(response_text, self.xnat_session)

        return self.xnat_session.create_object(response_text)

    def issue_token(self, user=None):
        """
        Issue a login token, by default for the current logged in user. If
        username is given, for that user. To issue tokens for other users
        you must be an admin.

        :param str user: User to issue token for, default is current user
        :return: Token in a named tuple (alias, secret)
        """
        uri = '/data/services/tokens/issue'
        if user:
            uri += '/user/{}'.format(user)

        result = self.xnat_session.get_json(uri)

        return TokenResult(result['alias'], result['secret'])

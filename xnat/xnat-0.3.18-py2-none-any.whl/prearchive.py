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
import datetime
import re

import isodate

from .core import XNATBaseObject
from .datatypes import to_date, to_time
from .utils import RequestsFileLike

try:
    PYDICOM_LOADED = True
    import pydicom
except ImportError:
    PYDICOM_LOADED = False


class PrearchiveSession(XNATBaseObject):
    @property
    def id(self):
        """
        A unique ID for the session in the prearchive
        :return:
        """
        return '{}/{}/{}'.format(self.data['project'], self.data['timestamp'], self.data['name'])

    @property
    def xpath(self):
        return "xnatpy:prearchiveSession"

    @property
    def fulldata(self):
        # There is a bug in 1.7.0-1.7.2 that misses a route in the REST API
        # this should be fixed from 1.7.3 onward
        if re.match('^1\.7\.[0-2]', self.xnat_session.xnat_version):
            # Find the xnat prearchive project uri
            project_uri = self.uri.rsplit('/', 2)[0]

            # We need to search for session with url field without the /data start
            target_uri = self.uri[5:] if self.uri.startswith('/data') else self.uri
            all_sessions = self.xnat_session.get_json(project_uri)
            for session in all_sessions['ResultSet']['Result']:
                if session['url'] == target_uri:
                    return session
            else:
                raise IndexError('Could not find specified prearchive session {}'.format(self.uri))
        else:
            return self.xnat_session.get_json(self.uri)['ResultSet']['Result'][0]

    @property
    def data(self):
        return self.fulldata

    @property
    def autoarchive(self):
        return self.data['autoarchive']

    @property
    def folder_name(self):
        return self.data['folderName']

    @property
    def lastmod(self):
        lastmod_string = self.data['lastmod']
        return datetime.datetime.strptime(lastmod_string, '%Y-%m-%d %H:%M:%S.%f')

    @property
    def name(self):
        return self.data['name']

    @property
    def label(self):
        return self.name

    @property
    def prevent_anon(self):
        return self.data['prevent_anon']

    @property
    def prevent_auto_commit(self):
        return self.data['prevent_auto_commit']

    @property
    def project(self):
        return self.data['project']

    @property
    def scan_date(self):
        try:
            return to_date(self.data['scan_date'])
        except isodate.ISO8601Error:
            return None

    @property
    def scan_time(self):
        try:
            return to_time(self.data['scan_time'])
        except isodate.ISO8601Error:
            return None

    @property
    def status(self):
        return self.data['status']

    @property
    def subject(self):
        return self.data['subject']

    @property
    def tag(self):
        return self.data['tag']

    @property
    def timestamp(self):
        return self.data['timestamp']

    @property
    def uploaded(self):
        """
        Datetime when the session was uploaded
        """
        uploaded_string = self.data['uploaded']
        try:
            return datetime.datetime.strptime(uploaded_string, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return None

    @property
    def scans(self):
        """
        List of scans in the prearchive session
        """
        data = self.xnat_session.get_json(self.uri + '/scans')
        # We need to prepend /data to our url (seems to be a bug?)

        return [PrearchiveScan('{}/scans/{}'.format(self.uri, x['ID']),
                               self.xnat_session,
                               id_=x['ID'],
                               datafields=x) for x in data['ResultSet']['Result']]

    def download(self, path):
        """
        Method to download the zip of the prearchive session

        :param str path: path to download to
        :return: path of the downloaded zip file
        :rtype: str
        """
        self.xnat_session.download_zip(self.uri, path)
        return path

    def archive(self, overwrite=None, quarantine=None, trigger_pipelines=None,
                project=None, subject=None, experiment=None):
        """
        Method to archive this prearchive session to the main archive

        :param str overwrite: how the handle existing data (none, append, delete)
        :param bool quarantine: flag to indicate session should be quarantined
        :param bool trigger_pipelines: indicate that archiving should trigger pipelines
        :param str project: the project in the archive to assign the session to
        :param str subject: the subject in the archive to assign the session to
        :param str experiment: the experiment in the archive to assign the session content to
        :return: the newly created experiment
        :rtype: xnat.classes.ExperimentData
        """
        query = {'src': self.uri}

        if overwrite is not None:
            if overwrite not in ['none', 'append', 'delete']:
                raise ValueError('Overwrite should be none, append or delete!')
            query['overwrite'] = overwrite

        if quarantine is not None:
            if isinstance(quarantine, bool):
                if quarantine:
                    query['quarantine'] = 'true'
                else:
                    query['quarantine'] = 'false'
            else:
                raise TypeError('Quarantine should be a boolean')

        if trigger_pipelines is not None:
            if isinstance(trigger_pipelines, bool):
                if trigger_pipelines:
                    query['triggerPipelines'] = 'true'
                else:
                    query['triggerPipelines'] = 'false'
            else:
                raise TypeError('trigger_pipelines should be a boolean')

        # Change the destination of the session
        # BEWARE the dest argument is completely ignored, but there is a work around:
        # HACK: See https://groups.google.com/forum/#!searchin/xnat_discussion/prearchive$20archive$20service/xnat_discussion/hwx3NOdfzCk/rQ6r2lRpZjwJ
        if project is not None:
            query['project'] = project

        if subject is not None:
            query['subject'] = subject

        if experiment is not None:
            query['session'] = experiment

        response = self.xnat_session.post('/data/services/archive', query=query)
        object_uri = response.text.strip()

        self.clearcache()  # Make object unavailable
        return self.xnat_session.create_object(object_uri)

    def delete(self, asynchronous=None):
        """
        Delete the session from the prearchive

        :param bool asynchronous: flag to delete asynchronously
        :return: requests response
        """
        query = {'src': self.uri}

        if asynchronous is not None:
            if isinstance(asynchronous, bool):
                if asynchronous:
                    query['async'] = 'true'
                else:
                    query['async'] = 'false'
            else:
                raise TypeError('async should be a boolean')

        response = self.xnat_session.post('/data/services/prearchive/delete', query=query)
        self.clearcache()
        return response

    def rebuild(self, asynchronous=None):
        """
        Rebuilt the session in the prearchive

        :param bool asynchronous: flag to rebuild asynchronously
        :return: requests response
        """
        query = {'src': self.uri}

        if asynchronous is not None:
            if isinstance(asynchronous, bool):
                if asynchronous:
                    query['async'] = 'true'
                else:
                    query['async'] = 'false'
            else:
                raise TypeError('async should be a boolean')

        response = self.xnat_session.post('/data/services/prearchive/rebuild', query=query)
        self.clearcache()
        return response

    def move(self, new_project, asynchronous=None):
        """
        Move the session to a different project in the prearchive

        :param str new_project: the id of the project to move to
        :param bool asynchronous: flag to move asynchronously
        :return: requests response
        """
        query = {'src': self.uri,
                 'newProject': new_project}

        if asynchronous is not None:
            if isinstance(asynchronous, bool):
                if asynchronous:
                    query['async'] = 'true'
                else:
                    query['async'] = 'false'
            else:
                raise TypeError('async should be a boolean')

        response = self.xnat_session.post('/data/services/prearchive/move', query=query)
        self.clearcache()
        return response


class PrearchiveScan(XNATBaseObject):
    def __init__(self, uri, xnat_session, id_=None, datafields=None, parent=None, fieldname=None):
        super(PrearchiveScan, self).__init__(uri=uri,
                                             xnat_session=xnat_session,
                                             id_=id_,
                                             datafields=datafields,
                                             parent=parent,
                                             fieldname=fieldname)

        self._fulldata = {'data_fields': datafields}

    @property
    def series_description(self):
        """
        The series description of the scan
        """
        return self.data['series_description']

    @property
    def files(self):
        """
        List of files contained in the scan
        """
        data = self.xnat_session.get_json(self.uri + '/resources/DICOM/files')

        return [PrearchiveFile(x['URI'],
                               self.xnat_session,
                               id_=x['Name'],
                               datafields=x) for x in data['ResultSet']['Result']]

    def download(self, path):
        """
        Download the scan as a zip

        :param str path: the path to download to
        :return: the path of the downloaded file
        :rtype: str
        """
        self.xnat_session.download_zip(self.uri, path)
        return path

    @property
    def data(self):
        return self.fulldata['data_fields']

    @property
    def fulldata(self):
        return self._fulldata

    @property
    def xpath(self):
        return "xnatpy:prearchiveScan"

    def dicom_dump(self, fields=None):
        """
        Retrieve a dicom dump as a JSON data structure
        See the XAPI documentation for more detailed information: `DICOM Dump Service <https://wiki.xnat.org/display/XAPI/DICOM+Dump+Service+API>`_

        :param list fields: Fields to filter for DICOM tags. It can either a tag name or tag number in the format GGGGEEEE (G = Group number, E = Element number)
        :return: JSON object (dict) representation of DICOM header
        :rtype: dict
        """

        # Get the uri in the following format /prearchive/projects/${project}/${timestamp}/${session}
        # Get the uri and remove the first five characters: /data
        uri = self.uri[5:]
        return self.xnat_session.services.dicom_dump(src=uri, fields=fields)

    def read_dicom(self, file=None, read_pixel_data=False, force=False):
        # Check https://gist.github.com/obskyr/b9d4b4223e7eaf4eedcd9defabb34f13 for partial loading?
        if not PYDICOM_LOADED:
            raise RuntimeError('Cannot read DICOM, missing required dependency: pydicom')

        if file is None:
            dicom_files = sorted(self.files, key=lambda x: x.name)
            file = dicom_files[0]
        else:
            if file not in self.files:
                raise ValueError('File {} not part of scan {} DICOM resource'.format(file, self))

        with file.open() as dicom_fh:
            dicom_data = pydicom.dcmread(dicom_fh,
                                         stop_before_pixels=not read_pixel_data,
                                         force=force)

        return dicom_data


class PrearchiveFile(XNATBaseObject):
    def __init__(self, uri, xnat_session, id_=None, datafields=None, parent=None, fieldname=None):
        super(PrearchiveFile, self).__init__(uri=uri,
                                             xnat_session=xnat_session,
                                             id_=id_,
                                             datafields=datafields,
                                             parent=parent,
                                             fieldname=fieldname)

        self._fulldata = datafields

    def open(self):
        uri = self.xnat_session.url_for(self)
        request = self.xnat_session.interface.get(uri, stream=True)
        return RequestsFileLike(request)

    @property
    def data(self):
        return self.fulldata

    @property
    def fulldata(self):
        return self._fulldata

    @property
    def name(self):
        """
        The name of the file
        """
        return self.data['Name']

    @property
    def size(self):
        """
        The size of the file
        """
        return self.data['Size']

    @property
    def xpath(self):
        return "xnatpy:prearchiveFile"

    def download(self, path):
        """
        Download the file

        :param str path: the path to download to
        :return: the path of the downloaded file
        :rtype: str
        """
        self.xnat_session.download_zip(self.uri, path)
        return path


class Prearchive(object):
    def __init__(self, xnat_session):
        self._xnat_session = xnat_session

    @property
    def xnat_session(self):
        return self._xnat_session

    def sessions(self, project=None):
        """
        Get the session in the prearchive, optionally filtered by project. This
        function is not cached and returns the results of a query at each call.

        :param str project: the project to filter on
        :return: list of prearchive session found
        :rtype: list
        """
        if project is None:
            uri = '/data/prearchive/projects'
        else:
            uri = '/data/prearchive/projects/{}'.format(project)

        data = self.xnat_session.get_json(uri)
        # We need to prepend /data to our url (seems to be a bug?)
        return [PrearchiveSession('/data{}'.format(x['url']), self.xnat_session) for x in data['ResultSet']['Result']]

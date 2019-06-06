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
import os
import tempfile
from gzip import GzipFile
from zipfile import ZipFile
from tarfile import TarFile

from six import BytesIO

from .core import caching, XNATBaseObject, XNATListing
from .search import SearchField
from .utils import mixedproperty

try:
    PYDICOM_LOADED = True
    import pydicom
except ImportError:
    PYDICOM_LOADED = False


class ProjectData(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = 'name'

    @property
    def fulluri(self):
        return '{}/projects/{}'.format(self.xnat_session.fulluri, self.id)

    @property
    @caching
    def subjects(self):
        return XNATListing(self.uri + '/subjects',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='subjects',
                           secondary_lookup_field='label',
                           xsi_type='xnat:subjectData')

    @property
    @caching
    def experiments(self):
        return XNATListing(self.uri + '/experiments',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='experiments',
                           secondary_lookup_field='label')

    @property
    @caching
    def files(self):
        return XNATListing(self.uri + '/files',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='files',
                           secondary_lookup_field='path',
                           xsi_type='xnat:fileData')

    @property
    @caching
    def resources(self):
        return XNATListing(self.uri + '/resources',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='resources',
                           secondary_lookup_field='label',
                           xsi_type='xnat:resourceCatalog')

    def download_dir(self, target_dir, verbose=True):
        """
        Download the entire project and unpack it in a given directory. Note
        that this method will create a directory structure following
        $target_dir/{project.name}/{subject.label}/{experiment.label}
        and unzip the experiment zips as given by XNAT into that. If
        the $target_dir/{project.name} does not exist, it will be created.

        :param str target_dir: directory to create project directory in
        :param bool verbose: show progress
        """

        project_dir = os.path.join(target_dir, self.name)
        if not os.path.isdir(project_dir):
            os.mkdir(project_dir)

        for subject in self.subjects.values():
            subject.download_dir(project_dir, verbose=verbose)

        if verbose:
            self.logger.info('Downloaded subject to {}'.format(project_dir))


class SubjectData(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = 'label'

    @property
    def fulluri(self):
        return '{}/projects/{}/subjects/{}'.format(self.xnat_session.fulluri, self.project, self.id)

    @mixedproperty
    def label(cls):
        # 0 Automatically generated Property, type: xs:string
        return SearchField(cls, "label")

    @label.getter
    def label(self):
        # Check if label is already inserted during listing, that should be valid
        # label for the project under which it was listed in the first place
        try:
            return self._overwrites['label']
        except KeyError:
            pass

        # Retrieve the label the hard and costly way
        try:
            # First check if subject is shared into current project
            sharing = next(x for x in self.fulldata['children'] if x['field'] == 'sharing/share')
            share_info = next(x for x in sharing['items'] if x['data_fields']['project'] == self.project)
            label = share_info['data_fields']['label']
        except (KeyError, StopIteration):
            label = self.get('label', type_=str)

        # Cache label for future use
        self._overwrites['label'] = label
        return label

    @label.setter
    def label(self, value):
        self.xnat_session.put(self.fulluri, query={'label': value})
        self.clearcache()

    @property
    @caching
    def files(self):
        return XNATListing(self.uri + '/files',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='files',
                           secondary_lookup_field='path',
                           xsi_type='xnat:fileData')

    def download_dir(self, target_dir, verbose=True):
        """
        Download the entire subject and unpack it in a given directory. Note
        that this method will create a directory structure following
        $target_dir/{subject.label}/{experiment.label}
        and unzip the experiment zips as given by XNAT into that. If
        the $target_dir/{subject.label} does not exist, it will be created.

        :param str target_dir: directory to create subject directory in
        :param bool verbose: show progress
        """
        subject_dir = os.path.join(target_dir, self.label)
        if not os.path.isdir(subject_dir):
            os.mkdir(subject_dir)

        for experiment in self.experiments.values():
            experiment.download_dir(subject_dir, verbose=verbose)

        if verbose:
            self.logger.info('Downloaded subject to {}'.format(subject_dir))

    def share(self, project, label=None):
        # Create the uri for sharing
        share_uri = '{}/projects/{}'.format(self.fulluri, project)

        # Add label if needed
        query = {}
        if label is not None:
            query['label'] = label

        self.xnat_session.put(share_uri, query=query)
        self.clearcache()


class ExperimentData(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = 'label'

    @mixedproperty
    def label(cls):
        return SearchField(cls, "label")

    @label.getter
    def label(self):
        # Check if label is already inserted during listing, that should be valid
        # label for the project under which it was listed in the first place
        try:
            return self._overwrites['label']
        except KeyError:
            pass

        # Retrieve the label the hard and costly way
        try:
            # First check if subject is shared into current project
            sharing = next(x for x in self.fulldata['children'] if x['field'] == 'sharing/share')
            share_info = next(x for x in sharing['items'] if x['data_fields']['project'] == self.project)
            label = share_info['data_fields']['label']
        except (KeyError, StopIteration):
            label = self.get('label', type_=str)

        # Cache label for future use
        self._overwrites['label'] = label
        return label

    @label.setter
    def label(self, value):
        self.xnat_session.put(self.fulluri, query={'label': value})
        self.clearcache()


class SubjectAssessorData(XNATBaseObject):
    @property
    def fulluri(self):
        return '/data/archive/projects/{}/subjects/{}/experiments/{}'.format(self.project, self.subject_id, self.id)

    @property
    def subject(self):
        return self.xnat_session.subjects[self.subject_id]


class ImageSessionData(XNATBaseObject):
    @property
    @caching
    def files(self):
        return XNATListing(self.uri + '/files',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='files',
                           secondary_lookup_field='path',
                           xsi_type='xnat:fileData')

    def create_assessor(self, label, type_):
        uri = '{}/assessors/{label}?xsiType={type}&label={label}&req_format=qs'.format(self.fulluri,
                                                                                       type=type_,
                                                                                       label=label)
        self.xnat_session.put(uri, accepted_status=(200, 201))
        self.clearcache()  # The resources changed, so we have to clear the cache
        return self.xnat_session.create_object('{}/assessors/{}'.format(self.fulluri, label), type_=type_)

    def download(self, path, verbose=True):
        self.xnat_session.download_zip(self.uri + '/scans/ALL/files', path, verbose=verbose)

    def download_dir(self, target_dir, verbose=True):
        """
        Download the entire experiment and unpack it in a given directory. Note
        that this method will create a directory structure following
        $target_dir/{experiment.label} and unzip the experiment zips
        as given by XNAT into that. If the $target_dir/{experiment.label} does
        not exist, it will be created.

        :param str target_dir: directory to create experiment directory in
        :param bool verbose: show progress
        """
        # Check if there are actually file to be found
        file_list = self.xnat_session.get_json(self.uri + '/scans/ALL/files')
        if len(file_list['ResultSet']['Result']) == 0:
            # Just make sure the target directory exists and stop
            if not os.path.exists(target_dir):
                os.mkdir(target_dir)
            return

        with tempfile.TemporaryFile() as temp_path:
            self.xnat_session.download_stream(self.uri + '/scans/ALL/files', temp_path, format='zip', verbose=verbose)

            with ZipFile(temp_path) as zip_file:
                zip_file.extractall(target_dir)

        if verbose:
            self.logger.info('\nDownloaded image session to {}'.format(target_dir))

    def share(self, project, label=None):
        # Create the uri for sharing
        share_uri = '{}/projects/{}'.format(self.fulluri, project)

        # Add label if needed
        query = {}
        if label is not None:
            query['label'] = label

        self.xnat_session.put(share_uri, query=query)
        self.clearcache()


class DerivedData(XNATBaseObject):
    @property
    def fulluri(self):
        return '/data/experiments/{}/assessors/{}'.format(self.image_session_id, self.id)

    @property
    @caching
    def files(self):
        return XNATListing(self.fulluri + '/files',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='files',
                           secondary_lookup_field='path',
                           xsi_type='xnat:fileData')

    @property
    @caching
    def resources(self):
        return XNATListing(self.fulluri + '/resources',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='resources',
                           secondary_lookup_field='label',
                           xsi_type='xnat:resourceCatalog')

    def create_resource(self, label, format=None, data_dir=None, method=None):
        uri = '{}/resources/{}'.format(self.fulluri, label)
        self.xnat_session.put(uri, format=format)
        self.clearcache()  # The resources changed, so we have to clear the cache
        resource = self.xnat_session.create_object(uri, type_='xnat:resourceCatalog')

        if data_dir is not None:
            resource.upload_dir(data_dir, method=method)

        return resource

    def download(self, path, verbose=True):
        self.xnat_session.download_zip(self.uri + '/files', path, verbose=verbose)


class ImageScanData(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = 'type'

    @property
    @caching
    def files(self):
        return XNATListing(self.uri + '/files',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='files',
                           secondary_lookup_field='path',
                           xsi_type='xnat:fileData')

    @property
    @caching
    def resources(self):
        return XNATListing(self.uri + '/resources',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='resources',
                           secondary_lookup_field='label',
                           xsi_type='xnat:resourceCatalog')

    def create_resource(self, label, format=None, data_dir=None, method='tgz_file'):
        uri = '{}/resources/{}'.format(self.uri, label)
        self.xnat_session.put(uri, format=format)
        self.clearcache()  # The resources changed, so we have to clear the cache
        resource = self.xnat_session.create_object(uri, type_='xnat:resourceCatalog')

        if data_dir is not None:
            resource.upload_dir(data_dir, method=method)

        return resource

    def download(self, path, verbose=True):
        self.xnat_session.download_zip(self.uri + '/files', path, verbose=verbose)

    def download_dir(self, target_dir, verbose=True):
        with tempfile.TemporaryFile() as temp_path:
            self.xnat_session.download_stream(self.uri + '/files', temp_path, format='zip', verbose=verbose)

            with ZipFile(temp_path) as zip_file:
                zip_file.extractall(target_dir)

        if verbose:
            self.logger.info('Downloaded image scan data to {}'.format(target_dir))

    def dicom_dump(self, fields=None):
        """
        Retrieve a dicom dump as a JSON data structure
        See the XAPI documentation for more detailed information: `DICOM Dump Service <https://wiki.xnat.org/display/XAPI/DICOM+Dump+Service+API>`_

        :param list fields: Fields to filter for DICOM tags. It can either a tag name or tag number in the format GGGGEEEE (G = Group number, E = Element number)
        :return: JSON object (dict) representation of DICOM header
        :rtype: dict
        """
        experiment = self.xnat_session.create_object('/data/experiments/{}'.format(self.image_session_id))

        uri = '/archive/projects/{}/experiments/{}/scans/{}'.format(
            experiment.project,
            self.image_session_id,
            self.id,
        )
        return self.xnat_session.services.dicom_dump(src=uri, fields=fields)

    def read_dicom(self, file=None, read_pixel_data=False, force=False):
        # Check https://gist.github.com/obskyr/b9d4b4223e7eaf4eedcd9defabb34f13 for partial loading?
        if not PYDICOM_LOADED:
            raise RuntimeError('Cannot read DICOM, missing required dependency: pydicom')

        dicom_resource = self.resources.get('DICOM')

        if dicom_resource is None:
            raise ValueError('Scan {} does not contain a DICOM resource!'.format(self))

        if file is None:
            dicom_files = sorted(dicom_resource.files.values(), key=lambda x: x.path)
            file = dicom_files[0]
        else:
            if file not in dicom_resource.files.values():
                raise ValueError('File {} not part of scan {} DICOM resource'.format(file, self))

        with file.open() as dicom_fh:
            dicom_data = pydicom.dcmread(dicom_fh,
                                         stop_before_pixels=not read_pixel_data,
                                         force=force)

        return dicom_data


class AbstractResource(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = 'label'

    def __init__(self,
                 uri=None,
                 xnat_session=None,
                 id_=None,
                 datafields=None,
                 parent=None,
                 fieldname=None,
                 overwrites=None,
                 data_dir=None,
                 upload_method=None,
                 **kwargs):

        super(AbstractResource, self).__init__(
            uri=uri,
            xnat_session=xnat_session,
            id_=id_,
            datafields=datafields,
            parent=parent,
            fieldname=fieldname,
            overwrites=overwrites,
            **kwargs
        )

        if data_dir is not None:
            self.upload_dir(data_dir, method=upload_method)

    @property
    @caching
    def fulldata(self):
        # FIXME: ugly hack because direct query fails
        uri, label = self.uri.rsplit('/', 1)
        data = self.xnat_session.get_json(uri)['ResultSet']['Result']
        
        def _guess_key( d ):
            if 'URI' not in d and 'ID' not in d and 'xnat_abstractresource_id' in d:
                # HACK: This is a Resource where the label is not part of the uri, it uses this xnat_abstractresource_id instead.
                return d['xnat_abstractresource_id']
            else:
                return d['label']

        try:
            data = next(x for x in data if _guess_key(x) == label)
        except StopIteration:
            raise ValueError('Cannot find full data!')

        data['ID'] = data['xnat_abstractresource_id']  # Make sure the ID is present
        return data

    @property
    def data(self):
        return self.fulldata

    @property
    def file_size(self):
        file_size = self.data['file_size']
        if file_size.strip() == '':
            return 0
        else:
            return int(file_size)

    @property
    def file_count(self):
        file_count = self.data['file_count']
        if file_count.strip() == '':
            return 0
        else:
            return int(file_count)

    @property
    @caching
    def files(self):
        return XNATListing(self.uri + '/files',
                           xnat_session=self.xnat_session,
                           parent=self,
                           field_name='files',
                           secondary_lookup_field='path',
                           xsi_type='xnat:fileData')

    def download(self, path, verbose=True):
        self.xnat_session.download_zip(self.uri + '/files', path, verbose=verbose)

    def download_dir(self, target_dir, verbose=True):
        """
        Download the entire resource and unpack it in a given directory

        :param str target_dir: directory to unpack to
        :param bool verbose: show progress
        """
        with tempfile.TemporaryFile() as temp_path:
            self.xnat_session.download_stream(self.uri + '/files', temp_path, format='zip', verbose=verbose)

            with ZipFile(temp_path) as zip_file:
                zip_file.extractall(target_dir)

        if verbose:
            self.logger.info('Downloaded resource data to {}'.format(target_dir))

    def upload(self, data, remotepath, overwrite=False, extract=False, **kwargs):
        uri = '{}/files/{}'.format(self.uri, remotepath.lstrip('/'))
        query = {}
        if extract:
            query['extract'] = 'true'
        self.xnat_session.upload(uri, data, overwrite=overwrite, query=query, **kwargs)
        self.files.clearcache()

    def upload_dir(self, directory, overwrite=False, method='tgz_file', **kwargs):
        """
        Upload a directory to an XNAT resource. This means that if you do
        resource.upload_dir(directory) that if there is a file directory/a.txt
        it will be uploaded to resource/files/a.txt

        The method has 5 options, default is tgz_file:

        #. ``per_file``: Scans the directory and uploads file by file
        #. ``tar_memory``: Create a tar archive in memory and upload it in one go
        #. ``tgz_memory``: Create a gzipped tar file in memory and upload that
        #. ``tar_file``: Create a temporary tar file and upload that
        #. ``tgz_file``: Create a temporary gzipped tar file and upload that

        The considerations are that sometimes you can fit things in memory so
        you can save disk IO by putting it in memory. The per file does not
        create additional archives, but has one request per file so might be
        slow when uploading many files.

        :param str directory: The directory to upload
        :param bool overwrite: Flag to force overwriting of files
        :param str method: The method to use
        """
        if not isinstance(directory, str):
            directory = str(directory)

        # Make sure that a None or empty string is replaced by the default
        method = method or 'tgz_file'

        if method == 'per_file':
            for root, _, files in os.walk(directory):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    if os.path.getsize(file_path) == 0:
                        continue

                    target_path = os.path.relpath(file_path, directory)
                    self.upload(file_path, target_path, overwrite=overwrite, **kwargs)
        elif method == 'tar_memory':
            fh = BytesIO()
            with TarFile(name='upload.tar', mode='w', fileobj=fh) as tar_file:
                tar_file.add(directory, '')
            fh.seek(0)
            self.upload(fh, 'upload.tar', overwrite=overwrite, extract=True, **kwargs)
            fh.close()
        elif method == 'tgz_memory':
            fh = BytesIO()
            with GzipFile(filename='upload.tar.gz', mode='w', fileobj=fh) as gzip_file:
                with TarFile(name='upload.tar', mode='w', fileobj=gzip_file) as tar_file:
                    tar_file.add(directory, '')

            fh.seek(0)
            self.upload(fh, 'upload.tar.gz', overwrite=overwrite, extract=True, **kwargs)
            fh.close()
        elif method == 'tar_file':
            with tempfile.TemporaryFile('wb+') as fh:
                with TarFile(name='upload.tar', mode='w', fileobj=fh) as tar_file:
                    tar_file.add(directory, '')
                fh.seek(0)
                self.upload(fh, 'upload.tar', overwrite=overwrite, extract=True, **kwargs)
        elif method == 'tgz_file':
            with tempfile.TemporaryFile('wb+') as fh:
                with GzipFile(filename='upload.tar.gz', mode='w', fileobj=fh) as gzip_file:
                    with TarFile(name='upload.tar', mode='w', fileobj=gzip_file) as tar_file:
                        tar_file.add(directory, '')

                fh.seek(0)
                self.upload(fh, 'upload.tar.gz', overwrite=overwrite, extract=True, **kwargs)
        else:
            print('Selected invalid upload directory method!')

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
This module contains the XNATStorage plugin for fastr
"""

import fnmatch

import netrc
import os
import re
import time
import tempfile
import urllib.parse
from collections import OrderedDict

import requests
from requests.exceptions import RequestException
import xnat
import xnat.exceptions

import fastr
import fastr.data
from fastr import exceptions
from fastr.core.ioplugin import IOPlugin


class XNATStorage(IOPlugin):

    """
    .. warning::

        As this IOPlugin is under development, it has not been thoroughly
        tested.

    The XNATStorage plugin is an IOPlugin that can download data from and
    upload data to an XNAT server. It uses its own ``xnat://`` URL scheme.
    This is a scheme specific for this plugin and though it looks somewhat
    like the XNAT rest interface, a different type or URL.

    Data resources can be access directly by a data url::

        xnat://xnat.example.com/data/archive/projects/sandbox/subjects/subject001/experiments/experiment001/scans/T1/resources/DICOM
        xnat://xnat.example.com/data/archive/projects/sandbox/subjects/subject001/experiments/*_BRAIN/scans/T1/resources/DICOM

    In the second URL you can see a wildcard being used. This is possible at
    long as it resolves to exactly one item.

    The ``id`` query element will change the field from the default experiment to
    subject and the ``label`` query element sets the use of the label as the
    fastr id (instead of the XNAT id) to ``True`` (the default is ``False``)

    To disable ``https`` transport and use ``http`` instead the query string
    can be modified to add ``insecure=true``. This will make the plugin send
    requests over ``http``::

        xnat://xnat.example.com/data/archive/projects/sandbox/subjects/subject001/experiments/*_BRAIN/scans/T1/resources/DICOM?insecure=true

    For sinks it is import to know where to save the data. Sometimes you want
    to save data in a new assessor/resource and it needs to be created. To
    allow the Fastr sink to create an object in XNAT, you have to supply the
    type as a query parameter::

        xnat://xnat.bmia.nl/data/archive/projects/sandbox/subjects/S01/experiments/_BRAIN/assessors/test_assessor/resources/IMAGE/files/image.nii.gz?resource_type=xnat:resourceCatalog&assessor_type=xnat:qcAssessmentData

    Valid options are: subject_type, experiment_type, assessor_type, scan_type,
    and resource_type.

    If you want to do a search where
    multiple resources are returned, it is possible to use a search url::

        xnat://xnat.example.com/search?projects=sandbox&subjects=subject[0-9][0-9][0-9]&experiments=*_BRAIN&scans=T1&resources=DICOM

    This will return all DICOMs for the T1 scans for experiments that end with _BRAIN that belong to a
    subjectXXX where XXX is a 3 digit number. By default the ID for the samples
    will be the experiment XNAT ID (e.g. XNAT_E00123). The wildcards that can
    be the used are the same UNIX shell-style wildcards as provided by the
    module :py:mod:`fnmatch`.

    It is possible to change the id to a different fields id or label. Valid
    fields are project, subject, experiment, scan, and resource::

        xnat://xnat.example.com/search?projects=sandbox&subjects=subject[0-9][0-9][0-9]&experiments=*_BRAIN&scans=T1&resources=DICOM&id=subject&label=true

    The following variables can be set in the search query:

    ============= ============== =============================================================================================
    variable      default        usage
    ============= ============== =============================================================================================
    projects      ``*``          The project(s) to select, can contain wildcards (see :py:mod:`fnmatch`)
    subjects      ``*``          The subject(s) to select, can contain wildcards (see :py:mod:`fnmatch`)
    experiments   ``*``          The experiment(s) to select, can contain wildcards (see :py:mod:`fnmatch`)
    scans         ``*``          The scan(s) to select, can contain wildcards (see :py:mod:`fnmatch`)
    resources     ``*``          The resource(s) to select, can contain wildcards (see :py:mod:`fnmatch`)
    id            ``experiment`` What field to use a the id, can be: project, subject, experiment, scan, or resource
    label         ``false``      Indicate the XNAT label should be used as fastr id, options ``true`` or ``false``
    insecure      ``false``      Change the url scheme to be used to http instead of https
    verify        ``true``       (Dis)able the verification of SSL certificates
    regex         ``false``      Change search to use regex :py:func:`re.match` instead of fnmatch for matching
    overwrite     ``false``      Tell XNAT to overwrite existing files if a file with the name is already present
    ============= ============== =============================================================================================

    For storing credentials the ``.netrc`` file can be used. This is a common
    way to store credentials on UNIX systems. It is required that the file is
    only accessible by the owner only or a ``NetrcParseError`` will be raised.
    A netrc file is really easy to create, as its entries look like::

        machine xnat.example.com
                login username
                password secret123

    See the :py:mod:`netrc module <netrc>` or the
    `GNU inet utils website <http://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html#The-_002enetrc-file>`_
    for more information about the ``.netrc`` file.

    .. note::

        On windows the location of the netrc file is assumed to be
        ``os.path.expanduser('~/_netrc')``. The leading underscore is
        because windows does not like filename starting with a dot.

    .. note::

        For scan the label will be the scan type (this is initially
        the same as the series description, but can be updated manually
        or the XNAT scan type cleanup).

    .. warning::

        labels in XNAT are not guaranteed to be unique, so be careful
        when using them as the sample ID.

    For background on XNAT, see the
    `XNAT API DIRECTORY <https://wiki.xnat.org/display/XNAT16/XNAT+REST+API+Directory>`_
    for the REST API of XNAT.
    """
    scheme = ('xnat', 'xnat+http', 'xnat+https')

    def __init__(self):
        # initialize the instance and register the scheme
        super(XNATStorage, self).__init__()
        self._xnat = (None, None)

    def cleanup(self):
        if self.xnat is not None:
            fastr.log.info('Attempting to cleanly disconnecting XNAT.')
            self.xnat.disconnect()

    @property
    def server(self):
        return self._xnat[0]

    @property
    def xnat(self):
        return self._xnat[1]

    def connect(self, server, path='', insecure=False, verify=True):
        if self.server != server:
            # Try to neatly clean previous connection
            if self.xnat is not None:
                self.xnat.disconnect()

            try:
                netrc_file = os.path.join('~', '_netrc' if os.name == 'nt' else '.netrc')
                netrc_file = os.path.expanduser(netrc_file)
                user, _, password = netrc.netrc(netrc_file).authenticators(server)
            except TypeError:
                raise exceptions.FastrValueError('Could not retrieve login info for "{}" from the .netrc file!'.format(server))

            # Create the URL for the XNAT connection
            schema = 'http' if insecure else 'https'
            session = xnat.connect(urllib.parse.urlunparse([schema, server, path, '', '', '']),
                                   user=user, password=password, debug=fastr.config.debug, verify=verify)

            # Time-out a request when no bytes are received for 120 seconds
            session.request_timeout = 120

            self._xnat = (server, session)

    @staticmethod
    def _path_to_dict(path):
        fastr.log.info('Converting {} to dict...'.format(path))
        if not path.startswith('/data/'):
            raise ValueError('Resources to be located should have a path starting with /data/ (found {})'.format(path))

        if path.startswith('/data/archive/'):
            path_prefix_parts = 2
        else:
            path_prefix_parts = 1

        # Break path apart
        parts = path.lstrip('/').split('/', 11 + path_prefix_parts)

        # Ignore first two parts and build a dict from /key/value/key/value pattern
        path_iterator = parts[path_prefix_parts:].__iter__()
        location = OrderedDict()
        for key, value in zip(path_iterator, path_iterator):
            if key == 'files':
                filepath = [value] + list(path_iterator)
                value = '/'.join(filepath)

            location[key] = value

        fastr.log.info('Found {}'.format(location))
        return location

    def _locate_resource(self, url, create=False, use_regex=False):
        resources = self._find_objects(url=url, create=create, use_regex=use_regex)

        if len(resources) == 0:
            raise ValueError('Could not find data object at {}'.format(url))
        elif len(resources) > 1:
            raise ValueError('Data item does not point to a unique resource! Matches found: {}'.format([x.fulluri for x in resources]))

        resource = resources[0]

        # Make sure the return value is actually a resource
        resource_cls = self.xnat.XNAT_CLASS_LOOKUP['xnat:abstractResource']
        if not isinstance(resource, resource_cls):
            raise TypeError('The resource should be an instance of {}'.format(resource_cls))

        return resource

    def parse_uri(self, url):
        url = urllib.parse.urlparse(url)

        if url.scheme not in self.scheme:
            raise exceptions.FastrValueError('URL scheme {} not of supported type {}!'.format(url.scheme,
                                                                                              self.scheme))

        query = urllib.parse.parse_qs(url.query)

        path_prefix = url.path[:url.path.find('/data/')]

        # Strip the prefix of the url path
        url = url._replace(path=url.path[len(path_prefix):])

        if not url.path.startswith('/data/archive/') and url.path.startswith('/data/'):
            fastr.log.info('Patching archive into url path starting with data')
            url = url._replace(path=url.path[:6] + 'archive/' + url.path[6:])

        url_str = urllib.parse.urlunparse(url)
        fastr.log.info('New URL: {}'.format(url_str))

        if not url.path.startswith('/data/archive'):
            raise exceptions.FastrValueError('Can only fetch urls with the /data/archive path')

        if url.scheme == 'xnat+http':
            insecure = True
        elif url.scheme == 'xnat+https':
            insecure = False
        else:
            fastr.log.warning('Using old-style insecure lookup, please use a xnat+http://'
                              ' or xnat+https:// url scheme instead!')
            insecure = query.get('insecure', ['0'])[0] in ['true', '1']

        verify = query.get('verify', ['1'])[0] in ['true', '1']
        use_regex = query.get('regex', ['0'])[0] in ['true', '1']

        return url, path_prefix, insecure, verify, use_regex, query

    def fetch_url(self, inurl, outpath):
        """
        Get the file(s) or values from XNAT.

        :param inurl: url to the item in the data store
        :param outpath: path where to store the fetch data locally
        """
        url, path_prefix, insecure, verify, use_regex, query = self.parse_uri(inurl)

        # Create a session for this retrieval
        self.connect(url.netloc, path=path_prefix, insecure=insecure, verify=verify)

        # Find the filepath within the resource
        location = self._path_to_dict(url.path)
        filepath = location.get('files', '')

        # Find the resource
        resource = self._locate_resource(inurl, use_regex=use_regex)

        # Download the Resource
        workdir = outpath
        if not os.path.isdir(workdir):
            directory, filename = os.path.split(workdir)
            workdir = os.path.join(directory, filename.replace('.', '_'))
            os.makedirs(workdir)

        # Create uniquer dir to download in
        workdir = tempfile.mkdtemp(prefix='fastr_xnat_{}_tmp'.format(resource.id), dir=workdir)

        # Retry downloading in case of connection reset
        max_tries = tries = 3
        success = False
        while tries > 0 and not success:
            try:
                fastr.log.info('Download attempt {} of {}'.format(max_tries - tries + 1, max_tries))
                tries -= 1
                resource.download_dir(workdir, verbose=False)
                success = True
            except requests.exceptions.ChunkedEncodingError:
                if tries <= 0:
                    raise
                else:
                    # Sleep 10 seconds times the amount of tries
                    time.sleep((max_tries - tries) * 10)

        # Find the file in the proper path
        resource_label = resource.label.replace(' ', '_')
        if filepath == '':
            filepath = file_name = 'files'
            target = 'resources/{}'.format(resource_label)
        else:
            file_directory, file_name = os.path.split(filepath)
            target = 'resources/{}/files/{}'.format(resource_label, file_directory).rstrip('/')

        for root, dirs, files in os.walk(workdir):
            if root.endswith(target) and (file_name in files or file_name in dirs):
                data_path = os.path.join(root, file_name)
                fastr.log.info('Found data in {}'.format(data_path))
                break
        else:
            message = "Could not find {} file in downloaded resource!".format(filepath)
            fastr.log.error(message)
            raise exceptions.FastrValueError(message)

        return data_path

    def put_url(self, inpath, outurl):
        """
        Upload the files to the XNAT storage

        :param inpath: path to the local data
        :param outurl: url to where to store the data in the external data store.
        """
        # Create a session for this retrieval
        url, path_prefix, insecure, verify, use_regex, query = self.parse_uri(outurl)
        self.connect(url.netloc, path=path_prefix, insecure=insecure, verify=verify)

        # Determine the resource to upload to
        resource = self._locate_resource(outurl, create=True, use_regex=use_regex)

        # Determine the file within xnat
        parsed_url = urllib.parse.urlparse(outurl)
        location = self._path_to_dict(parsed_url.path)

        # Upload the file
        fastr.log.info('Uploading to: {}'.format(resource.fulluri))
        fastr.log.info('Uploading to path: {}'.format(location['files']))
        try:
            overwrite = urllib.parse.parse_qs(url.query).get('overwrite', ['0'])[0] in ['true', '1']
            self.upload(resource, inpath, location['files'], overwrite=overwrite)
            return True
        except xnat.exceptions.XNATUploadError as exception:
            fastr.log.error('Encountered error when uploading data: {}'.format(exception))
            return False

    @staticmethod
    def upload(resource, in_path, location, retries=3, overwrite=False):
        # Initial upload
        success = False
        tries = retries
        file_size = os.path.getsize(in_path)

        # Open the file once for streaming uploades
        with open(in_path, 'rb') as in_file_handle:
            while not success and tries > 0:
                tries -= 1
                try:
                    in_file_handle.seek(0)
                    resource.upload(in_file_handle, location, overwrite=overwrite)
                    success = True
                except (xnat.exceptions.XNATError, RequestException) as exception:
                    fastr.log.warning('Encountered XNAT error during upload: {}'.format(exception))
                    if tries > 0:
                        fastr.log.warning('Retrying {} times'.format(tries))

            # Something went wrong, now forcefully try again
            max_retries = retries

            # Try multiple times to upload and try to avoid XNAT hiccups etc
            resource.clearcache()
            resource.files.clearcache()
            while location not in resource.files and retries > 0:
                resource.clearcache()
                resource.files.clearcache()
                retries -= 1

                try:
                    in_file_handle.seek(0)
                    resource.upload(in_file_handle, location, overwrite=True)
                except xnat.exceptions.XNATError:
                    # Allow exceptions to be raised again, just wait 10 seconds per try and retry
                    delay = 10 * (max_retries - retries)
                    fastr.log.warning('Got exception during upload, sleep {} seconds and retry'.format(
                        delay
                    ))
                    time.sleep(delay)

        # Check if upload is successful
        resource.clearcache()
        resource.files.clearcache()
        if location not in resource.files:
            raise xnat.exceptions.XNATUploadError("Problem with uploading to XNAT "
                                                  "(file not found, persisted after retries)")

        xnat_size = int(resource.files[location].size)
        if xnat_size != file_size:
            raise xnat.exceptions.XNATUploadError(
                "Problem with uploading to XNAT (file size differs uploaded {}, expected {})".format(
                    xnat_size, file_size
                )
            )
        else:
            fastr.log.info('It appears the file is uploaded to {} with a file size of {}'.format(
                resource.files[location].fulluri,
                xnat_size
            ))

    def _find_objects(self, url, create=False, use_regex=False):
        fastr.log.info('Locating {}'.format(url))
        # Parse url
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        if not path.startswith('/data/'):
            raise ValueError('Resources to be located should have a path starting with /data/')

        # Create a search uri
        location = self._path_to_dict(path)

        if 'resources' not in location:
            raise ValueError('All files should be located inside a resource, did not'
                             ' find resources level in {}'.format(location))

        # Sort xsi type directives neatly
        types = {
            'resources': 'xnat:resourceCatalog'
        }
        for key in location.keys():
            option1 = (key.rstrip('s') + '_type')
            option2 = (key + '_type')
            if option1 in query:
                types[key] = query[option1][0]
            if option2 in query:
                types[key] = query[option2][0]

        items = None
        # Parse location part by part
        for object_type, object_key in location.items():
            # We don't want to go into files, those are put but not created
            # and they get via the resources
            if object_type == 'files':
                break

            fastr.log.info('Locating {} / {} in {}'.format(object_type, object_key, items))
            new_items = self._resolve_url_part(object_type, object_key, use_regex=use_regex, parents=items)

            if len(new_items) == 0:
                if not create:
                    raise ValueError('Could not find data parent_object at {} (No values at level {})'.format(url,
                                                                                                              object_type))
                elif items is not None and len(items) == 1:
                    fastr.log.debug('Items: {}'.format(items))
                    parent_object = items[0]

                    # Get the required xsitype
                    if object_type in types:
                        xsi_type = types[object_type]
                    else:
                        raise ValueError('Could not find the correct xsi:type for {} (available hints: {})'.format(object_type,
                                                                                                                   types))

                    if '*' in object_key or '?' in object_key or '[' in object_key or ']' in object_key:
                        raise ValueError('Illegal characters found in name of object_key'
                                         ' to create! (characters ?*[] or illegal!), found: {}'.format(object_key))

                    fastr.log.info('Creating new object under {} with type {}'.format(parent_object.uri, xsi_type))

                    # Create the object with the correct secondary lookup
                    cls = self.xnat.XNAT_CLASS_LOOKUP[xsi_type]
                    kwargs = {cls.SECONDARY_LOOKUP_FIELD: object_key}
                    try:
                        cls(parent=parent_object, **kwargs)
                    except xnat.exceptions.XNATResponseError:
                        fastr.log.warning(('Got a response error when creating the object {} (parent {}),'
                                           ' continuing to check if creating was in a race'
                                           ' condition and another processed created it').format(
                            object_key,
                            parent_object,
                        ))

                    new_items = self._resolve_url_part(object_type, object_key, use_regex=use_regex, parents=items)

                    if len(new_items) != 1:
                        raise ValueError('There appears to be a problem creating the object_key!')
                else:
                    raise ValueError('To create an object, the path should point to a unique parent'
                                     ' object! Found {} matching items: {}'.format(len(items), items))
            # Accept the new items for the new level scan
            items = new_items

        return items

    def _resolve_url_part(self, level, query=None, use_regex=False, parents=None):
        """
        Get all matching projects

        :param dict query: the query to find projects to match for
        :return:
        """
        # If there are no parents, work directly on the session
        if parents is None:
            parents = [self.xnat]

        if query is None:
            query = '.*' if use_regex else '*'

        fastr.log.info('Find {}: {} (parents: {})'.format(level, query, parents))

        # Get all objects
        objects = []
        for parent in parents:
            extra_options = getattr(parent, level)
            if use_regex:
                objects.extend(x for x in extra_options.values() if re.match(query, getattr(x, extra_options.secondary_lookup_field)) or x.id == query)
            elif all(x not in query for x in '*?[]'):
                if query in extra_options:
                    objects.append(extra_options[query])
            else:
                objects.extend(x for x in extra_options.values() if fnmatch.fnmatchcase(getattr(x, extra_options.secondary_lookup_field), query) or x.id == query)

        fastr.log.info('Found: {}'.format(objects))

        return objects

    def expand_url(self, url):
        # Check if there is a wildcard in the URL:
        parsed_url = urllib.parse.urlparse(url)

        if parsed_url.path == '/search':
            # Parse the query
            query = urllib.parse.parse_qs(parsed_url.query)

            # Check if all fields given are valid fieldnames
            valid_fields = ("projects",
                            "subjects",
                            "experiments",
                            "scans",
                            "resources",
                            "id",
                            "label",
                            "insecure",
                            "verify",
                            "regex")

            valid_query = True
            for key in query.keys():
                if key not in valid_fields:
                    fastr.log.error('Using invalid query field {} options are {}!'.format(key,
                                                                                          valid_fields))
                    valid_query = False

            if not valid_query:
                raise ValueError('The query was malformed, see the error log for details.')

            id_field = query.get('id', ['experiment'])[0]
            id_use_label = query.get('label', ['0'])[0].lower() in ['1', 'true']
            use_regex = query.get('regex', ['0'])[0].lower() in ['1', 'true']
            insecure = query.get('insecure', ['0'])[0] in ['true', '1']
            verify = query.get('verify', ['1'])[0] in ['true', '1']

            # Make sure we are connect to the correct server
            self.connect(parsed_url.netloc, insecure=insecure, verify=verify)

            if id_field not in ['project', 'subject', 'experiment', 'scan', 'resource']:
                raise exceptions.FastrValueError('Requested id field ({}) is not a valid option!'.format(id_field))

            # Create the url version for the search
            default = ['.*'] if use_regex else ['*']
            search_path = '/data/archive/projects/{p}/subjects/{s}/experiments/{e}/scans/{sc}/resources/{r}'.format(
                p=query.get('projects', default)[0],
                s=query.get('subjects', default)[0],
                e=query.get('experiments', default)[0],
                sc=query.get('scans', default)[0],
                r=query.get('resources', default)[0]
            )

            # Find all matching resources
            resources = self._find_objects(search_path, use_regex=use_regex)

            # Format the new expanded urls
            urls = []
            for resource in resources:
                match = re.match(r'/data/experiments/(?P<experiment>[a-zA-Z0-9_\-]+)/scans/(?P<scan>[a-zA-Z0-9_\-]+)/resources/(?P<resource>[a-zA-Z0-9_\-]+)',
                                 resource.uri)
                experiment = self.xnat.experiments[match.group('experiment')]
                project = self.xnat.projects[experiment.project]
                subject = self.xnat.subjects[experiment.subject_id]
                scan = experiment.scans[match.group('scan')]

                # TODO: Just use resource.fulluri + '/files/filename' ?
                newpath = '/data/archive/projects/{}/subjects/{}/experiments/{}/scans/{}/resources/{}/files/{}'.format(
                    project.id,
                    subject.id,
                    experiment.id,
                    scan.id,
                    resource.id,
                    query.get('files', [''])[0]
                )

                newurl = urllib.parse.urlunparse(('xnat', parsed_url.netloc, newpath, parsed_url.params, '', ''))

                # Determine the ID of the sample
                if id_field == 'resource':
                    id_obj = resource
                elif id_field == 'scan':
                    id_obj = scan
                elif id_field == 'experiment':
                    id_obj = experiment
                elif id_field == 'subject':
                    id_obj = subject
                else:
                    # Must be project
                    id_obj = project

                if id_use_label:
                    id_ = id_obj.label
                else:
                    id_ = id_obj.id

                urls.append((id_, newurl))

            return tuple(urls)
        else:
            return url

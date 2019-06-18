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
This module contains the manager class for IOPlugins and the
base class for all IOPlugins
"""

from abc import abstractproperty
from abc import ABCMeta
import json
import os
import shutil
import urllib.parse as up

if __name__ == '__main__':
    FASTR_LOG_TYPE = 'console'

from .. import exceptions, resources
from ..abc.baseplugin import Plugin
from ..data import url as urltools
from ..datatypes import types, URLType, TypeGroup
from ..helpers import log, iohelpers


class IOPlugin(Plugin, metaclass=ABCMeta):
    """
    :py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>` are used for data import
    and export for the sources and sinks. The main use of the
    :py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>` is during execution (see
    :ref:`Execution <manual_execution>`). The :py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>`
    can be accessed via ``fastr.ioplugins``, but generally there should be no need
    for direct interaction with these objects. The use of is mainly via the URL
    used to specify source and sink data.
    """
    _instantiate = True

    def __init__(self):
        """
        Initialization for the IOPlugin

        :return: newly created IOPlugin
        """
        super(IOPlugin, self).__init__()
        self._results = {}

    @abstractproperty
    def scheme(self):
        """
        ``(abstract)`` This abstract property is to be overwritten by a subclass to indicate
        the url scheme associated with the IOPlugin.
        """
        raise exceptions.FastrNotImplementedError("IOPlugin scheme is not set")

    def url_to_path(self, url):
        """
        ``(abstract)`` Get the path to a file from a url.

        :param str url: the url to retrieve the path for
        :return: the corresponding path
        :rtype: str
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for working with urls'.format(self.scheme))

    def fetch_url(self, inurl, outfile):
        """
        ``(abstract)``  Fetch a file from an external data source.

        :param inurl: url to the item in the data store
        :param outpath: path where to store the fetch data locally
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for direct url data retrieval'.format(self.scheme))

    def fetch_value(self, inurl):
        """
        ``(abstract)``  Fetch a value from an external data source.

        :param inurl: the url of the value to retrieve
        :return: the fetched value
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for direct value data retrieval'.format(self.scheme))

    def put_url(self, inpath, outurl):
        """
        ``(abstract)`` Put the files to the external data store.

        :param inpath: path to the local data
        :param outurl: url to where to store the data in the external data store.
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for direct url data storage'.format(self.scheme))

    def put_value(self, value, outurl):
        """
        ``(abstract)`` Put the files to the external data store.

        :param value: the value to store
        :param outurl: url to where to store the data in the external data store.
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for direct value data storage'.format(self.scheme))

    def path_to_url(self, path, mountpoint=None):
        """
        ``(abstract)`` Construct an url from a given mount point and a relative
        path to the mount point.

        :param str path: the path to determine the url for
        :param mountpoint: the mount point to use, will be automatically
                           detected if None is given
        :type mountpoint: str or None
        :return: url matching the path
        :rtype: str
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument
        raise exceptions.FastrNotImplementedError('{} is not for working with urls'.format(self.scheme))

    def setup(self, *args, **kwargs):
        """
        ``(abstract)`` Setup before data transfer. This can be any function
        that needs to be used to prepare the plugin for data transfer.
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument,no-self-use
        pass

    def cleanup(self):
        """
        ``(abstract)`` Clean up the IOPlugin. This is to do things like
        closing files or connections. Will be called when the plugin is no
        longer required.
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument,no-self-use
        pass

    def expand_url(self, url):
        """
        ``(abstract)`` Expand an URL. This allows a source to collect multiple
        samples from a single url. The URL will have a wildcard or point to
        something with info and multiple urls will be returned.

        :param str url: url to expand
        :return: the resulting url(s), a tuple if multiple, otherwise a str
        :rtype: str or tuple of str
        """
        # This is a placeholder function, so we do no use our arguments
        # pylint: disable=unused-argument,no-self-use
        return url

    @staticmethod
    def isurl(string):
        """
        Test if given string is an url.

        :param str string: string to test
        :return: ``True`` if the string is an url, ``False`` otherwise
        :rtype: bool
        """
        parsed_url = up.urlparse(str(string))
        return parsed_url.scheme != ''

    @staticmethod
    def print_result(result):
        """
        Print the result of the IOPlugin to stdout to be picked up by the tool

        :param result: value to print as a result
        :return: None
        """
        print('__IOPLUGIN_OUT__={}'.format(json.dumps(result)))

    def pull_source_data(self, inurl, outdir, sample_id, datatype=None):
        """
        Transfer the source data from inurl to be available in outdir.

        :param str inurl: the input url to fetch data from
        :param str outdir: the directory to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        :return: None
        """
        results = {}
        self.setup()

        # First expand the URL
        valuelist = self.expand_url(inurl)

        log.debug('[{}] pulling sample {} with value {} and datatype {}'.format(
            self.scheme, sample_id, inurl, datatype)
        )

        if isinstance(valuelist, tuple):
            # We expanded the URL, so now process each new value/URL seperately
            if len(valuelist) == 0:
                raise exceptions.FastrValueError(('No data found when expanding'
                                                  ' URL {}, this probably means '
                                                  'the URL is not correct.').format(inurl))
            for cardinality_nr, (sub_sample_id, value) in enumerate(valuelist):
                if sub_sample_id is None:
                    log.debug('Changing sub sample id from None to {}'.format(sub_sample_id))
                    sub_sample_id = '{}_{}'.format(sample_id, cardinality_nr)
                log.debug('Found expanded item {}: {}'.format(sub_sample_id, value))
                if self.isurl(value):
                    # Expanded value is an URL, so it need to be processed
                    outsubdir = os.path.join(outdir, str(sub_sample_id))
                    if not os.path.isdir(outsubdir):
                        os.mkdir(outsubdir)
                    result = resources.ioplugins.pull_source_data(value, outsubdir, sub_sample_id, datatype)
                    results.update(result)
                else:
                    # Expanded value is a value, so we assume this is the value to be used
                    results[sub_sample_id] = (value,)
        elif isinstance(valuelist, str):
            # The expand did not change the URL
            if valuelist != inurl:
                raise exceptions.FastrValueError('If valuelist is a str, it should be the original inurl!')

            # Check against None to avoid issubclass throwing an error
            if datatype is not None and issubclass(datatype, TypeGroup):
                if all(issubclass(x, URLType) for x in datatype.members):
                    urltype = True
                elif all(not issubclass(x, URLType) for x in datatype.members):
                    urltype = False
                else:
                    raise exceptions.FastrNotImplementedError(
                        'Cannot use a SourceNode that can supply mixed URL and Value types'
                    )
            else:
                # Check against None to avoid issubclass throwing an error
                urltype = datatype is not None and issubclass(datatype, URLType)

            log.debug('[{}] the urltype found is {}'.format(self.scheme, urltype))

            if urltype:
                outfile = os.path.join(outdir, urltools.basename(inurl))
                result = self.fetch_url(inurl, outfile)

                if not result:
                    raise exceptions.FastrIOError('Could not retrieve data from {}'.format(inurl))

                if datatype is None or issubclass(datatype, TypeGroup):
                    datatype = types.guess_type(result, options=datatype)
                    log.debug('Refined datatype to {}'.format(datatype))

                if datatype is not None:
                    contents = datatype.content(inurl, result)
                    log.debug('Found contents {}'.format(contents))
                else:
                    contents = [(inurl, result)]

                for extrain, extraout in contents:
                    if extrain == inurl and extraout == result:
                        log.info('Skipping original file {} -> {}'.format(extrain, extraout))
                        continue

                    log.debug('Orig {} -> {}'.format(inurl, result))
                    log.debug('Processing original file {} -> {}'.format(extrain, extraout))

                    if os.path.exists(extraout):
                        continue

                    extra_result = self.fetch_url(extrain, extraout)
                    if not extra_result:
                        raise exceptions.FastrIOError('Could not retrieve data from {} to {}'.format(extrain, extraout))

                results[sample_id] = (result,)
            else:
                result = self.fetch_value(inurl)
                results[sample_id] = (result,)

            prov_filename = urltools.basename(inurl).replace('.', '_') + '.prov.json'
            prov_inurl = urltools.join(
                urltools.dirurl(inurl),
                prov_filename
            )
            prov_outfile = os.path.join(outdir, prov_filename)

            try:
                prov_result = self.fetch_url(prov_inurl, prov_outfile)

                if prov_result:
                    log.info('Got provenance file for {}'.format(inurl))

                    if prov_result != prov_outfile:
                        # Make sure the prov file is at the right place
                        iohelpers.link_or_copy(prov_result, prov_outfile)
                else:
                    log.info('Could not get provenance file for {}'.format(inurl))
            except Exception:
                # Cannot retrieve prov with this plugin
                log.info('Could not get provenance file for {}'.format(inurl))

        else:
            log.error('Expand of {} returned an invalid type! ({} after expansion)'.format(inurl, valuelist))

        return results

    def push_sink_data(self, inpath, outurl, datatype=None):
        """
        Write out the sink data from the inpath to the outurl.

        :param str inpath: the path of the data to be pushed
        :param str outurl: the url to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        :return: None
        """
        log.info('Push sink called with: {}, {}'.format(inpath, outurl))
        self.setup()

        if datatype is None or issubclass(datatype, TypeGroup):
            previous_datatype = datatype.id if datatype is not None else None
            datatype = types.guess_type(inpath, options=datatype)
            log.info('Determined specific datatype as {} (based on {})'.format(datatype.id, previous_datatype))

        if datatype is not None and issubclass(datatype, URLType):
            contents = datatype.content(inpath, outurl)
            log.info('Found URL contents: {}'.format(contents))
        else:
            contents = [(inpath, outurl)]
            log.info('Found value/simple contents: {}'.format(contents))

        for extracontent, extratarget in contents:
            if datatype is not None and issubclass(datatype, URLType):
                result = self.put_url(extracontent, extratarget)
            else:
                result = self.put_value(extracontent, extratarget)
            if not result:
                raise exceptions.FastrIOError('Could not store data from {} to {}'.format(extracontent, extratarget))

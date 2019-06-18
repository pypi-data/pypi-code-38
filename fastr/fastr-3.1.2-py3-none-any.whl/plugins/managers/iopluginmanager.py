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

import sys
import urllib.parse as up

from .pluginmanager import PluginSubManager
from ...core.ioplugin import IOPlugin
from ...core.tool import Tool
from ...core.version import Version


class IOPluginManager(PluginSubManager):
    """
    A mapping containing the IOPlugins known to this system
    """

    def __init__(self, parent):
        """
        Create the IOPluginManager and populate it.

        :return: newly created IOPluginManager
        """
        super().__init__(parent=parent,
                         plugin_class=IOPlugin)
        self._key_map = {}

    def cleanup(self):
        """
        Cleanup all plugins, this closes files, connections and other things
        that could be left dangling otherwise.
        """
        for ioplugin in list(self.values()):
            ioplugin.cleanup()

    def __keytransform__(self, key):
        try:
            return self._key_map[key]
        except KeyError:
            self._key_map.clear()
            for id_, value in self.data.items():
                if isinstance(value.scheme, tuple):
                    for scheme in value.scheme:
                        self._key_map[scheme] = id_
                else:
                    self._key_map[value.scheme] = id_

            return self._key_map[key]

    def __iter__(self):
        for value in self.data.values():
            if isinstance(value.scheme, tuple):
                for scheme in value.scheme:
                    yield scheme
            else:
                yield value.scheme

    def _print_key(self, key):
        """
        Get a printable string for the IOPlugin key

        :param key: key to get the printable version for
        :return: printable version of the key
        :rtype: str
        """
        return self[key].status.value, '{}://'.format(key)

    def expand_url(self, url):
        """
        Expand the url by filling the wildcards. This function checks the url scheme
        and uses the expand function of the correct IOPlugin.

        :param str url: url to expand
        :return: list of urls
        :rtype: list of str
        """
        parsed_url = up.urlparse(url)
        return self[parsed_url.scheme].expand_url(url)

    def pull_source_data(self, url, outdir, sample_id, datatype=None):
        """
        Retrieve data from an external source. This function checks the url scheme and
        selects the correct IOPlugin to retrieve the data.

        :param url: url to pull
        :param str outdir: the directory to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        :return: None
        """
        parsed_url = up.urlparse(url)
        return self[parsed_url.scheme].pull_source_data(url, outdir, sample_id, datatype)

    def push_sink_data(self, inpath, outurl, datatype=None):
        """
        Send data to an external source. This function checks the url scheme and
        selects the correct IOPlugin to retrieve the data.

        :param str inpath: the path of the data to be pushed
        :param str outurl: the url to write the data to
        :param DataType datatype: the datatype of the data, used for determining
                                  the total contents of the transfer
        """
        parsed_url = up.urlparse(outurl)
        return self[parsed_url.scheme].push_sink_data(inpath=inpath,
                                                      outurl=outurl,
                                                      datatype=datatype)

    def put_url(self, inpath, outurl):
        """
        Put the files to the external data store.

        :param inpath: path to the local data
        :param outurl: url to where to store the data in the external data store.
        """
        parsed_url = up.urlparse(outurl)
        return self[parsed_url.scheme].put_url(inpath, outurl)

    def url_to_path(self, url):
        """
        Retrieve the path for a given url

        :param str url: the url to parse
        :return: the path corresponding to the input url
        :rtype: str
        """
        parsed_url = up.urlparse(url)
        return self[parsed_url.scheme].url_to_path(url)

    @staticmethod
    def register_url_scheme(scheme):
        """
        Register a custom scheme to behave http like. This is needed to parse
        all things properly with urlparse.

        :param scheme: the scheme to register
        """
        for method in [s for s in dir(up) if s.startswith('uses_')]:
            if scheme not in getattr(up, method):
                getattr(up, method).append(scheme)

    @staticmethod
    def create_ioplugin_tool(tools, interfaces):
        """
        Create the tools which handles sinks and sources. The command of this tool is the main of core.ioplugin.
        """
        if ('fastr/Source:1.0', '1.0') not in tools:
            source_tool = Tool()
            source_tool._id = 'Source'
            source_tool.name = 'Source'
            source_tool.description = 'Tool to execute Fastr source nodes'
            source_tool.authors = []
            source_tool.version = Version('1.0')
            source_tool.namespace = 'fastr'
            source_tool.node_class = 'SourceNode'
            source_tool.filename = __file__
            source_tool.tests = []
            source_tool._target = None
            source_tool.command = {'authors': ['fastr devs'],
                                   'description': 'Source Tool: tool to handle SourceNode operation.',
                                   'targets': [{
                                       'os': '*',
                                       'arch': '*',
                                       'bin': 'source.py',
                                       'interpreter': sys.executable,
                                       'paths': '../../utils/cmd/',
                                       'module': None
                                   }],
                                   'url': 'http://www.bigr.nl/fastr',
                                   'version': Version('1.0')}

            input_params = [{'id': 'input',
                             'name': 'input',
                             'description': 'The data to be retrieved by the SourceNode',
                             'datatype': 'String',
                             'prefix': '--input',
                             'repeat_prefix': False,
                             'cardinality': '1-*',
                             'required': True,
                             'hidden': True},
                            {'id': 'datatype',
                             'name': 'datatype',
                             'datatype': 'String',
                             'prefix': '--datatype',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            {'id': 'targetdir',
                             'name': 'targetdir',
                             'description': 'The location to store the result',
                             'datatype': 'Directory',
                             'prefix': '--output',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            {'id': 'sample_id',
                             'name': 'sample_id',
                             'description': 'The sample id for the SourceJob that is run',
                             'datatype': 'String',
                             'prefix': '--sample_id',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True}]

            output_params = [{'id': 'output',
                              'name': 'The output urls in vfs scheme',
                              'description': '',
                              'datatype': 'AnyType',
                              'cardinality': 'unknown',
                              'automatic': True,
                              'location': '^__IOPLUGIN_OUT__=(.*)$',
                              'method': 'json'}]

            interface = {'inputs': input_params, 'outputs': output_params}
            source_tool.interface = interfaces['FastrInterface'](id_='source-interface', document=interface)

            # Register source tool with the ToolManager
            tools['fastr/Source:1.0', '1.0'] = source_tool

        if ('fastr/Sink:1.0', '1.0') not in tools:
            sink_tool = Tool()
            sink_tool._id = 'Sink'
            sink_tool.name = 'Sink'
            sink_tool.description = 'Tool to execute Fastr sink nodes'
            sink_tool.authors = []
            sink_tool.version = Version('1.0')
            sink_tool.namespace = 'fastr'
            sink_tool.node_class = 'SinkNode'
            sink_tool.filename = __file__
            sink_tool.tests = []
            sink_tool._target = None
            sink_tool.command = {'authors': ['fastr devs'],
                                 'description': 'Sink Tool: tool to handle Sink Node operation.',
                                 'targets': [{
                                     'os': '*',
                                     'arch': '*',
                                     'bin': 'sink.py',
                                     'interpreter': sys.executable,
                                     'paths': '../../utils/cmd/',
                                     'module': None
                                 }],
                                 'url': 'http://www.bigr.nl/fastr',
                                 'version': Version('1.0')}

            input_params = [{'id': 'input',
                             'name': 'The url to process (can also be a list)',
                             'description': 'The data to be store by the SinkNode',
                             'datatype': 'AnyType',
                             'prefix': '--input',
                             'cardinality': '1-*',
                             'required': True, },
                            {'id': 'output',
                             'name': 'output',
                             'datatype': 'String',
                             'prefix': '--output',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            {'id': 'datatype',
                             'name': 'datatype',
                             'datatype': 'String',
                             'prefix': '--datatype',
                             'cardinality': '1',
                             'required': True,
                             'hidden': True},
                            ]

            output_params = []

            interface = {'inputs': input_params, 'outputs': output_params}
            sink_tool.interface = interfaces['FastrInterface'](id_='sink-interface', document=interface)

            # Register sink tool with the ToolManager
            tools['fastr/Sink:1.0', '1.0'] = sink_tool



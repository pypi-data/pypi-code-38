from rockset import Client
from .command_rest import RESTCommand
from .util.parse_util import parse_collection_path

from docopt import docopt
from requests_toolbelt import MultipartEncoder

import json
import os
import sys
import yaml


class Upload(RESTCommand):
    def usage(self):
        return """
usage: rock upload --help
       rock upload <collection> [<files> ...] [options]
       rock upload --file=YAML_CONFIG_FILE

Add local files to a collection

arguments for `rock upload`:
  <collection>      name of the collection you wish to add data. Defaults to 'commons' workspace.
                    For collections inside other workspace, use 'workspace.collection' notation.
  <files>           add local files to the collection
                    use "-" for STDIN

options for `rock upload`:
  -h, --help                           show this help message and exit
  -f, --file <YAML configuration file>  upload all files specified in the YAML config file
  --format=CSV                         Specify the format of data. Uses the default format parameters.
                                       Use YAML file if specific format options need to be specified

examples:

    Upload a file:
        $ rock upload my-collection file.json --format=JSON

    Specify csv format parameters using yaml file:
    ```
    collection: my-collection
    files:
      - file.csv
    format_params:
      csv:
        firstLineAsColumnNames: false
        separator: ','
        columnNames:
            - c1
            - c2
        columnTypes:
            - BOOLEAN
            - INTEGER
    ```

    Specify xml format paramaters using yaml file:
    ```
    collection: my-collection
    files:
      - file.xml
    format_params:
      xml:
        root_tag: 'root'
        doc_tag: 'doc'
        attribute_prefix: '_'
        value_tag: 'my_value'
    ```

    Upload a file using yaml config:
        $ rock upload -f upload.yaml
        """
    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args, help=False))
        if parsed_args['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        fn = parsed_args['--file']
        if fn:
            self.set_batch_items('upload', self._parse_yaml_file(fn, upload=True))
            return {}

        upload = {}

        if parsed_args['<collection>']:
            upload['collection'] = parsed_args['<collection>']

        upload['format_params'] = {}
        if parsed_args['--format']:
            data_format = parsed_args['--format']
            if data_format == 'CSV':
                upload['format_params'] = {'csv': {'firstLineAsColumnNames': False}}
            elif data_format == 'XML':
                upload['format_params'] = {'xml': {'doc_tag':''}}

        files = []
        for localfile_path in parsed_args['<files>']:
            files.append(localfile_path)

        upload['files'] = files

        return {'upload': upload}

    def _input(self):
        return sys.stdin

    def go(self):
        client = Client(api_key=self.api_key, api_server=self.api_server)
        files = self.upload.pop('files')
        for localfile_path in files:
            try:
                localfile = None
                if localfile_path == '-':
                    localfile = self._input()
                    localfile_contents = localfile.read()
                    encoder = MultipartEncoder({'file': ('input', localfile_contents, None),
                        'size': str(len(localfile_contents))})
                else:
                    try:
                        index = localfile_path.rindex('/') + 1
                    except ValueError as e:
                        index = 0

                    size = os.path.getsize(localfile_path)
                    file_name = localfile_path[index:]
                    params = '{}'
                    if 'format_params' in self.upload:
                        params = json.dumps((self.upload['format_params']))
                    localfile = open(localfile_path, 'rb')
                    encoder = MultipartEncoder(
                            {'file': (file_name, localfile, None),
                                'params': params, 'size': str(size)})

                path = self.upload['collection']
                workspace, name = parse_collection_path(path)
                path = '/v1/orgs/{}/ws/{}/collections/{}/uploads'.format('self', workspace, name)
                resp = self.post(path, data=encoder, headers={'Content-Type': encoder.content_type}, timeout=None)['data']
                self.print_list_json(0, [resp])
            except (OSError, IOError) as e:
                self.error(
                        'Skipping file {} : Unable to open: {}'.format(
                            localfile_path, str(e)
                            )
                        )
                continue
            finally:
                if localfile_path != '-' and localfile:
                    localfile.close()

        return 0

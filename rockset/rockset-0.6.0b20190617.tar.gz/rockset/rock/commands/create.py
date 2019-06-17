import re
import yaml
from .command_auth import AuthCommand
from .util.parse_util import parse_collection_path
from datetime import timedelta
from docopt import docopt
from rockset.exception import InputError
from .util.type_util import IntegrationType


class Create(AuthCommand):
    def usage(self):
        return """
Usage:
    rock create [-h | -f=YAML_FILE]
    rock create collection <name> [--description=TEXT] [options] [<data_source_url>...]
    rock create workspace <name> [--description=TEXT]
    rock create integration gcs <name> [--description=TEXT] --service_account_key_file_json=JSON
    rock create integration dynamodb <name> [--description=TEXT] --aws_access_key_id=ID --aws_secret_access_key=SECRET
    rock create integration kinesis <name> [--description=TEXT] ( --aws_role_arn=ARN | --aws_access_key_id=ID --aws_secret_access_key=SECRET )
    rock create integration redshift <name> [--description=TEXT] --aws_access_key_id=ID --aws_secret_access_key=SECRET --host=HOST --port=PORT --username=USERNAME --password=PASSWORD --s3_bucket_path=PATH
    rock create integration s3 <name> [--description=TEXT] ( --aws_role_arn=ARN | --aws_access_key_id=ID --aws_secret_access_key=SECRET )


Options for `rock create`:

    -h, --help                                  Show this help message and exit.

    -f, --file=YAML_FILE                        Create all resources specified in the YAML file.
                                                Run `rock -o yaml describe <collection>` on an
                                                existing collection to see the YAML format.


Options for `rock create collection`:

    --integration=INTEGRATION_NAME              Specify an integration that will be used to access
                                                the source of this collection. For sources that don't need
                                                special access or credentials, this can be left unspecified.

    --event-time-field=FIELD_NAME               specify a root-level field, representing time in one of the
                                                formats supported by rockset (look at --event-time-format)
                                                this field will be mapped to event-time.

    --event-time-format TIME_FORMAT             specify the format of time in which the field mapped to event-time
                                                is formatted in your documents. (requires --event-time-field)
                                                supported formats   * milliseconds_since_epoch (default)
                                                                    * seconds_since_epoch

    --event-time-default-timezone TIME_ZONE     specify the time zone of event times in the documents which will be
                                                added into this collection. (requires --event-time-field)
                                                default is 'UTC' (supported time zones: one of standard IANA time zones)

    --retention RETENTION_DURATION              specify the minimum time duration using short-hand notation
                                                (such as 24h, 8d, or 13w) for which documents in this collection
                                                will be retained before being automatically deleted.
                                                (default: none i.e., documents will be retained indefinitely)

    --format CSV                                Specify the format of data in this source. If the data is
                                                comma separted values per line, then specify CSV. Other
                                                formats of data are auto detected and this parameter
                                                should not be specified for non-csv data formats.
                                                All options below only are only applicable when format is CSV.

    --csv-separator ","                         Separator for columns for csv files.

    --csv-encoding "UTF-8"                      Encoding, one of "UTF-8", "UTF-16", "ISO-8859-1".

    --csv-first-line-as-column-names false      If true, then use the first column as the column names.

    --csv-column-names "c1,col2",               A comma separated list of column names

    --csv-column-types "int,boolean",           A comma separated list of column types and should have a
                                                one-to-one mapping to the names specified in column-names.

    --csv-schema-file "/home/schema.yaml"       A file that specifies the schema of the data.
                                                It is an yaml file that specifies the name of each column
                                                and the type of data in each column. If a schema file is
                                                specified, then the values specified by csv-column-names
                                                and csv-column-types are ignored.


Data sources:

    <data_source_url>                           specify the data source to auto ingest in order to 
                                                populate the collection, e.g.:
                                                    s3://my-precious-s3-bucket
                                                    s3://my-precious-s3-bucket/data/path/prefix
                                                    dynamodb://my-precious-dynamodb-table-name
                                                    kinesis://my-precious-kinesis-stream-name
                                                    gs://server-logs
                                                    gs://server-logs/path/prefix


Examples:

    Create a collection and source all contents from an AWS S3 bucket:
        $ rock create collection customers s3://customers-mycompany-com

    Create a collection from an AWS S3 bucket but only pull a particular path prefix within the S3 bucket:
        $ rock create collection event-log s3://event-log.mycompany.com/root/path/in/bkt --integration aws-rockset-readonly

    Create a collection with a source that ingests data from kinesis stream:
        $ rock create collection events kinesis://click-streams --integration aws-rockset-readonly

    Create a collection and map a field to event-time:
        $ rock create collection my-event-data --event-time-field timestamp --event-time-format milliseconds_since_epoch

    Create a collection with retention set to 10 days:
        $ rock create collection my-event-data --retention="10d"

"""

    def parse_args(self, args):
        parsed = dict(docopt(self.usage(), argv=args, help=False))

        # handle help
        if parsed['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        # see if YAMLFILE was specified
        fn = parsed['--file']
        if fn:
            self.set_batch_items('resource', self._parse_yaml_file(fn))
            return {}

        # process args
        resource = {}

        resource['name'] = parsed['<name>']

        for option in [
            'aws_access_key_id',
            'aws_role_arn',
            'aws_secret_access_key',
            'description',
            'host',
            'password',
            'port',
            's3_bucket_path',
            'service_account_key_file_json',
            'username',
        ]:
            resource[option] = parsed['--{}'.format(option)]

        if parsed['workspace']:
            resource['type'] = 'WORKSPACE'

        elif parsed['integration']:
            resource['type'] = 'INTEGRATION'
            resource['integration_type'] = IntegrationType.UNKNOWN
            for t in ['dynamodb', 'gcs', 'kinesis', 's3', 'redshift']:
                if parsed[t]:
                    resource['integration_type'] = IntegrationType.parse(t)
                    break

        elif parsed['collection']:
            resource['workspace'], resource['name'] = parse_collection_path(
                parsed['<name>']
            )

            sources = []
            integration = None

            integration_name = parsed['--integration']
            if integration_name:
                resource['integration'] = integration_name
                try:
                    integration = self.client.Integration.retrieve(
                        name=integration_name
                    )
                except InputError as e:
                    ret = "Error: {}\n".format(str(e))
                    raise SystemExit(ret.strip())

            # Specifiy the format of data in collection source
            data_format = "auto_detect"
            format_params = None
            if parsed['--format'] is not None:
                data_format = parsed['--format']

            if data_format == "CSV":
                csv_separator = None
                csv_encoding = None
                csv_first_line_as_column_names = None
                csv_column_names = None
                csv_column_types = None
                if parsed['--csv-separator'] is not None:
                    csv_separator = parsed['--csv-separator']
                if parsed['--csv-encoding'] is not None:
                    csv_encoding = parsed['--csv-encoding']
                if parsed['--csv-first-line-as-column-names'] is not None:
                    csv_first_line_as_column_names = parsed[
                        '--csv-first-line-as-column-names'
                    ]
                if parsed['--csv-column-names'] is not None:
                    csv_column_names_str = parsed['--csv-column-names']
                    csv_column_names = csv_column_names_str.split(',')
                if parsed['--csv-column-types'] is not None:
                    csv_column_types_str = parsed['--csv-column-types']
                    csv_column_types = csv_column_types_str.split(',')

                # if this is a csv schema file, load it and extract
                # the column names and types from it.
                if parsed['--csv-schema-file'] is not None:
                    csv_schema_file = parsed['--csv-schema-file']
                    with open(csv_schema_file, 'r') as stream:
                        data_loaded = yaml.load(stream)

                        # fetch appropriate entry for this collection from the schema file
                        all_columns = data_loaded.get('fields')
                        if all_columns is None:
                            print(
                                'No fields entry ' + resource['name'] +
                                ' in file ' + csv_schema_file
                            )
                            raise SystemExit

                        # one entry in the file shows up as
                        # [{'col1': 'integer'}, {'col2': 'string'}, {'col3': 'boolean'}]

                        csv_column_names = []
                        csv_column_types = []
                        for i in range(len(all_columns)):
                            onecol = all_columns[i]
                            assert len(onecol) == 1
                            colnames = list(all_columns[i].keys())
                            csv_column_names.append(list(onecol.keys())[0])
                            csv_column_types.append(list(onecol.values())[0])

                format_params = self.client.Source.csv_params(
                    separator=csv_separator,
                    encoding=csv_encoding,
                    first_line_as_column_names=csv_first_line_as_column_names,
                    column_names=csv_column_names,
                    column_types=csv_column_types
                )

            resource['type'] = 'COLLECTION'
            for source in parsed['<data_source_url>']:
                if source[:5] == 's3://':
                    sources.append(
                        self._source_s3(source, integration, format_params)
                    )
                elif source[:11] == 'dynamodb://':
                    sources.append(self._source_dynamo(source, integration))
                elif source[:10] == 'kinesis://':
                    sources.append(self._source_kinesis(source, integration))
                elif source[:5] == 'gs://':
                    sources.append(
                        self._source_gcs(source, integration, format_params)
                    )
                else:
                    ret = 'Error: invalid data source URL "{}"\n'.format(source)
                    ret += self.usage()
                    raise SystemExit(ret.strip())

            # handle options related to event_time
            if parsed['--event-time-field'] is not None:
                resource['event_time_field'] = parsed['--event-time-field']
                resource['event_time_format'] = parsed['--event-time-format']
                resource['event_time_default_timezone'
                        ] = parsed['--event-time-default-timezone']
            elif parsed['--event-time-format'] is not None:
                ret = 'Error: --event-time-field is required to specify --event-time-format'
                ret += self.usage()
                raise SystemExit(ret.strip())
            elif parsed['--event-time-default-timezone'] is not None:
                ret = 'Error: --event-time-field is required to specify --event-time-default-timezone'
                ret += self.usage()
                raise SystemExit(ret.strip())

            #handle retention
            if parsed['--retention'] is not None:
                try:
                    retention = self._convert_to_seconds(parsed['--retention'])
                    resource['retention_secs'] = retention
                except ValueError as e:
                    ret = 'Error: invalid argument "{}" for --retention, {}'.format(
                        parsed['--retention'], str(e)
                    )
                    ret += self.usage()
                    raise SystemExit(ret)
                except OverflowError as e:
                    ret = 'Error: invalid value "{}" for --retention, {}'.format(
                        parsed['--retention'], str(e)
                    )
                    ret += self.usage()
                    raise SystemExit(ret)

            resource['sources'] = sources
        else:
            ret = self.usage()
            raise SystemExit(ret.strip())

        return {'resource': resource}

    def go(self):
        self.logger.info('create {}'.format(self.resource))
        rtype = self.resource.pop('type', None)
        if rtype is None:
            return 1
        if rtype == 'COLLECTION':
            return self.go_collection(self.resource)
        elif rtype == 'INTEGRATION':
            return self.go_integration(self.resource)
        elif rtype == 'WORKSPACE':
            return self.go_workspace(self.resource)
        return 1

    def go_collection(self, resource):
        name = resource.pop('name')
        workspace = resource.pop('workspace', 'commons')
        c = self.client.Collection.create(name, workspace=workspace, **resource)
        self.lprint(
            0, 'Collection "%s" was created successfully in workspace "%s".' %
            (c.name, c.workspace)
        )
        return 0

    def go_integration(self, resource):
        integration_type = resource['integration_type']

        try:
            if integration_type == IntegrationType.DYNAMODB:
                self.client.Integration.Dynamodb.create(
                    name=resource['name'],
                    description=resource['description'],
                    aws_access_key_id=resource['aws_access_key_id'],
                    aws_secret_access_key=resource['aws_secret_access_key'],
                )
            elif integration_type == IntegrationType.GCS:
                self.client.Integration.Gcs.create(
                    name=resource['name'],
                    description=resource['description'],
                    service_account_key_file_json=resource[
                        'service_account_key_file_json'
                    ],
                )
            elif integration_type == IntegrationType.KINESIS:
                self.client.Integration.Kinesis.create(
                    name=resource['name'],
                    description=resource['description'],
                    aws_access_key_id=resource['aws_access_key_id'],
                    aws_secret_access_key=resource['aws_secret_access_key'],
                    aws_role_arn=resource['aws_role_arn'],
                )
            elif integration_type == IntegrationType.REDSHIFT:
                self.client.Integration.Redshift.create(
                    name=resource['name'],
                    description=resource['description'],
                    aws_access_key_id=resource['aws_access_key_id'],
                    aws_secret_access_key=resource['aws_secret_access_key'],
                    username=resource['username'],
                    password=resource['password'],
                    host=resource['host'],
                    port=int(resource['port']),
                    s3_bucket_path=resource['s3_bucket_path'],
                )
            elif integration_type == IntegrationType.S3:
                self.client.Integration.S3.create(
                    name=resource['name'],
                    description=resource['description'],
                    aws_access_key_id=resource['aws_access_key_id'],
                    aws_secret_access_key=resource['aws_secret_access_key'],
                    aws_role_arn=resource['aws_role_arn'],
                )

            self.lprint(
                0, 'Integration {} was created successfully.'.format(
                    resource['name']
                )
            )

            return 0

        except ValueError as e:
            ret = "Error: {}\n".format(str(e))
            ret += self.usage('integration')
            raise SystemExit(ret.strip())

        return 1

    def go_workspace(self, resource):
        name = resource.pop('name')
        w = self.client.Workspace.create(name, **resource)
        self.lprint(0, 'Workspace "%s" was created successfully.' % (w.name))
        return 0

    def _convert_to_seconds(self, duration):

        num = duration[:-1]
        try:
            num = int(num)
        except ValueError as e:
            ret = 'invalid duration "{}"\n'.format(num)
            raise ValueError(ret)

        unit = duration[-1]
        try:
            if unit == 'h':
                time_delta = timedelta(hours=num)
            elif unit == 'd':
                time_delta = timedelta(days=num)
            elif unit == 'w':
                time_delta = timedelta(weeks=num)
            else:
                ret = 'invalid time unit "{}"\n'.format(unit)
                raise ValueError(ret)
        except OverflowError:
            ret = 'duration "{}" too large for specified time units\n'.format(
                num
            )
            raise OverflowError(ret)

        return int(time_delta.total_seconds())

    def _source_s3(self, s3_url, integration, format_params):
        parts = s3_url[5:].split('/')
        bucket = parts[0]
        path = '/'.join(parts[1:])
        prefix = None
        pattern = None

        matchPattern = re.compile(r'[*?{}]')
        if bool(matchPattern.search(path)):
            pattern = path
        else:
            prefix = path

        return self.client.Source.s3(
            bucket=bucket,
            prefix=prefix,
            pattern=pattern,
            integration=integration,
            format_params=format_params
        )

    def _source_dynamo(self, url, integration):
        table_name = url[11:]

        return self.client.Source.dynamo(
            table_name=table_name, integration=integration
        )

    def _source_kinesis(self, kinesis_url, integration):
        stream_name = kinesis_url[10:]

        return self.client.Source.kinesis(
            stream_name=stream_name, integration=integration
        )

    def _source_gcs(self, gcs_url, integration, format_params):
        parts = gcs_url[5:].split('/')
        bucket = parts[0]
        prefix = None
        if len(parts) > 1:
            path = '/'.join(parts[1:])
            prefix = path

        return self.client.Source.gcs(
            bucket=bucket,
            prefix=prefix,
            integration=integration,
            format_params=format_params
        )

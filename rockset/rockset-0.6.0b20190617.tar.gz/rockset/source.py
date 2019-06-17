"""
Introduction
------------
Source objects represent various data sources that could be used to create
collections.

Example usage
-------------
::

    from rockset import Client, Q, F
    import os

    rs = Client()

    # create a collection from an AWS S3 bucket
    integration = rs.Integration.retrieve('aws-rockset-read-only')
    s3 = rs.Source.s3(bucket='my-s3-bucket',
        integration=integration)
    newcoll = rs.Collection.create(name='newcoll', sources=[s3])

Create AWS S3 source for a collection
-------------------------------------
AWS S3 buckets can be used as a data source for collections::

    from rockset import Client, Q, F
    import os

    rs = Client()

    # create a collection from an AWS S3 bucket
    integration = rs.Integration.retrieve('aws-rockset-read-only')
    s3 = rs.Source.s3(bucket='my-s3-bucket',
        integration=integration)
    newcoll = rs.Collection.create(name='newcoll', sources=[s3])

.. automethod :: rockset.Source.s3

"""

from rockset.swagger_client.models import (
    FormatParams,
    Integration,
    CsvParams,
    XmlParams,
)


class Source(object):
    def __init__(self, integration, format_params):
        if isinstance(integration,
                      Integration) or isinstance(integration, dict):
            self.integration_name = integration.get('name')
        elif integration is not None:
            ret = 'TypeError: invalid object type {} for integration'.format(
                type(integration)
            )
            raise TypeError(ret)

        if format_params is not None:
            self.format_params = format_params

    def __str__(self):
        return str(vars(self))

    def __iter__(self):
        for k, v in vars(self).items():
            yield (k, v)

    @classmethod
    def s3(
        cls,
        bucket,
        prefixes=None,
        prefix=None,
        pattern=None,
        integration=None,
        format_params=None
    ):
        """ Creates a source object to represent an AWS S3 bucket as a
        data source for a collection.

        Args:
            bucket (str): Name of the S3 bucket
            prefix: Path prefix to only source S3 objects that
                are recursively within the given path. (optional)
            pattern: Path pattern to only source S3 objects that
                match the given pattern. (optional)
            integration (rockset.Integration): An Integration object (optional)
            format_params (FormatParams): the specifications of the format, CsvParams or XmlParams
        """
        return SourceS3(
            bucket=bucket,
            prefixes=prefixes,
            prefix=prefix,
            pattern=pattern,
            integration=integration,
            format_params=format_params
        )

    @classmethod
    def dynamo(
        cls,
        table_name,
        integration=None,
    ):
        """ Creates a source object to represent an AWS DynamoDB table as a
        data source for a collection.

        Args:
            table_name (str): Name of the DynamoDb table
            integration (rockset.Integration): An Integration object (optional)
        """
        return SourceDynamo(table_name=table_name, integration=integration)

    @classmethod
    def kinesis(
        cls,
        stream_name,
        integration,
    ):
        """ Created a source object to represent a Kinesis Stream as a
        data source for a collection

        Args:
            stream_name (str): Name of the Kinesis Stream
            integration (rockset.Integration): An Integration object (optional)
        """

        return SourceKinesis(stream_name=stream_name, integration=integration)

    @classmethod
    def csv_params(
        cls,
        separator=None,
        encoding=None,
        first_line_as_column_names=None,
        column_names=None,
        column_types=None
    ):
        """ Creates a object to represent options needed to parse a CSV file

        Args:
            separator (str): The separator between column values in a line
            encoding (str): The encoding format of data, one of "UTF-8",
                "UTF-16" "US_ASCII"
                [default: "US-ASCII"]
            first_line_as_column_names (boolean): Set to true if the first line
                of a data object has the names of columns to be used. If this is
                set to false, the the column names are auto generated.
                [default: False]
            column_names (list of strings): The names of columns
            column_types (list of strings): The types of columns
        """
        csv = CsvParams(
            separator=separator,
            encoding=encoding,
            first_line_as_column_names=first_line_as_column_names,
            column_names=column_names,
            column_types=column_types
        )
        return FormatParams(csv=csv)

    @classmethod
    def xml_params(
        cls,
        root_tag=None,
        doc_tag=None,
        encoding=None,
        value_tag=None,
        attribute_prefix=None
    ):
        """Creates a object to represent options needed to parse a XML file

        Args:
            root_tag (str): Outermost tag within an XML file to be treated as the root.
                            Any content outside the root tag is ignored.
            doc_tag (str): Every rockset document is contained between <doc_tag> and a </doc_tag>
            encoding (str): The encoding format of data. [default: 'UTF-8']
            value_tag (str): Tag used for the value when there are attributes in
                             the element having no child. [default: 'value']
            attribute_prefix (str): Attributes are transformed into key-value pairs in a Rockset document
                                   This prefix is used to tell attributes apart from nested tags in a Rockset document.
        """
        xml = XmlParams(
            root_tag=root_tag,
            doc_tag=doc_tag,
            encoding=encoding,
            value_tag=value_tag,
            attribute_prefix=attribute_prefix
        )
        return FormatParams(xml=xml)

    @classmethod
    def gcs(
        cls, bucket=None, prefix=None, integration=None, format_params=None
    ):
        """ Creates a source object to represent an Google Cloud Storage(GCS) bucket as a
        data source for a collection.

        Args:
            bucket (str): Name of the GCS bucket
            prefix: selects objects whose path matches the specified prefix within the bucket
            integration (rockset.Integration): An Integration object (optional)
            format_params (FormatParams): the specifications of the format, CsvParams or XmlParams
        """

        return SourceGcs(
            bucket=bucket,
            prefix=prefix,
            integration=integration,
            format_params=format_params
        )


class SourceS3(Source):
    def __init__(
        self,
        bucket=None,
        prefixes=None,
        prefix=None,
        pattern=None,
        integration=None,
        format_params=None
    ):
        super().__init__(integration, format_params)
        self.s3 = {
            'bucket': bucket,
        }
        if prefixes is not None:
            if len(prefixes) > 0:
                self.s3['prefix'] = prefixes[0]
            else:
                self.s3['prefix'] = ''

        if prefix is not None:
            self.s3['prefix'] = prefix
        elif pattern is not None:
            self.s3['pattern'] = pattern


class SourceDynamo(Source):
    def __init__(self, table_name=None, integration=None, format_params=None):
        super().__init__(integration, format_params)

        self.dynamodb = {'table_name': table_name}


class SourceKinesis(Source):
    def __init__(self, stream_name=None, integration=None, format_param=None):
        super().__init__(integration, format_param)

        self.kinesis = {'stream_name': stream_name}


class SourceGcs(Source):
    def __init__(
        self, bucket=None, prefix=None, integration=None, format_params=None
    ):
        super().__init__(integration, format_params)

        self.gcs = {'bucket': bucket, 'prefix': prefix}

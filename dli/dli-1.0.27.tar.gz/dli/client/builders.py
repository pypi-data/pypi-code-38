
class DatasetBuilder:
    """
    Dataset is grouping of related datafiles. It provides user with metadata required to consume and use the data.

    This builder object sets sensible defaults and exposes
    helper methods on how to configure its storage options..

    :param str package_id: Package ID to which the dataset belongs to.
    :param str name: A descriptive name of the dataset. It should be unique within the package the dataset
                    belongs to.
    :param str description: A short description of the dataset.
    :param str content_type: A way for the data steward to classify the type of data in the dataset
                        (e.g. pricing).
    :param str data_format: The format of the data: `CSV`, `IMAGE`, `JSON`, `PARQUET`, `TXT`, `XML`, `Other`.
    :param str publishing_frequency: The internal on which data is published. Possible values are: `Hourly`,
                                        `Daily`, `Weekday`, `Weekly`, `Monthly`, `Quarterly`, `Yearly`, `Not Specified`.
    :param list[str] taxonomy: A list of segments to be used for a taxonomy,
                                    the Data-<< Organization >>-<< topic >> prefix will be applied by the catalogue  For
                                    a taxonomy of Data-IHS Markit-Financial Markets-Credit-CDS, you would provide
                                    `taxonomy=["Credit", "CDS"]`
    :param list[str] keywords: Optional. User-defined list of separated keywords that can be used to find this dataset
                            through the search interface.
    :param str naming_convention: Optional. Key for how to read the dataset name.
    :param str documentation: Optional. Documentation about this dataset in markdown format.
    :param str load_type: Optional. Whether each datafile in this dataset should be considered as a full version of a
                        dataset or a delta or increment. Accepted types are `Full Load`, `Incremental Load`
    """

    def __init__(
        self,
        package_id,
        name,
        description,
        content_type,
        data_format,
        publishing_frequency,
        taxonomy,
        keywords=None,
        naming_convention=None,
        documentation=None,
        load_type=None
    ):
        self.payload = {
            "packageId": package_id,
            "name": name,
            "description": description,
            "keywords": keywords,
            "contentType": content_type,
            "location": None,
            "dataFormat": data_format,
            "publishingFrequency": publishing_frequency,
            "namingConvention": naming_convention,
            "documentation": documentation,
            "taxonomy": taxonomy,
            "loadType": load_type
        }

    def with_external_s3_storage(
        self,
        bucket_name,
        aws_account_id,
        prefix
    ):
        """
        Indicate that the dataset will be stored
        in a self-managed S3 bucket outside of the Data Lake.

        :param str bucket_name: Name of the bucket you want to link to this dataset.
        :param str aws_account_id: The AWS account id where this bucket currently resides.
                                   This account needs to be registed on the data lake previously
                                   and your account should have permissions to use it.
        :param str prefix: A valid path that specifies the absolute parent
                           for files in this dataset.
                           This value will be used when issuing access tokens so 
                           it is essential that it is as constrained as possible.
                           Cannot end with slash ("/").

        :rtype: dli.client.builders.DatasetBuilder

        - **Sample**

        .. code-block:: python

                from dli.client.builders import DatasetBuilder

                builder = DatasetBuilder(
                                package_id="package-id",
                                name="my test dataset",
                                description="My dataset description",
                                content_type="Pricing",
                                data_format="CSV",
                                publishing_frequency="Weekly",
                                taxonomy=["Credit", "CDS"]
                        )
                builder = builder.with_external_s3_storage(
                    bucket_name="external-s3-bucket-name",
                    aws_account_id=123456789,
                    prefix="/economic-data-package/my-test-dataset"
                )
                dataset = client.register_dataset(builder)
        """
        location_builder = DatasetLocationBuilder().with_external_s3_storage(
            bucket_name=bucket_name,
            aws_account_id=aws_account_id,
            prefix=prefix
        )
        self.payload.update(location_builder.build())
        return self

    def with_external_storage(self, location):
        """
        Allows specifying a non S3 location where
        the dataset resides.

        The location will be kept for informational purposes only.

        :param str location: A connection string or identifier where the dataset resides.

        :rtype: dli.client.builders.DatasetBuilder

        - **Sample**

        .. code-block:: python

                from dli.client.builders import DatasetBuilder

                builder = DatasetBuilder(
                                package_id="package-id",
                                name="my test dataset",
                                description="My dataset description",
                                content_type="Pricing",
                                data_format="CSV",
                                publishing_frequency="Weekly",
                                taxonomy=["Credit", "CDS"]
                        )
                builder = builder.with_external_storage("external-storage-location")
                dataset = client.register_dataset(builder)
        """
        location_builder = DatasetLocationBuilder().with_external_storage(location)
        self.payload.update(location_builder.build())
        return self

    def build(self):
        _validate_location_exists_in_payload(self.payload)
        # clean not set entries
        payload = {k: v for k, v in self.payload.items() if v is not None}
        return payload


class DatasetLocationBuilder:
    """
        A simple builder to specify dataset location.
    """

    def __init__(self):
        self.payload = {}

    def with_external_s3_storage(
        self,
        bucket_name,
        aws_account_id,
        prefix
    ):
        """
        Indicate that the dataset will be stored
        in a self-managed S3 bucket outside of the Data Lake.

        :param str bucket_name: Name of the bucket you want to link to this dataset.
        :param str aws_account_id: The AWS account id where this bucket currently resides.
                                   This account needs to be registed on the data lake previously
                                   and your account should have permissions to use it.
        :param str prefix: A vaild path that specifies the absolute parent
                           for files in this dataset.
                           This value will be used when issuing access tokens so 
                           it is essential that it is as constrained as possible.
                           Cannot end with slash ("/").

        :rtype: dli.client.builders.DatasetLocationBuilder

        - **Sample**

        .. code-block:: python

                from dli.client.builders import DatasetLocationBuilder

                location_builder = DatasetLocationBuilder().with_external_s3_storage(
                        bucket_name="external-s3-bucket-name",
                        aws_account_id=123456789,
                        prefix="/economic-data-package/my-test-dataset"
                    )
                # Build the location object
                location = location_builder.build()
        """
        self.payload["location"] = {
            "type": "S3",
            "owner": {
                "awsAccountId": str(aws_account_id)
            },
            "bucket": bucket_name,
            "prefix": prefix
        }
        return self

    def with_external_storage(self, location):
        """
        Allows specifying a non S3 location where
        the dataset resides.

        The location will be kept for informational purposes only.

        :param str location: A connection string or identifier where the dataset resides.

        :rtype: dli.client.builders.DatasetLocationBuilder

        - **Sample**

        .. code-block:: python

                from dli.client.builders import DatasetLocationBuilder

                location_builder = DatasetLocationBuilder().with_external_storage("external-storage-location")
                # Build the location object
                location = location_builder.build()
        """
        self.payload["location"] = {
            "type": "Other",
            "source": location
        }
        return self

    def build(self):
        _validate_location_exists_in_payload(self.payload)
        # clean not set entries
        payload = {k: v for k, v in self.payload.items() if v is not None}
        return payload


def _validate_location_exists_in_payload(payload):
    if not payload.get("location"):
        raise Exception(
            "No storage option was specified. Please use one of the following methods: "
            "with_external_s3_storage`, `with_external_storage`"
        )

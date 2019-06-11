from backports import tempfile
from tests.common import SdkIntegrationTestCase


class SDKSamples(SdkIntegrationTestCase):
    """
    This spec is just meant to catch issues in terms of signature changes
    all the methods are included in one way or another in the SDK documentation
    as samples.

    Avoid including assertions or similar as these tests are not replacements
    for unit or integration tests on these functions.
    """

    def test_get_datasets_in_package(self):
        client = self.client
        package_id = self.create_package("test_get_datasets_in_package")
        builder = self.dataset_builder(package_id, "dataset_for_test_get_dataset_details").with_external_storage(location="jdbc://connectionstring:1232/my-db")
        dataset = client.register_dataset(builder)

        # doc-start
        # returns list of datasets ordered by ascending name
        datasets = client.get_package_datasets(package_id)

        print("Retrieved {} datasets.".format(len(datasets)))
        for ds in datasets:
            print(ds.dataset_id, ds.name)

    def test_get_dataset_details(self):
        client = self.client
        package_id = self.create_package("package_for_test_get_dataset_details")
        builder = self.dataset_builder(package_id, "dataset_for_test_get_dataset_details").with_external_storage(location="jdbc://connectionstring:1232/my-db")
        dataset = client.register_dataset(builder)
        dataset_id = dataset.dataset_id

        # doc-start
        # given a `dataset_id`, dataset metadata can be retrieved as 
        dataset = client.get_dataset(dataset_id)

    def test_get_datafiles_in_dataset(self):
        client = self.client
        package_id = self.create_package("package_for_test_get_datafiles_in_dataset")
        builder = self.dataset_builder(package_id, "dataset_for_test_get_datafiles_in_dataset").with_external_storage(location="jdbc://connectionstring:1232/my-db")
        dataset = client.register_dataset(builder)
        dataset_id = dataset.dataset_id

        files = [{'path': "/path/to/file/A", 'size': 99999}, {'path': "/path/to/file/B", 'size': 88888}]
        datafile = client.register_datafile_metadata(
            dataset_id,
            "datafile_for_test_get_datafiles_in_dataset",
            files,
            '2000-01-01'
        )

        # doc-start
        # returns list of datafiles ordered by descending creation date
        datafiles = client.get_datafiles(dataset_id)

        print("Retrieved {} datafiles.".format(len(datafiles)))
        for df in datafiles:
            print((df.datafile_id, df.files))

    def test_download_datafile(self):
        client = self.client
        package_id = self.create_package("package_for_test_download_datafile")
        dataset = self.register_s3_dataset(package_id, "dataset_for_test_download_datafile", "external-bucket", prefix="samples")
        dataset_id = dataset.dataset_id

        datafile = client.register_s3_datafile(
            dataset_id,
            "datafile_for_test_download_datafile",
            [
                '../test_sandbox/samples/data/AAPL.csv',
                '../test_sandbox/samples/data/MSFT.csv'
            ],
            "samples/",
            '2000-01-01'
        )
        datafile_id = datafile.datafile_id

        with tempfile.TemporaryDirectory() as destination:
            # doc-start
            client.download_datafile(datafile_id, destination)

            import os
            os.listdir(destination)  # shows: ['AAPL.csv', 'MSFT.csv']

    def test_create_datafile_in_dl_s3_storage(self):
        client = self.client
        
        package_id = self.create_package("package_for_test_create_datafile_in_dl_s3_storage")
        dataset = self.register_s3_dataset(package_id, "dataset_for_test_create_datafile_in_dl_s3_storage", "external-bucket")
        dataset_id = dataset.dataset_id

        # doc-start
        # given a dataset with data lake managed storage
        # we can register and upload files into S3
        # which then can be used by your consumers
        datafile = client.register_s3_datafile(
            dataset_id,
            "My Datafile",
            files=[
                '../test_sandbox/samples/data/AAPL.csv',
                '../test_sandbox/samples/data/MSFT.csv'
            ],
            s3_prefix="prefix/",
            data_as_of='2000-01-01'
        )

    def test_create_datafile_in_external_s3_storage(self):
        client = self.client
        package_id = self.create_package("package_for_test_create_datafile_in_external_s3_storage")
        dataset = self.register_s3_dataset(package_id, "dataset_for_test_create_datafile_in_external_s3_storage", "external-bucket", prefix="path")
        dataset_id = dataset.dataset_id

        # doc-start
        # given a dataset with external storage, we want to register a new datafile under it
        # in this case the bucket `external-bucket` is not managed by the data lake, so the upload
        # needs to be done manually
        datafile = client.register_datafile_metadata(
            dataset_id,
            name="test",
            files=[
                {"path": "s3://external-bucket/path/to/file/A", "size": 10000},
                {"path": "s3://external-bucket/path/to/file/B", "size": 15222}
            ],
            data_as_of='2000-01-01'
        )

    def test_update_and_delete_datafile(self):
        client = self.client
        package_id = self.create_package("package_for_test_update_and_delete_datafile")
        builder = self.dataset_builder(package_id, "dataset_for_test_update_and_delete_datafile").with_external_storage(location="jdbc://connectionstring:1232/my-db")
        dataset = client.register_dataset(builder)
        dataset_id = dataset.dataset_id

        files = [{'path': "/path/to/file/A", 'size': 99999}, {'path': "/path/to/file/B", 'size': 88888}]
        datafile = client.register_datafile_metadata(
            dataset_id,
            "datafile_for_test_update_and_delete_datafile",
            files,
            '2000-01-01'
        )

        # doc-start
        # now that we have created a datafile, and have an id (under `datafile.datafile_id`)
        # we can make changes to the metadata
        # this function for example, would change the name
        # while leaving all other attributes as they are.
        updated = client.edit_datafile_metadata(
            datafile.datafile_id,
            name="Updating Datafile."
        )

        # we can also mark the datafile as deleted
        # if we don't want it to be available for consumption anymore.
        # this call only deletes the metadata and leaves
        # the actual data intact.
        client.delete_datafile(updated.datafile_id)

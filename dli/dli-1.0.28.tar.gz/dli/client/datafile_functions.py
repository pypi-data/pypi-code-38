import datetime
import logging
import posixpath

from dli.client.exceptions import (CatalogueEntityNotFoundException,
                                   DownloadFailed,
                                   MissingMandatoryArgumentException)
from dli.client.s3 import Client, S3DatafileWrapper
from dli.siren import siren_to_dict, siren_to_entity

logger = logging.getLogger(__name__)


class DatafileFunctions:

    @property
    def __root(self):
        return self.ctx.memoized(
            self.get_root_siren().datafiles_root,
            "datafiles_root"
        )

    def register_datafile_metadata(
        self,
        dataset_id,
        name,
        files,
        data_as_of,
        original_name=None
    ):
        """
        Submit a request to create a new datafile under a specified dataset in the Data Catalogue. This function
        ``WILL NOT`` upload files

        Datafile is an instance of the data within a dataset, representing a snapshot of the data at the time of
        publishing. A dataset can be composed by one or more related files that share a single schema. of related
        datafiles. It provides user with metadata required to consume and use the data.

        See description for each parameter, and whether they are optional or mandatory.

        :param str dataset_id: Dataset ID to which the datafile belongs to.
        :param str name: A descriptive name of a datafile. It should be unique within the dataset.
        :param list[dict] files: List of file dictionaries. A file dictionary will contain the full file path
                                and size (optional) as items.
        :param str data_as_of: The effective date for the data within the datafile.
                               Expected format is YYYY-MM-DD.
        :param str original_name: Optional. Name of the data uploaded into the data lake.

        :returns: Registered datafile
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                datafile = client.register_datafile_metadata(
                    dataset_id,
                    name="My Datafile",
                    files=[{'path': "/path/to/file/A", 'size': 99999}, {'path': "/path/to/file/B", 'size': 88888}],
                    data_as_of="2018-05-28"
                )
        """
        dataset = self.get_dataset(id=dataset_id)

        if not files:
            raise Exception("No files to register have been provided.")

        fields = {
            'datasetId': dataset.dataset_id,
            'name': name,
            'originalName': original_name,
            'dataAsOf': self._ensure_iso_date(data_as_of),
            'files': files,
        }

        payload = {k: v for k, v in fields.items() if v is not None}
        return siren_to_entity(self.__root.create_datafile(__json=payload))

    def register_s3_datafile(
        self,
        dataset_id,
        name,
        files,
        s3_prefix,
        data_as_of,
        original_name=None
    ):
        """
        Submit a request to create a new datafile under a specified dataset in the Data Catalogue.
        This function will perform an upload of the files to S3 data store.

        Datafile is an instance of the data within a dataset, representing a snapshot of the data at the time of publishing.
        A dataset can be composed by one or more related files that share a single schema. of related datafiles.
        It provides user with metadata required to consume and use the data.

        See description for each parameter, and whether they are optional or mandatory.

        :param str dataset_id: Dataset ID to which the datafile belongs to.
        :param str name: A descriptive name of a datafile. It should be unique within the dataset.
        :param list[str] files: Path of the files or folders to register.
        :param str s3_prefix: location of the files in the destination bucket. Cannot end with slash ("/")
        :param str data_as_of: The effective date for the data within the datafile.
                               Expected format is YYYY-MM-DD.
        :param str original_name: Optional. Name of the data uploaded into the data lake.

        :returns: Registered datafile.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                datafile = client.register_s3_datafile(
                    dataset_id=dataset_id,
                    name="My datafile",
                    files=["./test_sandbox/samples/data/AAPL.csv", "./test_sandbox/samples/data/MSFT.csv"],
                    s3_prefix="quotes/20180518",
                    data_as_of="2018-05-28"
                )
        """
        dataset = self.get_dataset(id=dataset_id)

        if not files:
            raise Exception("No files to register have been provided.")

        # upload files
        if dataset.location.type != 'S3':
            raise Exception(
                "Only datasets backed on S3 are supported. use register_datafile_metadata instead.")

        bucket = dataset.location.bucket
        if not bucket:
            raise Exception(
                "Dataset location is S3, however, "
                "there is no bucket associated with the dataset {}".format(
                    dataset_id)
            )

        s3_location = "{}/{}".format(bucket, s3_prefix)
        uploaded = self._process_s3_upload(files, s3_location, dataset_id)

        # register metadata
        return self.register_datafile_metadata(
            dataset_id,
            name=name,
            files=uploaded,
            original_name=original_name,
            data_as_of=self._ensure_iso_date(data_as_of),
        )

    def edit_datafile_metadata(
        self,
        datafile_id,
        name=None,
        original_name=None,
        data_as_of=None,
        files=None
    ):
        """
        Edits metadata for an existing datafile.
        This function WILL NOT upload files.
        Fields passed as ``None`` will retain their original value.

        :param str datafile_id: The id of the datafile we want to modify.
        :param str name: Optional. Name of the datafile.
        :param list[dict] files: Optional. List of file dicts. A file dict will contain file path and size(optional) as items.
        :param str original_name: Optional. Original Name for the datafile.
        :param str data_as_of: Optional. The effective date for the data within the datafile.
                               Expected format is YYYY-MM-DD.

        :returns: Registered datafile
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                updated_datafile = client.edit_datafile_metadata(
                    datafile_id,
                    name="My Datafile",
                    files=[{'path': "/path/to/file/A", 'size': 99999}, {'path': "/path/to/file/B", 'size': 88888}]
                )
        """

        datafile = self._get_datafile(datafile_id)

        fields = {
            'datasetId': datafile.datasetId,
            'name': name,
            'originalName': original_name,
            'dataAsOf': self._ensure_iso_date(data_as_of),
            'files': files
        }

        # clean up any unknown fields, and update the entity
        datafile_as_dict = siren_to_dict(datafile)
        for key in list(datafile_as_dict.keys()):
            if key not in fields:
                del datafile_as_dict[key]

        payload = {k: v for k, v in fields.items() if v is not None}
        datafile_as_dict.update(payload)

        # perform the update and return the resulting entity
        return siren_to_entity(datafile.edit_datafile(__json=datafile_as_dict))

    def delete_datafile(self, datafile_id):
        """
        Marks a datafile as deleted.

        :param str datafile_id: the unique id for the datafile we want to delete.

        :returns: None

        - **Sample**

        .. code-block:: python

                client.delete_datafile(datafile_id)
        """
        datafile = self._get_datafile(datafile_id)
        if not datafile:
            raise CatalogueEntityNotFoundException(
                'Datafile', params=datafile_id)

        datafile.delete_datafile(datafile_id=datafile_id)

    def get_s3_datafile(self, datafile_id):
        """
        Fetches an S3 datafile providing easy access to directly
        stream/load files without the need of downloading them.

        If the datafile is not stored in S3, or you don't have access to it
        then an error will be displayed.

        :param str datafile_id: The id of the datafile we want to load

        :returns: a datafile that can read files from S3
        :rtype: dli.client.s3.S3DatafileWrapper

        .. code-block:: python

                datafile = client.get_s3_datafile(datafile_id)
                with datafile.open_file("path/to/file/in/datafile") as f:
                    f.read() # do something with the file

                # or if you want a pandas dataframe created from it you can
                pd.read_csv(datafile.open_file("path/to/file/in/datafile"))

                # you can see all the files in the datafile by calling `files`
                datafile.files  # displays a list of files in this datafile

        """

        datafile = self.get_datafile(datafile_id)
        if not datafile:
            raise CatalogueEntityNotFoundException(
                'Datafile', params=datafile_id
            )

        keys = self.get_s3_access_keys_for_dataset(datafile.dataset_id)
        s3_access = Client(
            keys.access_key_id,
            keys.secret_access_key,
            keys.session_token
        )

        return S3DatafileWrapper(
            datafile._asdict(),
            s3_access.s3fs
        )

    def download_datafile(self, datafile_id, destination):
        """
        Helper function that downloads all files
        registered in a datafile into a given destination.

        This function is only supported for data-lake managed s3 buckets,
        otherwise an error will be displayed.

        Currently supports:
          - s3

        :param str datafile_id: The id of the datafile we want to download files from.
        :param str destination: Target location where to store the files (expected to be a directory).

        :returns: None

        - **Sample**

        .. code-block:: python

                client.download_datafile(datafile_id, destination)
        """

        # get the s3 keys
        # this requires access to be granted
        datafile = self._get_datafile(datafile_id)
        if not datafile:
            raise CatalogueEntityNotFoundException(
                'Datafile', params=datafile_id)

        keys = self.get_s3_access_keys_for_dataset(datafile.datasetId)
        s3_access = Client(
            keys.access_key_id,
            keys.secret_access_key,
            keys.session_token
        )

        # for each file/folder in the datafile, attempt to download the file
        # rather than failing at the same error, keep to download as much as possible
        # and fail at the end.
        failed = []
        files = [f["path"] for f in datafile.files]
        for file in files:
            try:
                s3_access.download_files_from_s3_path(file, destination)
            except Exception:
                logger.exception(
                    "Failed to download file `%s` from datafile `%s`", file, datafile_id)
                failed.append(file)

        if failed:
            raise DownloadFailed(
                "Some files in this datafile could not be downloaded, "
                "see logs for detailed information. Failed:\n%s"
                % "\n".join(failed)
            )

    def _process_s3_upload(self, files, s3_location, dataset_id):
        s3_access_keys = self.get_s3_access_keys_for_dataset(dataset_id)
        s3_client = Client(s3_access_keys.access_key_id,
                           s3_access_keys.secret_access_key, s3_access_keys.session_token)
        # Ensure trailing slash is included if missing
        s3_location = posixpath.join(s3_location, '')
        return s3_client.upload_files_to_s3(files, s3_location, lambda: self.get_s3_access_keys_for_dataset(dataset_id))

    def get_datafile(self, datafile_id):
        """
        Fetches datafile metadata for an existing datafile.

        :param str datafile_id: the unique id of the datafile we want to fetch.

        :returns: The datafile.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                datafile = client.get_datafile(datafile_id)
        """
        datafile = self._get_datafile(datafile_id)

        return siren_to_entity(datafile)

    def _get_datafile(self, datafile_id):

        if not datafile_id:
            raise MissingMandatoryArgumentException('datafile_id')

        datafile = self.__root.get_datafile(datafile_id=datafile_id)

        if not datafile:
            raise CatalogueEntityNotFoundException(
                'Datafile', params=datafile_id)

        return datafile

    def add_files_to_datafile(self, datafile_id, s3_prefix, files):
        """
        Upload files to existing datafile.

        :param str datafile_id: The id of the datafile to be updated.
        :param str s3_prefix: Location for the files in the destination s3 bucket. Cannot end with slash ("/").
        :param list[str] files: List of files to be added to the datafile.

        :returns: The updated datafile.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                datafile_updated_with_additional_files = client.add_files_to_datafile(
                                                              datafile_id=datafile_id,
                                                              s3_prefix="quotes/20180518",
                                                              files=["./data/AAPL.csv", "./data/MSFT.csv"],
                                                        )
        """
        datafile = self.get_datafile(datafile_id)
        if not datafile:
            raise CatalogueEntityNotFoundException(
                'Datafile', params=datafile_id)

        dataset = self.get_dataset(id=datafile.dataset_id)

        if dataset.location.type != "S3":
            raise Exception("Can not upload files to non-S3 datasets.")

        s3_location = "{}/{}".format(dataset.location.bucket, s3_prefix)
        uploaded_files = self._process_s3_upload(
            files,
            s3_location,
            datafile.dataset_id
        )

        if datafile.files:
            uploaded_files.extend(datafile.files)

        return self.edit_datafile_metadata(datafile_id, files=uploaded_files)

    @staticmethod
    def _ensure_iso_date(date):
        if date:
            return datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        return date

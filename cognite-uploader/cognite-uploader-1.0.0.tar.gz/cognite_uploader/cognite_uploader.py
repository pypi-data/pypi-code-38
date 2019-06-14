from itertools import islice
from typing import Any, Callable, Dict, Iterable, List

from cognite import APIError, CogniteClient
from cognite.client.stable.raw import RawClient, RawRow

UploadQueueDict = Dict[str, Dict[str, List[RawRow]]]


class Uploader:
    raw: RawClient

    def __init__(
        self, cdp_client: CogniteClient, post_upload_function: Callable[[int], None] = None, queue_threshold: int = -1
    ):
        """
        Utility to upload data to the RAW API.
        :param api_key:
        :param project:
        :param base_url:
        :param post_upload_function: A function that will be called after each upload. The function will be given one
          argument: An int representing the number of rows uploaded in total.
        :param queue_threshold:
        """

        self.raw = cdp_client.raw

        self.threshold = queue_threshold
        self.upload_queue_byte_size = 0
        self.upload_queue: UploadQueueDict = dict()

        self.rows_uploaded_total = 0

        self.post_upload_function = post_upload_function

    def add_to_upload_queue(self, database: str, table: str, raw_row: RawRow) -> None:
        """
        Adds raw object to the upload queue.
        The queue will be uploaded, if the queue byte size is larger than the threshold specified in the config.
        :param database: The database to upload the Raw object to
        :param table: The table to upload the Raw object to
        :param raw_row: The raw object
        """
        # Ensure that the dicts has correct keys
        if database not in self.upload_queue:
            self.upload_queue[database] = dict()
        if table not in self.upload_queue[database]:
            self.upload_queue[database][table] = []

        # Append row to queue
        self.upload_queue[database][table].append(raw_row)
        self.upload_queue_byte_size += len(repr(raw_row))

        # Check upload threshold
        if self.upload_queue_byte_size > self.threshold or self.threshold < 0:
            self.upload()

    def upload(self) -> None:
        """
        Uploads the queue to the raw database
        """
        for database, tables in self.upload_queue.items():
            for table, rows in tables.items():
                for limited_rows in Uploader._grouper(rows, 500):
                    # Upload
                    self.raw.create_rows(
                        database_name=database, table_name=table, rows=limited_rows, ensure_parent=True
                    )
                    self.rows_uploaded_total += len(limited_rows)
                    # Perform post-upload logic if applicable
                    if self.post_upload_function:
                        self.post_upload_function(self.rows_uploaded_total)

        self.upload_queue = dict()
        self.upload_queue_byte_size = 0

    def _ensure_database(self, database: str) -> None:
        """
        Ensures that the database exists in the current project
        :param database: Name of database
        """
        try:
            self.raw.create_databases(database_names=[database])
        except APIError as api_e:
            if not api_e.__str__() == "{'code': 400, 'message': 'DBs already created: " + database + "'}":
                raise

    def _ensure_table(self, database: str, table: str) -> None:
        """
        Ensures that the table exist in the database
        :param database: Name of database
        :param table: Name of table
        """
        self._ensure_database(database)
        try:
            self.raw.create_tables(database_name=database, table_names=[table])
        except APIError as api_e:
            if not api_e.__str__() == "{'code': 400, 'message': 'Tables already created: " + table + "'}":
                raise

    @staticmethod
    def _grouper(iterable: Iterable[Any], n: int) -> Iterable[Any]:
        """
        Generator that splits an iterable into chunks of length n
        :param iterable: The Iterable to split
        :param n: Length of chunk
        :return: Iterable of length n
        """
        it = iter(iterable)
        while True:
            chunk = list(islice(it, n))
            if not chunk:
                return
            yield chunk

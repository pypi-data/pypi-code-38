"""
Module containing uploader classes.
"""

import time
from abc import ABC, abstractmethod
from itertools import islice
from json import dumps
from typing import Any, Callable, Dict, Iterable, List, Optional

from cognite import APIError, CogniteClient
from cognite.client.stable.raw import RawClient, RawRow
from google.cloud import pubsub_v1  # type: ignore

UploadQueueDict = Dict[str, Dict[str, List[RawRow]]]


class Uploader(ABC):
    """
    Abstract uploader class, base for RawUploader and PubSubUploader.

    Args:
        post_upload_funtion (Callable[[int]): (Optional). A function that will be called after each upload. The function
            will be given one argument: An int representing the number of rows uploaded in total.
        queue_threshold (int): (Optional). Maximum size of upload queue. Defaults to no queue (ie upload after each
            add_to_upload_queue).
    """

    def __init__(
        self, post_upload_function: Optional[Callable[[int], None]] = None, queue_threshold: Optional[int] = None
    ):
        """
        Called by subclasses. Saves info and inits upload queue.
        """
        self.threshold = queue_threshold if queue_threshold is not None else -1
        self.upload_queue_byte_size = 0
        self.upload_queue: UploadQueueDict = dict()

        self.rows_uploaded_total = 0

        self.post_upload_function = post_upload_function

    def _inner_add_to_queue(self, database: str, table: str, obj: Any) -> Any:
        """
        Actually adds object to upload queue. Called by subclasses.

        Args:
            database (str): Which database to upload to
            table (str): Which table to upload to
            obj (Any): Object to upload

        Returns:
            Any: Result of upload, if upload happened.
        """
        # Ensure that the dicts has correct keys
        if database not in self.upload_queue:
            self.upload_queue[database] = dict()
        if table not in self.upload_queue[database]:
            self.upload_queue[database][table] = []

        # Append row to queue
        self.upload_queue[database][table].append(obj)
        self.upload_queue_byte_size += len(repr(obj))

        # Check upload threshold
        if self.upload_queue_byte_size > self.threshold or self.threshold < 0:
            return self.upload()

        return None

    @abstractmethod
    def add_to_upload_queue(self, database: str, table: str, raw_row: RawRow) -> Any:
        """
        Adds a row to the upload queue. The queue will be uploaded if the queue byte size is larger than the threshold
        specified in the config.

        Args:
            database (str): The database to upload the Raw object to
            table (str): The table to upload the Raw object to
            raw_row (RawRow): The row object

        Returns:
            Any: Result of upload, if applicable and if upload happened.
        """

    @abstractmethod
    def upload(self) -> Any:
        """
        Uploads the queue.

        Returns:
            Any: Result status of upload.
        """


class RawUploader(Uploader):
    """
    Utility to upload data to the RAW API.

    Args:
        cdp_client (CogniteClient): Cognite Data Fusion client
        post_upload_funtion (Callable[[int]): (Optional). A function that will be called after each upload. The function
            will be given one argument: An int representing the number of rows uploaded in total.
        queue_threshold (int): (Optional). Maximum size of upload queue. Defaults to no queue (ie upload after each
            add_to_upload_queue).
    """

    raw: RawClient

    def __init__(
        self,
        cdp_client: CogniteClient,
        post_upload_function: Optional[Callable[[int], None]] = None,
        queue_threshold: Optional[int] = None,
    ):
        # Super sets post_upload and threshold, and inits upload queue
        super().__init__(post_upload_function, queue_threshold)

        self.raw = cdp_client.raw

    def add_to_upload_queue(self, database: str, table: str, raw_row: RawRow) -> None:
        """
        Adds a row to the upload queue. The queue will be uploaded if the queue
        byte size is larger than the threshold specified in the config.

        Args:
            database (str): The database to upload the Raw object to
            table (str): The table to upload the Raw object to
            raw_row (RawRow): The row object

        Returns:
            None.
        """
        self._inner_add_to_queue(database, table, raw_row)

    def upload(self) -> None:
        """
        Uploads the queue to the RAW database.

        Returns:
            None.
        """
        for database, tables in self.upload_queue.items():
            for table, rows in tables.items():
                for limited_rows in RawUploader._grouper(rows, 500):
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
        Ensures that the database exists in the current project.

        Args:
            database (str): Name of database
        """
        try:
            self.raw.create_databases(database_names=[database])
        except APIError as api_e:
            if not api_e.__str__() == "{'code': 400, 'message': 'DBs already created: " + database + "'}":
                raise

    def _ensure_table(self, database: str, table: str) -> None:
        """
        Ensures that the table exist in the database.

        Args:
            database (str): Name of database
            table (str): Name of table
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

        Args:
            iterable (Iterable[Any]): The Iterable to split
            n (int): Length of chunk

        Returns:
            Iterable[Any]: Iterable of length n
        """
        it = iter(iterable)
        while True:
            chunk = list(islice(it, n))
            if not chunk:
                return
            yield chunk


class PubSubUploader(Uploader):
    """
    Utility to upload data to Google's Pub/Sub API

    Args:
        project_id (str): ID of Google Cloud Platform project to use.
        topic_name (str): Name of Pub/Sub topic to publish to
        post_upload_funtion (Callable[[int]): (Optional). A function that will be called after each upload. The function
            will be given one argument: An int representing the number of rows uploaded in total.
        queue_threshold (int): (Optional). Maximum size of upload queue. Defaults to no queue (ie upload after each
            add_to_upload_queue).
        always_ensure_topic (bool): (Optional). Call ensure_topic before each upload
    """

    def __init__(
        self,
        project_id: str,
        topic_name: str,
        post_upload_function: Optional[Callable[[int], None]] = None,
        queue_threshold: Optional[int] = None,
        always_ensure_topic: Optional[bool] = False,
    ):
        # Super sets post_upload and threshold, and inits upload queue
        super().__init__(post_upload_function, queue_threshold)

        # Init pub/sub
        self.pubsub_client = pubsub_v1.PublisherClient()

        # Save Google Pub/Sub info, construct topic path
        self.project_id = project_id
        self.project_path = self.pubsub_client.project_path(project_id)
        self.topic_name = topic_name
        self.topic_path = self.pubsub_client.topic_path(project_id, topic_name)

        self.always_ensure_topic = always_ensure_topic

    def ensure_topic(self):
        """
        Checks that the given topic name exists in project, and creates it if it doesn't.

        Note that this action requires extended previlegies on the cloud platform. The normal 'publisher' role is not
        allowed to view or manage topics.

        Raises:
            PermissionDenied: If API key stored in GOOGLE_APPLICATION_CREDENTIALS are not allowed to manipulate topics.
        """
        topic_paths = [topic.name for topic in self.pubsub_client.list_topics(self.project_path)]

        if not self.topic_path in topic_paths:
            self.pubsub_client.create_topic(self.topic_path)

    def add_to_upload_queue(self, database: str, table: str, raw_row: RawRow) -> List[Any]:
        """
        Adds a row to the upload queue. The queue will be uploaded if the queue
        byte size is larger than the threshold specified in the config.

        Args:
            database (str): The database to upload the Raw object to
            table (str): The table to upload the Raw object to
            raw_row (RawRow): The row object

        Returns:
            List[Any]: Pub/Sub message IDs, if an upload was made. None otherwise.
        """
        return self._inner_add_to_queue(database, table, {raw_row.key: raw_row.columns})

    def upload(self) -> List[Any]:
        """
        Publishes the queue to Google's Pub/Sub.

        Returns:
            List[Any]: Pub/Sub message IDs.
        """
        if self.always_ensure_topic:
            self.ensure_topic()

        futures = []
        ids = []

        # Upload each table as a separate Pub/Sub message
        for database, tables in self.upload_queue.items():
            for table, rows in tables.items():
                # Convert list of row dicts to one single bytestring
                bytestring = str.encode(dumps({"database": database, "table": table, "rows": rows}))

                # Publish
                pubsub_future = self.pubsub_client.publish(self.topic_path, bytestring)
                futures.append(pubsub_future)

                # Add message ID to ID list when message is sent
                pubsub_future.add_done_callback(lambda f: ids.append(f.result()))

                # Update upload stats
                self.rows_uploaded_total += len(rows)

                # Perform post-upload logic if applicable
                if self.post_upload_function:
                    self.post_upload_function(self.rows_uploaded_total)

        self.upload_queue = dict()
        self.upload_queue_byte_size = 0

        # Wait until all the messages are sent before returning. We can't use concurrent.futures.wait here since these
        # objects are instances of Google's own Future class and not the stdlib one.
        for future in futures:
            while future.running():
                time.sleep(0.1)

        return ids

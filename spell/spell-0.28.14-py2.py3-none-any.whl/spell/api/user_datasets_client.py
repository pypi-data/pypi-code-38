import json
import time
import posixpath

from tus_client import client
from tus_client.exceptions import TusCommunicationError

from spell.api.exceptions import ClientException, UnauthorizedRequest
from spell.api import base_client, models
from spell.api.utils import url_path_join

USER_DATASET_RESOURCE_URL = "datasets"
# AWS Multi-part uploads require a minimum of 5MB per request
# https://docs.aws.amazon.com/AmazonS3/latest/dev/qfacts.html
UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024


class UserDatasetsClient(base_client.BaseClient):

    def new_dataset(self, name, compressed):
        """Create a new user dataset

        Keyword arguments:
        name -- the name of this dataset
        compressed -- if true, the data must be decompressed

        Returns:
        a UserDataset object for the created dataset
        """
        payload = {"name": name, "compressed": compressed}
        r = self.request("post", url_path_join(USER_DATASET_RESOURCE_URL, self.owner), payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["user_dataset"]

    def remove_dataset(self, name):
        """Delete the user's dataset

        Keyword arguments:
        name -- the name of the dataset to be deleted

        Returns:
        nothing if successful
        """
        payload = {"name": name}
        r = self.request("delete", url_path_join(USER_DATASET_RESOURCE_URL, self.owner), payload=payload)
        self.check_and_raise(r)

    def complete_upload(self, dataset_id):
        """Report upload completion for a dataset

        Keyword arguments:
        dataset_id -- the id of the dataset
        """
        r = self.request("post", url_path_join(
            USER_DATASET_RESOURCE_URL, self.owner, str(dataset_id), "upload_complete"))
        self.check_and_raise(r)

    def upload_file(self, fullpath, dataset_id, dataset_path, q=None, terminate=None, retries=1, retry_delay=30):
        """Upload a dataset file to Spell

        Keyword arguments:
        fullpath -- the local path on disk to the file to upload
        dataset_id -- the id of the dataset
        dataset_path -- the relative path of the file within the root of the dataset
        q -- an optional queue.Queue to which uploaded byte updates will be pushed
        terminate -- an optional threading.Event, which if becomes set, will terminate the upload
        retries -- an optional number of retries to attempt for communication issues before throwing an exception
        retry_delay -- an optional delay to specify for waiting between retry attempts
        """
        try:
            upload_url = posixpath.join(self.base_url, self.version_str, USER_DATASET_RESOURCE_URL, "upload")
            tus_client = client.TusClient(upload_url, headers={'Authorization': 'Bearer {}'.format(self.token)})
            attempts = 0
            while True:
                try:
                    metadata = {
                        "path": posixpath.join(str(dataset_id), dataset_path)
                    }
                    uploader = tus_client.uploader(fullpath,
                                                   metadata=metadata,
                                                   retries=retries,
                                                   retry_delay=retry_delay,
                                                   chunk_size=UPLOAD_CHUNK_SIZE)
                    break
                except TusCommunicationError as e:
                    if attempts < retries:
                        attempts += 1
                        time.sleep(30)
                    else:
                        raise e
            if q:
                prev, curr = 0, uploader.offset
                q.put(curr-prev)
            while uploader.offset < uploader.file_size and (not terminate.is_set() if terminate else True):
                uploader.upload_chunk()
                if q:
                    prev, curr = curr, uploader.offset
                    q.put(curr-prev)
        except TusCommunicationError as e:
            # attempt to decode spell exceptions
            if hasattr(e, "response_content") and e.response_content:
                error = None
                try:
                    error = json.loads(e.response_content, object_hook=models.Error.response_dict_to_object)
                    if e.status_code == 401:
                        raise UnauthorizedRequest(msg=str(error))
                    else:
                        raise ClientException(msg=str(error))
                except Exception:
                    pass
                if error:
                    raise ClientException(msg=str(error))
            raise e

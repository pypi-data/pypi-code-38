import pathlib
import sys
import time
# TODO: Replace with cloudpickle. Pyarrow is great for in-memory and tabular data, but it sucks for everything else.
import uuid
from logging import StreamHandler
from crayons import blue, magenta
import cloudpickle
from coolname import generate_slug
from funtime import Store
from loguru import logger

from spaceman.meta import Meta
from spaceman.store import SpaceStorage

logger.add(StreamHandler(sys.stderr), format="{message}")
logger.add("file_test.log")




class CheckpointInformation(object):
    def __init__(self, *args, **kwargs):
        pass

    def __setattr__(self, name, value):
        self.__dict__[name] = value


# TODO: Rename to SPACEMAN! Spaceman!!!! It's a checkpointing system
class Checkpoint(object):
    """ Library used to checkpoint your models. """

    def __init__(self, storage_type="local", store_folder="/tmp/checkpoint", bucket="checkpoint", s3_creds={}, use_step=False, step_back=1, mongo_host="localhost", mongo_store="global", **kwargs):
        """
            params:
                use_step: bool
                    - At the beginning of a store, we'll search the "query" to see if there's a previous insertion that exist with the int variable "step"
                    - if not, add the variable 0 
                step_back: int
                    - The number of steps back we want to look with a given load query. Knowing this in advanced will allow us to get any information 
        """
        self._store = Store(mongo_host).create_lib(
            mongo_store).get_store()[mongo_store]
        self.meta = Meta()
        self.storage = SpaceStorage(
            provider=storage_type, folder_bucket_name=bucket)
        self.storage_type = storage_type
        self.store_folder = store_folder
        self.bucket = bucket
        self.checkpoint_info = CheckpointInformation
        self.use_step = use_step
        self.step_back = 1

        # Create a folder if it doesn't exist yet
        if self.storage_type == "local":
            pathlib.Path(store_folder).mkdir(parents=True, exist_ok=True)

        # We haven't planned for s3 yet. Do so after
    def valid(self, name):
        return not name[0].isdigit() and all(c.isalnum() or c == '-' for c in name)

    def count_step(self, query):
        if not isinstance(query, dict):
            raise TypeError("Query object must be a dict")

        # Pop the timestamp here
        ts = query.pop("timestamp", None)
        query["limit"] = 2

        # set a current limit
        last_two = list(self._store.query_latest(query))
        last = None
        if len(last_two) > 0:
            last = last_two[0]

        step_number = 0
        if last is not None:
            current_step = last.get("step")
            if current_step is not None:
                step_number = current_step+1
        query['timestamp'] = ts
        query.pop("limit", None)
        query['step'] = step_number
        return query

    def store(self, obj, name="", is_parquet=False, query={"type": "general"}, current_time=True, generated_name=True, extension="cereal"):
        query["name"] = name
        query = self.meta.store_meta(
            query, _is_current_time=current_time, generate_name=generated_name)
        self.checkpoint_info.name = query['name']
        self.checkpoint_info.file_name = query['filename']
        self.checkpoint_info.provider = self.storage_type
        self.checkpoint_info.bucket = self.bucket
        self.checkpoint_info.type = query['type']
        self.checkpoint_info.folder = self.store_folder
        self.checkpoint_info.loc = f"{self.store_folder}/{query['filename']}"
        self.checkpoint_info.timestamp = query['timestamp']
        self.checkpoint_info.query = query

        query['loc'] = f"{self.store_folder}/{query['filename']}"
        query['provider'] = self.storage_type

        try:
            self.storage.add(obj, query['filename'])
            self._store.store(query)
        except Exception as e:
            logger.exception(e)

        return self.checkpoint_info

    def load(self, obj_loc=None, get_latest=True, storage_type="local", query={"type": "general"}, is_before=False, minutes=None, seconds=30, already_shifted=False):
        # TODO: Add steps option.
        # TODO: Add Seconds Before
        total_seconds = 0
        is_timefore = False
        _timestamp = query.get("timestamp")
        if is_before == True and _timestamp is not None:
            is_timefore = True

            if minutes is not None:
                total_seconds = 60 * minutes
            elif seconds is not None:
                total_seconds = seconds

        # Add a variable to say the shift already exist. Ensure to add that here

        if self.use_step:
            # TODO: Get the number of steps and calculate everything necessary from here
            query.pop("step", None)
        self.current_file = None
        if storage_type == "local":
            if obj_loc is not None:
                p = pathlib.Path(obj_loc)
                if p.exists():
                    cerealized = p.read_bytes()
                    self.current_file = cloudpickle.loads(cerealized)
                    return self.current_file
            elif get_latest == True and is_timefore == False:
                files = list(self._store.query_latest(query))

                if len(files) > 0:
                    current_file_record = files[0]
                    meta_data = self.storage.get(
                        current_file_record['filename'])
                    if meta_data['file'] is not None:
                        return meta_data['file']
                    return
                    # p = pathlib.Path(current_file_record['loc'])
                    # if p.exists():
                    #     cerealized = p.read_bytes()
                    #     self.current_file = cloudpickle.loads(cerealized)
                    #     return self.current_file

            elif is_timefore == True:
                if already_shifted == False:
                    query['timestamp'] = _timestamp-(total_seconds)

                # print(blue(query))
                timestamp = float(query['timestamp'])
                query["timestamp"] = timestamp
                # print(blue(timestamp))
                file = self._store.query_closest(query)
                # files = self._store.query_latest(query)
                # print(magenta(file))
                if file is not None:
                    current_file_record = file
                    meta_data = self.storage.get(
                        current_file_record['filename']
                    )

                    if meta_data['file'] is not None:
                        return meta_data['file']
                    return
                    # p = pathlib.Path(current_file_record['loc'])
                    # if p.exists():
                    #     cerealized = p.read_bytes()
                    #     self.current_file = cloudpickle.loads(cerealized)
                    #     return self.current_file
        # Place in s3 storage type and
        return self.current_file

    def __enter__(self):
        try:
            return self
        except Exception as e:
            err = e

    def __exit__(self, exception_type, exception_value, traceback):
        pass


"""
    with Checkpoint() as check:
        info = check.store(obj, query={"type":"sample", ...})


"""


if __name__ == "__main__":
    with Checkpoint() as check:
        info = check.store(["one", {}])
        f = check.load(query=info.query)
        print(f)

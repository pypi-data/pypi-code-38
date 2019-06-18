from collections import deque
from time import sleep
import boto3


class KinesisConsumer:
    """Consume from a kinesis stream"""

    def __init__(self, stream_name, client=None, shard_iterator_type="LATEST"):
        self.client = client or boto3.Session().client("kinesis")
        self.shard_iterator_type = shard_iterator_type
        self.stream_name = stream_name
        self.shards = {}
        # need to take into account resharding (i.e expired shards)
        self.update_shards()

    def __iter__(self):
        while True:
            records = self.get_records()
            while records:
                yield records.pop()

    def update_shards(self):
        """Return a dict of {ShardId, ShardIterator}"""
        if not self.shards:
            self.shards = {}
        shards = self.client.list_shards(StreamName=self.stream_name)["Shards"]
        shard_iterators = dict()
        for shard in shards:
            self.shards[shard["ShardId"]] = self.client.get_shard_iterator(
                StreamName=self.stream_name,
                ShardId=shard["ShardId"],
                ShardIteratorType=self.shard_iterator_type,
            ).get("ShardIterator")
        return shard_iterators

    def get_records(self, sleep_time=0.25):
        records_queue = deque()
        # Go through each shard and look for records
        for shard_id, shard_iterator in self.shards.items():
            # In case of expiry
            if shard_iterator:
                records = self.client.get_records(ShardIterator=shard_iterator)
                if records.get("Records"):
                    for record in records["Records"]:
                        records_queue.append(record)
                sleep(sleep_time)
                self.shards[shard_id] = records.get("NextShardIterator")
        return records_queue

from collections import deque
from random import randint
from time import sleep
import boto3


class KinesisProducer:
    def __init__(self, stream_name, max_queue=500, client=None):
        self._client = client or boto3.client("kinesis")
        self._stream_name = stream_name
        self.queue = deque()
        self._max_queue = max_queue

    def __del__(self):
        self.flush()

    @staticmethod
    def random_partition():
        return randint(0, 10 ** 12).__str__()

    def put_record(self, message):
        self._client.put_record(
            StreamName=self._stream_name,
            Data=message,
            PartitionKey=self.random_partition(),
        )

    def queue_message(self, message):
        self.queue.append({"Data": message, "PartitionKey": self.random_partition()})
        if len(self.queue) >= self._max_queue:
            self.flush()

    def flush(self):
        while self.queue:
            self._client.put_records(
                Records=list(self.queue[:500]), StreamName=self._stream_name
            )
            del self.queue[:500]
            sleep(0.25)

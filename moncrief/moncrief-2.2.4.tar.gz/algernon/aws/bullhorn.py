from queue import Queue
from threading import Thread
from typing import Dict

import boto3


class Bullhorn:
    def __init__(self, topic_map: Dict[str, str], client=None):
        if not client:
            client = boto3.client('sns')
        self._client = client
        self._topic_map = topic_map
        self._batch_mode = False

    def __enter__(self, num_threads: int = 15):
        self._workers = []
        self._batch = Queue()
        self._batch_mode = True
        for _ in range(25):
            worker = Thread(target=self._batch_publish)
            worker.start()
            self._workers.append(worker)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type and not exc_val:
            self._shutdown_workers()
            self._workers = []
            self._batch_mode = False
            return True
        raise (exc_type(exc_val))

    @classmethod
    def retrieve(cls, resource=None, profile=None):
        topic_map = {}
        if not resource:
            resource = boto3.resource('sns')
            if profile:
                resource = boto3.Session(profile_name=profile).resource('sns')
        topic_iterator = resource.topics.all()
        for entry in topic_iterator:
            attributes = entry.attributes
            topic_arn = attributes['TopicArn']
            display_name = attributes['DisplayName']
            if display_name:
                topic_map[display_name] = topic_arn
        client = boto3.client('sns')
        if profile:
            client = boto3.Session(profile_name=profile).client('sns')
        return cls(topic_map, client)

    @property
    def topic_map(self):
        return self._topic_map

    def _shutdown_workers(self):
        for worker in self._workers:
            self._batch.put(None)
            worker.join()

    def find_task_arn(self,  task_name):
        return self._topic_map.get(task_name)

    def publish(self, message_subject: str, topic_arn: str, message_body: str):
        if self._batch_mode:
            self._batch.put((message_subject, topic_arn, message_body))
            return
        response = self._client.publish(
            TopicArn=topic_arn,
            Subject=message_subject,
            Message=message_body
        )
        return response['MessageId']

    def _batch_publish(self):
        while True:
            order = self._batch.get()
            if order is None:
                return
            self.publish(*order)

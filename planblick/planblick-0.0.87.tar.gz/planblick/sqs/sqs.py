import json
import os
import boto3
import threading
from time import sleep
from ..encryption.encryption import Encryption

class Sqs:

    def __init__(self, QueueName=None, Attributes={"VisibilityTimeout": "60"}):
        self.ENVIRONMENT = json.loads(os.getenv("CLUSTER_CONFIG")).get("environment")
        self.kong_api = json.loads(os.getenv("CLUSTER_CONFIG")).get("kong-admin-url")

        boto3.setup_default_session(region_name='eu-central-1')
        self.sqs = boto3.resource('sqs')
        self.sqs_client = boto3.client('sqs', region_name='eu-central-1')
        self.cipher = json.loads(os.getenv("CLUSTER_CONFIG")).get("cipher-key")
        self.crypt = Encryption()

        if QueueName is not None:
            self.set_queue(QueueName=QueueName, Attributes=Attributes)

    def get_all_queues(self):
        for queue in self.sqs.queues.all():
            print(queue.url)

    def set_queue(self, QueueName, Attributes=None):
        try:
            self.queue = self.sqs.get_queue_by_name(QueueName=QueueName)
        except Exception as e:
            if hasattr(e, "response") and e.response.get("Error").get("Code") == "AWS.SimpleQueueService.NonExistentQueue":
                print("Trying to auto-create queue...")
                self.create_queue(QueueName=QueueName, Attributes=Attributes)
            else:
                raise
        return True

    def create_queue(self, QueueName, Attributes={}):
        try:
            self.queue = self.sqs.create_queue(QueueName=QueueName, Attributes=Attributes)
            self.queue_url = self.sqs_client.get_queue_url(QueueName=QueueName)['QueueUrl']
            self.queue_attrs = self.sqs_client.get_queue_attributes(QueueUrl=self.queue_url, AttributeNames=['All'])[
                'Attributes']
            self.queue_arn = self.queue_attrs['QueueArn']
            if ':sqs.' in self.queue_arn:
                self.queue_arn = self.queue_arn.replace(':sqs.', ':')

        except Exception as e:
            if hasattr(e, 'response') and e.response.get("Error").get("Code") == "AWS.SimpleQueueService.QueueDeletedRecently":
                print(e.response)
                print("Waiting 60 seconds and try again automatically...")
                sleep(62)
                self.queue = self.sqs.create_queue(QueueName=QueueName, Attributes=Attributes)
                self.queue_url = self.sqs_client.get_queue_url(QueueName=QueueName)['QueueUrl']
                self.queue_attrs = \
                self.sqs_client.get_queue_attributes(QueueUrl=self.queue_url, AttributeNames=['All'])[
                    'Attributes']
                self.queue_arn = self.queue_attrs['QueueArn']
                if ':sqs.' in self.queue_arn:
                    self.queue_arn = self.queue_arn.replace(':sqs.', ':')
            else:
                raise

        print("Queue '{0}' created successfully!".format(QueueName))

    def subscribe_to_topic(self, topic):
        # Subscribe SQS queue to SNS
        response = self.sqs_client.set_queue_attributes(
            QueueUrl=self.queue_url,
            Attributes={
                "Policy": self.allow_sns_to_write_to_sqs()
            }
        )

        sns_client = boto3.client('sns', region_name='eu-central-1')
        response = sns_client.subscribe(
            TopicArn="arn:aws:sns:eu-central-1:282615081127:" + topic,
            Protocol='sqs',
            Endpoint=self.queue_arn
        )

        print(response)

    def create_topic(self,topic):
        sns_client = boto3.client('sns', region_name='eu-central-1')
        topic_res = sns_client.create_topic(Name=topic)
        sns_topic_arn = topic_res['TopicArn']
        return sns_topic_arn

    def send(self, MessageBody, MessageAttributes={}):
        if type(MessageBody) == dict:
            MessageBody = json.dumps(MessageBody)
            MessageBody = self.crypt.encrypt(MessageBody, self.cipher)
        self.queue.send_message(MessageBody=MessageBody, MessageAttributes=MessageAttributes)

        return True

    def receive(self, callback=None, MaxNumberOfMessages=10, endless=False):
        while (1):
            for message in self.queue.receive_messages(MaxNumberOfMessages=MaxNumberOfMessages):
                if callback is not None and callable(callback):
                    result = callback(message)
                elif isinstance(callback, object) and type(self) in callback.__class__.__bases__:
                    self.load_message(message)
                    result = self.handleTopic(callback)
                if result == True:
                    message.delete()
            if endless is not True:
                break
            else:
                sleep(3)

    def handleMessage(self, message):
        print(
            "No Message-Handler-Provided. Please use this class, extend from it and implement your own handleMessage funktion")
        return False

    def load_message(self, message):
        body = self.crypt.decrypt(message.body, self.cipher)
        self.msg = json.loads(body)

    def handleTopic(self, callback):
        topic = self.getTopic()
        if hasattr(callback, topic):
            method_to_call = getattr(callback, self.getTopic())
            return method_to_call(self.msg.get("Message"))
        else:
            print("No handler for topic: " + topic)
            return False

    def getTopic(self):
        topic_arn = self.msg.get("TopicArn")
        return topic_arn.split(':')[-1]

    def addConsumer(self, callback=None, MaxNumberOfMessages=10):
        t = threading.Thread(target=self.receive, args=([callback, MaxNumberOfMessages, True]))
        t.daemon = True
        t.start()

    def allow_sns_to_write_to_sqs(self):
        policy_document = {
            "Version": "2012-10-17",
            "Id": self.queue_arn + "/SQSDefaultPolicy",
            "Statement": [
                {
                    "Sid": "Sid1548944236219",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "SQS:SendMessage",
                    "Resource": self.queue_arn,
                    "Condition": {
                        "ArnEquals": {
                            "aws:SourceArn": "arn:aws:sns:eu-central-1:282615081127:*"
                        }
                    }
                }
            ]
        }

        return json.dumps(policy_document)

import boto3
import json
import os
from ..encryption.encryption import Encryption

class Sns:

    def __init__(self):
        self.cipher = json.loads(os.getenv("CLUSTER_CONFIG")).get("cipher-key")
        self.crypt = Encryption()

    def publish_event(self, correlationId, eventKind, payload):
        payload["correlationId"] = correlationId
        sns_client = boto3.client('sns', region_name='eu-central-1')

        sns_topic_arn = "arn:aws:sns:eu-central-1:282615081127:" + str(eventKind)
        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=self.crypt.encrypt(json.dumps(payload), self.cipher),
            MessageStructure='raw')

        return response

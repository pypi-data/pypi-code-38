import boto3
import json
from logging import exception
from pprint import pprint
from requests import post
from sys import argv


class Ansiblelogs():
    def __init__(self):
        self.ledger = []
        self.client = 1
        self.client = boto3.client('logs', region_name='ap-south-1')
        self.logGropup = 'ecs/runner'

    def fechLogsFromStartAndTail(self, taskId):
        stream = self.logGropup+'/'+taskId
        print(stream)
        response = self.client.get_log_events(
            logGroupName='/'+self.logGropup,
            logStreamName=stream,
            limit=500
        )
        # print(response)
        for event in response['events']:
            pprint(event['message'])

        while 'nextForwardToken' in response:
            # print("*"*20)
            response = self.client.get_log_events(
                logGroupName='/'+self.logGropup,
                logStreamName=self.logGropup+'/'+taskId,
                nextToken=response['nextForwardToken'],
                limit=50
            )
            # if len(response['events']) == 0:
            #     break
            for event in response['events']:
                pprint(event['message'])

        # print(response['nextForwardToken'])

    def getTaskId(self, controllerId, timestamp):
        url = "https://k70o77mvse.execute-api.ap-south-1.amazonaws.com/Prod/users/checkDynamoForUpdate"
        try:
            data = {
                'cid': [str(controllerId)],
                'ts': timestamp
            }
            print(data)
            r = post(url, json=data)
            print(r.text)
            data = json.loads(r.text)
            print(data)
            return data[0]['taskId']
        except Exception as e:
            print(e)
            exception(controllerId)

    def processArgument(self, argument):
        contollerId = argument[0]
        timestamp = argument[1]+' '+argument[2]
        return contollerId, timestamp


if __name__ == "__main__":
    # argumet = argv[4:]
    obj = Ansiblelogs()
    # print(obj.processArgument(argument=argumet))
    # obj.getTaskId('2803','2019-06-03 16:41:13')
    obj.fechLogsFromStartAndTail("6e0dd7e2-c486-499a-b1e2-9de45a1eb156")

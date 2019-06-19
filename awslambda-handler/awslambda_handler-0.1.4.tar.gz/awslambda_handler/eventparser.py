
all_in = lambda a, b:  all(elem in a for elem in b)

class EventParser(object):
    @property
    def caller(self):
        return self.__caller

    @caller.setter
    def caller(self, event):
        """
        Lambda function event parser to identify the service making the request
        """
        callers_conditions = {
            'cloudformation': eval(
                "all_in(event.keys(), ['StackId', 'RequestType', 'ResourceType'])"
            ),
            'cloudwatchlogs': eval(
                "'awslogs' in event.keys() and 'data' in event['awslogs'].keys()"
            ),
            'apigatewayauthorization': eval(
                "'authorizationToken' in event.keys() and event['authorizationToken'] == 'incoming-client-token'"
            ),
            'cloudfront': eval(
                "'Records' in event.keys() and 'cf' in event['Records'][0].keys()"
            ),
            'sns': eval(
                "'Records' in event.keys() and (event['Records'][0]['EventSource'] == 'aws:sns')"
            ),
            'codecommit': eval(
                "'Records' in event.keys() and (event['Records'][0]['eventSource'] == 'aws:codecommit')"
            ),
            'ses': eval(
                "'Records' in event.keys() and (event['Records'][0]['eventSource'] == 'aws:ses')"
            ),
            'kinesis': eval(
                "'Records' in event.keys() and (event['Records'][0]['eventSource'] == 'aws:kinesis')"
            ),
            's3': eval(
                "'Records' in event.keys() and (event['Records'][0]['eventSource'] == 'aws:s3')",
            ),
            'dynamodb': eval(
                "'Records' in event.keys() and (event['Records'][0]['eventSource'] == 'aws:dynamodb')"
            ),
            'events': eval(
                "'source' in event.keys() and event['source'] == 'aws.events'"
            )
        }
        for key in callers_conditions.keys():
            if callers_conditions[key]:
                self.__caller = key
                return
        self.__caller = 'NotFound'

    def __init__(self, event):
        """
        Args:
            event: Lambda function event
        """
        self.caller = event

    def __repr__(self):
        return self.caller


if __name__ == '__main__':
    EVENT = {
        'StackId': 'Id234',
        'RequestType': 'Create',
        'ResourceType': 'custom',
        'ResourceProperties': {'toto': 'tata'}
    }
    print(EVENT.keys())
    PARSER = EventParser(EVENT)
    print ("Parser", PARSER)


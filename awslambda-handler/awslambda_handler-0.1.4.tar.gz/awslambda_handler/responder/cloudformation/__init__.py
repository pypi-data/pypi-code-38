import json
import requests

from awslambda_handler.tools import check_params_exist


class Cloudformation(object):
    def __init__(self, event):
        """
        Responder to CloudFormation
        """

        required_fields = [
            'ResponseURL', 'RequestType', 'StackId', 'ResourceType'
        ]
        check_params_exist(required_fields, event)

    def respond(self, event, context,
                response_status, reason=None,
                response_data=None, physical_resource_id=None):
        """
        Function that responds back to Cloudformation after execution of the Lambda function
          Args:
            event: lambda_handler event
            context: lambda_handler context
            response_status: SUCCESS or FAILED from the code executed by the lambda
            reason: String to explain why the call failed
            data: dict of key-value returning information or values from lambda to CFN. Use GetAtt
            resource_id: resource ID of the function. Generate it or use the named based on stream
        Returns:
            sends response to CFN via API call
        """
        response_data = response_data or {}
        response_body = json.dumps(
            {
                'Status': response_status,
                'Reason': reason or "Log Stream: " + context.log_stream_name,
                'PhysicalResourceId': physical_resource_id or context.log_stream_name,
                'StackId': event['StackId'],
                'RequestId': event['RequestId'],
                'LogicalResourceId': event['LogicalResourceId'],
                'Data': response_data
            }
        )
        try:
            req = requests.put(event['ResponseURL'], data=response_body)
            if req.status_code != 200:
                print(req.text)
                raise Exception(f'CFN responded with a code {req.status_code}')
            return
        except requests.exceptions.RequestException as error:
            print(error)
            raise


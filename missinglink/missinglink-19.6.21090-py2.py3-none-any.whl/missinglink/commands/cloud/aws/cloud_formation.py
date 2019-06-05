import logging

from missinglink.commands.utilities import TupleArray
from .base_aws import AwsBase
from .wrappers import handle_not_found

logger = logging.getLogger('CF')

notification_arn = 'arn:aws:sns:us-east-2:502812207255:t1'


class Cf(AwsBase):
    def __init__(self, aws_ctx, org):
        super(Cf, self).__init__(aws_ctx, org)
        self.client = AwsBase.client('cloudformation', aws_ctx)

    def create(self, stack_name, stack_data, parameters=None, tags=None):
        parameters = sorted(TupleArray.dict_to_tuple_array(parameters or {}, key='ParameterKey', value='ParameterValue', value_transformer=self.ensure_str), key=lambda x: x['ParameterKey'])
        tags = TupleArray.dict_to_tuple_array(tags or {}, value_transformer=self.ensure_str)
        logger.info('Create: %s: %s', stack_name, stack_data)
        result = self.client.create_stack(
            StackName=stack_name,
            TemplateBody=stack_data,
            Parameters=parameters,
            Tags=tags,
            Capabilities=['CAPABILITY_NAMED_IAM'],
        )
        return result

    @handle_not_found
    def get(self, stack_name):
        response = self.client.describe_stacks(
            StackName=stack_name
        )
        stack = response['Stacks'][0]
        output_dict = TupleArray.tuple_array_do_dict(stack.get('Outputs', []), key='OutputKey', value='OutputValue')
        response = {'_src': stack, 'status': stack['StackStatus'], 'name': stack['StackName'], 'id': stack['StackId'], 'outputs': output_dict}
        return response

    @handle_not_found
    def resources(self, stack_name):
        response = self.client.describe_stack_resources(
            StackName=stack_name
        )
        stack = response['StackResources']
        output_dict = [{
            'LogicalResourceId': resource.get('LogicalResourceId'),
            'ResourceStatusReason': resource.get('ResourceStatusReason'),
            'ResourceStatus': resource.get('ResourceStatus')
        } for resource in stack]
        return output_dict

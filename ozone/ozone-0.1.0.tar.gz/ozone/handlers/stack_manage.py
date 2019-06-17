"""
Functions to help creation / update of stacks
"""
import boto3
from ozone.handlers import UPDATABLE_STATUSES
from botocore.exceptions import ValidationError, ClientError

def check_if_stack_exists(client, stack_name):
    """
    Args:
      stack_name: name of the CFN stack
      region: name of the region where the stack is looked up
    Returns:
      boolean True if found, False if not or failed
    """
    res = {}
    try:
        res = client.describe_stacks(StackName=stack_name)
    except (ClientError, ValidationError) as error:
        response = error.response['Error']
        if (response['Code'] == 'ValidationError' and
            response['Message'].find('does not exist')):
            return (False, None)
    if 'Stacks' in res.keys() and res['Stacks']:
        if res['Stacks'][0]['StackStatus'] in UPDATABLE_STATUSES:
            return (True, res['Stacks'][0])


def create_update_stack(client, **cfn_args):
    """
    Args:
        region: name of the AWS region to create / update the stack into
        cfn_args: arguments for CFN Create / Update stack call
    Returns:
        {'StackId': stack_id} from boto3 response
    """
    stack_exists = check_if_stack_exists(
        client, cfn_args['StackName']
    )

    if stack_exists is not None and stack_exists[0]:
        for key in ['EnableTerminationProtection', 'OnFailure']:
            if key in cfn_args.keys():
                cfn_args.pop(key, None)
        try:
            stack_r = client.update_stack(**cfn_args)
            return stack_r
        except ClientError as error:
            response = error.response['Error']
            if (response['Code'] == 'ValidationError' and
                response['Message'] == 'No updates are to be performed.'):
                return {'StackId' : stack_exists[1]['StackId']}
    else:
        stack_r = client.create_stack(**cfn_args)
        return stack_r

def check_if_stackset_exists(client, stackset_name):
    """
    Args:
      stackset_name: name of the CFN stackset
      region: name of the region where the stackset is looked up
    Returns:
      boolean True if found, False if not or failed
    """
    res = {}
    try:
        res = client.describe_stack_set(StacksetName=stack_name)
    except (ClientError, ValidationError) as error:
        response = error.response['Error']
        if (response['Code'] == 'ValidationError' and
            response['Message'].find('does not exist')):
            return (False, None)
    if 'Stacks' in res.keys() and res['Stacks']:
        if res['Stacks'][0]['StackStatus'] in UPDATABLE_STATUSES:
            return (True, res['Stacks'][0])


def create_update_stack_set(client, **cfn_args):
    """
    Args:
        region: name of the AWS region to create / update the stack into
        cfn_args: arguments for CFN Create / Update stack call
    Returns:
        {'StackId': stack_id} from boto3 response
    """
    stackset_exists = check_if_stack_set_exists(
        client, cfn_args['StackName']
    )

    if stackset_exists is not None and stackset_exists[0]:
        try:
            stack_r = client.update_stack_set(**cfn_args)
        except ClientError as error:
            response = error.response['Error']
            if (response['Code'] == 'ValidationError' and
                response['Message'] == 'No updates are to be performed.'):
                return {'StackId' : stackset_exists[1]['StackId']}
        return stack_r
    else:
        stack_r = client.create_stack_set(**cfn_args)
        return stack_r

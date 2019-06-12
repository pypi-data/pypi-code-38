from functools import wraps
from botocore import exceptions


def handle_not_found(fn):
    @wraps(fn)
    def try_error(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except exceptions.ClientError as e:
            # http://boto3.readthedocs.io/en/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks incorrectly indicates that `AmazonCloudFormationException` is supposed to be risen
            if e.args[0].endswith('does not exist') or '(NoSuchEntity)' in e.args[0]:
                return None

            raise

    return try_error

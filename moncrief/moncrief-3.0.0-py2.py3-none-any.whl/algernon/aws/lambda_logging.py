import logging
import os

from aws_xray_sdk.core import patch_all


def lambda_logged(lambda_function):
    def wrapper(*args):
        patch_all()
        event = args[0]
        context = args[1]
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)
        log_level = logging.INFO
        if os.getenv('DEBUG', 'false').lower() == 'true':
            log_level = logging.DEBUG
        logging.basicConfig(format='[%(levelname)s] ||' +
                                   f'function_name:{context.function_name}|function_arn:{context.invoked_function_arn}|'
                                   f'request_id:{context.aws_request_id}' +
                                   '|| %(asctime)s %(message)s', level=log_level)
        logging.getLogger('aws_xray_sdk').setLevel(logging.WARNING)
        logging.getLogger('botocore').setLevel(logging.WARNING)
        results = lambda_function(event, context)
        return results
    return wrapper

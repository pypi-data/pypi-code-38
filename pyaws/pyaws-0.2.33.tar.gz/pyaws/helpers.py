from contextlib import contextmanager
import inspect
import logging

from botocore.exceptions import ClientError

from pyaws import __version__

logger = logging.getLogger(__version__)

@contextmanager
def handle_boto_error(message_template=None):
    '''
    Context manager for wrapping a potentially-ClientError raising block of code
    with a consistent error handler/reporter.

    Example usage:

    >>> from botocore.exceptions import ClientError
    >>> with handle_boto_error():
    ...     # do something that raises a ClientError
    ...
    
    '''
    message_template = message_template or '{function}: boto3 error occured (Code: {code} Message: {message})'
    try:
        yield
    except ClientError as e:
        logger.exception(
            message_template.format(
                function=inspect.stack()[0][3],
                code=e.response['Error']['Code'],
                message=e.response['Error']['Message']
            )
        )
        raise
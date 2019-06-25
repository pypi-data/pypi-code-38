from __future__ import print_function
import sys
import traceback
import logging
import datetime
import os
import json


# https://github.com/gene1wood/cfnlambda/blob/master/cfnlambda.py
class PythonObjectEncoder(json.JSONEncoder):
    """Custom JSON Encoder that allows encoding of un-serializable objects
    For object types which the json module cannot natively serialize, if the
    object type has a __repr__ method, serialize that string instead.
    Usage:
        >>> example_unserializable_object = {'example': set([1,2,3])}
        >>> print(json.dumps(example_unserializable_object,
                             cls=PythonObjectEncoder))
        {"example": "set([1, 2, 3])"}
    """

    def default(self, obj):
        if isinstance(obj,
                      (list, dict, str, unicode,
                       int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        elif hasattr(obj, '__repr__'):
            return obj.__repr__()
        else:
            return json.JSONEncoder.default(self, obj.__repr__())


def handler(event, context):
    print("Event:\n",   event)
    print("Context:\n", context)
    # Need to try to get an API_KEY from the incoming request and add it to the environment
    retval = None
    dfunc = None

    if (context.get("__d_df_func")):
        dfunc = context.get("__d_df_func")

    try:
        if (dfunc == None):
            import function
            dfunc = function.data_function
        raw_function_result = dfunc(event)

        if(raw_function_result.get('result') is not None):
            ### This is a temp hack to keep Jason's existing data function deploys
            ### It should be removed in a month or so.
            retval = {"result": raw_function_result['result']}
        else:
            retval = {"result": raw_function_result}
    except:
        # log error
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        transaction_id = None
        if(event and event.get('transaction_id') is not None):
            transaction_id = event['transaction_id']

        error_info = {
            "error": "".join(lines),
            "transaction_id": transaction_id,
            # "event": event,
            # "context": json.loads(json.dumps(vars(context), cls=PythonObjectEncoder)),
            # "env": dict(**os.environ),
            "data_function_name": os.environ.get("AWS_LAMBDA_FUNCTION_NAME"),
            "data_function_version": os.environ.get("AWS_LAMBDA_FUNCTION_VERSION"),
            "error_type": "caught_exception_in_client_code",
            "log_level": 'error',
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        print(json.dumps(error_info, sort_keys=True))
        retval = error_info
    finally:
        return retval

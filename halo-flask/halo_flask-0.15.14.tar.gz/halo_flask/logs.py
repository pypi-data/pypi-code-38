from __future__ import print_function


from .flask.utilx import Util

def append_error(params, err):
    """

    :param params:
    :param err:
    :return:
    """
    dict_items = params.copy()
    if err:
        stack = None
        if hasattr(err, "stack"):
            stack = err.stack
        error = {"errorName": str(type(err).__name__), "errorMessage": str(err), "stackTrace": str(stack)}
        dict_items.update(error)
    logMsg = {key: value for (key, value) in (dict_items.items())}
    return logMsg


def log_json(req_context, params=None, err=None):
    """

    :param req_context:
    :param params:
    :param err:
    :return:
    """
    context = Util.get_context()
    dict_items = dict(req_context)
    dict_items.update(context)
    logMsg = {key: value for (key, value) in (dict_items.items())}
    if params or err:
        pe = append_error(params, err)
        if pe:
            logMsg['params'] = pe

    # logger.debug(json.dumps(logMsg))
    return logMsg
    # return json.dumps(logMsg)
    # {"aws_request_id": "1fcf5a10-9d44-49dd-bbad-9f23945c306f", "level": "DEBUG", "x-user-agent": "halolib:/:GET:f55a", "awsRegion": "REGION", "x-correlation-id": "1f271213-6d32-40b7-b1dc-12e3a9a31bf4", "debug-log-enabled": "false", "functionVersion": "VER", "message": "we did it", "stage": "STAGE", "functionMemorySize": "MEM", "functionName": "halolib"}

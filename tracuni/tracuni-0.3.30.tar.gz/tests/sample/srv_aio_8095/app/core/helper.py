import json
import logging
from urllib.parse import parse_qs

import datetime

import decimal

import io
from aiohttp import BytesPayload


class Error(Exception):
    pass


class GracefulExit(SystemExit):
    pass


class PrepareError(Error):
    pass


class TaskFormatError(Error):
    pass


class ValidationResponseError(Error):
    pass


class WidgetResponseError(Error):
    pass


class UnknownTaskError(Error):
    pass


class BadTaskParamsError(Error):
    pass


class PayErrorException(Error):
    pass


def handler_decorator(func):
    async def wrapper(*args, **kwargs):
        res = await func(*args, **kwargs)
        res.__setattr__('function', func.__name__)

        request = args[1]
        body = await request.text()

        if body:
            params = parse_qs(body)
            if not params:
                params = json.loads(body)
        else:
            params = {}

        res.__setattr__('request_headers', request.headers)
        res.__setattr__('request', params)
        return res

    return wrapper


def flatten(iterable):
    """
    :param iterable: {'hdrs': 'trololo', 'http_code': 12, 'terr': [1, 2, 3], 'z': [1]}
    :return: {'hdrs': 'trololo', 'http_code': 12, 'terr': [1, 2, 3], 'z': 1}
    """
    res = {}
    for k, v in iterable.items():
        if isinstance(v, (tuple, list)) and len(v) == 1:  # len(v) <= 1 # exclude dict
            res[k] = v[0]
        else:
            res[k] = v
    return res


async def get_post_params(request):
    body = await request.text()
    try:
        params = parse_qs(body)
        params = flatten(params)
    except Exception as e:
        logging.error('Cannot parse request body: %s.', body)
        params = {}
    return params


async def get_json_params(request):
    """
    :param request: '{"method": "PaymentInit", "msisdn": "79268638461", "gid": "1"}'
    :return: dict {'method': 'PaymentInit', 'msisdn': '79268638461', 'gid': '1'}
    """
    body = await request.text()
    try:
        params = json.loads(body)
        params = flatten(params)
    except Exception as e:
        logging.error('Cannot parse request body: %s.', body)
        params = {}
    return params


async def get_get_params(request):
    """
    :param request: 'http://inplat:8093/mocker/hexml/paymentbalance?ACCOUNT=InPlat&PWD=InPlat&MSISDN=79295803749'
    :return: dict {'ACCOUNT': 'InPlat', 'PWD': 'InPlat', 'MSISDN': '79295803749'}
    """
    get_row = request.GET
    try:
        params = dict(get_row)
    except Exception as e:
        logging.error('Cannot parse request get string: %s.', get_row)
        params = ''
    return params


def gen_log_config(config):
    if 'system' in config:
        sysconfig = config['system']
        log_config = {
            'log_format': sysconfig.get('log_format', "%(levelname)-8s [%(asctime)s] %(message)s"),
            'log_file': sysconfig.get('log_file', "logs/mocker2.log"),
            'log_mode': sysconfig.get('log_mode', "STDOUT"),
            'log_level': sysconfig.get('log_level', "INFO"),
        }
        return log_config
    else:
        raise KeyError("'system' does not exists in config!")


def set_python_log(config):

    levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }

    log_level = levels[config.get('log_level', 'INFO').upper()]

    log_formatter = logging.Formatter(config['log_format'])
    root_logger = logging.getLogger()

    def log2file():
        file_handler = logging.FileHandler(config['log_file'])
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

    def log2stdout():
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

    log_mode = config.get('log_mode', 'stdout').lower()

    if log_mode == 'file':
        log2file()
    elif log_mode == 'stdout':
        log2stdout()
    else:
        log2file()
        log2stdout()

    return root_logger


def json_encoder(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    if isinstance(obj, datetime.time):
        return obj.strftime('%H:%M:%S.%f%z')
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    if isinstance(obj, bytes):
        try:
            return obj.decode('UTF8')
        except:
            return str(obj)
    return repr(obj)


def json_encode(data):
    return json.dumps(data, default=json_encoder)


def annotate_bytes(span, data):
    if isinstance(data, BytesPayload):
        pl = io.BytesIO()
        data.write(pl)
        data = pl.getvalue()
    try:
        data_str = data.decode("UTF8")
    except Exception:
        data_str = str(data)
    span.annotate(data_str or 'null')


def raise_graceful_exit():
    raise GracefulExit()

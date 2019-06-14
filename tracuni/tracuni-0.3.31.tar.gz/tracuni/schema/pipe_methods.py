import re
import json
import io
from collections import namedtuple
from itertools import islice
from urllib.parse import parse_qs, urlparse
from json import JSONDecodeError

from aiohttp import BytesPayload
from aiohttp.web_response import Response

from typing import (
    TYPE_CHECKING,
    Any,
    Union,
    Dict,
    Sequence,
    Tuple,
)

from tracuni.schema.lib import (
    catch_essential,
    mask_secret,
    make_cut,
    pick_items,
)
from tracuni.misc.helper import (
    PostgreSQLRecord,
    json_dumps_decode,
)
from tracuni.define.const import (
    CUT_LIMIT,
    CUT_LINE,
    UNKNOWN_NAME,
    LOG_STRING_WRAP,
)
from tracuni.define.type import (
    TeeDescriptor,
    PipelineTee,
    DestinationSection,
    PipeCommand,
)
from tracuni.misc.select_coroutine import get_coroutine_decorator
async_decorator = get_coroutine_decorator()

if TYPE_CHECKING:
    from tracuni.adapter import AdapterType


pattern_module_method_names = re.compile(r'.*/(.*)\.py:\d+\.(.*)$')


###############################################################################
# Новые проверенные


def pipe_debug(data):
    return PipeCommand.DEBUG


@async_decorator
def ext_http_in_aiohttp_request(arguments: namedtuple) -> Dict[str, Any]:
    """Получить данные входящего HTTP запроса для AIOHTTP

    Parameters
    ----------
    arguments
        Аргументы точки вызова

    Returns
    -------
        Описание и нагрузку запроса, включая заголовки трассера

    """
    request = None
    widget_id = None
    if hasattr(arguments, 'self'):
        request = getattr(arguments.self, 'request', None)
        system = getattr(arguments.self, 'system', None)
        if system:
            widget_id = system.widget_id
        if widget_id is None:
            widget_id = getattr(arguments.self, 'widget_id', None)
    if not request:
        request = getattr(arguments, 'request', None)
    if request is None:
        return {}

    try:
        body = yield from request.json()
    except JSONDecodeError:
        body = yield from request.text()
        body = pipe_qs_to_dict(body)

    query = None
    if hasattr(request, 'query'):
        query = dict(request.query)

    headers = {}
    zipkin_headers = {}

    content_length = request.content_length

    for header_name, header_value in request.headers.items():
        header_name_up = header_name.upper()
        if header_name_up.startswith('X-B3-'):
            zipkin_headers[header_name_up] = header_value
        else:
            headers[header_name] = header_value

    url_path = request.url.path
    url_wo_query = str(request.url.parent) + request.url.path
    remote_ip = request.remote

    body.pop('jsonParams', None)
    res = {
        'body': body,
        'query_str': '?' + request.query_string if request.query_string else '',
        'query_dict': query,
        'url': url_wo_query,
        'url_path': url_path,
        'url_host': request.url.parent,
        'remote_ip': remote_ip,
        'method': request.method,
        'widget_id': widget_id,
        'length': content_length,
        'headers': headers,
        'zipkin_headers': zipkin_headers,
    }
    return res


def ext_http_in_tornado_request(arguments: namedtuple) -> Dict[str, Any]:
    """Получить данные входящего HTTP запроса для Tornado

    Parameters
    ----------
    arguments
        Аргументы точки вызова

    Returns
    -------
        Описание и нагрузку запроса, включая заголовки трассера

    """
    widget_id = None
    request = None
    if hasattr(arguments, 'self'):
        request = getattr(arguments.self, 'request', None)
        system = getattr(arguments.self, 'system', None)
        if system:
            widget_id = getattr(system, 'widget_id', None)
        if widget_id is None:
            widget_id = getattr(arguments.self, 'widget_id', None)

    if not request:
        request = getattr(arguments, 'request', None)
    if request is None:
        return {}

    body_str = request.body.decode() or "{}"
    try:
        body = json.loads(body_str)
    except JSONDecodeError:
        body = body_str

    zipkin_headers = {}

    headers = dict(request.headers)
    content_length = headers.get('Content-Length', len(body_str))
    for header_name, header_value in request.headers.items():
        if header_name.startswith('X-B3-'):
            zipkin_headers[header_name] = header_value
        else:
            headers[header_name] = header_value

    url = request.protocol + "://" + request.host + request.path
    url_path = request.path

    remote_ip = request.remote_ip

    try:
        if 'pop' in body:
            body.pop('jsonParams'
                     ''
                     '', None)
    except TypeError:
        pass

    res = {
        'body': body,
        'query_str': '?' + request.query if request.query else '',
        'query_dict': parse_qs(request.query or ''),
        'url': url,
        'url_path': url_path,
        'url_host': request.host,
        'remote_ip': remote_ip,
        'method': request.method,
        'widget_id': widget_id,
        'length': content_length,
        'headers': headers,
        'zipkin_headers': zipkin_headers,
    }
    return res


def ext_out_headers(args):
    self = getattr(args, 'self', None)
    if self is not None:
        return getattr(getattr(self, 'request', None), 'headers', None)
    return getattr(args, 'headers', None)


def pipe_head(seq: Sequence[Any], indexes=0) -> Any:
    """Получить первый элемент из обрабатываемого набора данных

    Parameters
    ----------
    seq
        Список извлечённых данных (каждый источник представлен одним элементом)

    Returns
    -------
        Первый элемент списка
    """
    v = pick_items.do(seq, indexes)
    return v


def pipe_check_skip(data: Tuple[str, 'AdapterType']):
    """Для входящих HTTP: находится ли адрес обработчика в списке игнорируемых

    Parameters
    ----------
    data
        кортеж: проверяемый путь и ссылка на адаптер

    Returns
    -------
        флаг, показывающий надо ли пропускать
    """
    path, adapter = data
    flag = adapter.should_not_trace(path)
    return flag


def pipe_sep_string(
    data: Sequence,
    sep: Union[Sequence[str], str] = ' '
) -> str:
    """Преобразует несколько значений в одну строку с разделителями

        Можно передавать несколько разделителей, тогда первый станет
        разделителем первой пары значений, второй - второй и так далее,
        если раздлителей меньше. чем пар значений, то последний разделитель
        будет использован для всех оставшихся

    Parameters
    ----------
    data
        Список обрабатываемых данных
    sep
        Набор разделителей для объединения списка

    Returns
    -------
        Строку значений с указанными разделителями
    """
    if not data:
        return ''

    if isinstance(sep, str):
        sep = (sep, )

    if not sep:
        sep = ('', )

    placeholder = '{}'
    place_len = len(placeholder)
    n = len(data)
    tmpl = placeholder * n
    sep_tail = (sep[-1],) * (n - len(sep))

    placeholder_line = [
        tmpl[idx:idx + place_len]
        for idx in range(0, len(tmpl), place_len)
    ]
    separators = sep + sep_tail
    zipped = list(zip(placeholder_line, separators))
    if len(data) != len(sep):
        zipped[-1] = (zipped[-1][0],)

    composed = ''.join([
        el
        for sublist in zipped
        for el in sublist
    ]).format(*data)
    return composed


def pipe_catch_essential(data):
    # return catch_essential.do(data)
    # obsolete - essentials are caught inside mask secret method
    return data


def pipe_mask_secret_catch_essentials(data):
    return mask_secret.do(data)


def pipe_by_name(data, name: str) -> Any:
    return getattr(
        data,
        name,
        data.get(name)
        if getattr(data, "get", False)
        else UNKNOWN_NAME
    )


def pipe_complex_result(data, key):
    if (
        isinstance(data, tuple)
        and
        len(data) == 2
        and isinstance(data[0], Response)
    ):
        data = data[0]
    if isinstance(data, Response):
        value = getattr(data, key, None)
        if isinstance(value, bytes):
            value = value.decode()
        return value
    if not isinstance(data, dict) or not key:
        return data
    res = data.get(key, {})
    if key in ('response_headers', 'request_headers'):
        res = dict((k, v) for k, v in res.items() if not k.startswith('X-B3'))
    return res


def pipe_dump(data):
    if isinstance(data, bytes):
        return data.decode()
    if isinstance(data, (dict, tuple, list)):
        return json_dumps_decode(data, indent=4)
    return data


def pipe_cut(data, cut_limit=CUT_LIMIT, cut_line=CUT_LINE):
    if isinstance(data, (dict, tuple, list)):
        prepared_data = json_dumps_decode(data, indent=4)
    else:
        prepared_data = str(data)
    cut, _, is_cut = make_cut.do(
        prepared_data,
        cut_limit,
        cut_line
    )
    if len(cut) > 2:
        cut = cut[1:-1].replace('\\\"', '"').replace('\\n', '\n')
    return cut if is_cut else data


def pipe_inject_headers(data, prefix_key=None):
    if len(data) < 2:
        data = (*data, {})
    if len(data) < 3:
        data = (*data, UNKNOWN_NAME)
    span, headers, service_name = data
    if headers is None:
        headers = {}

    headers = span.enrich_headers(headers, prefix_key)
    name_record = {'X-B3-ServiceName': service_name}
    if prefix_key:
        headers[prefix_key].update(name_record)
    else:
        headers.update(name_record)
    return headers


def ext_tracer_out_point(track, name_variant='short', shift=1):
    data_l = len(track)

    name_variant += '_path'
    if name_variant == 'compact_path':
        full_name = track[shift]['full_path']
        compact_name = pattern_module_method_names.match(full_name).groups()
        track[shift][name_variant] = '.'.join(compact_name)

    if data_l > shift:
        return track[shift][name_variant]
    elif data_l:
        return track[0][name_variant]
    return ''


def ext_http_out_url(params):
    res = getattr(params, 'url', '')
    res = ''.join([urlparse(res)[0], '://', *urlparse(res)[1:3]])
    return res


def pipe_db_service_name_from_config(data):
    """Подставляет имя партнерского сервиса из конфигурации, если данный URL
    в ней есть, иначе оставляет url

    Parameters
    ----------
    data type: tuple
        (словарь настроек, строка url)

    Returns
    -------
        Наименование партнерского сервиса
    """
    return (getattr(data, "config", {}) or {}).get('dbname', 'db')


def pipe_service_name_from_config(data):
    """Подставляет имя партнерского сервиса из конфигурации, если данный URL
    в ней есть, иначе оставляет url

    Parameters
    ----------
    data type: tuple
        (словарь настроек, строка url)

    Returns
    -------
        Наименование партнерского сервиса
    """
    val = data[1]
    if len(data) > 1:
        try:
            val = data[0][data[1]].replace('_url', '')
        except (IndexError, KeyError):
            pass
    return val


def ext_send_request_args(data):
    v = getattr(data, 'req', None)
    if not v:
        v = getattr(data, 'body', '')
    if isinstance(v, str):
        v_dict = parse_qs(v)
        if not v_dict:
            step = LOG_STRING_WRAP
            chunks = [v[idx:idx+step] for idx in range(0, len(v), step)]
            v = '\n'.join(chunks)
        else:
            v = v_dict
    return v


def ext_api_kind(engine):
    return engine.schema_feed.variant.api_kind.name.lower()


def ext_tracer_path(track, length=5):
    track_short_list = tuple(islice(
        (
            path_element
            for path_element in (el.get('short_path') for el in track)
            if path_element not in ('run', 'run_loop', 'main')
        ),
        0,
        length
    ))
    return (' > '.join(
        ('{}',)*len(track_short_list)
    )).format(*reversed(track_short_list))


def ext_tracer_full_path(track):
    full_path = ''
    if len(track) > 1:
        full_path = track[1].get('full_path')
    return full_path


def ext_tracer_short_path(track):
    full_path = ''
    if len(track) > 1:
        full_path = track[1].get('short_path')
    return full_path


def ext_sql_args(arguments):
    # noinspection PyProtectedMember
    res = dict(
        (k, v)
        for k, v in arguments._asdict().items()
        if k not in ('self', 'sql')
    )
    if 'method_arguments_without_names' in res and len(res) == 1:
        res = res['method_arguments_without_names']
        if res and len(res) == 1:
            res = res[0]
    return res


def ext_sql_response(res):
    if PostgreSQLRecord and isinstance(res, PostgreSQLRecord):
        return dict(res)
    return res


###############################################################################
# Старые


# noinspection SpellCheckingInspection
def pipe_convert_dict(dikt: dict):
    return convert(dikt)


def pipe_convert_bytes(data):
    res = annotate_bytes(data)
    if res == 'None':
        res = None
    return res


def get_space(_):
    return ' '


def pipe_identity(v):
    return v


def pipe_qs_to_dict(data):
    if isinstance(data, str):
        res = parse_qs(data)
        res = dict((k, v[0] if len(v) == 1 else v) for k, v in res.items())
        return res
    return data


def ext_http_in_path(arguments):
    """Поулчить адрес входящего запроса

    Parameters
    ----------
    arguments
        Аргументы точки вызова

    Returns
    -------
        URL из запроса, если найден в ожидаемых атрибутах
    """
    request = getattr(arguments.self, 'request', None)
    if not request:
        request = getattr(arguments, 'request', None)
    return request.path


def load_dict(data):
    try:
        return json.loads(str(data))
    except JSONDecodeError:
        string_payload_value = getattr(data, '_value', None)
        if string_payload_value:
            return string_payload_value
        return str(data)


def convert(data):
    data_type = type(data)

    if data_type == bytes:
        return data.decode()
    if data_type in (str, int, bool):
        return str(data)
    if data is None:
        return None

    if data_type == dict:
        data = data.items()

    return data_type(map(convert, data))


def annotate_bytes(data, fallback_value='<unknown>'):
    if isinstance(data, BytesPayload):
        pl = io.BytesIO()
        # noinspection PyTypeChecker
        data.write(pl)
        data = pl.getvalue()
    try:
        data_str = data.decode("UTF8")
    except (AttributeError, UnicodeDecodeError):
        data_str = str(data)

    return data_str or fallback_value


def pipe_normalize_json_string(json_data):
    try:
        return json.dumps(json.loads(json_data))
    except (TypeError, json.JSONDecodeError):
        return json_data


def pipe_get_send_request_core(point_args):
    url = getattr(point_args, 'url', None)
    parsed_url = urlparse(url)
    url_hostname = parsed_url.hostname
    url_address = ''.join([parsed_url[0], '://', *parsed_url[1]])
    url_path = parsed_url[2] or '/'
    query_parsed = parsed_url[4]
    body = None if query_parsed else getattr(point_args, 'body', None)
    return {
        "body": body,
        "query": query_parsed,
        "url": url,
        "url_hostname": url_hostname,
        "url_address": url_address,
        "url_path": url_path,
        "method": getattr(point_args, 'method', 'POST'),
        "headers": getattr(point_args, 'headers', None),
    }


def pipe_get_send_request_tornado(point_args):
    url = getattr(point_args, 'url', None)
    parsed_url = urlparse(url)
    url_hostname = parsed_url.hostname
    url_address = ''.join([parsed_url[0], '://', *urlparse(url)[1]])
    url_path = parsed_url[2] or '/'
    body = getattr(point_args, 'req', None)
    query = getattr(point_args, 'body', None)
    return {
        "body": body,
        "query": query,
        "url": url,
        "url_hostname": url_hostname,
        "url_address": url_address,
        "url_path": url_path,
        "method": getattr(point_args, 'method', 'POST'),
        "headers": getattr(point_args, 'headers', None),
    }

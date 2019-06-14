from functools import partial

from tracuni.define.type import (
    Rule,
    Destination,
    DestinationSection,
    Origin,
    OriginSection,
    Stage,
    PipeCommand,
)
from tracuni.misc.helper import nerf_tail_digits
from tracuni.schema.pipe_methods import (
    ext_out_headers,
    ext_tracer_out_point,
    ext_http_out_url,
    pipe_inject_headers,
    pipe_head,
    pipe_sep_string,
    pipe_service_name_from_config,
    pipe_catch_essential,
    pipe_mask_secret_catch_essentials,
    pipe_dump,
    pipe_cut,
    ext_send_request_args,
    ext_api_kind,
    pipe_get_send_request_core,
    ext_tracer_path,
    ext_tracer_full_path,
)


def deb(x):
    return x


ruleset = (
    Rule(
        description="Путь по методам, вызвавшим запрос",
        destination=Destination(DestinationSection.SPAN_TAGS, 'app.path'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.CALL_STACK, ext_tracer_path),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Метод, вызвавший запрос",
        destination=Destination(DestinationSection.SPAN_TAGS, 'app.method'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.CALL_STACK, ext_tracer_full_path),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Сохранить данные запроса из аргументов для переиспользвоания",
        destination=Destination(DestinationSection.REUSE, 'request'),
        pipeline=(
            pipe_head,
            pipe_get_send_request_core,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, None),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Задать имя участку",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'name'
        ),
        pipeline=(
            lambda x: [x[0], nerf_tail_digits(x[1])],
            lambda x: ("http", x[0].lower(), x[1]),
            partial(pipe_sep_string, **{'sep': ('::', ' (', ')')}),
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['method'],
            ),
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['url_path'],
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Записать заголовки в запрос",
        destination=Destination(DestinationSection.POINT_ARGS, 'headers'),
        pipeline=(
            pipe_inject_headers,
        ),
        origins=(
            Origin(
                OriginSection.SPAN, None,
            ),
            Origin(
                OriginSection.POINT_ARGS, ext_out_headers,
            ),
            Origin(
                OriginSection.ADAPTER,
                lambda adapter: adapter.config.service_name,
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Сохранить информацию об ответе",
        destination=Destination(DestinationSection.REUSE, 'response'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.POINT_RESULT, None),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести в тэги код статуса ответа",
        destination=Destination(DestinationSection.SPAN_TAGS,
                                'rsp.status'),
        pipeline=(
            pipe_head,
            lambda response: (response or {}).get('http_code', 500),
        ),
        origins=(
            Origin(OriginSection.REUSE, 'response'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести параметры строки запроса в журнал участка ",
        destination=Destination(DestinationSection.SPAN_LOGS, 'request_query_params'),
        pipeline=(
            pipe_head,
            pipe_dump,
            pipe_cut,
            pipe_mask_secret_catch_essentials,
            partial(pipe_head, **{'indexes': 1}),
            PipeCommand.TEE,
            Destination(DestinationSection.SPAN_TAGS, {}),
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.REUSE, lambda data: data['request']['query']),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести тело запроса в аннотации участка ",
        destination=Destination(DestinationSection.SPAN_LOGS, 'request_body'),
        pipeline=(
            pipe_head,
            lambda x: x or '',
            pipe_dump,
            pipe_cut,
            pipe_mask_secret_catch_essentials,
            lambda x: x[1],
            PipeCommand.TEE,
            Destination(DestinationSection.SPAN_TAGS, {}),
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.REUSE, lambda data: data['request']['body']),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести в логи заголовки запроса",
        destination=Destination(
            DestinationSection.SPAN_LOGS,
            'http.req.headers',
        ),
        pipeline=(
            pipe_head,
            pipe_dump,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['headers'],
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Разделитель запроса и ответа",
        destination=Destination(
            DestinationSection.SPAN_LOGS,
            'divider',
        ),
        pipeline=(
            lambda _: "--------------------------------",
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                None,
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести тело ответа на запрос",
        destination=Destination(DestinationSection.SPAN_LOGS, 'response_body'),
        pipeline=(
            deb,
            pipe_head,
            lambda response: (response or {}).get('response', ''),
            pipe_dump,
            pipe_cut,
            pipe_mask_secret_catch_essentials,
            lambda x: x[1],
            PipeCommand.TEE,
            Destination(DestinationSection.SPAN_TAGS, {}),
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'response'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести в логи заголовки ответа",
        destination=Destination(
            DestinationSection.SPAN_LOGS,
            'http.rsp.headers',
        ),
        pipeline=(
            pipe_head,
            lambda response: (response or {}).get('response_headers', {}),
            lambda headers: dict(headers) if headers else None,
            pipe_dump,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'response'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Наименование партнерского сервиса сохранить для "
                    "переиспользования",
        destination=Destination(
            DestinationSection.REUSE,
            'peer_name',
          ),
        pipeline=(
            pipe_service_name_from_config,
        ),
        origins=(
            Origin(OriginSection.ADAPTER, 'url_service_map'),
            Origin(OriginSection.POINT_ARGS, ext_http_out_url),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Наименование партнерского сервиса записать в участок",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'remote_endpoint',
          ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'peer_name'),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Хост партнерского сервиса",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'peer.url',
          ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, ext_http_out_url),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести адрес запроса",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'rq.url',
        ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data.get('request', {}).get('url', ''),
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести хост из адреса запроса",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'rq.url.hostname',
        ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data.get('request', {}).get('url_hostname', ''),
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести хост из адреса запроса",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'rq.url.address',
        ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data.get('request', {}).get('url_address', ''),
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести путь из адреса запроса",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'rq.url.path',
        ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data.get('request', {}).get('url_path', ''),
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Запомнить ошибку для вывода",
        destination=Destination(DestinationSection.REUSE, 'error'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.SPAN, 'error'),
        ),
        stage=Stage.POST,
    ),
)

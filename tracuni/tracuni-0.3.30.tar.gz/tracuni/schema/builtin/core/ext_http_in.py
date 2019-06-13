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
    ext_http_in_aiohttp_request,
    pipe_head,
    pipe_check_skip,
    pipe_sep_string,
    pipe_catch_essential,
    pipe_mask_secret_catch_essentials,
    pipe_dump,
    pipe_cut,
)


def decode_body(response):
    body = getattr(response, 'body', b'')
    try:
        body = body.decode()
    except AttributeError:
        try:
            body = body._value.decode()
        except AttributeError:
            pass
    return body


ruleset = (
    Rule(
        description="Метод, вызвавший запрос",
        destination=Destination(DestinationSection.SPAN_TAGS, 'app.method'),
        pipeline=(
            pipe_head,
            lambda path: path[0].get('full_path') if path else None,
        ),
        origins=(
            Origin(OriginSection.CALL_STACK, None),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Получить данные запроса и сохранить"
                    "для переиспользования",
        destination=Destination(DestinationSection.REUSE, 'request'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, ext_http_in_aiohttp_request),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Поставить флаг пропуска трассировки, если HTTP путь"
                    "в списке игнорируемых",
        destination=Destination(DestinationSection.REUSE, 'should_not_trace'),
        pipeline=(
            pipe_check_skip,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['url_path'],
            ),
            Origin(OriginSection.ADAPTER, None),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Разместить заголовки контекста трассера там, "
                    "где фабрика участков их ищет",
        destination=Destination(DestinationSection.REUSE, 'tracer_headers'),
        pipeline=(
            pipe_head,
            lambda headers: dict((k.lower(), v) for k, v in (headers or {}).items()),
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['zipkin_headers'],
            ),
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
            lambda x: print(x) or x,
            lambda x: [x[0], nerf_tail_digits(x[1])],
            lambda x: print(x) or x,
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
        description="Задать имя партнёрской точки для участка",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'remote_endpoint',
        ),
        pipeline=(
            lambda x: x[0] or x[1],
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data.get('tracer_headers', {}).get('x-b3-servicename', ''),
            ),
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['remote_ip'],
            ),
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
            'rq.url.host',
        ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data.get('request', {}).get('url_host', ''),
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
            pipe_head,
            lambda response: getattr(response, 'status', 500),
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
            Origin(OriginSection.REUSE, lambda data: data['request']['query_str']),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести тело запроса в аннотации участка ",
        destination=Destination(DestinationSection.SPAN_LOGS, 'request_body'),
        pipeline=(
            pipe_head,
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
            pipe_head,
            pipe_head,
            # lambda response: getattr(response, 'body', b'').decode(),
            decode_body,
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
            pipe_head,
            lambda response: getattr(response, 'headers', {}),
            lambda headers: dict(headers) if headers else None,
            pipe_dump,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'response'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести идентификатор виджета в теги",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'app.widget',
        ),
        pipeline=(
            pipe_head,
            lambda request: str(request.get('widget_id') or ''),
        ),
        origins=(
            Origin(OriginSection.REUSE, 'request'),
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

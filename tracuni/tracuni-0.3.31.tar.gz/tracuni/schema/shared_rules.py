from functools import partial

from tracuni.define.type import Rule, Destination, DestinationSection, Origin, OriginSection, Stage
from tracuni.schema.pipe_methods import pipe_head, pipe_inject_headers, ext_out_headers


rule_amqp_out_tracer_context = Rule(
    description="Записать X-B3- заголовки в заголовки сообщения",
    destination=Destination(DestinationSection.POINT_ARGS, 'properties'),
    pipeline=(
        lambda data: (data[:3], data[3]),
        lambda data: (data[0], getattr(data[1], 'context_amqp_name', None)),
        pipe_head,
        partial(pipe_inject_headers, **{'prefix_key': 'headers'}),
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
        Origin(OriginSection.ADAPTER, "config",),
    ),
    stage=Stage.PRE,
)


rule_amqp_out_in_body_tracer_context = Rule(
    description="Записать X-B3- заголовки в заголовки сообщения",
    destination=Destination(DestinationSection.POINT_ARGS, 'message'),
    pipeline=(
        lambda data: (data[0], data[1], data[2], getattr(data[3], 'context_amqp_name', None), data[4]),
        lambda data: dict(data[4], **{data[3]: pipe_inject_headers(data[:3])}) if data[3] is not None else data[4],
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
        Origin(OriginSection.ADAPTER, "config",),
        Origin(
            OriginSection.POINT_ARGS, "message",
        ),
    ),
    stage=Stage.PRE,
)


rule_inner_out_tracer_context = Rule(
    description="Записать X-B3- заголовки в параметр точки",
    destination=Destination(DestinationSection.POINT_ARGS, 'xb3_headers'),
    pipeline=(
        pipe_inject_headers,
    ),
    origins=(
        Origin(
            OriginSection.SPAN, None,
        ),
        Origin(
            OriginSection.ADAPTER,
            lambda _: None,
        ),
        Origin(
            OriginSection.ADAPTER,
            lambda adapter: adapter.config.service_name,
        ),
    ),
    stage=Stage.PRE,
)


rule_inner_in_tracer_context = Rule(
    description="Разместить заголовки контекста трассера там, "
                "где фабрика участков их ищет",
    destination=Destination(DestinationSection.REUSE, 'tracer_headers'),
    pipeline=(
        pipe_head,
        lambda x: dict((k.lower(), v) for k, v in (x or {}).items()),
    ),
    origins=(
        Origin(
            OriginSection.POINT_ARGS, "xb3_headers"
        ),
    ),
    stage=Stage.INIT,
)


rule_span_peer_name_from_application_name = Rule(
    description="Задать имя партнёрской точки для участка",
    destination=Destination(
        DestinationSection.SPAN_NAME,
        'remote_endpoint',
    ),
    pipeline=(
        pipe_head,
    ),
    origins=(
        Origin(
            OriginSection.ADAPTER,
            lambda adapter: adapter.config.service_name,
        ),
    ),
    stage=Stage.PRE,
)

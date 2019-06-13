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
from tracuni.schema.pipe_methods import (
    ext_tracer_out_point,
    ext_tracer_path,
    ext_tracer_full_path,
    pipe_head,
    pipe_sep_string,
    pipe_catch_essential,
    pipe_mask_secret_catch_essentials,
    pipe_dump,
    pipe_cut,
    ext_api_kind,
    pipe_inject_headers,
    ext_out_headers,
)
from tracuni.schema.shared_rules import rule_amqp_out_tracer_context, rule_amqp_out_in_body_tracer_context

ruleset = (
    rule_amqp_out_tracer_context,
    rule_amqp_out_in_body_tracer_context,
    Rule(
        description="Сохранить тело сообщения",
        destination=Destination(DestinationSection.REUSE, 'message'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.POINT_ARGS, "message",
            ),
        ),
        stage=Stage.INIT,
    ),
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
        description="Задать имя участку",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'name',
        ),
        pipeline=(
            lambda x: ("amqp", x[0].get('method', '').lower() or x[2], x[1]['exchange'].lower()),
            partial(pipe_sep_string, **{'sep': ('::', ' (', ')')}),
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, 'message'),
            Origin(OriginSection.POINT_ARGS, 'config'),
            Origin(OriginSection.POINT_ARGS, 'routing_key'),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Наименование партнерского сервиса сохранить для "
                    "переиспользования",
        destination=Destination(
            DestinationSection.REUSE,
            'peer_name',
        ),
        pipeline=(
            pipe_head,
            lambda v: v.get('exchange', v.get('exchange_name')),
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, 'config'),
        ),
        stage=Stage.INIT,
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
        description="Вывести тело сообщения в аннотации",
        destination=Destination(DestinationSection.SPAN_LOGS, 'message'),
        pipeline=(
            pipe_head,
            # pipe_catch_essential,
            pipe_dump,
            pipe_cut,
            pipe_mask_secret_catch_essentials,
            lambda x: x[1],
            PipeCommand.TEE,
            Destination(DestinationSection.SPAN_TAGS, {}),
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.REUSE, "message",
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
